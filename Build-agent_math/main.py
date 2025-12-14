import os
from typing import Dict, List , Union
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import  tool
import re

load_dotenv()

model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
llm_api_version = os.getenv("AZURE_OPENAI_API_VERSION")



#  using @tool decorator
# The recommended way to create tools is using the @tool decorator
@tool
# หรือจะใส่แบบนี้ 
# @tool(description="Adds a list of numbers from a string and returns the result")
def add_numbers(inputs: str) -> str:
    # @tool ต้องมีคำอธิบายของ tool เป็น metadata
    """Adds a list of numbers from a string and returns the result."""
    #numbers = [int(x) for x in inputs.replace(",","").split() if x.isdigit()]
    # Use regular expressions to extract all numbers from the input
    numbers = [int(num) for num in re.findall(r'\d+', inputs)]
    result = sum(numbers)
    return {"result" : result}

#  เมื่อใช้ @tool ตัว decorator จะคืนค่าเป็น StructuredTool (object) แทนฟังก์ชันเดิม ดังนั้น add_numbers("1 2") จะกลายเป็นการเรียก 
# object ที่ไม่สามารถถูก call ได้ 

# print("Name: \n", add_numbers.name)
# print("Description: \n", add_numbers.description) 
# print("Args: \n", add_numbers.args) 

# test_input = "what is the sum between 10, 20 and 30 " 
# print(add_numbers.invoke(test_input))  # Example usage of the tool



# @tool-StructuredTool

# Comparing the tool vs Tool class approach

# print("Tool Constructor Approach:")

# print(f"Has Schema: {hasattr(add_tool, 'args_schema')}")
# print("\n")

# print("@tool Decorator Approach:")


# print(f"Has Schema: {hasattr(add_numbers, 'args_schema')}")
# print(f"Args Schema Info: {add_numbers.args}")
 

@tool
def add_numbers_with_options(numbers: List[float], absolute: bool = False) -> float:
    """
    Adds a list of numbers provided as input.

    Parameters:
    - numbers (List[float]): A list of numbers to be summed.
    - absolute (bool): If True, use the absolute values of the numbers before summing.

    Returns:
    - float: The total sum of the numbers.
    """
    if absolute:
        numbers = [abs(n) for n in numbers]
    return sum(numbers)

# print(f"Args Schema Info: {add_numbers_with_options.args}")
# print(f"Args Schema Info: {add_numbers.args}")

# print(add_numbers_with_options.invoke({"numbers":[-1.1,-2.1,-3.0],"absolute":False}))
# print(add_numbers_with_options.invoke({"numbers":[-1.1,-2.1,-3.0],"absolute":True}))

@tool
def sum_numbers_with_complex_output(inputs: str) -> Dict[str, Union[float, str]]:
    """
    Extracts and sums all integers and decimal numbers from the input string.

    Parameters:
    - inputs (str): A string that may contain numeric values.

    Returns:
    - dict: A dictionary with the key "result". If numbers are found, the value is their sum (float). 
            If no numbers are found or an error occurs, the value is a corresponding message (str).

    Example Input:
    "Add 10, 20.5, and -3."

    Example Output:
    {"result": 27.5}
    """
    matches = re.findall(r'-?\d+(?:\.\d+)?', inputs)
    if not matches:
        return {"result": "No numbers found in input."}
    try:
        numbers = [float(num) for num in matches]
        total = sum(numbers)
        return {"result": total}
    except Exception as e:
        return {"result": f"Error during summation: {str(e)}"}

@tool
def sum_numbers_from_text(inputs: str) -> float:
    """
    Adds a list of numbers provided in the input string.
    
    Args:
        text: A string containing numbers that should be extracted and summed.
        
    Returns:
        The sum of all numbers found in the input.
    """
    # Use regular expressions to extract all numbers from the input
    numbers = [int(num) for num in re.findall(r'\d+', inputs)]
    result = sum(numbers)
    return result

# Key parameters of initialize_agent

# tools- see above

# llm see above

# agent:

# Specifies the reasoning framework for the agent.
# "zero-shot-react-description" enables:
# Zero-shot reasoning: The agent can solve tasks it hasn't seen before by thinking through the problem step by step.
# React framework: A logical loop of:
# Reason → Think about the task.
# Act → Use a tool to perform an action.
# Observe → Check the tool's output.
# Plan → Decide what to do next.
# verbose:

# If True, it prints detailed logs of the agent's thought process.
# Useful for debugging or understanding how the agent makes decisions.

def main():

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
    
    response = llm.invoke("What is tool calling in langchain?")
    print("\nResponse Content: ", response.content)



if __name__ == "__main__":
    main()
