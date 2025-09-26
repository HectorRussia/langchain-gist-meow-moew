from pprint import pprint
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI
import requests
from bs4 import BeautifulSoup
import json
from langchain.agents.react.agent import create_react_agent
from langchain.agents import AgentExecutor
from langchain_core.runnables import RunnableLambda
from langchain import hub
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.tools import tool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts.prompt import CRYPTO_ANALYSIS_PROMPT
from schemas.schemas import AgentResponse, CryptoData
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

load_dotenv()

def clean_content(content: str) -> str:
    cleaned = ' '.join(content.split())
    return cleaned

@tool
def url_reader(url: str) -> str:

    """Read content from a URL and return it as JSON.
    
    Args:
        url: The URL to read content from
        
    Returns:
        JSON string containing the URL content, title, and metadata
    """
    try:
      
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        result = {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "No title",
            "content": clean_content(soup.get_text().strip()[:5000]),  # Limit content length
            "status_code": response.status_code,
            "content_type": response.headers.get('content-type', ''),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
   
    except Exception as e:
        error_result = {
            "url": url,
            "error": f"Request failed: {str(e)}",
            "status": "failed"
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


# Export the tool
# url_reader_tool = url_reader

# result = url_reader("https://coinmarketcap.com/")

# print(result)

def safe_parse_output(text: str) -> AgentResponse:
    """Safely parse LLM output, handling different JSON formats"""
    try:
        # Clean the text - remove any markdown formatting
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]  # Remove ```json
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]  # Remove ```
        clean_text = clean_text.strip()
        
        # Try to parse as JSON first
        data = json.loads(clean_text)
        
        # Check if it's already in AgentResponse format
        if "answer" in data:
            output_parser = PydanticOutputParser(pydantic_object=AgentResponse)
            return output_parser.parse(clean_text)
        
        # If it's crypto data format, convert it
        crypto_data = []
        if "cryptocurrencies" in data:
            for crypto in data["cryptocurrencies"]:
                crypto_data.append(CryptoData(
                    name=crypto.get("name", ""),
                    symbol=crypto.get("symbol", ""),
                    price=crypto.get("price", ""),
                    change_24h=crypto.get("change_24h", ""),
                    market_cap=crypto.get("market_cap", ""),
                    volume_24h=crypto.get("volume_24h", ""),
                    rank=str(crypto.get("rank", 0))  # Convert to string
                ))
        
        # Create AgentResponse with crypto data
        return AgentResponse(
            answer=data.get("market_summary", "Cryptocurrency data extracted successfully"),
            sources=[data.get("url", "https://coinmarketcap.com/th/")],
            crypto_data=crypto_data,
            raw_data=clean_text
        )
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Text being parsed: {text[:200]}...")
        # If it's not JSON, treat as plain text
        return AgentResponse(
            answer=text,
            sources=[],
            crypto_data=[],
            raw_data=None
        )
    except Exception as e:
        print(f"General parsing error: {e}")
        # If parsing fails, create a basic AgentResponse
        return AgentResponse(
            answer=f"Error parsing output: {str(e)}",
            sources=[],
            crypto_data=[],
            raw_data=text
        )
url_reader_tool = url_reader

if __name__ == "__main__":
    
    # Test the tool directly
    # result = url_reader("https://coinmarketcap.com/")
    # print("Direct tool result:")
    # print(result)
    
    # Setup agent

    output_parser = PydanticOutputParser(pydantic_object=AgentResponse)

    crypto_prompt = PromptTemplate(
        template=CRYPTO_ANALYSIS_PROMPT,
        input_variables=["input", "agent_scratchpad", "tool_names", "tools"],
    ).partial(format_instructions=output_parser.get_format_instructions())
   
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o", 
        api_version="2024-12-01-preview", 
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # print("ssssssssssssssss " , llm.invoke(input = result))

    # Create agent with proper tools list
    tools = [url_reader_tool]  # Must be a list
    
    agent = create_react_agent(
        llm=llm,
        tools=tools,  # Pass list of tools
        prompt=crypto_prompt
    )
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    extract_output = RunnableLambda(lambda x: x["output"])
    parse_output = RunnableLambda(lambda x: safe_parse_output(x))
    
    chain = agent_executor | extract_output | parse_output
    
   # ...existing code...
    def main():
        result = chain.invoke(
            input={
                "input": "Please read the content from https://coinmarketcap.com/th/ and return it as JSON"
            }
        )
        
        print("\n" + "="*60)
        print("🚀 CRYPTOCURRENCY MARKET ANALYSIS")
        print("="*60)
        
        # Market Summary
        print(f"\n📊 Market Summary:")
        print(f"   {result.answer}")
        
        # Top Cryptocurrencies
        print(f"\n💰 Top {len(result.crypto_data)} Cryptocurrencies:")
        print("-" * 60)
        
        for crypto in result.crypto_data:
            change_icon = "📈" if crypto.change_24h.startswith("+") else "📉"
            print(f"{crypto.rank:2d}. {crypto.name} ({crypto.symbol})")
            print(f"    💵 Price: {crypto.price}")
            print(f"    {change_icon} 24h Change: {crypto.change_24h}")
            print(f"    📊 Market Cap: {crypto.market_cap}")
            print(f"    💹 Volume: {crypto.volume_24h}")
            print()
        
        # JSON Export
        result_dict = {
            "market_summary": result.answer,
            "sources": result.sources,
            "cryptocurrencies": [
                {
                    "rank": crypto.rank,
                    "name": crypto.name,
                    "symbol": crypto.symbol,
                    "price": crypto.price,
                    "change_24h": crypto.change_24h,
                    "market_cap": crypto.market_cap,
                    "volume_24h": crypto.volume_24h
                }
                for crypto in result.crypto_data
            ],
            "total_count": len(result.crypto_data),
            "timestamp": "2024-09-22T00:00:00Z"
        }
        
        print("=" * 60)
        print("📋 JSON OUTPUT:")
        print("=" * 60)
        print(json.dumps(result_dict, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        return result
# ...existing code...
    main()