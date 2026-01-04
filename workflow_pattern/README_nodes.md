README — การตั้งชื่อ Node ใน LangGraph (Implicit vs Explicit)

Purpose

สรุปความแตกต่างระหว่างการเพิ่ม node แบบ implicit และ explicit ใน `StateGraph` พร้อมตัวอย่าง, แนวปฏิบัติ และวิธีตรวจสอบ

Quick Summary

- Implicit: `graph.add_node(translate_to_french)` — ไลบรารีใช้ `translate_to_french.__name__` เป็น node id อัตโนมัติ
- Explicit: `graph.add_node("translate_french", translate_to_french)` — คุณกำหนด node id เอง (ชัดเจน ป้องกันการชนชื่อ)

พฤติกรรมหลัก

- Implicit name:
  - ใช้ชื่อฟังก์ชันเป็น id อัตโนมัติ เช่น `"translate_to_french"`.
  - สะดวกเมื่อชื่อฟังก์ชันไม่ซ้ำและอ่านได้ชัดเจน.

- Explicit name:
  - ระบุ id ด้วยสตริงเอง เหมาะเมื่อต้องการชื่อที่สั้นกว่า/สื่อความหมายต่างจากชื่อฟังก์ชัน หรือต้องการหลีกเลี่ยงการชนชื่อ.

การอ้างอิง (edges, entry, finish)

เมธอดเช่น `add_edge`, `set_entry_point`, `set_finish_point` มักรับได้ทั้ง `str` หรือ object ฟังก์ชัน — ภายในจะ normalize เป็น node id (string).

ตัวอย่างที่ใช้งานได้ทั้งสองรูปแบบ:

- `graph.add_edge("translate_to_french", "aggregator")`
- `graph.add_edge(translate_to_french, aggregator)`
- `graph.set_entry_point("translate_to_french")` หรือ `graph.set_entry_point(translate_to_french)`

ตัวอย่าง (ตัวอย่างสั้น):

- Implicit:
```python
graph.add_node(translate_to_french)
graph.add_edge(START, translate_to_french)
```

- Explicit:
```python
graph.add_node("translate_french", translate_to_french)
graph.add_edge("START", "translate_french")
```

ข้อดี / ข้อเสีย (สรุป):

- Implicit:
  - + โค้ดสั้น, อ่านสะดวกเมื่อไม่มีข้อจำกัด
  - - เสี่ยงชนชื่อ (lambda/partial/ฟังก์ชันซ้ำ)

- Explicit:
  - + ชัดเจน, ป้องกันชนชื่อ, ดีต่อ visualization/เอกสาร
  - - ต้องเขียนชื่อเพิ่ม แต่ทำให้ intent ชัดเจน

Best Practices (คำแนะนำ):

- ถ้าโปรเจคเล็ก ฟังก์ชันชื่อชัดเจน และไม่มีความเสี่ยงชนชื่อ: ใช้ `add_node(func)` สะดวกดี.
- ถ้าโปรเจคใหญ่ มีหลายโมดูล/หลายทีม หรือใช้ lambdas/partials, หรือต้องการชื่อที่คนอ่านเข้าใจเร็ว: ใช้ `add_node("my_node_name", func)` เพื่อความปลอดภัยและอ่านง่าย.
- ตั้ง coding-style ให้ทีม: เลือกแบบหนึ่งแล้วใช้ให้สม่ำเสมอ (explicit names มักลดปัญหาในระยะยาวได้มากสุด).

Debugging & Inspection (ตรวจสอบสถานะ):

- ดู node ids ที่จริง:
```python
print(workflow.nodes.keys())
```
- ดู edges:
```python
print(workflow.edges)
```
- ตรวจสอบ entry/finish:
```python
print(getattr(workflow, "finish_points", getattr(workflow, "_finish_point", None)))
```

Decision Checklist (จะเลือกแบบไหน):

- ต้องการชื่อกำหนดเองหรือไม่? → ใช้ explicit.
- ฟังก์ชันเป็น lambda/partial หรือชื่อซ้ำ? → ใช้ explicit.
- ต้องการโค้ดกระชับและชื่อฟังก์ชันชัดเจน? → ใช้ implicit.

Appendix — ตัวอย่างไฟล์เล็กๆ:

Implicit:
```python
graph.add_node(translate_to_french)
graph.add_node(translate_to_spanish)
graph.add_edge(START, translate_to_french)
```

Explicit:
```python
graph.add_node("translate_fr", translate_to_french)
graph.add_node("translate_es", translate_to_spanish)
graph.add_edge("START", "translate_fr")
```

ถ้าต้องการ ผมช่วยปรับไฟล์ `parallel_pattern.py` ให้ใช้ explicit names ทั้งหมด แล้วรันให้ดูผลได้ครับ.