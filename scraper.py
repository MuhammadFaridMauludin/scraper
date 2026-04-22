from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from db import init_db, save_jobs
from config import KEYWORDS, MAX_PAGES, DELAY
import time

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def parse_jobs(driver, keyword, page):
    jobs = []
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-job-id]"))
        )
        cards = driver.find_elements(By.CSS_SELECTOR, "article[data-job-id]")

        for card in cards:
            try:
                job_id = card.get_attribute("data-job-id") or ""

                try:
                    title = card.find_element(By.CSS_SELECTOR, "a[data-automation='jobTitle']").text.strip()
                except:
                    title = ""

                try:
                    company = card.find_element(By.CSS_SELECTOR, "a[data-automation='jobCompany']").text.strip()
                except:
                    company = ""

                try:
                    location = card.find_element(By.CSS_SELECTOR, "a[data-automation='jobLocation']").text.strip()
                except:
                    location = ""

                try:
                    salary = card.find_element(By.CSS_SELECTOR, "span[data-automation='jobSalary']").text.strip()
                except:
                    salary = "Tidak dicantumkan"

                try:
                    job_type = card.find_element(By.CSS_SELECTOR, "span[data-automation='jobWorkType']").text.strip()
                except:
                    job_type = ""

                try:
                    classification = card.find_element(By.CSS_SELECTOR, "a[data-automation='jobClassification']").text.strip()
                except:
                    classification = ""

                try:
                    date_posted = card.find_element(By.CSS_SELECTOR, "span[data-automation='jobListingDate']").text.strip()
                except:
                    date_posted = ""

                try:
                    job_url = card.find_element(By.CSS_SELECTOR, "a[data-automation='jobTitle']").get_attribute("href")
                except:
                    job_url = ""

                if title and job_id:
                    jobs.append({
                        "job_id": job_id,
                        "title": title,
                        "company": company,
                        "location": location,
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
            time.sleep(DELAY)
            jobs = parse_jobs(driver, keyword, page)

            if not jobs:
                print(f"  ⚠️ Tidak ada job di halaman {page}, berhenti.")
                break

            print(f"  ✅ {len(jobs)} job ditemukan")
            all_jobs.extend(jobs)
            save_jobs(jobs)

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