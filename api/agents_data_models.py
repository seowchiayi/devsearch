from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, Iterable, Union
from jinja2 import Template
from openai import OpenAI
from ingest import get_conn
from asyncio import run



class SearchIssues(BaseModel):
    """
    Use this when the user wants to get original issue information from the database 
    """

    query: Optional[str]
    repo: str = Field(
        description="the repo to search for issues in, should be in the format of 'owner/repo'"
    )

    @field_validator("repo")
    def validate_repo(cls, v: str, info: ValidationInfo):
        matched_repo = find_closest_repo(v, info.context["repos"])
        if matched_repo is None:
            raise ValueError(
                f"Unable to match repo {v} to a list of known repos of {info.context['repos']}"
            )
        return matched_repo

    async def execute(self, conn, limit: int):
        if self.query:
            embedding = (
                OpenAI()
                .embeddings.create(input=self.query, model="text-embedding-3-small")
                .data[0]
                .embedding
            )
            args = [self.repo, limit, embedding]
        else:
            args = [self.repo, limit]
            embedding = None

        sql_query = Template(
            """
            SELECT *
            FROM {{ table_name }}
            WHERE repo_name = '{{ repo_name }}'
            {%- if embedding is not none %}
            ORDER BY embedding <=> '{{ embedding }}'
            {%- endif %}
            LIMIT {{ limit }}
            """
        ).render(table_name="github_issues", repo_name=self.repo, limit=limit, embedding=embedding)

        return await conn.fetch(sql_query, *args)
 
class RunSQLReturnPandas(BaseModel):
    """
    Use this function when the user wants to do time-series analysis or data analysis and we don't have a tool that can supply the necessary information
    """

    query: str = Field(description="Description of user's query")
    repos: list[str] = Field(
        description="the repos to run the query on, should be in the format of 'owner/repo'"
    )
    async def execute(self, conn, limit: int):
        pass


class SearchSummaries(BaseModel):
    """
		This function retrieves summarized information about GitHub issues that match/are similar to a specific query, It's particularly useful for obtaining a quick snapshot of issue trends or patterns within a project.
    """

    query: Optional[str] = Field(description="Relevant user query if any")
    repo: str = Field(
        description="the repo to search for issues in, should be in the format of 'owner/repo'"
    )

    @field_validator("repo")
    def validate_repo(cls, v: str, info: ValidationInfo):
        matched_repo = find_closest_repo(v, info.context["repos"])
        if matched_repo is None:
            raise ValueError(
                f"Unable to match repo {v} to a list of known repos of {info.context['repos']}"
            )
        return matched_repo

    async def execute(self, conn, limit: int):
        if self.query:
            embedding = (
                OpenAI()
                .embeddings.create(input=self.query, model="text-embedding-3-small")
                .data[0]
                .embedding
            )
            args = [self.repo, limit, embedding]
        else:
            args = [self.repo, limit]
            embedding = None
        sql_query = Template(
            """
            SELECT *
            FROM {{ table_name }}
            WHERE repo_name = '{{ repo_name }}'
            {%- if embedding is not none %}
            ORDER BY embedding <=> '{{ embedding }}'
            {%- endif %}
            LIMIT {{ limit }}
            """
        ).render(table_name="github_issue_summaries", repo_name=self.repo, limit=limit, embedding=embedding)
        
        cur = conn.cursor()
        cur.execute(sql_query)

        return cur

from fuzzywuzzy import process

def find_closest_repo(query: str, repos: list[str]) -> str | None:
    if not query:
        return None

    best_match = process.extractOne(query, repos)
    return best_match[0] if best_match[1] >= 80 else None

def test_fuzzywuzzy():
    repos = [
        "rust-lang/rust",
        "kubernetes/kubernetes",
        "apache/spark",
        "golang/go",
        "tensorflow/tensorflow",
        "MicrosoftDocs/azure-docs",
        "pytorch/pytorch",
        "Microsoft/TypeScript",
        "python/cpython",
        "facebook/react",
        "django/django",
        "rails/rails",
        "bitcoin/bitcoin",
        "nodejs/node",
        "ocaml/opam-repository",
        "apache/airflow",
        "scipy/scipy",
        "vercel/next.js",
    ]

    test = [
        ["kuberntes", "kubernetes/kubernetes"],
        ["next.js", "vercel/next.js"],
        ["scipy", "scipy/scipy"],
        ["", None],
        ["fakerepo", None],
    ]

    for query, expected in test:
        assert find_closest_repo(query, repos) == expected
    
def test_agentic_tooling_with_openai():
    tests = [
        [
            "What is the average time to first response for issues in the azure repository over the last 6 months? Has this metric improved or worsened?",
            [RunSQLReturnPandas],
        ],
        [
            "How many issues mentioned issues with Cohere in the 'vercel/next.js' repository in the last 6 months?",
            [SearchIssues],
        ],
        [
            "What were some of the big features that were implemented in the last 4 months for the scipy repo that addressed some previously open issues?",
            [SearchSummaries],
        ],
    ]
    for query, expected_result in tests:
        response = one_step_agent(query)
        for expected_call, agent_call in zip(expected_result, response):
            assert isinstance(agent_call, expected_call)

                                     
async def test_embedding_search_with_sql():
    conn = await get_conn()
    limit = 10
    resp_cur = await SearchSummaries(query=query, repo="kubernetes/kubernetes").execute(
        conn, limit
    )
    for buff in resp_cur:
        row = {}
        c = 0
        for col in resp_cur.description:
            row.update({str(col[0]): buff[c]})
            c += 1
        print(row["text"])


def one_step_agent(question: str, repos):
    import instructor
    import openai

    client = instructor.from_openai(
        openai.OpenAI(), mode=instructor.Mode.PARALLEL_TOOLS
    )

    repos = [
        "rust-lang/rust",
        "kubernetes/kubernetes",
        "apache/spark",
        "golang/go",
        "tensorflow/tensorflow",
        "MicrosoftDocs/azure-docs",
        "pytorch/pytorch",
        "Microsoft/TypeScript",
        "python/cpython",
        "facebook/react",
        "django/django",
        "rails/rails",
        "bitcoin/bitcoin",
        "nodejs/node",
        "ocaml/opam-repository",
        "apache/airflow",
        "scipy/scipy",
        "vercel/next.js",
    ]

    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that helps users query and analyze GitHub issues stored in a PostgreSQL database. Search for summaries when the user wants to understand the trends or patterns within a project. Otherwise just get the issues and return them. Only resort to SQL queries if the other tools are not able to answer the user's query.",
            },
            {"role": "user", "content": Template(
                    """
                    Here is the user's question: {{ question }}
                    Here is a list of repos that we have stored in our database. Choose the one that is most relevant to the user's query:
                    {% for repo in repos %}
                    - {{ repo }}
                    {% endfor %}
                    """
                ).render(question=question, repos=repos),
            },
        ],
        validation_context={"repos": repos},
        response_model=Iterable[
            Union[
                RunSQLReturnPandas,
                SearchIssues,
                SearchSummaries,
            ]
        ],
    )

import instructor
from pydantic import BaseModel
from asyncpg import Record
from typing import Optional
from jinja2 import Template
from openai import OpenAI

class Summary(BaseModel):
    chain_of_thought: str
    summary: str

def summarize_content(issues: list[Record], query: Optional[str]):
    client = instructor.from_openai(OpenAI())
    return client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You're a helpful assistant that summarizes information about issues from a github repository. Be sure to output your response in a single paragraph that is concise and to the point.""",
            },
            {
                "role": "user",
                "content": Template(
                    """
                    Here are the relevant issues:
                    {% for issue in issues %}
                    - {{ issue['text'] }}
                    {% endfor %}
                    {% if query %}
                    My specific query is: {{ query }}
                    {% else %}
                    Please provide a broad summary and key insights from the issues above.
                    {% endif %}
                    """
                ).render(issues=issues, query=query),
            },
        ],
        response_model=Summary,
        model="gpt-4o-mini",
    )


async def test_one_stop_agent(query):
    #query = "What are the main issues people face with endpoint connectivity between different pods in kubernetes?"
    repos = [
        "rust-lang/rust",
        "kubernetes/kubernetes",
        "apache/spark",
        "golang/go",
        "tensorflow/tensorflow",
        "MicrosoftDocs/azure-docs",
        "pytorch/pytorch",
        "Microsoft/TypeScript",
        "python/cpython",
        "facebook/react",
        "django/django",
        "rails/rails",
        "bitcoin/bitcoin",
        "nodejs/node",
        "ocaml/opam-repository",
        "apache/airflow",
        "scipy/scipy",
        "vercel/next.js",
    ]

    resp = one_step_agent(query, repos)

    conn = await get_conn()
    limit = 10

    tools = [tool for tool in resp]
    print(tools)
    #> [SearchSummaries(query='endpoint connectivity pods kubernetes', repo='kubernetes/kubernetes')]

    result = await tools[0].execute(conn, limit)

    summary = summarize_content(result, query)
    
    return summary.summary
    #> Users face endpoint connectivity issues in Kubernetes potentially due to networking setup errors with plugins like Calico, misconfigured network interfaces, and lack of clear documentation that hinders proper setup and troubleshooting. Proper handling of these aspects is essential for ensuring connectivity between different pods.

if __name__ == "__main__":
    query = "What are the main problems people are facing with installation with Kubernetes"
    run(test_one_stop_agent())
    

    