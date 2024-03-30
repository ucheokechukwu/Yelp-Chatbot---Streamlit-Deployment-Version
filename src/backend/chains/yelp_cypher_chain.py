import os
import streamlit as st
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# YELP_CYPHER_MODEL=st.secrets["YELP_CYPHER_MODEL")
# YELP_QA_MODEL=st.secrets["YELP_QA_MODEL")
#
# graph = Neo4jGraph(
#     url=st.secrets["NEO4J_URI"),
#     username=st.secrets["NEO4J_USERNAME"),
#     password=st.secrets["NEO4J_PASSWORD"),
# )

YELP_CYPHER_MODEL=st.secrets["YELP_CYPHER_MODEL"]
YELP_QA_MODEL=st.secrets["YELP_QA_MODEL"]

graph = Neo4jGraph(
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
)


graph.refresh_schema() # to sync recent changes

cypher_generation_template="""
Task:
Generate Cypher query for a Neo4j graph database.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Schema:
{schema}

Note:
Do not include any explanations or apologies in yoru responses.
Do not respond to any quyestions that might ask anything other than for you to construct a Cypher statement.
Do not include an text except the generated Cypher statement.
Make sure that the direction of the relationship is corect in your queries.
Make sure you alias both entities and relationships properly.
Do not run any queries that would add to or delete from the database.
Make sure to alias all statements that follow as with statement (e.g. WITH b as b.stars as stars).
If you need to divide numbers make sure to filter the denominator to non-zero.

Examples:
# What department stores in Arizona are closed?
MATCH (b:Business) WHERE b.state='AZ' AND b.categories CONTAINS 'Department Stores' AND b.is_open="0"
RETURN b.name LIMIT 2

# What businesses do the most prolific users (i.e. the users who write the largest number of reviews) write the most about?
MATCH (user:User)-[:WRITES]->(review:Review)<-[:HAS]-(business:Business)
WITH business, COUNT(review) AS review_count
ORDER BY review_count DESC
LIMIT 10
RETURN business.name, business.address, business.city, business.state, review_count


String category values:
Use abbreviations when filtering on state names (e.g. "Texas" is "TX", "Arizona" is "AZ", etc)
Make sure to use IS NULL or IS NOT NULL when analyzing missing properties
You must never include the statement "GROUP BY" in your query. 
Make sure to alias all statements that follow as with statement (e.g. WITH b as business, b.state as
state)
If you need to divide numbers, make sure to filter the denominator to be non zero.

The question is:
{question}
"""

cypher_generation_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=cypher_generation_template
)


qa_generation_template = """You are an assistant that takes the results
from a Neo4j Cypher query and forms a human-readable response. The
query results section contains the results of a Cypher query that was
generated based on a user's natural language question. The provided
information is authoritative, you must never doubt it or try to use
your internal knowledge to correct it. Make the answer sound like a
response to the question.

Query Results:
{context}

Question:
{question}

If the provided information is empty, say you don't know the answer.
Empty information looks like this: []

If the information is not empty, you must provide an answer using the
results. If the question involves a time duration, assume the query
results are in units of days unless otherwise specified.

When names are provided in the query results, such as business names,
beware of any names that have special characters or hyphens. For example "1-800-GOT-JUNK? Central Coast"
a single business name, not multiple hospitals. Make sure you return any list of names in
a way that isn't ambiguous and allows someone to tell what the full
names are.

Never say you don't have the right information if there is data in
the query results. Always use the data in the query results.

Helpful Answer:
"""

qa_generation_prompt = PromptTemplate(
    input_variables=["context", "question"], template=qa_generation_template
)


yelp_cypher_chain = GraphCypherQAChain.from_llm(
    cypher_llm=ChatOpenAI(model=YELP_CYPHER_MODEL, temperature=0),
    qa_llm=ChatOpenAI(model=YELP_QA_MODEL, temperature=0),
    graph=graph,
    verbose=True,
    qa_prompt=qa_generation_prompt,
    cypher_prompt=cypher_generation_prompt,
    validate_cypher=True,
    top_k=100
)