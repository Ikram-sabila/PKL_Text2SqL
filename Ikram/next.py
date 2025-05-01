import streamlit as st
import requests
import extract_mysql
import json

# schema_string = json.dumps(extract_mysql.tabel_info, indent=2)

def text_to_sql(prompt):
    relevant_tables = detect_relevant_tables(prompt, extract_mysql.tabel_info)
    schema_string = json.dumps(relevant_tables, indent=2)

    url = "http://localhost:11434/api/generate"
    data = {
        "model": "mistral",
        "prompt": f"""
        You are a SQL expert. With the following database schema:

        {schema_string}

        Convert the question below into a syntactically correct SQL query, using only the relevant tables and columns.

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

st.set_page_config(page_title="Text to SQL with Mistral", page_icon="🤖")
st.title("💬 Text to SQL Generator")
st.markdown("Ketik pertanyaan dalam bahasa natural, lalu lihat hasil SQL-nya.")

question = st.text_area("Pertanyaan (Natural Language):", height=150)

if st.button("🔍 Convert to SQL"):
    if question.strip() == "":
        st.warning("Masukkan pertanyaan dulu ya.")
    else:
        with st.spinner("Menggunakan Mistral via Ollama..."):
            sql_result = text_to_sql(question)
        st.code(sql_result, language="sql")        