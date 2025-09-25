# 📚 LangChain Guide

## 🤖 AgentExecutor

**AgentExecutor** คือ คลาส Agent ที่ใช้เครื่องมือ (tools) ซึ่งทำหน้าที่ควบคุมและจัดการลูปการดำเนินการของ Agent โดยพื้นฐานแล้ว AgentExecutor เป็นส่วนหนึ่งของ Chain และ นำอินเทอร์เฟซ Runnable มาใช้ (implements the standard Runnable Interface)

การที่ AgentExecutor เป็น Runnable ทำให้มันมีเมธอดและคุณสมบัติเพิ่มเติมมากมาย เช่น `with_config`, `with_types`, และ `with_retry`

### 🔧 องค์ประกอบหลักที่จำเป็นสำหรับการทำงาน

เพื่อให้ AgentExecutor สามารถดำเนินการได้ ต้องมีการกำหนดองค์ประกอบสำคัญสองส่วน:

1. **Agent**: คือ Agent ที่จะถูกรันเพื่อ สร้างแผนและกำหนดการดำเนินการ (determining actions) ที่จะใช้ในแต่ละขั้นตอนของลูปการดำเนินการ (execution loop) Agent นี้สามารถเป็น `BaseSingleActionAgent`, `BaseMultiActionAgent`, หรือ `Runnable` ก็ได้

2. **Tools**: คือ ชุดเครื่องมือที่ถูกต้อง (`Sequence[BaseTool]`) ที่ Agent สามารถเรียกใช้ได้ การกำหนดเครื่องมือเหล่านี้เป็นสิ่งที่จำเป็น (Required)

> **💡 เทิพ:** ยังมีวิธีการสร้าง AgentExecutor โดยตรงจาก Agent และ Tools ผ่านเมธอด `from_agent_and_tools`

### ⚙️ กลไกการดำเนินการและการควบคุม

AgentExecutor มีพารามิเตอร์หลายตัวที่ใช้ในการควบคุมและปรับแต่งวิธีการดำเนินการของ Agent:

- **📊 จำนวนรอบสูงสุด (`max_iterations`)**: จำนวนขั้นตอนสูงสุดที่จะดำเนินการก่อนสิ้นสุดลูป โดยค่าเริ่มต้นคือ 15 การตั้งค่าเป็น `None` อาจนำไปสู่ลูปที่ไม่สิ้นสุดได้

- **⏱️ เวลาดำเนินการสูงสุด (`max_execution_time`)**: จำนวนเวลา (wall clock time) สูงสุดที่จะใช้ในลูปการดำเนินการ

- **🛑 วิธีการหยุดก่อนกำหนด (`early_stopping_method`)**: ใช้ในกรณีที่ Agent ไม่ส่งคืน AgentFinish โดยมี 2 วิธี:
  - `'force'`: ส่งคืนสตริงที่ระบุว่าหยุดเนื่องจากถึงขีดจำกัดด้านเวลาหรือจำนวนรอบแล้ว
  - `'generate'`: เรียก LLM Chain ของ Agent เป็นครั้งสุดท้าย เพื่อสร้างคำตอบสุดท้ายโดยอิงจากขั้นตอนที่ผ่านมา

- **🔧 การจัดการข้อผิดพลาดในการแยกวิเคราะห์ (`handle_parsing_errors`)**: กำหนดว่าจะจัดการกับข้อผิดพลาดที่เกิดจาก Output Parser ของ Agent อย่างไร
  - ค่าเริ่มต้นคือ `False` ซึ่งจะยกข้อผิดพลาดขึ้น
  - ถ้าเป็น `True` ข้อผิดพลาดจะถูกส่งกลับไปยัง LLM ในรูปแบบของ "observation"
  - หากเป็นสตริง สตริงนั้นจะถูกส่งไปยัง LLM ในรูปแบบ "observation"
  - หากเป็นฟังก์ชันที่สามารถเรียกได้ (callable function) ฟังก์ชันนั้นจะถูกเรียกด้วยข้อผิดพลาดเป็นอาร์กิวเมนต์ และผลลัพธ์ของฟังก์ชันจะถูกส่งต่อไปยัง Agent ในรูปแบบ "observation"

- **💾 Memory**: สามารถใช้ `BaseMemory` เสริมเพื่อโหลดตัวแปร ณ จุดเริ่มต้นและบันทึกตัวแปรที่ถูกส่งคืนเมื่อสิ้นสุด Chain

- **📋 การคืนค่าขั้นตอนระหว่างกลาง (`return_intermediate_steps`)**: เป็นการตั้งค่าว่าจะให้ส่งคืนวิถีของขั้นตอนระหว่างกลาง (trajectory of intermediate steps) ของ Agent เมื่อสิ้นสุดการทำงาน นอกเหนือจากเอาต์พุตสุดท้ายหรือไม่

### 🔗 อินเทอร์เฟซและการเรียกใช้งาน

เนื่องจาก AgentExecutor เป็นส่วนหนึ่งของ Chain และ implements Runnable จึงรองรับการดำเนินการหลายรูปแบบ:

- **🔄 การเรียกใช้งานปกติ**: เมธอดที่แนะนำสำหรับการแปลงอินพุตเดียวเป็นเอาต์พุตคือ `invoke()` (เมธอดเก่าอย่าง `__call__()` และ `run()` ถูกยกเลิกตั้งแต่เวอร์ชัน 0.1.0 และแนะนำให้ใช้ `invoke()` แทน)

- **⚡ การเรียกใช้งานแบบอะซิงโครนัส**: เมธอดที่แนะนำคือ `ainvoke()` (เมธอดเก่าอย่าง `acall()` และ `arun()` ถูกยกเลิกเช่นกัน)

- **📡 การสตรีมมิ่ง**: รองรับการสตรีมมิ่งผลลัพธ์โดยใช้เมธอด `stream()` (แบบซิงโครนัส) และ `astream()` (แบบอะซิงโครนัส)

- **🚀 การทำงานแบบขนาน**: รองรับการประมวลผลอินพุตหลายรายการพร้อมกันผ่านเมธอด `batch()` และ `abatch()`

---

## ✨ ทำไม AgentExecutor ถึง "Fancy" กว่าลูปธรรมดา

โดยพื้นฐานแล้ว AgentExecutor คือสิ่งที่เข้ามาจัดการและควบคุม **"ลูปการดำเนินการ"** (execution loop) ของ Agent อย่างเป็นทางการและเป็นระบบ ซึ่งทำให้มัน "fancy" กว่าการวนซ้ำทั่วไปมาก

ถ้าเปรียบเทียบกับลูปธรรมดา (เช่น `while True` ในโค้ด) AgentExecutor จะเพิ่มโครงสร้าง การควบคุม และความสามารถที่ซับซ้อนดังนี้:

### 🎯 1. การควบคุมการวนซ้ำ (Controlled Looping)

AgentExecutor ถูกออกแบบมาเพื่อจัดการให้ Agent วนซ้ำการทำงาน (การคิดแผน → การเรียกใช้เครื่องมือ → การรับผลลัพธ์) จนกว่าจะถึงจุดสิ้นสุด โดยมีการควบคุมดังนี้:

- **📊 จำนวนรอบสูงสุด (`max_iterations`)**: กำหนดจำนวนขั้นตอนสูงสุดที่จะดำเนินการก่อนที่ลูปจะสิ้นสุด โดยค่าเริ่มต้นคือ 15 รอบ หากตั้งเป็น `None` อาจนำไปสู่ลูปที่ไม่สิ้นสุดได้

- **⏱️ เวลาดำเนินการสูงสุด (`max_execution_time`)**: กำหนดจำนวนเวลา (wall clock time) สูงสุดที่สามารถใช้ในลูปการดำเนินการได้

- **🛑 การหยุดก่อนกำหนด (`early_stopping_method`)**: เป็นกลไกที่ใช้เมื่อ Agent ไม่สามารถส่งคืน AgentFinish ได้ โดยสามารถตั้งค่าเป็น:
  - `'force'`: ส่งคืนสตริงที่ระบุว่าหยุดเพราะถึงขีดจำกัดเวลาหรือจำนวนรอบแล้ว
  - `'generate'`: จะเรียก LLM Chain ของ Agent เป็นครั้งสุดท้ายเพื่อสร้างคำตอบสุดท้ายโดยอิงจากขั้นตอนที่ผ่านมา

### 🚀 2. ความสามารถแบบ "Fancy" ผ่าน Runnable Interface

ความ "fancy" ที่แท้จริงของ AgentExecutor มาจากการที่มันเป็นคลาส Chain และ นำอินเทอร์เฟซ Runnable มาใช้ (implements the standard Runnable Interface) ซึ่งเป็นองค์ประกอบหลักของ LangChain Expression Language (LCEL)

การเป็น Runnable ทำให้ AgentExecutor รองรับฟังก์ชันการทำงานระดับสูง ซึ่งเป็นสิ่งที่ลูปพื้นฐานทำไม่ได้:

| ความสามารถ | รายละเอียดที่ทำให้ "Fancy" |
|-------------|----------------------------|
| **🔀 การทำงานแบบขนาน (Parallel Execution)** | สามารถรัน AgentExecutor หลายตัวพร้อมกันด้วยอินพุตหลายชุดผ่านเมธอด `batch()` (ซิงโครนัส) และ `abatch()` (อะซิงโครนัส) ซึ่งช่วยลดเวลาแฝงอย่างมาก |
| **📡 การสตรีมมิ่ง (Streaming)** | สามารถส่งคืนผลลัพธ์แบบทีละขั้นตอน (incremental output) ผ่านเมธอด `stream()` และ `astream()` ช่วยให้ผู้ใช้เห็นความคืบหน้าทันที |
| **🔧 การจัดการข้อผิดพลาด** | มีพารามิเตอร์ `handle_parsing_errors` ซึ่งกำหนดวิธีจัดการกับข้อผิดพลาดที่เกิดจาก Output Parser ของ Agent เช่น การส่งข้อผิดพลาดนั้นกลับไปให้ LLM ในรูปแบบ "observation" เพื่อให้ Agent แก้ไขตัวเอง |
| **⚙️ การปรับแต่งที่รันไทม์** | รองรับเมธอดเช่น `with_config` และ `with_retry` ทำให้สามารถเปลี่ยนพฤติกรรมหรือเพิ่มกลไกการลองใหม่ (retry) ได้อย่างง่ายดายโดยไม่ต้องเขียนลูปใหม่ทั้งหมด |

> **🎯 สรุป:** AgentExecutor คือโครงสร้างที่สร้างขึ้นเพื่อวนซ้ำการตัดสินใจและการใช้เครื่องมือของ Agent อย่างมีระบบ, มีการควบคุมขีดจำกัด, มีการจัดการข้อผิดพลาด, และมีความสามารถในการทำงานแบบขนานและการสตรีมมิ่งที่ซับซ้อน ซึ่งทั้งหมดนี้รวมอยู่ในอินเทอร์เฟซมาตรฐาน

---

## 🧠 create_react_agent

`create_react_agent` เป็นฟังก์ชันที่ใช้ใน LangChain เพื่อ **สร้าง Agent ที่ใช้กลไกการกระตุ้นแบบ ReAct** (ReAct prompting) ซึ่งเป็นแนวคิดที่อิงตามบทความวิจัยชื่อ _"ReAct: Synergizing Reasoning and Acting in Language Models"_

Agent ที่ถูกสร้างขึ้นโดยฟังก์ชันนี้จะส่งคืนเป็น **ลำดับของ Runnable**

### ⚠️ คำเตือนสำคัญเกี่ยวกับเวอร์ชัน

การใช้งาน `create_react_agent` นี้เป็น **เวอร์ชันที่เก่ากว่า** และ **ไม่เหมาะสำหรับการใช้งานในแอปพลิเคชันระดับ Production** แหล่งข้อมูลแนะนำว่า หากต้องการใช้งาน ReAct ที่มีความเสถียรและมีฟีเจอร์ที่สมบูรณ์ ควรใช้ฟังก์ชัน `create_react_agent` จากไลบรารี **LangGraph** แทน

### 🔧 องค์ประกอบที่จำเป็นในการสร้าง Agent

ในการใช้ฟังก์ชัน `create_react_agent` จะต้องกำหนดพารามิเตอร์หลักสามตัวเพื่อสร้าง Agent ที่ทำงานได้:

1. **🤖 llm (`BaseLanguageModel`)**: คือ LLM ที่จะถูกใช้เป็นตัว Agent ในการตัดสินใจและสร้างแผน
2. **🛠️ tools (`Sequence[BaseTool]`)**: คือ ชุดเครื่องมือที่ Agent สามารถเข้าถึงได้
3. **📝 prompt (`BasePromptTemplate`)**: คือ Prompt ที่ใช้ในการชี้นำ LLM ให้ทำงานตามรูปแบบ ReAct

### 📋 ข้อกำหนดของ Prompt สำหรับ ReAct

เนื่องจากกลไก ReAct ต้องการให้ Agent สลับระหว่างการคิด (Thought) และการกระทำ (Action) Prompt ที่ใช้จึง **ต้องมีคีย์อินพุตที่กำหนด** เพื่อรองรับข้อมูลการวนซ้ำนี้:

- **🛠️ tools**: จะต้องมีคำอธิบายและ Argument สำหรับเครื่องมือแต่ละชิ้น
- **🏷️ tool_names**: จะต้องมีชื่อของเครื่องมือทั้งหมด
- **📝 agent_scratchpad**: ใช้สำหรับเก็บการดำเนินการของ Agent และเอาต์พุตของเครื่องมือในรอบก่อนหน้าในรูปแบบสตริง (ซึ่งสะท้อนถึงประวัติการคิดและการกระทำ)

รูปแบบมาตรฐานของ ReAct Prompt มักจะชี้นำให้ LLM สร้างเอาต์พุตตามลำดับ **Thought → Action → Action Input → Observation** โดยมีการทำซ้ำไปเรื่อย ๆ จนกว่าจะได้คำตอบสุดท้าย (Final Answer)

### ⚙️ การควบคุมและการส่งคืนผลลัพธ์

- **📤 ผลลัพธ์**: Agent ที่สร้างขึ้นจะส่งคืนผลลัพธ์เป็น `AgentAction` (หากต้องการเรียกใช้เครื่องมือ) หรือ `AgentFinish` (หากได้คำตอบสุดท้ายแล้ว)

- **🎨 tools_renderer**: เป็นฟังก์ชันที่ควบคุมวิธีการแปลงรายการ Tools ให้กลายเป็นสตริงเพื่อนำไปใส่ใน Prompt สำหรับ LLM โดยค่าเริ่มต้นคือ `render_text_description`

- **🛑 stop_sequence**: โดยค่าเริ่มต้นคือ `True` ซึ่งจะ **เพิ่มโทเค็นหยุด ("Observation:")** เพื่อช่วยให้ LLM หยุดสร้างเอาต์พุตที่เกินความจำเป็น ซึ่งเป็นกลไกเพื่อหลีกเลี่ยงการสร้างภาพหลอน (hallucinates)

### 🔗 ความสัมพันธ์กับ AgentExecutor

Agent ที่สร้างโดย `create_react_agent` จะถูกนำไปใช้ร่วมกับ **AgentExecutor** (ตามที่ได้อธิบายในการสนทนาก่อนหน้า) โดย AgentExecutor ทำหน้าที่จัดการ **ลูปการดำเนินการ** โดยรับ Agent ที่ถูกสร้างขึ้น (ในที่นี้คือ Agent แบบ ReAct) และชุดเครื่องมือ (tools) ไปเป็นส่วนประกอบหลัก เพื่อรันกระบวนการทั้งหมด

---

## 🔧 RunnableLambda

`RunnableLambda` คือ **วิธีหลักที่แนะนำในการสร้าง custom Runnable** จากฟังก์ชัน Python ธรรมดา ซึ่งเป็นส่วนสำคัญที่ทำให้คุณสามารถเพิ่มตรรกะการประมวลผลที่กำหนดเอง (arbitrary logic) เข้าไปใน LangChain Expression Language (LCEL) ได้อย่างง่ายดาย

### 🤔 1. คืออะไร

`RunnableLambda` คือคลาสที่ใช้สำหรับ **สร้าง Runnable ที่เป็นฟังก์ชันของคุณเอง** กล่าวคือ มันทำหน้าที่ห่อหุ้มฟังก์ชัน (function) ธรรมดา เพื่อให้ฟังก์ชันนั้นมีคุณสมบัติและเมธอดทั้งหมดของ Runnable Interface

### 🎯 2. ใช้ทำอะไร (วัตถุประสงค์หลัก)

วัตถุประสงค์หลักของ `RunnableLambda` คือ:

#### 🔗 เพิ่มตรรกะที่กำหนดเองใน Chain
เมื่อคุณกำลังประกอบ Runnable หลายตัวเข้าด้วยกันโดยใช้ LCEL (`|` operator) และต้องการแทรกขั้นตอนการประมวลผลข้อมูลแบบกำหนดเอง (custom processing logic) ในระหว่างขั้นตอนใดขั้นตอนหนึ่ง `RunnableLambda` จะเข้ามามีบทบาท

> **💡 ตัวอย่าง:** หากคุณมีรายการเอกสาร (List of Documents) และต้องการแปลงให้เป็นสตริงที่จัดรูปแบบก่อนส่งต่อให้ LLM คุณสามารถใช้ `RunnableLambda` ห่อหุ้มฟังก์ชันการจัดรูปแบบนั้นได้

#### 🔄 การแปลงข้อมูลอย่างง่าย (Simple Transformations)
`RunnableLambda` เหมาะสำหรับงานการแปลงข้อมูลที่ไม่ซับซ้อนและ **ไม่จำเป็นต้องมีการสตรีมมิ่ง** (streaming is not required) 

> **⚠️ หมายเหตุ:** หากงานนั้นซับซ้อนและต้องการการสตรีมมิ่งเอาต์พุต ควรใช้ `RunnableGenerator` แทน

### 🔄 3. การทำงานร่วมกับ LCEL (Coercion)

ใน LangChain Expression Language (LCEL) มีคุณสมบัติที่เรียกว่า **Coercion** ซึ่งช่วยให้โค้ดกระชับขึ้น:

#### 🤖 การแปลงอัตโนมัติ
ภายในนิพจน์ LCEL หากคุณใช้ฟังก์ชัน Python ธรรมดา (`def some_func(x): return x`) ตัวฟังก์ชันนั้นจะถูกแปลงเป็น `RunnableLambda` โดยอัตโนมัติ

```python
# โค้ดที่เขียนแบบย่อใน LCEL
chain = some_func | runnable1

# ถูกแปลงโดยอัตโนมัติเป็น:
chain = RunnableSequence([RunnableLambda(some_func), runnable1])
```

### 🚀 4. ประโยชน์เพิ่มเติมในฐานะ Runnable

เนื่องจาก `RunnableLambda` ห่อหุ้มฟังก์ชันให้เป็น Runnable อย่างสมบูรณ์ ทำให้ฟังก์ชันที่ถูกห่อหุ้มนั้นได้รับคุณสมบัติขั้นสูงทั้งหมดของ Runnable Interface เช่น:

- **⚡ รองรับการดำเนินการแบบอะซิงโครนัส**: `ainvoke()`, `astream()`
- **⚙️ รองรับการกำหนดค่ารันไทม์ (Runtime Configuration)**: สามารถใช้เมธอดต่าง ๆ เช่น `with_config`, `with_listeners`, หรือ `with_alisteners` เพื่อเพิ่มคุณสมบัติ เช่น การจัดการ Callbacks, Tags, หรือ Metadata ในขณะเรียกใช้ได้
- **🔄 รองรับการจัดการข้อผิดพลาดซ้ำ (Retries)**: สามารถเพิ่มกลไกการลองใหม่เมื่อเกิดข้อผิดพลาดโดยใช้ `with_retry`

---

## 📝 การใช้งาน `.partial()` ใน PromptTemplate

### 🎯 คำอธิบาย `.partial()`

`.partial(format_instructions=output_parser.get_format_instructions())` หมายถึงการ **กำหนดค่าให้กับตัวแปร `format_instructions` ล่วงหน้า** ใน PromptTemplate

```python
# format_instructions จะถูกกำหนดค่าล่วงหน้า
react_prompt_with_format_instructions = PromptTemplate(
    template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS, 
    input_variables=["input", "agent_scratchpad", "tool_names","tools"],
).partial(format_instructions=output_parser.get_format_instructions())
```

### 💡 ประโยชน์ของการใช้ `.partial()`:

- ✅ **ไม่ต้องส่ง `format_instructions` ทุกครั้งที่ invoke**
- ✅ **ค่าคงที่** - format instructions จะเหมือนเดิมตลอด
- ✅ **ลดความซับซ้อน** - input variables ที่เหลือจะมีแค่ที่เปลี่ยนแปลงจริงๆ เช่น `input`, `agent_scratchpad` เท่านั้น

> **📌 หมายเหตุ:** โดยปกติถ้าไม่ใช้ `.partial()` คุณจะต้องส่ง `format_instructions` ใน input dict ทุกครั้งที่เรียกใช้ prompt

### 🔄 เปรียบเทียบการใช้งาน:

#### ❌ ถ้าไม่ใช้ `.partial()`:
```python
output_parser = PydanticOutputParser(pydantic_object=AgentResponseMain)
react_prompt_with_format_instructions = PromptTemplate(
    template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS, 
    input_variables=["input", "agent_scratchpad", "tool_names","tools", "format_instructions"],
)

def main():
    result = chain.invoke(
        input={
            "input": "Please read the content from https://crypto.news/sp-500-surges-as-nvidia-bets-big-on-intel/ and return it as JSON",
            "format_instructions": output_parser.get_format_instructions()
        }
    )
    print("Your Results", result)
```

#### ✅ ใช้ `.partial()` (แบบเดิม):
```python
output_parser = PydanticOutputParser(pydantic_object=AgentResponseMain)
react_prompt_with_format_instructions = PromptTemplate(
    template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS, 
    input_variables=["input", "agent_scratchpad", "tool_names","tools"],
).partial(format_instructions=output_parser.get_format_instructions())

def main():
    result = chain.invoke(
        input={
            "input": "Please read the content from https://crypto.news/sp-500-surges-as-nvidia-bets-big-on-intel/ and return it as JSON"
        }
    )
    print("Your Results", result)
```

### 📊 ความแตกต่างสรุป:

| 🔧 การใช้งาน | ❌ ไม่ใช้ `.partial()` | ✅ ใช้ `.partial()` |
|-------------|----------------------|-------------------|
| **input_variables** | ต้องเพิ่ม `"format_instructions"` | ไม่ต้องระบุ `"format_instructions"` |
| **การ invoke** | ต้องส่ง `format_instructions` ทุกครั้ง | ไม่ต้องส่ง `format_instructions` |
| **ความยุ่งยาก** | ยุ่งยากกว่าเพราะต้องจำส่งค่านี้ทุกครั้ง | สะดวกกว่าเพราะค่านี้ถูกกำหนดไว้แล้ว |

> **🎯 สรุป:** การใช้ `.partial()` ทำให้โค้ดสะอาดและใช้งานง่ายกว่า เพราะไม่ต้องส่งค่าที่ไม่เปลี่ยนแปลงซ้ำๆ ทุกครั้ง