import os
import time
import requests
import streamlit as st
from backend import entrypoint

CHATBOT_URL = st.secrets["CHATBOT_URL"]

with st.sidebar:
    
    st.header("Status Update (11.04.2024)")
    st.markdown(
        """Due to API credit limits, the demo is down. It will be live again on 01.05.2024. Interested users can clone the repo and update the secrets.toml file accordingly to test-run its functionality."""
    )
    
    st.header("About")
    st.markdown(
        """
                This chatbot interfaces with a
                [LangChain](https://python.langchain.com/docs/get_started/introduction)
                agent to answer questions about (a subset of) users, businesses, 
                and reviews on [Yelp](https://www.yelp.com/). Dataset provided by [Yelp](https://www.yelp.com/dataset).
                The agent uses  retrieval-augment generation (RAG) over both
                structured and unstructured data. Data is hosted by [Neo4js](https://neo4j.com/) Graph Database Management System.
                """
    )
    st.header("Example Questions")
    st.markdown("- Where do people think were the best party venues in 2022?")
    st.markdown("- Which state has the lowest reviewed department stores?")
    st.markdown("- Which city has the most recreation facilities?")
    st.markdown("- Where do people find cheap clothes in Texas?")
    st.markdown("- How quickly can you get to Jon's Bar & Grille from 767 S 9th St, Philadelphia?")
    

    
st.title("YelpBot 🤖")
st.info(
    "Ask me questions about businesses, reviews, users and travel times!"
)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []    
    
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        if "output" in message.keys():
            st.markdown(message['output'])
        if "explanation" in message.keys():
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])
                
if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user", "output":prompt})
    # data = {"text": prompt}
    data = {"input": prompt, "chat_history":st.session_state.chat_history}
    
    with st.spinner("The 🤖 is thinking..."):
        response = requests.post(CHATBOT_URL, json=data)
        if response.status_code == 200:
            output_text = response.json()["output"]
            explanation = response.json()["intermediate_steps"]
            st.session_state.chat_history += ['Human: '+prompt+'\nAI: '+output_text+'\n']
        else:
            output_text = """An error occurred while processing your message.
            Please try again or rephrase your message."""
            explantion = output_text
    
    st.chat_message("assistant").markdown(output_text)
    st.status("How was this generated", state="complete").info(explanation)
    
    st.session_state.messages.append(
        {"role": "assistant",
        "output": output_text,
        "explanation": explanation
    }
    )
    
    
    