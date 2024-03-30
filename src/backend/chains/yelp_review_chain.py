import os
import streamlit as st
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate)
    
YELP_QA_MODEL=st.secrets["YELP_QA_MODEL"]

neo4j_vector_index = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="reviews",
    node_label="Review",
    text_node_properties=["text", "stars", "date", 
                        'business_name', 'business_state', 'business_categories'],
    embedding_node_property="embedding",
    # join_statement="""
    # MATCH (Review:Review)<-[h:HAS]-(Business:Business)
    # RETURN Review.text AS text,
    #        Review.stars AS stars,
    #        Review.date AS date,
    #        Business.name AS business_name,
    #        Business.state AS business_state,
    #        Business.categories AS business_categories
    # """
)

review_template = """Your job is to use user reviews to answer questions about their experience at the businesses.
Use the following context to answer questions. Be as detailed as possible, but don't make up any information
that is not from the context. If you don't know the answer, say you don't know.
{context}"""

review_system_prompt = SystemMessagePromptTemplate(
                                prompt=PromptTemplate(
                                        input_variables=['context'],
                                        template=review_template
                                        ))
review_human_prompt = HumanMessagePromptTemplate(
                                prompt=PromptTemplate(
                                        input_variables=['question'],
                                        template='{question}'
                                        ))
messages = [review_system_prompt, review_human_prompt]

review_prompt = ChatPromptTemplate(
                    input_variables=['context', 'question'], messages=messages
                    )

reviews_vector_chain = RetrievalQA.from_chain_type(
                        llm=ChatOpenAI(model=YELP_QA_MODEL, temperature=0),
                        chain_type='stuff',
                        retriever=neo4j_vector_index.as_retriever(k=12)
                        )
reviews_vector_chain.combine_documents_chain.llm_chain.prompt = review_prompt