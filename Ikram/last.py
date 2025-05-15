import pymysql.cursors
import streamlit as st
import requests
import extract_mysql
import json
import pandas as pd
from sqlalchemy import create_engine
import pymysql

def text_to_sql(prompt):
    relevant_tables = detect_relevant_tables(prompt, extract_mysql.tabel_info)
    schema_string = json.dumps(relevant_tables, indent=2)

    url = "http://localhost:11434/api/generate"
    data = {
        "model": "mistral",
        "prompt": f"""
        You are a helpful assistant that only returns valid MySQL queries. 
        Given the database schema below:

        {schema_string}

        Convert the following question into a valid SQL query. 
        Do not use quotes around column names. Return only the SQL code.

        Question:
        {prompt}

        SQL:
        """,
        "stream": False,
        "temperature": 0.2
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

def detect_relevant_tables(prompt, tabel_info):
    relevant = {}
    prompt_lower = prompt.lower()
    for table, columns in tabel_info.items():
        if table.lower() in prompt_lower:
            relevant[table] = columns
        else:
            for col in columns:
                if col.lower() in prompt_lower:
                    relevant[table] = columns
                    break
    return relevant

def run_sql(sql):
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="abc",
            database="preposyandu",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        print("Hasil dari cursor.fetchall():")
        print(results)
        return pd.DataFrame(results)
        # df = pd.read_sql(sql, conn)
        # conn.close()
        # return df
    except Exception as e:
        return f"❌ Query Execution Error: {str(e)}"


# Streamlit UI
st.set_page_config(page_title="Text to SQL with Mistral", page_icon="🤖")
st.title("💬 Text to SQL Generator + Executor")
st.markdown("Ketik pertanyaan dalam bahasa natural, lalu lihat hasil SQL-nya dan jalankan langsung.")

question = st.text_area("Pertanyaan (Natural Language):", height=150)

sql_result = ""
if st.button("🔍 Convert to SQL"):
    if question.strip() == "":
        st.warning("Masukkan pertanyaan dulu ya.")
    else:
        with st.spinner("Menggunakan Mistral via Ollama..."):
            sql_result = text_to_sql(question)
        st.session_state.generated_sql = sql_result
        st.code(sql_result, language="sql")

if "generated_sql" in st.session_state:
    if st.button("Execute SQL"):
        with st.spinner("Mengeksekusi query..."):
            result = run_sql(st.session_state.generated_sql)
            if isinstance(result, pd.DataFrame):
                st.success("✅ Query berhasil dijalankan!")
                
                st.write("Isi DataFrame:", result.head())
                st.dataframe(result)
            else:
                st.error(result)

            # st.write("Isi DataFrame:")
            # st.code(st.session_state.generated_sql)
            # st.write(result.head())

            # if isinstance(result, pd.DataFrame):
            #     st.success("✅ Query berhasil dijalankan!")
            #     st.dataframe(result)
            # else:
            #     st.error(result)