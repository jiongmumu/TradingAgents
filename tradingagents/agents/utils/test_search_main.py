from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import OpenAI  # or your preferred LLM

# Initialize components
llm = OpenAI(temperature=0)
search = DuckDuckGoSearchRun()

# Define tools
tools = [
    Tool(
        name="Web Search",
        func=search.run,
        description="Search the internet for current information"
    )
]

# Create agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use the agent
response = agent.run(""""What are AVGO competitors? Find the top 5 competitors. 
                     For each competitors, call Web search tool with the company name and find the moat. 
                     Finally, compare AVGO with those competitors and summarize the result.""")
print(response)

