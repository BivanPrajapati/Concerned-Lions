import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.bu.edu/academics/cas/courses/"

HEADERS = {
    "User-Agent": "CourseScraper/1.0 (DS-X Hackathon)"
}

def normalize_course(course_name):
    course_name = course_name.lower()
    course_name = re.sub(r'\b(comp\s*sci|computer\s*science)\b', 'cs', course_name)
    course_name = re.sub(r'\s+', ' ', course_name).strip()
    match = re.match(r'([a-z]+)\s*-?\s*(\d+)', course_name)
    if match:
        dept, number = match.groups()
        return f"cas-{dept}-{number}"
    else:
        return None

def get_course_url(finding_url):
    normalized = normalize_course(finding_url)
    if normalized:
        return URL + normalized + "/"
    else:
        return None

def scrape_course_description(course_name):
    course_url = get_course_url(course_name)
    if not course_url:
        return "Course not found."
    
    try:
        response = requests.get(course_url, headers=HEADERS)
        if response.status_code != 200:
            return f"Failed to fetch course page. Status code: {response.status_code}"
        
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.find("main") or soup
        
        # Exclude notes and accreditation text
        exclude_text = "Boston University is accredited by the New England Commission of Higher Education(NECHE)."
        description_parts = []

        # Get all normal paragraphs
        for p in content.find_all("p"):
            text = p.get_text(strip=True)
            if text and not text.startswith("Note") and exclude_text not in text:
                description_parts.append(text)

        # Get all paragraphs inside a div/span with class 'content' (info boxes)
        info_boxes = content.find_all(class_="content")
        for box in info_boxes:
            for p in box.find_all("p"):
                box_text = p.get_text(strip=True)
                if box_text:
                    description_parts.append(box_text)
        
        if description_parts:
            return "\n".join(description_parts)
        else:
            return "Course description not found on page."
    
    except Exception as e:
        return f"Error scraping course: {e}"
    