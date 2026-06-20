from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from storage import upload_raw
from config import KEYWORDS, MAX_PAGES, DELAY
import time
import random
import json
import datetime

IMPERSONATE_LIST = ["edge101", "edge99", "chrome136", "chrome131", "firefox135"]

PROVINCES = [
    "east java", "west java", "central java", "jakarta",
    "banten", "bali", "yogyakarta", "di yogyakarta",
    "north sumatra", "west sumatra", "south sumatra",
    "riau", "riau islands",
    "east kalimantan", "west kalimantan", "south kalimantan",
    "north kalimantan", "central kalimantan",
    "south sulawesi", "north sulawesi", "central sulawesi",
    "southeast sulawesi", "west sulawesi",
    "papua", "west papua", "maluku", "north maluku",
    "lampung", "aceh", "jambi", "bengkulu",
    "bangka belitung", "gorontalo",
    "jawa timur", "jawa barat", "jawa tengah", "dki jakarta",
    "kalimantan timur", "kalimantan barat", "kalimantan selatan",
    "sulawesi selatan", "sumatera utara", "kepulauan riau",
]

NOISE = [
    "urgently hiring", "at", "private advertiser", "featured",
    "full time", "part time", "contract", "internship", "magang",
    "this is a full time job", "this is a part time job",
]


def parse_jobs(html, keyword):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("article")
    jobs  = []

    for card in cards:
        try:
            job_id = card.get("data-job-id", "")
            if not job_id:
                continue

            title_el = card.find("a", {"data-automation": "jobTitle"})
            title    = title_el.text.strip() if title_el else ""

            company_el = card.find("a", {"data-automation": "jobCompany"})
            company    = company_el.text.strip() if company_el else ""

            location_el = card.find("a", {"data-automation": "jobLocation"})
            location    = location_el.text.strip() if location_el else ""

            city = province = ""
            for el in card.find_all(True):
                text = el.get_text(strip=True)
                if not text or len(text) > 60 or "\n" in text:
                    continue
                if text.lower() in NOISE:
                    continue
                if "," in text:
                    parts = text.split(",", 1)
                    prov  = parts[1].strip().lower()
                    if prov in PROVINCES:
                        city     = parts[0].strip()
                        province = parts[1].strip().title()
                        break

            salary_el = card.find("span", {"data-automation": "jobSalary"})
            salary    = salary_el.text.strip() if salary_el else "Tidak dicantumkan"

            job_type = "Full Time"
            for span in card.find_all("span"):
                t = span.text.strip().lower()
                if "part" in t and "time" in t:
                    job_type = "Part Time"; break
                elif t in ["contract", "kontrak"]:
                    job_type = "Contract"; break
                elif t in ["internship", "magang"]:
                    job_type = "Internship"; break

            class_el       = card.find("a", {"data-automation": "jobClassification"})
            classification = class_el.text.strip() if class_el else ""

            date_el     = card.find("span", {"data-automation": "jobListingDate"})
            date_posted = date_el.text.strip() if date_el else ""

            job_url = title_el.get("href", "") if title_el else ""

            if title and job_id:
                jobs.append({
                    "job_id":         job_id,
                    "title":          title,
                    "company":        company,
                    "location":       location,
                    "city":           city,
                    "province":       province,
                    "salary":         salary,
                    "job_type":       job_type,
                    "classification": classification,
                    "date_posted":    date_posted,
                    "job_url":        job_url,
                    "keyword":        keyword,
                })

        except Exception as e:
            print(f"    ⚠️ Skip 1 card: {e}")
            continue

    return jobs


def scrape_keyword(keyword):
    print(f"\n🔍 Scraping keyword: '{keyword}'")
    all_jobs    = []
    keyword_url = keyword.replace(" ", "-")

    for page in range(1, MAX_PAGES + 1):
        url = f"https://id.jobstreet.com/{keyword_url}-jobs?pg={page}"
        print(f"  📄 Halaman {page}: {url}")

        try:
            impersonate = random.choice(IMPERSONATE_LIST)
            resp = cffi_requests.get(
                url,
                impersonate=impersonate,
                timeout=30,
                headers={
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )

            if resp.status_code == 403:
                print(f"  ❌ HTTP 403 — coba lagi dengan delay")
                time.sleep(10)
                resp = cffi_requests.get(url, impersonate="chrome", timeout=30)

            if resp.status_code != 200:
                print(f"  ❌ HTTP {resp.status_code}")
                break

            if "Just a moment" in resp.text:
                print(f"  ❌ Cloudflare block, skip halaman {page}")
                break

            jobs = parse_jobs(resp.text, keyword)

            if not jobs:
                print(f"  ⚠️ Tidak ada job di halaman {page}, berhenti.")
                break

            print(f"  ✅ {len(jobs)} job ditemukan")
            all_jobs.extend(jobs)
            time.sleep(DELAY)

        except Exception as e:
            print(f"  ❌ Error halaman {page}: {e}")
            continue

    return all_jobs


def main():
    print("🚀 Jobstreet Scraper - Indonesia")
    print("=" * 40)

    total = 0
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    for keyword in KEYWORDS:
        jobs = scrape_keyword(keyword)
        total += len(jobs)

        if jobs:
            safe_kw     = keyword.replace(" ", "_").lower()
            object_name = f"raw/{safe_kw}_{timestamp}.json"
            status      = upload_raw(jobs, object_name)
            if status == 200:
                print(f"  ☁️  Uploaded: {object_name} ({len(jobs)} jobs)")
            else:
                print(f"  ❌ Upload gagal: {object_name} (status {status})")

        time.sleep(random.randint(10, 20))

    print(f"\n🎉 Selesai! Total {total} job berhasil di-scrape")


if __name__ == "__main__":
    main()