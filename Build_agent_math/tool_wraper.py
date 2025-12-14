from langchain_core.tools import Tool , tool
import re


def add_numbers(inputs: str) -> str:
    # @tool ต้องมีคำอธิบายของ tool เป็น metadata
    """Adds a list of numbers from a string and returns the result."""
    #numbers = [int(x) for x in inputs.replace(",","").split() if x.isdigit()]
    # Use regular expressions to extract all numbers from the input
    numbers = [int(num) for num in re.findall(r'\d+', inputs)]
    result = sum(numbers)
    return {"result" : result}

# The `Tool` class in LangChain serves as a structured wrapper that converts regular Python functions into agent-compatible tools. Each tool needs three key components:
add_tool=Tool(
        name="AddTool",
        func=add_numbers,
        description="Adds a list of numbers and returns the result.")

# Tool name
# print("Tool Name:")
# print(add_tool.name)

# # Tool description
# print("Tool Description:")
# print(add_tool.description)

# # Tool function
# print("Tool Function:")
# print(add_tool.invoke)