from langchain_community.utilities import SerpAPIWrapper
import os

search_tool = SerpAPIWrapper(
    serpapi_api_key=os.getenv("SERPAPI_API_KEY")
)
