# YelpBot

### Deployed @ [Yelp Chatbot on Streamlit](https://yelp-chatbot.streamlit.app/)

<span style="color:brown">Currently down due to API credit limits! Check out the demo again at the start of the next month or clone the repo and update the `.streamlit/secrets.toml` file with own API key. </span>.

![Screenshot](images/Screenshot.png)

This chatbot interfaces with a [LangChain](https://python.langchain.com/docs/get_started/introduction) agent designed to answer questions about a subset of users, businesses, and reviews on [Yelp](https://www.yelp.com/).
The agent uses retrieval-augment generation (RAG) over both structured and unstructured data. Data is hosted by [Neo4js](https://neo4j.com/) Graph Database Management System.
Dataset provided by [Yelp](https://www.yelp.com/dataset).

### Credits

- Yelp Dataset provided by [Yelp Open Dataset](https://www.yelp.com/dataset).
- Geomapping and distance calculations based on the API tools provided by [Nominatim Project](https://nominatim.org/) and [Project OSRM](https://project-osrm.org/).

### To Do

1. Restrict to domain-specific queries. ("I can only answer questions pertaining to Yelp data.")
2. ✨ Update `yelp_review_chain`/`Experience` tool, to integrate business identifying information into the embedding for the reviews.
3. ✨ Scale (< 10% total data currently deployed due to github file size limitations.) Goal: Full Yelp datasets, including `tips.csv`. **Update 11.04.2024** - Need to readjust expectations due to space limitations of Neo4js.

- ~~`yelp_agent.py`: Complete `TripTimes` Tool integration.~~ ✅ 29.03.2024
- ~~Deploy on streamlit community cloud.~~ ✅ 30.03.2024
- ~~Enhance TripTimes tool: add query filter for location specification.~~ ✅ 31.03.2024
- ~~`yelp_bulk_csv_write.py`: Fix issues with specifying data types that are affecting aggregation queries.~~ ✅ 31.03.2024
- ~~Add Memory i.e. making the YelpBot a conversational bot.~~ ✅ 09.04.2024
- ~~New Tool: NearestBusiness (formerly ProximityFinder). (find closest business by trip time). `tools/nearestbusiness_chain.py`~~ ✅ 11.04.2024
