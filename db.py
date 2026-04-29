import mysql.connector
from dotenv import load_dotenv
import os
from etl import parse_salary, detect_experience, detect_skills

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host="168.110.192.215",
        port=3306,
        user="scraper",
        password="@Corazon015.",
        database="job_analisis"
    )


def save_jobs_raw(jobs):
    conn = get_connection()
    cursor = conn.cursor()

    for job in jobs:
        cursor.execute("""
            INSERT INTO jobs_raw 
            (job_id, title, company, location, salary, job_type, classification, date_posted, job_url, keyword)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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

    conn.commit()
    cursor.close()
    conn.close()


def transform_and_load(jobs):
    conn = get_connection()
    cursor = conn.cursor()

    for job in jobs:
        salary_min, salary_max = parse_salary(job.get("salary"))
        experience = detect_experience(job.get("title"))

        # 🔥 skill detection
        text_combined = (job.get("title") or "") + " " + (job.get("classification") or "")
        skills = detect_skills(text_combined)

        cursor.execute("""
            INSERT INTO jobs_clean
            (job_id, title, company, location, salary_min, salary_max, experience_level, keyword, skills, job_type)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE 
                scraped_at = NOW(),
                skills = VALUES(skills),
                job_type = VALUES(job_type)
        """, (
            job.get("job_id"),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            salary_min,
            salary_max,
            experience,
            job.get("keyword"),
            skills,
            job.get("job_type"),
        ))

    conn.commit()
    cursor.close()
    conn.close()