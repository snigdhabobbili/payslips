from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# ---------------- DB CONNECTION ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- CREATE TABLES ----------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payslips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        month TEXT,
        year TEXT,
        file_path TEXT
    )
    """)

    conn.commit()
    conn.close()

#  (creates tables when app starts)
init_db()

# ---------------- SETUP (INSERT DATA) ----------------
@app.route('/setup')
def setup():
    conn = get_db()
    cur = conn.cursor()

    # Clear old data (prevents duplicates)
    cur.execute("DELETE FROM employees")
    cur.execute("DELETE FROM payslips")

    # Employees
    cur.execute("INSERT INTO employees VALUES (?, ?)",
                ("16501345", "1234"))

    cur.execute("INSERT INTO employees VALUES (?, ?)",
                ("16501346", "5678"))

    # Payslips
    cur.execute("""
    INSERT INTO payslips (employee_id, month, year, file_path)
    VALUES (?, ?, ?, ?)
    """, ("16501345", "03", "2026", "uploads/16501345_03_2026.pdf"))

    cur.execute("""
    INSERT INTO payslips (employee_id, month, year, file_path)
    VALUES (?, ?, ?, ?)
    """, ("16501346", "03", "2026", "uploads/16501346_03_2026.pdf"))

    conn.commit()
    conn.close()

    return "Database setup complete"

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    emp_id = data['employee_id']
    password = data['password']

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM employees WHERE employee_id=? AND password=?",
        (emp_id, password)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"}), 401

# ---------------- GET PAYSLIP ----------------
@app.route('/payslip', methods=['POST'])
def get_payslip():
    data = request.json
    emp_id = data['employee_id']
    month = data['month']
    year = data['year']

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM payslips
    WHERE employee_id=? AND month=? AND year=?
    """, (emp_id, month, year))

    slip = cur.fetchone()
    conn.close()

    if slip:
        return jsonify(dict(slip))
    else:
        return jsonify({"error": "No data available"}), 404

# ---------------- SERVE PDF ----------------
@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory('uploads', filename)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)