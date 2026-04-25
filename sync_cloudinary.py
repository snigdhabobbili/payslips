import cloudinary
import cloudinary.api
import sqlite3

# ⚠️ Replace with NEW credentials (rotate your secret!)
cloudinary.config(
    cloud_name="dyaijms6g",
    api_key="737786234689224",
    api_secret="8UGpDODAQD9j3M-c24MW9EkZtJk"
)

conn = sqlite3.connect("database.db")
cur = conn.cursor()

try:
    resources = cloudinary.api.resources(
        resource_type="image",   # ✅ FIXED
        max_results=500
    )

    count = 0

    for res in resources["resources"]:
        public_id = res["public_id"]        # 16501369_02_2026
        url = res["secure_url"]

        filename = public_id + ".pdf"       # match DB

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