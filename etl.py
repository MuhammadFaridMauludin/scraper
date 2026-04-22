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