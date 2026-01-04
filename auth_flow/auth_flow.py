from typing import Optional, TypedDict

# State
class AuthState(TypedDict):
    username: Optional[str]
    password: Optional[str]
    is_authenticated: Optional[bool]
    output: Optional[str]

"""
    ทำไมต้องใช้ TypedDict + Optional
    TypedDict
    บังคับโครงสร้าง state ให้เหมือนกันทุก node
    ป้องกัน “node นึงคิดว่า field นี้มี แต่อีก node ไม่มี”
    ใน production:
    TypedDict = guardrail ของ agent system
"""

# success state
auth_state_1: AuthState = {
    "username": "Horn123",
    "password": "123H",
    "is_authenticated": True,
    "output": "auth Successful"
}

print(f"auth_state_1: {auth_state_1}")

# Unsuccessful state
auth_state_2: AuthState = {
    "username": "",
    "password": "wrongpassword",
    "is_authenticated": False,
    "output": "auth Unsuccessful"
}

print(f"auth_state_2: {auth_state_2}")

# Node
def input_node(state : AuthState) -> AuthState:

    print(state)

    if state.get("username","") == "":
        state["username"] = input("What is your name")

    password = input("Enter your password: ")

    return {**state , "password":password}

input_node(auth_state_1)
input_node(auth_state_2)

# Defining the Validate Credentials Node
def validate_credentials_node(state : AuthState) -> AuthState:
    username = state.get("username","")
    password = state.get("password","")

    # print("Username: " , username , "Password: ", password)

    # Simulated credential validation
    if username == "test_user" and password == "secure_password":
        is_authenticated = True
    else:
        is_authenticated = False

    return {**state , "is_authenticated": is_authenticated}

print (validate_credentials_node(auth_state_1))

# Correct Format
auth_state_3: AuthState = {
    "username":"test_user",
    "password":  "secure_password",
    "is_authenticated": False,
    "output": "Authentication failed. Please try again."
}
print(f"auth_state_3: {auth_state_3}")
print (validate_credentials_node(auth_state_3))


# Defining the Success Node
def success_node(state:AuthState) -> AuthState:
    return {**state,"output": "Auth successful! Welcome"}

success_node(auth_state_3)

# Defining the Failure Node
def failure_node(state: AuthState) -> AuthState:
    return {**state , "output": "Auth Failure 🤬 "}


# Defining the Router Node
# หัวใจของ LangGraph นี่แหละที่ทำให้กราฟ “ตัดสินใจ” ได้
def router(state : AuthState) -> str:
    if state["is_authenticated"] is True :
        return "success_node"
    else:
        return "failure_node"
    
# ทำไมต้อง is True?
# เพราะ Optional[bool] อาจเป็น None และเราอยากให้ None ไป failure
# Creating the Graph

from langgraph.graph import StateGraph , END

workflow = StateGraph(AuthState)

workflow.add_node("InputNode", input_node)
workflow.add_node("ValidateCredential", validate_credentials_node)
workflow.add_node("Success", success_node)
workflow.add_node("Failure", failure_node)


# Edges
workflow.add_edge("InputNode","ValidateCredential")

# Adding the Edge Between Success Node and END
workflow.add_edge("Success", END)

# Adding the Edge Between Failure Node and InputNode
workflow.add_edge("Failure", "InputNode")

# Conditional Edges มีลักษณะพการเขียนได้หลายท่ามาก
workflow.add_conditional_edges(
    "ValidateCredential",
    router,{
        "success_node":"Success", #key need match
        "failure_node":"Failure"
    })

# Setting endpoint
# This method sets the starting point for the workflow.
# we start at Input right?
workflow.set_entry_point("InputNode")


# Compiling the Workflow
app = workflow.compile()


# Running the Applications
inputs = {"username": "test_user"}
result = app.invoke(inputs)

print(result)
