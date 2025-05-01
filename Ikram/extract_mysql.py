from sqlalchemy import create_engine, inspect

engine = create_engine("mysql+pymysql://root:abc@localhost:3306/preposyandu")

inspector = inspect(engine)
tables = inspector.get_table_names()

tabel_info = {}

for table_name in tables:
    columns = inspector.get_columns(table_name)
    tabel_info[table_name] = {}
    for col in columns:
        tipe = str(col["type"]).split(" ")[0].replace('"utf8mb4_unicode_ci"', "").replace("COLLATE", "").strip()
        tabel_info[table_name][col["name"]]=tipe

# for table_name in tables:
#     columns = inspector.get_columns(table_name)
#     info = {
#         "tabel": table_name,
#         "kolom": []
#     }

#     for col in columns:
#         tipe = str(col["type"]).split(" ")[0].replace('"utf8mb4_unicode_ci"', "").replace("COLLATE", "").strip()
#         info["kolom"].append({
#             "nama": col["name"],
#             "tipe": tipe
#         })
#     tabel_info.append(info)

import json
print(json.dumps(tabel_info, indent=2))
