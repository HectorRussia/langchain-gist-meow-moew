import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from main import sum_numbers_from_text, sum_numbers_with_complex_output
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

load_dotenv()

model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
llm_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if not model or not llm_api_version:
    
    raise ValueError("Please set the AZURE_OPENAI_DEPLOYMENT_NAME and AZURE_OPENAI_API_VERSION environment variables.")

llm = AzureChatOpenAI(
    azure_deployment=model, 
    api_version=llm_api_version, 
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

tools = [sum_numbers_from_text,sum_numbers_with_complex_output]


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools when needed."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

resp = agent_executor.invoke({"input": "Add 10, 20 and 30"})
print(resp["output"])

