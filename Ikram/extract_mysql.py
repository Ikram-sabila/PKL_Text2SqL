from sqlalchemy import create_engine, inspect

engine = create_engine("mysql+pymysql://root:abc@localhost:3306/preposyandu")

inspector = inspect(engine)
tables = inspector.get_table_names()

tabel_info = []

for table_name in tables:
    columns = inspector.get_columns(table_name)
    info = {
        "tabel": table_name,
        "kolom": [] 
    }

    for col in columns:
        info["kolom"].append({
            "nama": col["name"],
            "tipe": str(col["type"])
        })
    tabel_info.append(info)

from pprint import pprint
pprint(tabel_info)

# Optional: print sebagai JSON agar lebih rapi
# import json
# print(json.dumps(tabel_info, indent=2, ensure_ascii=False))
