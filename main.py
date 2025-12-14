import os
from typing import Dict, List , Union
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import  tool
import re

load_dotenv()

model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
llm_api_version = os.getenv("AZURE_OPENAI_API_VERSION")


@tool
def add_numbers(inputs: str) -> str:
    """Adds a list of numbers from a string and returns the result."""
    #numbers = [int(x) for x in inputs.replace(",","").split() if x.isdigit()]
    # Use regular expressions to extract all numbers from the input
    numbers = [int(num) for num in re.findall(r'\d+', inputs)]
    result = sum(numbers)
    return {"result" : result}

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
