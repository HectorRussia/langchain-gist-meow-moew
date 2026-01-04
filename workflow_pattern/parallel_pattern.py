from langgraph.graph import StateGraph, END,START
from typing import TypedDict
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, StateGraph
from IPython.display import display , Image
from dotenv import load_dotenv
import os

load_dotenv()

model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
llm_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
llm = AzureChatOpenAI(
    azure_deployment=model, 
    api_version=llm_api_version, 
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

class State(TypedDict):
    text: str
    french: str
    spanish: str
    japanese: str
    combined_output: str

def translate_to_french(state: State) -> dict:
    prompt = f"Translate the following text to French:\n\n{state['text']}"
    response = llm.invoke(prompt)
    return {"french": response.content.strip()}

def translate_to_spanish(state: State) -> dict:
    prompt = f"Translate the following text to Spanish:\n\n{state['text']}"
    response = llm.invoke(prompt)
    return {"spanish": response.content.strip()}

def translate_to_japanese(state: State) -> dict:
    prompt = f"Translate the following text to Japanese:\n\n{state['text']}"
    response = llm.invoke(prompt)
    return {"japanese": response.content.strip()}

def aggregator(state: State) -> dict:
    combined = (
        f"French: {state['french']}\n"
        f"Spanish: {state['spanish']}\n"
        f"Japanese: {state['japanese']}"
    )
    return {"combined_output": combined}

graph = StateGraph(State)

graph.add_node("translate_to_french",translate_to_french)
graph.add_node("translate_to_spanish",translate_to_spanish)
graph.add_node("translate_to_japanese",translate_to_japanese)
graph.add_node(aggregator, finish_point=True)

# Connect parallel nodes from START
graph.add_edge(START, "translate_to_french")
graph.add_edge(START, "translate_to_spanish")
graph.add_edge(START, "translate_to_japanese")

# Connect all translation nodes to the aggregator
graph.add_edge("translate_to_french", "aggregator")
graph.add_edge("translate_to_spanish", "aggregator")
graph.add_edge("translate_to_japanese", "aggregator")

# Final Node
graph.add_edge("aggregator", END)

app = graph.compile()

input_text = {
        "text": "Good morning! I hope you have a wonderful day."
}

print("\n=== RUNNING WORKFLOW ===")
result = app.invoke(input_text)

print("\n=== RESULTS ===")
print("Combined Output:")
print(result["combined_output"])