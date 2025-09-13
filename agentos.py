from agno.os import AgentOS
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.models.google import Gemini
import os
from dotenv import load_dotenv
load_dotenv()

web_research_agent = Agent(
    model=Gemini(id="gemini-2.5-flash",api_key=os.getenv("GOOGLE_API_KEY")),
    tools=[FirecrawlTools(enable_scrape=True, enable_crawl=True,api_key=os.getenv("FIRECRAWL_API_KEY"))],
    markdown=True,
    description="An assistant that can search the web.",
    instructions="You are a helpful assistant. " \
    "Answer user questions using Firecrawl tools when needed.",
)

# Setup AgentOS with MCP enabled
agent_os = AgentOS(
    description="Example app with MCP enabled",
    agents=[web_research_agent],
    enable_mcp=True,  # This enables a LLM-friendly MCP server at /mcp
)

app = agent_os.get_app()

if __name__ == "__main__":
    # Your MCP server will be available at http://localhost:7777/mcp
    agent_os.serve(app="z33:app", reload=True)
