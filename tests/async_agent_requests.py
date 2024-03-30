import asyncio
import time
import httpx
import json

CHATBOT_URL = "http://localhost:8000/yelp-agent"

async def make_async_post(url, data):
    timeout = httpx.Timeout(timeout=120)
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, timeout=timeout)
        return response
async def make_bulk_requests(url, data):
    tasks = [make_async_post(url, payload) for payload in data]
    responses = await asyncio.gather(*tasks)
    outputs = [r.json()["output"] for r in responses]
    print(outputs)

    return outputs
    
questions=[
    "What category of businesses get the most reviews?"
    "How state has the smallest reviewed department stores?"
    "Which city has the most recreation facilities?"
    # "What are users saying about wedding venues in Illinois?",
    # "What businesses get the most reviews in New York?",
    # "How many sports centers are in California?",
    # "Where do people think were the best party venues in 2022?",
    # "Where do people find cheap clothes in Texas?"
]
request_bodies = [{"text": q} for q in questions]
start_time = time.perf_counter()
outputs = asyncio.run(make_bulk_requests(CHATBOT_URL, request_bodies))
end_time = time.perf_counter()

print(f"Run time: {end_time - start_time} seconds")