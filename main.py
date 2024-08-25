import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from Tools.search_tool import SearchTool

import gradio as gr

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential
from langchain_groq import ChatGroq

credential = DefaultAzureCredential()
os.environ["OPENAI_API_TYPE"] = "azure_ad"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
os.environ["AZURE_OPENAI_API_KEY"] = credential.get_token("https://cognitiveservices.azure.com/.default").token

llmOpenAi = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2023-03-15-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
    # dimensions: Optional[int] = None, # Can specify dimensions with new text-embedding-3 models
    openai_api_version="2023-05-15",
)

llmGroq = ChatGroq(
    model="mixtral-8x7b-32768", #'gemma2-9b-it'
    #api_key = os.environ['GROQ_KEY'],
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

duckduckgo_search = DuckDuckGoSearchRun()

def create_crewai_setup(job_role, country, ideal_position):
    # Define Agents
    duckduckgo_job_searcher = Agent(
        role="DuckDuckGo Job Search Expert",
        goal=f"""Search through duck duck go job postings by jon role {job_role}, ideal job position {ideal_position} in country {country}
                 and suggest other relevant job roles""",
        backstory=f"""Expert at searching through duck duck go search to find particular jobs offer.""",
        verbose=True,
        llm=llmGroq,
        allow_delegation=True,
        tools=[duckduckgo_search],
    )
    
    google_job_searcher = Agent(
        role="Google Job Search Expert",
        goal=f"""Search through google job postings by jon role {job_role}, ideal job position {ideal_position} in country {country}
                 and suggest other relevant job roles""",
        backstory=f"""Expert at searching through google search to find particular jobs offer.""",
        verbose=True,
        llm=llmGroq,
        allow_delegation=True,
        tools=[SearchTool.search_scrape_google_jobs, SearchTool.scrape_website],
    )
    
    internet_job_searcher = Agent(
        role="Internet Job Search Expert",
        goal=f"""Search through internet job postings by jon role {job_role}, ideal job position {ideal_position} in country {country}
                 and suggest other relevant job roles""",
        backstory=f"""Expert at searching through internet search to find particular jobs offer.""",
        verbose=True,
        llm=llmGroq,
        allow_delegation=True,
        tools=[SearchTool.search_internet, SearchTool.scrape_website],
    )

    job_search_expert = Agent(
            role="Job Search Expert",
            goal=f"""Provide recommendations for job role {job_role} in country {country} and ideal job position {ideal_position} or similar for the user""",
            backstory=f"""Expert at providing recommendations for job role {job_role} in country {country} and ideal job position {ideal_position} or similar for the user""",
            verbose=True,
            llm=llmGroq,
            allow_delegation=True,
        )
    
    job_search_task = Task(
        description=f"""Provide recommendations for job role {job_role} in country {country} and ideal job position {ideal_position} or similar for the user""",
        agent=job_search_expert,
        llm=llmGroq,
        expected_output="A list of job recommendations including job title, company, location, and a brief description."
    )

    job_search_crew = Crew(
        agents=[duckduckgo_job_searcher, google_job_searcher, internet_job_searcher],
        tasks=[job_search_task],
        verbose=True,
        process=Process.sequential,
    )

    crew_result = job_search_crew.kickoff()

    return crew_result

def run_crewai_app(job_role, country, ideal_position):
    crew_result = create_crewai_setup(job_role, country, ideal_position)
    return crew_result

iface = gr.Interface(
    fn=run_crewai_app, 
    inputs=["text", "text", "text"], 
    outputs="text",
    title="CrewAI Agentic job searches platform",
    description="Enter your ideal job role, ideal position and country to support you in your job searches."
)

iface.launch()
