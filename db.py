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

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs_raw (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id VARCHAR(50) UNIQUE,
            title VARCHAR(255),
            company VARCHAR(255),
            location VARCHAR(255),
            city VARCHAR(100),
            province VARCHAR(100),
            salary VARCHAR(255),
            job_type VARCHAR(100),
            classification VARCHAR(100),
            date_posted VARCHAR(100),
            job_url TEXT,
            keyword VARCHAR(100),
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs_clean (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id VARCHAR(50) UNIQUE,
            title VARCHAR(255),
            company VARCHAR(255),
            location VARCHAR(255),
            city VARCHAR(100),
            province VARCHAR(100),
            salary_min BIGINT,
            salary_max BIGINT,
            experience_level VARCHAR(50),
            job_type VARCHAR(100),
            skills TEXT,
            keyword VARCHAR(100),
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tabel jobs siap!")


def save_jobs_raw(jobs):
    conn = get_connection()
    cursor = conn.cursor()

    for job in jobs:
        cursor.execute("""
            INSERT IGNORE INTO jobs_raw 
            (job_id, title, company, location, city, province, salary, job_type, classification, date_posted, job_url, keyword)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            job.get("job_id"),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("city", ""),      # ✅ ditambah
            job.get("province", ""),  # ✅ ditambah
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

        text_combined = (job.get("title") or "") + " " + (job.get("classification") or "")
        skills = detect_skills(text_combined)

        cursor.execute("""
            INSERT INTO jobs_clean
            (job_id, title, company, location, city, province, salary_min, salary_max, experience_level, keyword, skills, job_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                scraped_at = NOW(),
                skills = VALUES(skills),
                job_type = VALUES(job_type),
                city = VALUES(city),
                province = VALUES(province)
        """, (
            job.get("job_id"),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("city", ""),      
            job.get("province", ""),  
            salary_min,
            salary_max,
            experience,
            job.get("keyword"),
            skills,
            job.get("job_type"),  # ✅ sekarang 12 nilai = 12 kolom
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

        text_combined = (job.get("title") or "") + " " + (job.get("classification") or "")
        skills = detect_skills(text_combined)

        cursor.execute("""
            INSERT INTO jobs_clean
            (job_id, title, company, location, city, province, salary_min, salary_max, experience_level, keyword, skills, job_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                scraped_at = NOW(),
                skills = VALUES(skills),
                job_type = VALUES(job_type),
                city = VALUES(city),
                province = VALUES(province)
        """, (
            job.get("job_id"),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("city", ""),      
            job.get("province", ""),  
            salary_min,
            salary_max,
            experience,
            job.get("keyword"),
            skills,
            job.get("job_type"),  # ✅ sekarang 12 nilai = 12 kolom
        ))

    conn.commit()
    cursor.close()
    conn.close()