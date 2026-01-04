from typing import Optional, TypedDict


class QAState(TypedDict):
    question: Optional[str]
    context: Optional[str]
    answer: Optional[str]
    valid: Optional[bool]
    error: Optional[str]


qa_state_example = QAState(
    question="What is the purpose of this guided project?",
    context="This project focuses on building a chatbot using Python.",
    answer=None
)

# for key , value in qa_state_example.items():
#     print(f"key is {key} & value is {value}")

# Input Validation Node
def input_validation(state: QAState) -> QAState:

    question = state.get("question","").strip()

    if not question:
        return {**state , "valid": False,"error": "Question cannot be empty."}
    
    return {**state ,"valid": True}

# input_validation(qa_state_example)

# Context Provider
def context_provider_node(state: QAState) -> QAState:
    question = state.get("question","")

    if "langgraph" in question.lower() or "guided project" in question.lower():

        context = (
            "This guided project is about using LangGraph, a Python library to design state-based workflows. "
            "LangGraph simplifies building complex applications by connecting modular nodes with conditional edges."
        )

        return {**state,"context": context}
    
    return {**state,"context": None}

# Integration LLM for QA workflow
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

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
# QANode = จุดเดียวที่ “อนุญาตให้ LLM พูด”
def llm_qa_node(state: QAState) -> QAState:
    question = state.get("question","")
    context = state.get("context","")

    # Guard
    # Anti Hallucination gate
    if not context:
        return {"answer": "I don't have enough context to answer that your question."}
    
    # Construct the prompt dynamically
    prompt = f"Context: {context}\nQuestion: {question}\nAnswer the question based on the context provided."

    try:
        response = llm.invoke(prompt)

        return {**state , "answer": response.content.strip()}
    
    except Exception as e:
        return {**state , "answer": f"An error occurred while generating the answer: {str(e)}"}


def should_continue_after_validation(state: QAState) -> str:
    """Determine the next step after input validation"""
    if state.get("valid", False):
        return "ContextProviderNode"
    else:
        return "END"

#  Creating the QA Workflow Graph
from langgraph.graph import StateGraph , END

# ทุก node ใน workflow นี้ จะสื่อสารกันผ่าน QAState เท่านั้น
# initialize the state-based graph
qa_workflow = StateGraph(QAState)


qa_workflow.add_node("InputNode", input_validation)
qa_workflow.add_node("ContextProviderNode", context_provider_node)
qa_workflow.add_node("QANode", llm_qa_node)


# บอก LangGraph ว่า state แรกจะถูกส่งเข้า node ไหนเป็นอันดับแรก
qa_workflow.set_entry_point("InputNode")

qa_workflow.add_conditional_edges(
    "InputNode",
    should_continue_after_validation,
    {
        "ContextProviderNode": "ContextProviderNode",
        "END": END
    }
)

qa_workflow.add_edge("ContextProviderNode", "QANode")

# (ในภาพเขียนเป็น “final edge” ไป END)
# แนวคิดคือ:
# หลังตอบเสร็จ ให้ workflow “จบ” ทันที
qa_workflow.add_edge("QANode", END)


# compile() = แปลง “กราฟ” ให้เป็น “โปรแกรมที่รันได้”
qa_app = qa_workflow.compile()

print("=== Testing QA Workflow ===\n")

questions = [
    "What is the weather today?",
    "What is LangGraph?", 
    "What is the best guided project?"
]

for idx, question in enumerate(questions, start=1):
    print(f"Question {idx}: {question}")
    result = qa_app.invoke({"question": question})
    print(f"Answer {idx}: {result.get("answer","No answer generated.")}\n")
    print("-"*50 + "\n")