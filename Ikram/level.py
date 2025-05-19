import pymysql.cursors
import streamlit as st
import requests
import extract_mysql
import json
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import re

# ==== CACHED CONNECTION ====
@st.cache_resource
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="abc",
        database="preposyandu",
        cursorclass=pymysql.cursors.DictCursor
    )

# ==== LLM: TEXT TO SQL ====
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
    
# ==== DETEKSI SQL BERBAHAYA ====
def is_dangerous_query(sql):
    dangerous = ['drop', 'delete', 'truncate', 'alter', 'update', 'insert']
    tokens = re.findall(r'\b\w+\b', sql.lower())
    return any(word in tokens for word in dangerous)

# ==== DETECT RELEVANT TABLES ====
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

# ==== RUN SQL ====
def run_sql(sql):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        # print("Hasil dari cursor.fetchall():")
        print(results)
        return pd.DataFrame(results)
    except Exception as e:
        return f"❌ Query Execution Error: {str(e)}"

# ==== STREAMLIT UI ====
st.set_page_config(page_title="Text to SQL with Mistral", page_icon="🤖")

st.sidebar.title("Database Schema")
for table, columns in extract_mysql.tabel_info.items():
    st.sidebar.markdown(f"### {table}")
    st.sidebar.write(", ".join(columns))

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

# ==== EXECUTE SQL ====
if "generated_sql" in st.session_state:
    if st.button("Execute SQL"):
        sql = st.session_state.generated_sql
        st.code(sql, language="sql")

        if is_dangerous_query(sql):
            st.error("⚠️ Query terdeteksi berbahaya dan dibatalkan.")
        else:
            with st.spinner("Mengeksekusi query..."):
                result = run_sql(sql)

            if isinstance(result, pd.DataFrame):
                st.success("✅ Query berhasil dijalankan!")
                st.dataframe(result)

                st.download_button(
                    "⬇️ Download CSV",
                    data=result.to_csv(index=False),
                    file_name="query_result.csv",
                    mime="text/csv"
                )
            else:
                st.error(result)