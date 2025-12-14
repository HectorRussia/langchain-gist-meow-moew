from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import AzureChatOpenAI
from prompts.prompt import REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS
from schemas.schemas import AgentResponseMain
from dotenv import load_dotenv

from Build_agent_cypto.read_url_content import tools

load_dotenv()


llm = AzureChatOpenAI(
        azure_deployment="gpt-4o", 
        api_version="2024-12-01-preview", 
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

#react_prompt (ซึ่งเป็น standard ReAct prompt hub.pull("hwchase17/react")) จะไม่ต้องใช้ parse_output 
# Standard ReAct prompt จะให้ output เป็น plain text ไม่ได้มี structured format ที่ต้อง parse เป็น Pydantic object
# react_prompt_with_format_instructions ถึงจะต้องใช้ parse_output เพราะมี format instructions ที่บอกให้ LLM สร้าง output ตาม schema ที่กำหนด
react_prompt = hub.pull("hwchase17/react")

output_parser = PydanticOutputParser(pydantic_object=AgentResponseMain)

react_prompt_with_format_instructions = PromptTemplate(
    template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS, 
    input_variables=["input", "agent_scratchpad", "tool_names","tools"],
).partial(format_instructions=output_parser.get_format_instructions())

# set-up agent ต้องใส่ 3 parameter เทพ นี้น้ะ
agent = create_react_agent(
    llm = llm,
    tools = tools,
    prompt= react_prompt_with_format_instructions,#react_prompt
)

# if use react_prompt not need have parse_output

agent_executor = AgentExecutor(agent= agent,tools=tools, verbose=True)

extract_output = RunnableLambda(lambda x: x["output"])

parse_output = RunnableLambda(lambda x: output_parser.parse(x))

chain  = agent_executor | extract_output | parse_output

def  main():
    result = chain.invoke(
        input={
            "input": "Please read the content from https://crypto.news/sp-500-surges-as-nvidia-bets-big-on-intel/ and return it as JSON",
        }
    )

    print("Your Results",result)

if __name__ == "__main__":
 main()
