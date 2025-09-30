# pip install agno streamlit python-dotenv

import os
import streamlit as st
import datetime
import asyncio
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.cerebras import CerebrasOpenAI

from agno.tools.mcp import MCPTools

load_dotenv()

st.set_page_config(page_title="MCP Assistant", page_icon="🤖", layout="centered")
st.markdown(
    "<h1><span style='color:#fc4503;'>⚡MCP </span><span style='color:#0313fc;'>Assistant</span></h1>",
    unsafe_allow_html=True
)

st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox(
    "Choose Model",
    ["gpt-oss-120b","qwen-3-235b-a22b-instruct-2507"],
    index=0
)

server_url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={os.getenv('TAVILY_API_KEY')}"


if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# User input
# ----------------------------
if prompt := st.chat_input("💬 Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    async def ask_mcp_async(query):
        mcp_tools = MCPTools(transport="streamable-http", url=server_url)
        await mcp_tools.connect()
        try:
            agent = Agent(
                model=CerebrasOpenAI(id=model_choice, api_key=os.getenv("CEREBRAS_API_KEY")),
                tools=[mcp_tools],
                instructions=(
                    f"You are a helpful assistant. "
                    f"Answer user questions at {datetime.datetime.now()} "
                    f"using MCP tools via web search when needed."
                ),
                markdown=True
            )
            return await agent.arun(query)  # <-- async call
        finally:
            await mcp_tools.close()

    # Run async MCP agent
    response = asyncio.run(ask_mcp_async(prompt))

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response.content)

    st.session_state.messages.append({"role": "assistant", "content": response.content})
