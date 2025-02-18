from agents_data_models import find_closest_repo, RunSQLReturnPandas, SearchIssues, SearchSummaries, one_step_agent, summarize_content
from ingest import get_conn

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

                                     
async def test_embedding_search_with_sql(query):
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

async def test_one_step_agent(query):
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
    print(resp)
    tools = [tool for tool in resp]
    print(tools)
    #> [SearchSummaries(query='endpoint connectivity pods kubernetes', repo='kubernetes/kubernetes')]

    result = await tools[0].execute(conn, limit)

    summary = summarize_content(result, query)
    #> Users face endpoint connectivity issues in Kubernetes potentially due to networking setup errors with plugins like Calico, misconfigured network interfaces, and lack of clear documentation that hinders proper setup and troubleshooting. Proper handling of these aspects is essential for ensuring connectivity between different pods.
    
    return summary.summary