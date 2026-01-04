from langgraph.graph import StateGraph, END,START
from typing import TypedDict
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, StateGraph
from IPython.display import display , Image
from dotenv import load_dotenv
import os

load_dotenv()

# Exercises: Building a Multi-Agent Routing System with LangGraph

model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
llm_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

def print_workflow_info(workflow,app=None):
    
    """Prints comprehensive information about a LangGraph workflow."""
    print("WORKFLOW INFORMATION")
    print("====================")
    print(f"Nodes: {workflow.nodes}")
    print(f"Edges: {workflow.edges}")

    try:
        finish_points = workflow.finish_points
        print(f"Finish Points: {finish_points}")
    except:
        try:
            # Alternative approaches
            print(f"Finish point: {workflow._finish_point}")
        except:
            print("Finish points attribute not directly accessible")

    if app:
        print("\nWorkflow Visualization:")
       
        display(app.get_graph().draw_png())

llm = AzureChatOpenAI(
    azure_deployment=model, 
    api_version=llm_api_version, 
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

class ChainState(TypedDict):
    job_description: str
    resume_summary: str
    cover_letter: str


# Resume Summary Agent
def generate_resume_summary(state: ChainState) -> ChainState:

    prompt = f"""
        You're a resume assistant. Read the following job description and summarize the key qualifications and experience the ideal candidate should have, phrased as if from the perspective of a strong applicant's resume summary.

        Job Description:
        {state['job_description']}
    """

    response = llm.invoke(prompt)

    return {**state, "resume_summary": response.content}


#  Generate Cover Letter Agent

def generate_cover_letter(state: ChainState) -> ChainState:
    prompt = f"""
        You're a cover letter assistant. Using the following job description and resume summary, draft a compelling cover letter tailored to the job.

        Job Description:
        {state['job_description']}

        Resume Summary:
        {state['resume_summary']}
    """

    response = llm.invoke(prompt)

    return {**state, "cover_letter": response.content}

workflow = StateGraph(ChainState)
workflow.add_node("generate_resume_summary", generate_resume_summary)
workflow.add_node("generate_cover_letter", generate_cover_letter)

workflow.set_entry_point("generate_resume_summary")

workflow.add_edge("generate_resume_summary", "generate_cover_letter")
# workflow.add_edge("generate_cover_letter", END) ถ้า END มันจบโฟวเลย

workflow.set_finish_point("generate_cover_letter")

print_workflow_info(workflow)

app = workflow.compile()

print("\n=== WORKFLOW GRAPH (ASCII) ===")
print(app.get_graph().draw_ascii())

input_state = {
        "job_description": "We are looking for a data scientist with experience in machine learning, NLP, and Python. Prior work with large datasets and experience deploying models into production is required."
}

result = app.invoke(input_state)

print("=== Generated Resume Summary ===\n")
print(result["resume_summary"])


#  Workflow Pattern : Routing

