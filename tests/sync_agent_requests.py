import time
import requests
import json

CHATBOT_URL = "http://localhost:8000/yelp-agent"

questions=[
    "What are users saying about wedding venues in Illinois?",
    "What businesses get the most reviews in New York?",
    "How many sports centers are in California?",
    "Where do people think were the best party venues in 2022?",
    "Where do people find cheap clothes in Texas?"
]
request_bodies = [{"text": q} for q in questions]
start_time = time.perf_counter()
outputs = [requests.post(CHATBOT_URL, json=data) for data in request_bodies]
print(outputs)
end_time = time.perf_counter()

print(f"Run time: {end_time - start_time} seconds")


