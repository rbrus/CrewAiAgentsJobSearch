import json
import os
from langchain.tools import tool
import requests
from crewai_tools import ScrapeWebsiteTool


class SearchTool():
    
    @tool("Search and scrape data from Google Jobs")
    def search_scrape_google_jobs(query):
        """
        Useful to search jobs on google jobs and scrape the data from the jobs available
        """
        params = {
            'q': f'{query}',                        # search string
            'ibp': 'htl;jobs',                            # google jobs
            'hl': 'es-419',                                    # language 
            'gl': 'co',                                    # country of the search
        }
        url = f"https://www.google.com/search?q={params['q']}&ibp={params['ibp']}&hl={params['hl']}&gl={params['gl']}"
        tool = ScrapeWebsiteTool(url)
        text = tool.run()
        return text


    @tool("Search on internet")
    def search_internet(query):
        """
        Useful to search the internet about a given
        topic and return relevant results
        """
        print("Searching the internet...")
        top_result_to_return = 5
        url = "https://google.serper.dev/search"
        payload = json.dumps(
            {"q": query, "gl": "co", "hl": "es"}
        )
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # check if there is an organic key
        if 'organic' not in response.json():
            return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
        else:
            results = response.json()['organic']
            string = []
            print("Results:", results[:top_result_to_return])
            for result in results[:top_result_to_return]:
                try:
                    # Attempt to extract the date
                    string.append('\n'.join([
                        f"Title: {result['title']}",
                        f"Link: {result['link']}",
                        f"Snippet: {result['snippet']}",
                        "\n-----------------"
                    ]))
                except KeyError:
                    next

            return '\n'.join(string)
        
    @tool("Scrape data from website")
    def scrape_website(link):
        """
        Useful to scrape data from a website in case needed

        """
        tool = ScrapeWebsiteTool(link)
        text = tool.run()
        return text