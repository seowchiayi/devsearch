# Table of Contents
- [Table of Contents](#table-of-contents)
- [DevSearch](#devsearch)
  - [Features](#features)
  - [Installation](#installation)
  - [Deployment](#deployment)
  - [Conclusion](#conclusion)

# DevSearch

DevSearch is an app for mid level developers to make their first open source contribution. [See the demo here](https://www.loom.com/share/0923becbdd234c34a9be19cac3bc2acd?sid=49d97a9d-9552-4f2b-8790-43c25c4342ee)

## Features

- Answers questions like `How many issues mentioned issues with Cohere in the 'vercel/next.js' repository in the last 6 months?` and `What were some of the big features that were implemented in the last 4 months for the scipy repo that addressed some previously open issues?`

## Installation

If you want to examine the source code or change some things according to your needs, you can install it by following these steps:

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/seowchiayi/devsearch.git
   ```

2. Install the required dependencies:
   ```
   bun install
   ```
   ```
   pip install -r requirements.txt
   ```

3. Now you need to set up environment variables by creating a .env file in the project root directory and adding the following variables:
  
  - GITHUB_ACCESS_TOKEN
  - OPENAI_API_KEY
  - SUPABASE_URI
  - HF_TOKEN

4. As the last step, you can run the program on your local machine by entering this command into your console:
   ```
   bun run dev
   ```
   You can access the interface by navigating to http://localhost:3000 in your web browser.

## Deployment

We hosted our application on Vercel. It can be hosted anywhere that supports Next.js frontend and FastAPI backend. If you also want to use [Vercel](https://vercel.com/login), you'll need to create an account and follow these steps:

1. Install the Vercel Command Line Interface (CLI) tool globally on your machine using npm or yarn. This CLI tool allows you to deploy projects directly from your terminal.
   ```
   bun install -g vercel
   ```

2. Once the CLI is installed, log in to your Vercel account from the terminal using the following command:
   ```
   vercel login
   ```
3. Then, you can initialize your project. Navigate to your project directory and use the following command:
   ```
   vercel init
   ```
   This command will prompt you to link your project directory to a Vercel project. Follow the prompts to select your project and configure deployment settings.

4. Once the project is initialized, you can deploy it to Vercel. This command will start the deployment process and upload your project files to Vercel's servers. Once the deployment is complete, Vercel will provide you with a unique URL where your application is hosted.
   ```
   vercel --prod
   ```

As you can see, hosting your website on Vercel is a straightforward process. Even though Vercel originally offers frontend hosting servers,  its support for serverless functions enables you to effortlessly host your backend as well. Additionally, Vercel offers templates that serve as excellent starting points for your projects. In this project, I used [nextjs&fastapi template](https://vercel.com/templates/next.js/nextjs-fastapi-starter). You can find other templates on the resources page of the Vercel site.

## Credits
Check out the [original open source repo](https://github.com/timescale/rag-is-more-than-vector-search) I am building this on top of
