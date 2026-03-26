"""
agents/text_to_sql_agent.py
Loads agriculture CSVs into SQLite and converts
natural language queries to SQL using Claude.
"""
import os
import sqlite3
import pandas as pd
import anthropic

DB_PATH = "data/processed/agriculture.db"


def init_db():
    os.makedirs("data/processed", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    crop_path = "data/raw/crop_recommendation.csv"
    if os.path.exists(crop_path):
        df = pd.read_csv(crop_path)
        df.to_sql("crops", conn, if_exists="replace", index=False)
        print(f"Loaded crops table: {len(df)} rows")

    fert_path = "data/raw/fertilizer_prediction.csv"
    if os.path.exists(fert_path):
        df2 = pd.read_csv(fert_path)
        df2.columns = df2.columns.str.strip()
        df2.to_sql("fertilizers", conn, if_exists="replace", index=False)
        print(f"Loaded fertilizers table: {len(df2)} rows")

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_PATH}")


def get_schema() -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        col_str = ", ".join([f"{c[1]} ({c[2]})" for c in cols])
        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
        sample = cursor.fetchall()
        parts.append(f"Table: {table}\nColumns: {col_str}\nSample: {sample}")
    conn.close()
    return "\n\n".join(parts)


def nl_to_sql(question: str) -> str:
    client = anthropic.Anthropic()
    schema = get_schema()

    system = """You are an expert SQL generator for agriculture databases.
Given a natural language question and a database schema, generate ONLY a valid SQLite SQL query.
Return ONLY the SQL query — no explanation, no markdown, no backticks.
The query must be SELECT only — never INSERT, UPDATE, or DELETE."""

    prompt = f"""Database Schema:
{schema}

Natural language question: {question}

Generate a SQLite SELECT query to answer this question."""

    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def execute_query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        raise e


def explain_result(question: str, sql: str, result_df: pd.DataFrame) -> str:
    client = anthropic.Anthropic()
    result_str = result_df.to_string(index=False) if not result_df.empty else "No results found."

    prompt = f"""A farmer asked: "{question}"

SQL query executed:
{sql}

Query result:
{result_str}

Explain this result in simple, clear language that a farmer can understand.
Be concise — 2 to 3 sentences maximum."""

    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


class TextToSQLAgent:
    def __init__(self):
        if not os.path.exists(DB_PATH):
            init_db()

    def query(self, question: str) -> dict:
        try:
            sql       = nl_to_sql(question)
            result_df = execute_query(sql)
            explanation = explain_result(question, sql, result_df)
            return {
                "question":    question,
                "sql":         sql,
                "result":      result_df,
                "explanation": explanation,
                "error":       None,
            }
        except Exception as e:
            return {
                "question":    question,
                "sql":         "",
                "result":      pd.DataFrame(),
                "explanation": "",
                "error":       str(e),
            }


if __name__ == "__main__":
    init_db()
    agent = TextToSQLAgent()

    test_questions = [
        "Show crops with the highest average nitrogen requirement",
        "Which crop needs the most rainfall on average?",
        "Compare average potassium levels across different crops",
        "What are the top 5 crops by average humidity requirement?",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        result = agent.query(q)
        print(f"SQL: {result['sql']}")
        print(f"Result:\n{result['result']}")
        print(f"Explanation: {result['explanation']}")
