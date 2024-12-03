from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from github import Github
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import uvicorn
import requests
import openai
import os
import re
import markdown

load_dotenv()  # load environment variables
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("NEXT_PUBLIC_VERCEL_URL")],  # Allow the Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



openai.api_key = os.getenv("OPENAI_API_KEY")
# initialize github api
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN") 
GITHUB = Github(GITHUB_ACCESS_TOKEN)
GITHUB_API_BASE = "https://api.github.com/repos/"

class Message(BaseModel):
    content: str

@app.post("/chat")
async def chat(message: Message):
    # Mock response - in a real scenario, this would search the internal documentation
    response = f"You asked about: {message.content}. This is a mock response from the internal documentation system."
    return {"response": response}


# function to convert string to list
# used for formatting the chatgpt response
def string_to_list(faq,list):
    faq_items = faq.split("\n")

    for item in faq_items:
        if re.match(r'^Q\d', item):  # Check if item starts with a digit
            break
        faq_items.remove(item)
    
    for index in range(len(faq_items)):
        item = faq_items[index]
        temp = []
        
        if (not (item.isspace() or item == "")) and re.match(r'^Q\d', item):
            temp.append(item)
            answer = []
            
            while index < len(faq_items) - 1 and not re.match(r'^Q\d', faq_items[index + 1]):
                answer.append(faq_items[index + 1])
                index += 1
                
            answer = " ".join(answer)
            temp.append(answer)
            list.append(temp)
    return list



def process_file(file,index):
    faqs = []
    url = file[0]
    content = file[1]
    number_of_questions = 5
    
    if content is None:
        return []   
    
    # if file is in database and up to date, return directly stored faq
    # enumaration is done here, in order to keep it consistent
    # if is_up_to_date(url):
    #     stored_faq = get_faq(url)     
    #     for i,faq in enumerate(stored_faq):
    #         question_number = faq[0].split('.')[0]
    #         updated_question = faq[0].replace(question_number, f"Q{index}")
    #         stored_faq[i][0] = updated_question
    #         index += 1
        
    #     return stored_faq
    prompt = (
        f"Generate {number_of_questions} frequently asked questions (FAQ) for the following content."        
        f"First, read the content and choose a question that you think users may ask frequently, consider the parts where users may struggle to understand the content and require assistance. Detect the most complex and complicated sections."
        f"Then, rewrite the question you've chosen first as a title and after writing the question as a title, under that title, provide the answer to the question."
        f"Afterwards, repeat the same process for all generated questions one by one, rewriting the question first then answering the question under the question."
        f"I want these question and answer paragraphs enumerated, starting from {index} to {index + number_of_questions - 1}"
        f"Questions must start with Q letter"
        f"For example:\n"
        f"Q{index}. How to write prompts?\n"
        f"In order to write prompts, you need to ....\n"
        f"{index + 4}. How to edit a written prompt?\n"
        f"Editing a prompt is easy, you need to.....\n"
        f"Content :\n{content}"
    )

    message_history = []
    message_history.append({"role": "user", "content": prompt})
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = message_history
    )

    faq = response.choices[0].message.content
    #string_to_list(faq, faqs)
    
    #store_faq(url, faq)
    return faq


@app.post("/url")
async def chat(message: Message):
    urls = [message.content.split(" has been uploaded")[0]]
    # return {"response": message.content}
    contents = []
    content_info = []
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}
    
    for url in urls:
        content_info.append(url)
        #current_content = get_markdown_content(url, headers)
        response = requests.get(url, headers)
        response.raise_for_status()
        
        if response.status_code == 200:
            if url.endswith('.md'):
                current_content = response.text
                html_content = markdown.markdown(current_content)  # or use markdown2.markdown() if using markdown2
                def trim_markdown_content(markdown_text):
                    # Simple heuristic to remove certain sections, e.g., examples, credits, etc.
                    trimmed_lines = []
                    skip_section = False
                    
                    for line in markdown_text.splitlines():
                        if "Example" in line or "Credit" in line:
                            skip_section = True
                        elif skip_section and line.startswith("#"):
                            skip_section = False
                        if not skip_section:
                            trimmed_lines.append(line)
                    
                    return "\n".join(trimmed_lines)

                trimmed_content = trim_markdown_content(html_content)

        if current_content == -1:
            return -1
        
        content_info.append(trimmed_content)
        contents.append(content_info)
        content_info = []
        
     #return contents

    if contents == -1:
        return -1
    
    #generate_faq_multithreaded(contents)
    faqs = []
    index = 1
    number_of_questions = 5
    # with ThreadPoolExecutor() as executor:
    #     futures = []
    for file in contents:
        faq = process_file(file, index)
        #     future = executor.submit(process_file, file, index)
        #     futures.append(future)
        #     index += number_of_questions
            
        # for future in futures:
        #     faqs.extend(future.result())
    return {"response": faq}
    #return {"response": message.content}

    
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

