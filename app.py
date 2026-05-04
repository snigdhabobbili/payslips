import os
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory, abort

app = Flask(__name__, template_folder="templates", static_folder="static")

# -------- MONTH MAP --------
MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March",
    "04": "April", "05": "May", "06": "June",
    "07": "July", "08": "August", "09": "September",
    "10": "October", "11": "November", "12": "December"
}

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12"
}

# -------- HOME --------
@app.route("/")
def home():
    return render_template("index.html")

# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# -------- LOGIN --------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    emp_id = data.get("employee_id")
    password = data.get("password")

    if emp_id and password and password == emp_id[-4:]:
        return jsonify({"status": "success"})

    return jsonify({"status": "fail"}), 401

# -------- FILE SERVING --------
@app.route("/files/<filename>")
def get_file(filename):
    path = os.path.join("uploads", filename)

    if not os.path.exists(path):
        abort(404)

    return send_from_directory("uploads", filename)

# -------- DB HELPERS --------
def fetch_latest(emp_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT filename, month, year
        FROM payslips
        WHERE employee_id=?
        ORDER BY year DESC, month DESC
        LIMIT 1
    """, (emp_id,))

    row = cur.fetchone()
    conn.close()
    return row


def fetch_exact(emp_id, month, year):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT filename
        FROM payslips
        WHERE employee_id=? AND month=? AND year=?
    """, (emp_id, month, year))

    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# -------- LATEST --------
@app.route("/latest/<emp_id>")
def latest(emp_id):
    row = fetch_latest(emp_id)

    if not row:
        return jsonify({"file": None, "label": "No payslip found"})

    filename, m, y = row
    m = str(m).zfill(2)

    return jsonify({
        "file": f"/files/{filename}",
        "month": m,
        "year": str(y),
        "label": f"Showing {MONTH_NAMES.get(m)} {y} Payslip"
    })

# -------- CHAT (SIMPLIFIED - NO FOLLOW-UP) --------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = (data.get("message") or "").lower()
    emp_id = data.get("employee_id")

    # Extract month
    month = None
    for k, v in MONTH_MAP.items():
        if k in msg:
            month = v
            break

    # Extract year
    year = None
    for w in msg.split():
        if w.isdigit() and len(w) == 4:
            year = w
            break

    # ❌ REMOVE follow-up logic
    # ✅ Force both month + year

    if month and not year:
        return jsonify({
            "reply": "Please specify month and year (e.g., March 2026)",
            "file": None
        })

    if month and year:
        filename = fetch_exact(emp_id, month, year)

        if filename:
            return jsonify({
                "file": f"/files/{filename}",
                "reply": f"Showing {MONTH_NAMES.get(month)} {year} Payslip",
                "month": month,
                "year": str(year)
            })

        return jsonify({
            "reply": f"No payslip for {MONTH_NAMES.get(month)} {year}",
            "file": None
        })

    # fallback → latest
    return latest(emp_id)

# -------- PAYSLIP PAGE --------
@app.route("/payslip")
def payslip():
    return render_template("payslip.html")

# -------- RUN --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)