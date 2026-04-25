import os
from flask import Flask, request, jsonify, render_template
import sqlite3

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

pending = {}

# -------- HOME --------
@app.route("/")
def home():
    return render_template("index.html")

# -------- LOGIN --------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    emp_id = data.get("employee_id")
    password = data.get("password")

    if password == emp_id[-4:]:
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 401

# -------- DB HELPERS --------
def fetch_latest(emp_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT file_url, month, year
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
        SELECT file_url
        FROM payslips
        WHERE employee_id=? AND month=? AND year=?
    """, (emp_id, month, year))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def fetch_year_latest(emp_id, year):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT file_url, month
        FROM payslips
        WHERE employee_id=? AND year=?
        ORDER BY month DESC
        LIMIT 1
    """, (emp_id, year))
    row = cur.fetchone()
    conn.close()
    return row

def month_exists_any_year(emp_id, month):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM payslips
        WHERE employee_id=? AND month=?
        LIMIT 1
    """, (emp_id, month))
    exists = cur.fetchone()
    conn.close()
    return bool(exists)

# -------- SYNC FUNCTION --------
def run_sync():
    import cloudinary
    import cloudinary.api

    cloudinary.config(
        cloud_name="dyaijms6g",
        api_key="737786234689224",
        api_secret="8UGpDODAQD9j3M-c24MW9EkZtJk"
    )

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # 🔥 Fetch BOTH image + raw
    img = cloudinary.api.resources(resource_type="image", max_results=500)
    raw = cloudinary.api.resources(resource_type="raw", max_results=500)

    all_resources = img["resources"] + raw["resources"]

    for res in all_resources:
        public_id = res["public_id"]
        url = res["secure_url"]

        try:
            emp, month, year = public_id.split("_")
        except:
            continue

        filename = public_id + ".pdf"

        # 🔥 INSERT OR UPDATE
        cur.execute("""
            INSERT INTO payslips (employee_id, month, year, filename, file_url)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(employee_id, month, year)
            DO UPDATE SET file_url=excluded.file_url
        """, (emp, month, year, filename, url))

    conn.commit()
    conn.close()

# -------- SYNC ROUTE --------
@app.route("/sync")
def sync():
    try:
        run_sync()
        return "✅ Sync completed!"
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# -------- LATEST --------
@app.route("/latest/<emp_id>")
def latest(emp_id):
    run_sync()   # 🔥 AUTO SYNC

    row = fetch_latest(emp_id)
    if row:
        file_url, m, y = row
        label = f"Showing {MONTH_NAMES[m]} {y} Payslip"
        return jsonify({
            "file": file_url,
            "month": m,
            "year": y,
            "label": label,
            "reply": label
        })
    return jsonify({
        "file": None,
        "label": "No payslip found",
        "reply": "No payslip found"
    })

# -------- CHAT --------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = (data.get("message") or "").lower()
    emp_id = data.get("employee_id")

    month = None
    for k, v in MONTH_MAP.items():
        if k in msg:
            month = v
            break

    year = None
    for w in msg.split():
        if w.isdigit() and len(w) == 4:
            year = w
            break

    if emp_id in pending:
        if not month:
            month = pending[emp_id].get("month")
        if not year:
            year = pending[emp_id].get("year")

    if month and not month_exists_any_year(emp_id, month):
        pending.pop(emp_id, None)
        return jsonify({
            "reply": f"No payslips found for {MONTH_NAMES[month]}",
            "file": None
        })

    if month and not year:
        pending[emp_id] = {"month": month}
        return jsonify({
            "reply": f"Which year for {MONTH_NAMES[month]}?"
        })

    if month and year:
        run_sync()   # 🔥 ensure latest data

        file_url = fetch_exact(emp_id, month, year)
        pending.pop(emp_id, None)

        if file_url:
            label = f"Showing {MONTH_NAMES[month]} {year} Payslip"
            return jsonify({
                "file": file_url,
                "month": month,
                "year": year,
                "label": label,
                "reply": label
            })
        else:
            return jsonify({
                "reply": f"Payslip not available for {MONTH_NAMES[month]} {year}",
                "file": None
            })

    if year:
        row = fetch_year_latest(emp_id, year)
        if row:
            file_url, m = row
            label = f"Showing {MONTH_NAMES[m]} {year} Payslip"
            return jsonify({
                "file": file_url,
                "month": m,
                "year": year,
                "label": label,
                "reply": label
            })
        else:
            return jsonify({
                "reply": f"No payslips found for year {year}",
                "file": None
            })

    return latest(emp_id)

# -------- RUN --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))