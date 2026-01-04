import random
import string
from typing import TypedDict

from langgraph.graph import StateGraph, END


# Exercise 1 - Define the State type
# Here, you will define the state schema used by the graph. It should keep track of:
# - `n`: a counter starting from 1.
# - `letter`: a randomly generated lowercase letter at each step.

class CounterState(TypedDict):
    n: int
    letter: str

# Exercise 2 - Create `add()` node Function

# This node should represent the `increment` step such that:
# - It adds 1 to the current value of n.
# - It randomly selects a lowercase letter and updates the letter field.

def add(state: CounterState) -> CounterState:
    new_n = state["n"] + 1
    new_letter = random.choice(string.ascii_lowercase)
    return {**state , 
            "n": new_n, 
            "letter": new_letter
    }

# Exercise 3 - Create `print_out()` node Function
# This node should print the current state such that:
# - It logs the value of n and the current random letter.
# - The state is returned.

def print_out(state: CounterState) -> CounterState:
    print(f"n: {state['n']}, letter: {state['letter']}")
    return state

# Exercise 4 - Stop Condition
# Create a function that has a termination condition:
# - If the counter reaches 13 or more, the workflow should end.
# - Otherwise, it should loop back to add node.
def stop_condition(state: CounterState) -> bool:
    return state["n"] >= 13


# Exercise 5 - Graph Construction

# In this exercise, you'll build the LangGraph flow:

# - Create a `StateGraph` object using the `ChainState` that you made.
# - Add nodes `add` and `print`.
# - Add an edge between `add` and `print`
# - Add a conditional edge between `print` and `END` based on `stop_condition`.
# - Set `add` as entry point of the graph.

workflow = StateGraph(CounterState)

workflow.add_node("AddNode", add)
workflow.add_node("PrintNode", print_out)
workflow.set_entry_point("AddNode")

workflow.add_edge("AddNode", "PrintNode")
workflow.add_conditional_edges(
    "PrintNode",
    lambda state: "END" if stop_condition(state) else "AddNode",
    {
        "END": END,
        "AddNode": "AddNode"
    }
)
#  เขียนได้หลายท่า
# workflow.add_conditional_edges("print", stop_condition, {
#     True: END,
#     False: "add",
# })

# Exercise 6 - Compile and Run
# Compile the graph and start execution with the given initial input:
# - The counter should begin at 1.
# - Keep letter empty (to be filled in by the add node).
my_app = workflow.compile()
results = my_app.invoke({"n": 1, "letter": ""})


