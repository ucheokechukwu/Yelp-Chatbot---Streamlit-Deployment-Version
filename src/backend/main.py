from fastapi import FastAPI
from src.backend.agents.yelp_agent import yelp_agent_executor
from src.backend.models.yelp_query import YelpQueryInput, YelpQueryOutput
from src.backend.utils.async_utils import async_retry

app = FastAPI(
    title="Yelp Chatbot 🤖",
    description="Endpoints for a Graph/RAG chatbot for Yelp"
)

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query:str):
    """Retry the agent if the tool fails to run.
    Can happen during intermittent connection issues to external APIs."""
    return await yelp_agent_executor.ainvoke({"input":query})
    
@app.get("/")
async def get_status():
    return {"status":"running"}

@app.post("/yelp-agent")
async def query_yelp_agent(query: YelpQueryInput) -> YelpQueryOutput:
    response = await invoke_agent_with_retry(query.text)
    response['intermediate_steps'] = [str(s) for s in response['intermediate_steps']]
    return response