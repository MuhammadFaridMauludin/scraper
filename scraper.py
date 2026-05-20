from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db import init_db, save_jobs_raw, transform_and_load
from config import KEYWORDS, MAX_PAGES, DELAY
import time
import undetected_chromedriver as uc
import os
import shutil

# Daftar provinsi untuk mendeteksi lokasi
PROVINCES = [
    "east java", "west java", "central java", "jakarta",
    "banten", "bali", "yogyakarta", "di yogyakarta",
    "north sumatra", "west sumatra", "south sumatra",
    "riau", "riau islands",
    "east kalimantan", "west kalimantan", "south kalimantan",
    "north kalimantan", "central kalimantan",
    "south sulawesi", "north sulawesi", "central sulawesi",
    "southeast sulawesi", "west sulawesi",
    "papua", "west papua",
    "maluku", "north maluku",
    "lampung", "aceh", "jambi", "bengkulu",
    "bangka belitung", "gorontalo",
    "jawa timur", "jawa barat", "jawa tengah", "dki jakarta",
    "kalimantan timur", "kalimantan barat", "kalimantan selatan",
    "sulawesi selatan", "sumatera utara", "kepulauan riau",
]

# Teks yang diabaikan saat parsing lokasi
NOISE = [
    "urgently hiring",
    "at",
    "private advertiser",
    "featured",
    "full time",
    "part time",
    "contract",
    "internship",
    "magang",
    "this is a full time job",
    "this is a part time job",
]


def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")        
    options.add_argument("--disable-gpu")         
    options.add_argument("--window-size=1920,1080")

    # Auto-detect Chrome binary
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    chrome_bin = next((p for p in chrome_paths if os.path.exists(p)), None)
    
    if chrome_bin is None:
        raise RuntimeError("❌ Chrome binary tidak ditemukan di container!")
    
    print(f"✅ Menggunakan Chrome: {chrome_bin}")

    driver = uc.Chrome(
        options=options,
        browser_executable_path=chrome_bin, 
        headless=True,    
    )
    return driver



def parse_jobs(driver, keyword, page):
    jobs = []

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-job-id]"))
        )

        cards = driver.find_elements(By.CSS_SELECTOR, "article")

        for card in cards:
            try:
                job_id = card.get_attribute("data-job-id") or ""

                try:
                    title = card.find_element(
                        By.CSS_SELECTOR,
                        "a[data-automation='jobTitle']"
                    ).text.strip()
                except:
                    title = ""

                try:
                    company = card.find_element(
                        By.CSS_SELECTOR,
                        "a[data-automation='jobCompany']"
                    ).text.strip()
                except:
                    company = ""

                try:
                    location = card.find_element(
                        By.CSS_SELECTOR,
                        "a[data-automation='jobLocation']"
                    ).text.strip()
                except:
                    location = ""

                # Parse city & province
                city = ""
                province = ""

                elements = card.find_elements(By.XPATH, ".//*")

                for el in elements:
                    text = el.text.strip()
                    text_lower = text.lower()

                    if not text or len(text) > 60 or "\n" in text:
                        continue

                    if text_lower in NOISE:
                        continue

                    if "," in text:
                        parts = text.split(",", 1)
                        kota = parts[0].strip()
                        prov = parts[1].strip().lower()

                        if prov in PROVINCES:
                            city = kota
                            province = parts[1].strip().title()
                            break

                # Salary
                try:
                    salary = card.find_element(
                        By.CSS_SELECTOR,
                        "span[data-automation='jobSalary']"
                    ).text.strip()
                except:
                    salary = "Tidak dicantumkan"

                # Job type
                job_type = "Full Time"
                spans = card.find_elements(By.TAG_NAME, "span")

                for span in spans:
                    text = span.text.strip().lower()

                    if "jenis pekerjaan" in text:
                        if "part" in text:
                            job_type = "Part Time"
                        elif "contract" in text:
                            job_type = "Contract"
                        elif "internship" in text or "magang" in text:
                            job_type = "Internship"
                        break

                    elif text in ["part time", "part-time", "paruh waktu"]:
                        job_type = "Part Time"
                        break

                    elif text in ["contract", "kontrak"]:
                        job_type = "Contract"
                        break

                    elif text in ["internship", "magang"]:
                        job_type = "Internship"
                        break

                # Classification
                try:
                    classification = card.find_element(
                        By.CSS_SELECTOR,
                        "a[data-automation='jobClassification']"
                    ).text.strip()
                except:
                    classification = ""

                # Date posted
                try:
                    date_posted = card.find_element(
                        By.CSS_SELECTOR,
                        "span[data-automation='jobListingDate']"
                    ).text.strip()
                except:
                    date_posted = ""

                # Job URL
                try:
                    job_url = card.find_element(
                        By.CSS_SELECTOR,
                        "a[data-automation='jobTitle']"
                    ).get_attribute("href")
                except:
                    job_url = ""

                # Simpan jika valid
                if title and job_id:
                    jobs.append({
                        "job_id": job_id,
                        "title": title,
                        "company": company,
                        "location": location,
                        "city": city,
                        "province": province,
                        "salary": salary,
                        "job_type": job_type,
                        "classification": classification,
                        "date_posted": date_posted,
                        "job_url": job_url,
                        "keyword": keyword,
                    })

            except Exception as e:
                print(f"    ⚠️ Skip 1 card: {e}")
                continue

    except Exception as e:
        print(f"  ❌ Gagal parse halaman {page}: {e}")

    return jobs



def scrape_keyword(driver, keyword):
    print(f"\n🔍 Scraping keyword: '{keyword}'")
    all_jobs = []
    keyword_url = keyword.replace(" ", "-")

    for page in range(1, MAX_PAGES + 1):
        url = f"https://id.jobstreet.com/{keyword_url}-jobs?pg={page}"
        print(f"  📄 Halaman {page}: {url}")

        try:
            driver.get(url)
            time.sleep(DELAY + 3)

            jobs = parse_jobs(driver, keyword, page)

            if not jobs:
                print(f"  ⚠️ Tidak ada job di halaman {page}, berhenti.")
                break

            print(f"  ✅ {len(jobs)} job ditemukan")

            all_jobs.extend(jobs)
            save_jobs_raw(jobs)
            transform_and_load(jobs)

        except Exception as e:
            print(f"  ❌ Error halaman {page}: {e}")
            continue

    return all_jobs



def main():
    print("🚀 Jobstreet Scraper - Indonesia")
    print("=" * 40)

    init_db()

    driver = init_driver()
    total = 0

    try:
        for keyword in KEYWORDS:
            jobs = scrape_keyword(driver, keyword)
            total += len(jobs)
            time.sleep(2)
    finally:
        driver.quit()

    print(f"\n🎉 Selesai! Total {total} job berhasil di-scrape")


if __name__ == "__main__":
    main()