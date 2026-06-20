import requests
import os
from dotenv import load_dotenv
from etl import parse_salary, detect_experience, detect_skills
import datetime

load_dotenv()

ORDS_BASE = os.getenv("ORDS_BASE_URL")
ORDS_USER = os.getenv("ORDS_USER")
ORDS_PASS = os.getenv("ORDS_PASSWORD")


def clean(value):
    if value is None:
        return ""
    return str(value).replace("\xa0", " ").replace("\u200b", "").strip()


def get_session():
    s = requests.Session()
    s.auth = (ORDS_USER, ORDS_PASS)
    s.headers.update({"Content-Type": "application/json"})
    return s


def transform_jobs(jobs):
    """Transform raw jobs menjadi format clean. Pure function, tidak ada I/O."""
    result = []
    for job in jobs:
        salary_min, salary_max = parse_salary(job.get("salary"))
        experience = detect_experience(job.get("title", ""))
        text       = (job.get("title") or "") + " " + (job.get("classification") or "")
        skills     = detect_skills(text)

        result.append({
            "job_id":           clean(job.get("job_id")),
            "title":            clean(job.get("title")),
            "company":          clean(job.get("company")),
            "location":         clean(job.get("location")),
            "city":             clean(job.get("city")),
            "province":         clean(job.get("province")),
            "salary_min":       salary_min,
            "salary_max":       salary_max,
            "experience_level": experience,
            "job_type":         clean(job.get("job_type")),
            "skills":           skills,
            "keyword":          clean(job.get("keyword")),
        })
    return result

def save_raw_to_db(jobs):
    session = get_session()
    now = datetime.datetime.utcnow().isoformat()
    for job in jobs:
        payload = {
            "job_id":         clean(job.get("job_id")),
            "title":          clean(job.get("title")),
            "company":        clean(job.get("company")),
            "location":       clean(job.get("location")),
            "city":           clean(job.get("city")),
            "province":       clean(job.get("province")),
            "salary":         clean(job.get("salary")),
            "job_type":       clean(job.get("job_type")),
            "classification": clean(job.get("classification")),
            "date_posted":    clean(job.get("date_posted")),
            "job_url":        "https://id.jobstreet.com" + clean(job.get("job_url")) if job.get("job_url") else "",
            "keyword":        clean(job.get("keyword")),
            "scraped_at":     now,
        }
        try:
            resp = session.post(f"{ORDS_BASE}/jobs_raw/", json=payload)
            if resp.status_code in (200, 201):
                pass
            elif resp.status_code == 409 or "ORA-00001" in resp.text:
                pass
            else:
                print(f"    jobs_raw error {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"    jobs_raw exception: {e}")

def save_clean_to_db(jobs_clean):
    """Simpan hasil transform ke jobs_clean via ORDS."""
    session = get_session()
    now = datetime.datetime.utcnow().isoformat()
    for job in jobs_clean:
        job["scraped_at"] = now  # tambahkan timestamp eksplisit
        try:
            resp = session.post(f"{ORDS_BASE}/jobs_clean/", json=job)
            if resp.status_code in (200, 201):
                pass
            elif resp.status_code == 409 or "ORA-00001" in resp.text:
                pass
            else:
                print(f"    jobs_clean error {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"    jobs_clean exception: {e}")