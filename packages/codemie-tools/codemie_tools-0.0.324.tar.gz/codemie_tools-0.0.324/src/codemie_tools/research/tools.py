from typing import Type, Optional

import requests
from bs4 import BeautifulSoup
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_google_community import GoogleSearchAPIWrapper
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.research.tools_vars import (
    WEB_SCRAPPER_TOOL, GOOGLE_SEARCH_RESULTS_TOOL, WIKIPEDIA_TOOL,
    GOOGLE_PLACES_TOOL, GOOGLE_PLACES_FIND_NEAR_TOOL
)
from codemie_tools.research.google_places_wrapper import GooglePlacesAPIWrapper


class WebScrapperToolInput(BaseModel):
    url: str = Field(description="URL or resource to scrape information from.")


class WebScrapperTool(CodeMieTool):
    tokens_size_limit: int = 5000
    name: str = WEB_SCRAPPER_TOOL.name
    description: str = WEB_SCRAPPER_TOOL.description
    args_schema: Type[BaseModel] = WebScrapperToolInput

    def execute(self, url: str):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        raw_text_content = soup.get_text()
        return raw_text_content


class GoogleSearchResultsInput(BaseModel):
    query: str = Field(description="Query to look up in Google.")


class GooglePlacesSchema(BaseModel):
    query: str = Field(description="Query for google maps")


class GooglePlacesFindNearSchema(BaseModel):
    current_location_query: str = Field(
        description="Detailed user query of current user location or where to start from")
    target: str = Field(description="The target location or query which user wants to find")
    radius: Optional[int] = Field(description="The radius of the search. This is optional field")


class GoogleSearchResults(CodeMieTool):
    name: str = GOOGLE_SEARCH_RESULTS_TOOL.name
    description: str = GOOGLE_SEARCH_RESULTS_TOOL.description
    num_results: int = 10
    api_wrapper: GoogleSearchAPIWrapper
    args_schema: Type[BaseModel] = GoogleSearchResultsInput

    def execute(self, query: str):
        return str(self.api_wrapper.results(query, self.num_results))


class GooglePlacesTool(CodeMieTool):
    name: str = GOOGLE_PLACES_TOOL.name
    description: str = GOOGLE_PLACES_TOOL.description
    api_wrapper: GooglePlacesAPIWrapper
    args_schema: Type[BaseModel] = GooglePlacesSchema

    def execute(self, query: str) -> str:
        return self.api_wrapper.places(query)


class GooglePlacesFindNearTool(CodeMieTool):
    name: str = GOOGLE_PLACES_FIND_NEAR_TOOL.name
    description: str = GOOGLE_PLACES_FIND_NEAR_TOOL.description
    api_wrapper: GooglePlacesAPIWrapper
    args_schema: Type[BaseModel] = GooglePlacesFindNearSchema
    default_radius: int = 10000

    def execute(self, current_location_query: str, target: str, radius: Optional[int] = default_radius) -> str:
        return self.api_wrapper.find_near(current_location_query=current_location_query, target=target, radius=radius)


class WikipediaQueryInput(BaseModel):
    query: str = Field(description="Query to look up on Wikipedia.")


class WikipediaQueryRun(CodeMieTool):
    name: str = WIKIPEDIA_TOOL.name
    description: str = WIKIPEDIA_TOOL.description
    api_wrapper: WikipediaAPIWrapper
    args_schema: Type[BaseModel] = WikipediaQueryInput

    def execute(self, query: str):
        return self.api_wrapper.run(query)
