import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS payslips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT,
    month TEXT,
    year TEXT,
    filename TEXT,
    UNIQUE(employee_id, month, year)
)
""")

conn.commit()
conn.close()

print("DB ready")