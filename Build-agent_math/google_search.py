from langchain_classic.agents import create_tool_calling_agent, AgentExecutor, Tool
from langchain_openai import OpenAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.prompts import ChatPromptTemplate

# 1. Define your tools
search = GoogleSearchAPIWrapper()
tools = [
    Tool(
        name="Google Search",
        description="Search Google for recent events.",
        func=search.run,
    )
]

# 2. Initialize your model
llm = OpenAI(temperature=0)

# 3. Build a simple chat prompt template similar to the older agent behavior
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools when needed."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 4. Create the agent using the modern API and wrap with an executor
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# 5. Run the agent
resp = agent_executor.invoke({"input": "What is the current price of gold?"})
print(resp.get("output"))
