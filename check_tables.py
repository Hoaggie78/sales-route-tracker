import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM customers"))
        row = result.fetchone()
        print(f"Connection SUCCESS! Found {row[0]} customers in the table.")
except Exception as e:
    print(f"Check failed: {e}")
