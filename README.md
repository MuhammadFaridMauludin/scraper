# JobAnalytic Scraper

Pipeline scraping dan ETL untuk mengumpulkan data lowongan pekerjaan dari berbagai platform dan memuatnya ke Oracle Cloud Infrastructure.

## Overview

Project ini bertugas untuk:

1. Mengambil data lowongan pekerjaan dari berbagai sumber.
2. Menyimpan data mentah (raw data) ke Oracle Object Storage.
3. Melakukan proses Extract, Transform, Load (ETL).
4. Memuat data hasil transformasi ke Oracle Autonomous Database melalui ORDS REST API.
5. Menjalankan proses secara otomatis menggunakan scheduler.

## Architecture

```text
Data Source
     │
     ▼
Scraper (Python)
     │
     ▼
Oracle Object Storage (raw)
     │
     ▼
ETL Process
     │
     ▼
Oracle Autonomous Database
```

## Project Structure

```text
scraper/
├── scraper.py          # Job scraping process
├── etl.py              # Data transformation logic
├── etl_job.py          # ETL execution script
├── db.py               # Database/API connection
├── config.py           # Configuration
├── requirements.txt
├── Dockerfile
└── README.md
```

## Technology Stack

- Python
- Selenium
- Pandas
- Docker
- Oracle Object Storage
- Oracle Autonomous Database
- ORDS REST API

## Setup

### Clone Repository

```bash
git clone <repository-url>
cd scraper
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Scraper

```bash
python scraper.py
```

## Run ETL

```bash
python etl_job.py
```

## Docker

Build image:

```bash
docker build -t jobanalytic-scraper .
```

Run container:

```bash
docker run jobanalytic-scraper
```

## Data Pipeline Schedule

| Process | Time |
|----------|----------|
| Scraping | 02:00 |
| ETL | 03:00 |

## Authors
- Achmad Doli Harahap
- Bagas Yudha Aditya
- Daril Oktavian
- Muhammad Farid Mauludin