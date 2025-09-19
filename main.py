from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama

from prompt import REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS
from schemas import AgentResponse
from agent_tool import url_reader_tool


tools = [url_reader_tool]

llm = ChatOllama(temperature=0, model="deepseek-r1:1.5b")

react_prompt = hub.pull("hwchase17/react")

output_parser = PydanticOutputParser(pydantic_object=AgentResponse)
react_prompt_with_format_instructions = PromptTemplate(
    template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS, 
    input_variables=["input", "agent_scratchpad", "tool_names","tools"],
).partial(format_instructions=output_parser.get_format_instructions())

agent = create_react_agent(
    llm = llm,
    tools = tools,
    prompt= react_prompt#react_prompt_with_format_instructions,#react_prompt
)

agent_executor = AgentExecutor(agent= agent,tools=tools, verbose=True)

extract_output = RunnableLambda(lambda x: x["output"])
parse_output = RunnableLambda(lambda x: output_parser.parse(x))

chain = agent_executor | extract_output | parse_output

def  main():
    result = chain.invoke(
        input={
            "input": "Please read the content from https://crypto.news/sp-500-surges-as-nvidia-bets-big-on-intel/ and return it as JSON",
        }
    )

    print("Your Results",result)

if __name__ == "__main__":
 main()
