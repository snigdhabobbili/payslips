import time
import os
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

UPLOAD_FOLDER = "uploads"

def insert_db(emp, month, year, filename):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO payslips (employee_id, month, year, filename)
        VALUES (?, ?, ?, ?)
        """, (emp, month, year, filename))
        conn.commit()
        print("Inserted:", filename)
    except:
        print("Duplicate/Invalid:", filename)
    conn.close()

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file = os.path.basename(event.src_path)

        if not file.endswith(".pdf"):
            return

        time.sleep(1)

        try:
            parts = file.replace(".pdf", "").split("_")
            if len(parts) != 3:
                print("Invalid:", file)
                return

            emp, month, year = parts
            insert_db(emp, month, year, file)

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), UPLOAD_FOLDER, recursive=False)
    observer.start()

    print("Watcher running...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()