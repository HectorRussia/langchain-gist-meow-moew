import re
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor, Tool
from langchain_openai import AzureChatOpenAI, OpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
llm_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Exercise: Create a power tool to calculate exponents
def calculate_power(input_text: str) -> str:
    """Calculate x^y from a small variety of text inputs and return a string result."""
    # Try to extract expressions like "5^2"
    match = re.search(r"(\d+(?:\.\d+)?)\s*\^+\s*(\d+(?:\.\d+)?)", input_text)
    if match:
        base = float(match.group(1))
        exponent = float(match.group(2))
        return str(base ** exponent)

    # Try to extract expressions like "2 to the power of 3"
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:to\s+the\s+power\s+of)\s*(\d+(?:\.\d+)?)", input_text, re.IGNORECASE)
    if match:
        base = float(match.group(1))
        exponent = float(match.group(2))
        return str(base ** exponent)

    # Fallback: assume two numbers separated by space or comma
    try:
        numbers = [float(num) for num in input_text.replace(",", " ").split()]
        if len(numbers) != 2:
            return "Invalid input. Please provide exactly two numbers."
        base, exponent = numbers
        return str(base ** exponent)
    except ValueError:
        return "Could not parse numbers from input."


power_tool = Tool(
    name="PowerTool",
    func=calculate_power,
    description="Calculates the power of a number (x^y). Input should be two numbers: base and exponent.",
)

tools = [power_tool]

# Minimal model initialization for local testing
llm = AzureChatOpenAI(
    azure_deployment=model, 
    api_version=llm_api_version, 
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
# Prompt template similar to the older initialize_agent behavior
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools when needed."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

resp = agent_executor.invoke({"input": "Calculate 5 to the power of 2."})
print(resp.get("output"))