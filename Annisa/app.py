import streamlit as st
import sqlite3
import subprocess
import semogabisa

# Fungsi untuk mengonversi query teks ke SQL menggunakan API lokal
def generate_sql(text_query):
    model = "mistral"
    # prompt = f"Convert the following question to SQL only, no explanations or extra text:\n\n{text_query}\n\nSQL:"
    prompt: f"""
        You are a SQL expert. With the following database schema:

        {extract_mysql.tabel_info}

        Convert the question below into a syntactically correct SQL query, using only the relevant tables and columns.

        Question:
        {text_query}

        SQL:
        """
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()

# Fungsi untuk mengeksekusi query SQL pada database
def execute_sql(sql_query):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.commit()
    except Exception as e:
        results = str(e)
    conn.close()
    return results

# UI Streamlit
st.title("Text to SQL Converter (Ollama)")

user_input = st.text_area("Enter your query in natural language:")

if st.button("Convert to SQL"):
    if user_input.strip() == "":
        st.warning("Please enter a question first.")
    else:
        sql_query = generate_sql(user_input)
        st.text_area("Generated SQL Query:", sql_query, height=100)

        if st.button("Execute SQL"):
            result = execute_sql(sql_query)
            st.write("Results:", result)
