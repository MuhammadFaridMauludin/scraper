import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id VARCHAR(50) UNIQUE,
            title VARCHAR(255),
            company VARCHAR(255),
            location VARCHAR(255),
            salary VARCHAR(255),
            job_type VARCHAR(100),
            classification VARCHAR(100),
            date_posted VARCHAR(100),
            job_url TEXT,
            keyword VARCHAR(100),
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tabel jobs siap!")

def save_jobs(jobs):
    if not jobs:
        return
    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    for job in jobs:
        try:
            cursor.execute("""
                INSERT INTO jobs 
                    (job_id, title, company, location, salary, job_type, classification, date_posted, job_url, keyword)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE scraped_at=NOW()
            """, (
                job.get("job_id"),
                job.get("title"),
                job.get("company"),
                job.get("location"),
                job.get("salary"),
                job.get("job_type"),
                job.get("classification"),
                job.get("date_posted"),
                job.get("job_url"),
                job.get("keyword"),
            ))
            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ⚠️ Error insert: {e}")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"  💾 {inserted} baru disimpan, {skipped} duplikat dilewati")