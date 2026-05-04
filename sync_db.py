import os
import sqlite3

UPLOAD_FOLDER = "uploads"

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# CREATE TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS payslips (
    employee_id TEXT,
    month TEXT,
    year TEXT,
    filename TEXT,
    UNIQUE(employee_id, month, year)
)
""")

# INSERT FILES
for file in os.listdir(UPLOAD_FOLDER):
    if not file.endswith(".pdf"):
        continue

    parts = file.replace(".pdf", "").split("_")

    if len(parts) != 3:
        print("Skipping:", file)
        continue

    emp, month, year = parts

    try:
        cur.execute("""
        INSERT INTO payslips (employee_id, month, year, filename)
        VALUES (?, ?, ?, ?)
        """, (emp, month, year, file))

        print("Inserted:", file)

    except:
        print("Already exists:", file)

conn.commit()
conn.close()

print("✅ Database ready")