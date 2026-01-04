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

# Exercises: Building a Multi-Agent Routing System

# Exercise 1 - Create State Management and Router Tool
# Define the state structure and classification tool for your multi-agent routing system. You need to create a TypedDict for state management and a Pydantic model for LLM tool binding.
# Your task: Create the foundational components for routing between ride hailing, restaurant orders, groceries, and default handling.

# TODO: Define your RouterState TypedDict with three fields
class RouterState(TypedDict):
    user_input: str
    task_type: str
    output: str

# TODO: Create a Router BaseModel with proper field description
class Router(BaseModel):
    role: str = Field(
        ..., 
        description="Classify the user request. Return exactly one of: 'ride_hailing_call', 'restaurant_order', 'groceries' and if you do not know output 'default_handler'"
)

# TODO: Bind the router tool to your LLM
llm_router = llm.bind_tools([Router])

# Exercise 2 - Implement Router Logic

# Create the router node function that classifies user input 
# and handles cases where the LLM doesn't return a tool call. 
# Also implement the router decision function.

# Your task: Build the classification logic with proper error handling for unclassified requests.
# TODO: Implement router_node function with tool call handling
# TODO: Add fallback to "default_handler" when no tool calls
# TODO: Create router function that returns task_type from state
def router_node(state: RouterState) -> RouterState:
    response = llm_router.invoke(state['user_input'])
    
    if response.tool_calls:
        tool_call = response.tool_calls[0]['args']['role']
        return {**state, "task_type": tool_call}
    else:
        return {**state, "task_type": "default_handler"}

def router(state: RouterState) -> str:
    return state['task_type']


def ride_hailing_node(state: RouterState) -> RouterState:
    """
    Processes ride hailing requests by extracting pickup/dropoff locations and preferences
    """
    prompt = f"""
    You are a ride hailing assistant. Based on the user's request, extract and organize the following information:
    
    - Pickup location
    - Destination/dropoff location  
    - Preferred ride type (if mentioned)
    - Any special requirements
    - Estimated timing preferences
    
    User Request: "{state['user_input']}"
    
    Provide a clear summary of the ride request with all available details.
    """
    
    response = llm.invoke(prompt)
    
    return {
        **state, 
        "task_type": "ride_hailing_call", 
        "output": response.content.strip()
    }

def restaurant_order_node(state: RouterState) -> RouterState:
    """
    Processes restaurant orders by organizing menu items, quantities, and preferences
    """
    prompt = f"""
    You are a restaurant ordering assistant. Based on the user's request, organize the following information:
    
    - Menu items requested
    - Quantities for each item
    - Special modifications or dietary restrictions
    - Delivery or pickup preference
    - Any timing requirements
    
    User Request: "{state['user_input']}"
    
    Provide a clear, organized summary of the restaurant order with all details.
    """
    
    response = llm.invoke(prompt)
    
    return {
        **state, 
        "task_type": "restaurant_order", 
        "output": response.content.strip()
    }

def groceries_node(state: RouterState) -> RouterState:
    """
    Processes grocery delivery requests with driver pickup service
    """
    prompt = f"""
    You are a grocery delivery assistant for a service where our drivers pick up groceries for customers.
    
    Based on the user's request, organize the following information:
    
    Shopping List:
    - List of grocery items needed
    - Quantities or amounts for each item
    - Brand preferences (if mentioned)
    - Any dietary restrictions or organic preferences
    
    Store Information:
    - Preferred store or location
    - Budget considerations
    - Special instructions for finding items
    
    Delivery Details:
    - Delivery address (if provided)
    - Preferred delivery time window
    - Any special delivery instructions
    - Contact information for driver coordination
    
    Driver Instructions:
    - Substitution preferences (if item unavailable)
    - How to handle out-of-stock items
    - Any items requiring special handling (fragile, cold items)
    - Payment method (if mentioned)
    
    User Request: "{state['user_input']}"
    
    Provide a comprehensive delivery order summary that our driver can use to efficiently shop and deliver groceries. 
    Include estimated pickup time and any special notes for the shopping trip.
    
    Format the response as a clear, organized delivery order that includes all necessary details for our driver service.
    """
    
    response = llm.invoke(prompt)
    
    return {
        **state, 
        "task_type": "groceries", 
        "output": response.content.strip()
    }

def default_handler_node(state: RouterState) -> RouterState:
    prompt = f"""
    I couldn't classify your request into a specific category. 
    Let me provide general assistance for: "{state['user_input']}"
    
    I can help you with:
    - Ride hailing services
    -  Restaurant orders  
    -  Grocery shopping
    
    Please rephrase your request to match one of these services, or if you need assistance with something else, I will connect you with our customer support team who can provide personalized help.
    
    Would you like me to:
    1. Help you rephrase your request for one of our services
    2. Connect you with customer support for additional assistance
    """
    response = llm.invoke(prompt)
    return {**state, "task_type": "default_handler", "output": response.content.strip()}


# Exercise 3 - Assemble the Complete Workflow

# Put all the pieces together by building the StateGraph, adding nodes, 
# setting up routing logic, and compiling the application.

# Your task: Create the complete workflow graph with proper routing and finish points,
#  and call it ```app```.

# TODO: Create StateGraph with RouterState
workflow = StateGraph(RouterState)
# TODO: Add all five nodes (router + 4 processing nodes)
# Add all nodes
workflow.add_node("router", router_node)
workflow.add_node("ride_hailing_call", ride_hailing_node)
workflow.add_node("restaurant_order", restaurant_order_node)
workflow.add_node("groceries", groceries_node)
workflow.add_node("default_handler", default_handler_node)

# TODO: Set router as entry point
# Set entry point
workflow.set_entry_point("router")

# TODO: Add conditional edges with all four routing options
# Add conditional routing
workflow.add_conditional_edges("router", router, {
    "groceries": "groceries", 
    "restaurant_order": "restaurant_order",
    "ride_hailing_call": "ride_hailing_call",
    "default_handler": "default_handler"
})

# TODO: Set finish points for all processing nodes
# Set finish points
workflow.set_finish_point("ride_hailing_call")
workflow.set_finish_point("restaurant_order")
workflow.set_finish_point("groceries")
workflow.set_finish_point("default_handler")

# TODO: Compile the application
# Compile the application
app = workflow.compile()


#  Test case

test_cases = [
    {"user_input": "I need a ride from downtown to the airport at 3pm"},
    {"user_input": "I want to order 2 large pepperoni pizzas for delivery"},
    {"user_input": "I need milk, bread, eggs, and vegetables for the week"},
    {"user_input": "What's the weather like today?"},  # Default/unclassified example
]

for i, test_input in enumerate(test_cases, 1):
    result=app.invoke(test_input)


    print(f"question {test_input["user_input"]}\n")
    print(f"task_type {result['task_type']}\n")
    print(f"output: {result['output']}\n")
    print('-----------------------------------')


#  output 
"""question I need a ride from downtown to the airport at 3pm

task_type ride_hailing_call

output: **Ride Request Summary:**

- **Pickup Location:** Downtown  
- **Destination/Dropoff Location:** Airport  
- **Preferred Ride Type:** Not mentioned  
- **Special Requirements:** None mentioned  
- **Estimated Timing Preferences:** 3:00 PM

-----------------------------------
question I want to order 2 large pepperoni pizzas for delivery

task_type restaurant_order

output: **Restaurant Order Summary:**

- **Menu Items Requested:**  
  - Large Pepperoni Pizza  

- **Quantities for Each Item:**  
  - 2  

- **Special Modifications or Dietary Restrictions:**  
  - None specified  

- **Delivery or Pickup Preference:**  
  - Delivery  

- **Timing Requirements:**  
  - None specified

-----------------------------------
question I need milk, bread, eggs, and vegetables for the week

task_type groceries

output: ### Delivery Order Summary

---

#### **Shopping List**
- **Grocery Items Needed**:
  - Milk (quantity not specified)
  - Bread (quantity not specified)
  - Eggs (quantity not specified)
  - Vegetables (for the week; specific types not specified)
- **Brand Preferences**: None mentioned
- **Dietary Restrictions/Organic Preferences**: None mentioned

---

#### **Store Information**
- **Preferred Store/Location**: Not specified (driver may choose a convenient store with fresh produce and basic grocery items)
- **Budget Considerations**: None mentioned
- **Special Instructions for Finding Items**: Ensure vegetables are fresh and suitable for weekly use.

---
#### **Driver Instructions**
- **Substitution Preferences**: If an item is unavailable, choose a similar alternative (e.g., whole milk if skim milk is unavailable, or a different brand of bread/eggs).
- **Handling Out-of-Stock Items**: Contact the customer for approval before making substitutions.
- **Special Handling**:
  - Milk and eggs should be kept cold during transport.
  - Bread should be handled carefully to avoid squishing.
  - Vegetables should be packed separately to avoid damage.
- **Payment Method**: Not mentioned (driver should confirm payment details with the customer).

---

#### **Estimated Pickup Time**
- **Pickup Time**: Within 1-2 hours of order confirmation (adjust based on customer’s delivery time preference).

---

#### **Special Notes**
- Contact the customer to confirm delivery address, preferred delivery time, and any additional details about the shopping list (e.g., specific types of vegetables, quantities, or brand preferences).
- Ensure all items are fresh and in good condition before checkout.

---

This summary provides all necessary details for the driver to efficiently shop and deliver groceries.

-----------------------------------
question What's the weather like today?

task_type default_handler

output: It seems like you're looking for information about the weather, but the system you're interacting with is designed for specific services like ride-hailing, restaurant orders, or grocery shopping. Here's what you can do:

1. **Rephrase your request**: If your query is related to one of the services mentioned (e.g., needing a ride due to weather conditions or ordering food/groceries), you can reframe your question accordingly.

2. **Connect with customer support**: If your request doesn't fit into these categories, selecting the option to connect with customer support might be the best way to get personalized help.

If you'd like, I can help you rephrase your request or guide you further! Let me know how you'd like to proceed.

-----------------------------------
"""