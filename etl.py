import re

def parse_salary(salary_text):
    if not salary_text or "Tidak" in salary_text:
        return None, None

    numbers = re.findall(r"\d[\d\.]+", salary_text)
    numbers = [int(n.replace(".", "")) for n in numbers]

    if len(numbers) == 1:
        return numbers[0], numbers[0]
    elif len(numbers) >= 2:
        return numbers[0], numbers[1]

    return None, None


def detect_experience(title):
    title = title.lower()

    if "intern" in title:
        return "Internship"
    elif "senior" in title:
        return "Senior"
    elif "junior" in title or "entry" in title:
        return "Junior"

    return "Unknown"


def detect_skills(text):
    if not text:
        return ""

    text = text.lower()

    skill_list = [
    # --- Skill Dasar & Analisis ---
    "python", "sql", "excel", "spreadsheet", "tableau", "power bi", 
    "looker", "data studio", "statistics", "statistik",
    "data analysis", "data analytics",

    # --- Programming Languages ---
    "java", "javascript", "typescript", "c#", "c++", "php", "go", "golang",
    "ruby", "bash", "shell scripting",

    # --- Web Development ---
    "html", "css", "sass", "bootstrap", "tailwind",
    "react", "react.js", "next.js",
    "vue", "vue.js", "nuxt.js",
    "angular",
    "node.js", "express.js",
    "laravel", "django", "flask", "spring boot",
    "rest api", "restful api", "graphql",

    # --- Database ---
    "mysql", "postgresql", "mongodb", "nosql",
    "oracle", "sql server", "firebase",
    "database design", "query optimization",

    # --- Mobile Development ---
    "kotlin", "java android", "android",
    "swift", "ios",
    "flutter", "dart",
    "react native", "xamarin",

    # --- DevOps & Tools ---
    "git", "github", "gitlab", "bitbucket",
    "docker", "kubernetes",
    "jenkins", "github actions", "gitlab ci", "ci/cd",
    "terraform", "ansible",

    # --- Cloud ---
    "aws", "amazon web services",
    "gcp", "google cloud",
    "azure", "microsoft azure",
    "oci", "oracle cloud infrastructure",
    "cloud computing", "cloud architecture",

    # --- Monitoring & SRE ---
    "prometheus", "grafana", "elk stack", "logstash", "kibana",
    "monitoring", "logging", "alerting",

    # --- Data Engineering ---
    "etl", "elt", "data pipeline",
    "apache spark", "hadoop", "airflow",
    "data warehouse", "data lake",

    # --- Data Science / AI ---
    "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "keras",
    "machine learning", "deep learning",
    "nlp", "computer vision",

    # --- System & Architecture ---
    "system design", "microservices", "distributed systems",
    "uml", "architecture design",

    # --- Methodology ---
    "agile", "scrum", "kanban",
    "waterfall", "jira", "confluence",

    # --- IT Support & Infra ---
    "troubleshooting", "debugging",
    "windows", "linux", "unix",
    "networking", "tcp/ip", "dns", "vpn",

    # --- Security ---
    "cyber security", "information security",
    "penetration testing", "owasp",

    # --- ERP / Enterprise ---
    "sap", "odoo", "erp", "crm",

    # --- Soft Skill / Business ---
    "business analysis", "requirement gathering",
    "stakeholder management", "communication",
    "project management",

    # --- Testing ---
    "unit testing", "integration testing",
    "selenium", "automation testing", "qa",

    # --- Misc ---
    "api integration", "json", "xml",
    "performance optimization", "scalability"
]

    found = []

    for skill in skill_list:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found.append(skill)

    return ", ".join(set(found))