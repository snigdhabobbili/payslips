import os
import sqlite3

UPLOAD_FOLDER = "uploads"

print("🔄 Initial load started...\n")

# Check if uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    print("❌ 'uploads' folder not found")
    exit()

files = os.listdir(UPLOAD_FOLDER)

print(f"📁 Total files found in uploads: {len(files)}\n")

conn = sqlite3.connect("database.db")
cur = conn.cursor()

inserted = 0
skipped = 0

for file in files:
    print("➡️ Checking:", file)

    # Only process PDFs
    if not file.endswith(".pdf"):
        print("   ⏭️ Skipped (not a PDF)")
        skipped += 1
        continue

    parts = file.replace(".pdf", "").split("_")

    if len(parts) != 3:
        print("   ❌ Invalid filename format")
        skipped += 1
        continue

    emp, month, year = parts

    try:
        cur.execute("""
        INSERT INTO payslips (employee_id, month, year, filename)
        VALUES (?, ?, ?, ?)
        """, (emp, month, year, file))

        print("   ✅ Inserted:", file)
        inserted += 1

    except sqlite3.IntegrityError:
        print("   ⚠️ Duplicate:", file)
        skipped += 1

conn.commit()
conn.close()

print("\n🎯 Summary:")
print("Inserted:", inserted)
print("Skipped:", skipped)
print("✅ Initial load complete")