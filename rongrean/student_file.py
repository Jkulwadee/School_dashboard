import pandas as pd
import json

# อ่านไฟล์ JSON
with open('student.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ตรวจสอบว่าไฟล์ JSON ของคุณมีโครงสร้างอย่างไร
# ถ้าเป็น array ของ objects คุณสามารถแปลงเป็น DataFrame ได้โดยตรง
if isinstance(data, list):
    df = pd.DataFrame(data)
else:
    # ถ้า JSON ของคุณมีโครงสร้างซับซ้อนกว่านี้ คุณอาจต้องปรับเปลี่ยนข้อมูลก่อน
    df = pd.json_normalize(data)

# เขียน DataFrame เป็นไฟล์ CSV
df.to_csv('student.csv', index=False)

