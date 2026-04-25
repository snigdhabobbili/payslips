import cloudinary
import cloudinary.api
import sqlite3

# 🔐 Replace with your real credentials
cloudinary.config(
    cloud_name="dyaijms6g",
    api_key="737786234689224",
    api_secret="8UGpDODAQD9j3M-c24MW9EkZtJk"
)

# Connect to database
conn = sqlite3.connect("database.db")
cur = conn.cursor()

try:
    # ✅ Fetch PDFs (IMPORTANT: resource_type="raw")
    resources = cloudinary.api.resources(resource_type="raw", max_results=500)

    count = 0

    for res in resources["resources"]:
        public_id = res["public_id"]        # e.g. 16501369_02_2026
        url = res["secure_url"]             # full correct URL

        filename = public_id + ".pdf"

        # Update DB
        cur.execute(
            "UPDATE payslips SET file_url=? WHERE filename=?",
            (url, filename)
        )

        if cur.rowcount > 0:
            count += 1

    conn.commit()

    print(f"✅ Done! Updated {count} records")

except Exception as e:
    print("❌ Error:", e)

finally:
    conn.close()