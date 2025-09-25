# 🔗 LangChain Expression Language (LCEL)

**LangChain Expression Language (LCEL)** เป็นวิธีการแบบประกาศ (declarative approach) ที่ใช้ในการสร้าง Runnables ใหม่จาก Runnables ที่มีอยู่แล้ว Runnable ที่สร้างด้วย LCEL มักถูกเรียกว่า **"chain"** และมันจะดำเนินการตาม Runnable Interface อย่างสมบูรณ์

นี่คือตัวอย่างการใช้งาน LCEL ที่แสดงให้เห็นถึงไวยากรณ์และวิธีการประกอบหลัก (Composition Primitives) ที่ใช้ในการสร้าง chain:

---

## 🔄 1. การประกอบแบบเรียงตามลำดับ (Sequential Composition)

การประกอบแบบเรียงตามลำดับคือการนำเอา **output ของ Runnable ตัวหนึ่งไปเป็น input ของ Runnable ตัวถัดไป**

### A. การใช้คลาส RunnableSequence

คุณสามารถสร้าง chain ที่ทำงานตามลำดับได้โดยใช้คลาส `RunnableSequence`:

```python
from langchain_core.runnables import RunnableSequence

chain = RunnableSequence([runnable1, runnable2])
```

การเรียกใช้งาน chain ด้วย `some_input` จะเทียบเท่ากับการที่ `runnable1` ประมวลผล `some_input` และผลลัพธ์จาก `runnable1` จะถูกส่งต่อไปให้ `runnable2` ประมวลผลต่อไป

### B. การใช้ตัวดำเนินการท่อ (| operator) 🔗 (Shorthand)

เนื่องจาก `RunnableSequence` เป็นรูปแบบการใช้งานที่พบบ่อย LangChain จึงมีการกำหนดตัวดำเนินการ `|` (pipe operator) ให้สามารถใช้แทนการสร้าง `RunnableSequence` ได้:

```python
chain = runnable1 | runnable2
```

โค้ดนี้เทียบเท่ากับการใช้ `RunnableSequence([runnable1, runnable2])`

นอกจากนี้ คุณยังสามารถใช้เมธอด `.pipe` แทนตัวดำเนินการ `|` ได้ด้วย:

```python
chain = runnable1.pipe(runnable2)
```

---

## 🔀 2. การประกอบแบบขนาน (Parallel Composition)

การประกอบแบบขนาน (Concurrent) ช่วยให้คุณเรียกใช้ **Runnables หลายตัวพร้อมกัน** โดยใช้ input เดียวกันสำหรับแต่ละตัว

### A. การใช้คลาส RunnableParallel

คุณสามารถสร้าง chain ที่ทำงานแบบขนานได้โดยใช้คลาส `RunnableParallel`:

```python
from langchain_core.runnables import RunnableParallel

chain = RunnableParallel({
    "key1": runnable1,
    "key2": runnable2,
})
```

เมื่อเรียกใช้งาน chain นี้ด้วย `some_input` ผลลัพธ์ที่ได้จะเป็น dictionary ที่มีคีย์ตรงกับที่กำหนดไว้ โดยค่าของแต่ละคีย์จะเป็น output จาก Runnable นั้น ๆ:

```python
{
    "key1": runnable1.invoke(some_input),
    "key2": runnable2.invoke(some_input),
}
```

> **⚡ ข้อดี:** การทำงานนี้จะเกิดขึ้นพร้อมกัน (concurrently) ทำให้เวลาการประมวลผลเร็วขึ้น

### B. การใช้ Dictionary ร่วมกับตัวดำเนินการ | (Automatic Coercion)

ภายในนิพจน์ LCEL (LCEL expression) ตัว **Dictionary จะถูกแปลงเป็น RunnableParallel โดยอัตโนมัติ**:

```python
mapping = {
    "key1": runnable1,
    "key2": runnable2,
}
chain = mapping | runnable3
```

โค้ดด้านบนจะถูกแปลงโดยอัตโนมัติให้เทียบเท่ากับ:

```python
chain = RunnableSequence([RunnableParallel(mapping), runnable3])
```

กล่าวคือ ข้อมูล input จะถูกส่งเข้า `RunnableParallel(mapping)` ก่อน จากนั้น output (ที่เป็น dictionary) จะถูกส่งต่อไปยัง `runnable3`

---

## 🔧 3. การแปลงฟังก์ชันเป็น Runnable (Function Coercion)

ในนิพจน์ LCEL หากคุณใช้ฟังก์ชัน Python ธรรมดา **ฟังก์ชันนั้นจะถูกแปลงเป็น RunnableLambda โดยอัตโนมัติ**:

```python
def some_func(x):
    return x

chain = some_func | runnable1
```

โค้ดนี้ถูกแปลงให้เทียบเท่ากับ:

```python
chain = RunnableSequence([RunnableLambda(some_func), runnable1])
```

---

## ⚙️ 4. ตัวอย่างการใช้เมธอดของ Runnable Interface กับ LCEL

AgentExecutor และองค์ประกอบอื่น ๆ ใน LangChain ล้วน implement มาตรฐาน **Runnable Interface** ซึ่งรวมถึงเมธอดเพิ่มเติมที่สามารถใช้ในการปรับแต่ง chains ที่สร้างด้วย LCEL:

### A. การผูกค่า (Binding Arguments) ด้วย `.bind()`

คุณสามารถผูกอาร์กิวเมนต์เข้ากับ Runnable โดยใช้เมธอด `.bind()` ซึ่งมีประโยชน์เมื่อ Runnable ใน chain ต้องการอาร์กิวเมนต์ที่ไม่ได้มาจาก output ของ Runnable ก่อนหน้า หรือไม่ได้มาจาก input ของผู้ใช้:

```python
# ตัวอย่างการใช้ .bind() เพื่อกำหนด stop sequence
chain = llm.bind(stop=["three"]) | StrOutputParser()

# เมื่อเรียก chain.invoke("Repeat quoted words exactly: 'One two three four five.'")
# Output คือ 'One two' (เนื่องจากมีการหยุดที่ "three")
```

### B. การกำหนดค่าที่สามารถปรับเปลี่ยนได้ (Configurable Runnables)

คุณสามารถสร้าง Runnable ที่สามารถกำหนดค่าต่าง ๆ ได้ในขณะรันไทม์ (runtime) โดยใช้เมธอดที่เกี่ยวข้องกับ Configurable Runnables:

#### 1. 🔧 `.configurable_fields()` (ปรับแต่งคุณลักษณะเฉพาะ)

ใช้เพื่อกำหนดค่าของแอตทริบิวต์เฉพาะใน Runnable เช่น `max_tokens` ของ ChatOpenAI:

```python
model = ChatOpenAI(max_tokens=20).configurable_fields(
    max_tokens=ConfigurableField(
        id="output_token_number",
        name="Max tokens in the output",
        description="The maximum number of tokens in the output",
    )
)

# หากต้องการเปลี่ยนค่า max_tokens เป็น 200 ในขณะรันไทม์:
# model.with_config(configurable={"output_token_number": 200}).invoke(...)
```

#### 2. 🔀 `.configurable_alternatives()` (เลือก Runnable ทางเลือก)

ใช้เพื่อระบุ Runnable ทางเลือกที่สามารถรันได้ในขณะรันไทม์ เช่น การสลับไปมาระหว่างโมเดลภาษาที่แตกต่างกัน:

```python
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-20250219"
).configurable_alternatives(
    ConfigurableField(id="llm"),
    default_key="anthropic",
    openai=ChatOpenAI(),
)

# หากต้องการใช้ ChatOpenAI แทน ChatAnthropic:
# model.with_config(configurable={"llm": "openai"}).invoke(...)
```

### C. 🧠 การใช้ ReAct Agent (ซึ่งเป็น Runnable Sequence)

ฟังก์ชัน `create_react_agent` จะส่งคืน **Runnable sequence** ที่แสดงถึง agent:

```python
# ตัวอย่างโครงสร้างการสร้าง ReAct Agent (AgentExecutor ใช้ Runnable Interface)
agent = create_react_agent(model, tools, prompt)  # agent เป็น Runnable
agent_executor = AgentExecutor(agent=agent, tools=tools)
agent_executor.invoke({"input": "hi"})
```

---

## 🎯 สรุป

โดยรวมแล้ว **ตัวดำเนินการท่อ (`|`)** และ **การแปลงอัตโนมัติของ Dictionary และ Function** เป็นตัวอย่างหลักของ LCEL ที่ช่วยให้การประกอบ "chain" ต่างๆ ใน LangChain ง่ายและกระชับขึ้น

### 🌟 จุดเด่นของ LCEL:

- **🔗 Pipe Operator (`|`)**: ใช้เชื่อมต่อ Runnables อย่างง่ายดาย
- **🔀 Parallel Processing**: ประมวลผลแบบขนานเพื่อความเร็ว
- **🤖 Auto Coercion**: แปลง Dictionary และ Function เป็น Runnable อัตโนมัติ
- **⚙️ Configurable**: ปรับแต่งค่าต่างๆ ได้ในขณะรันไทม์
- **🔧 Flexible Binding**: ผูกค่าพารามิเตอร์ได้อย่างยืดหยุ่น

> **💡 ข้อสำคัญ:** LCEL ทำให้การสร้างและจัดการ LangChain applications ง่ายขึ้น โดยใช้ไวยากรณ์ที่เข้าใจง่ายและมีประสิทธิภาพสูง