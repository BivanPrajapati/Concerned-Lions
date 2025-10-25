import requests
from bs4 import BeautifulSoup
import time
import csv
import re
URL = "https://www.bu.edu/academics/cas/courses/"

HEADERS = {
    "User-Agent": "CourseScraper/1.0 (DS-X Hackathon)"
}

def normalize_course(course_name):
    # Convert to lowercase
    course_name = course_name.lower()
    course_name = re.sub(r'\b(comp\s*sci|computer\s*science)\b', 'cs', course_name)
    course_name = re.sub(r'\s+', ' ', course_name).strip()
    match = re.match(r'([a-z]+)\s*-?\s*(\d+)', course_name)
    if match:
        dept, number = match.groups()
        return f"cas-{dept}-{number}"
    else:
        return None

def find_class(finding_url):
    if finding_url != None:
        return URL + finding_url + "/"
    else:
        return None
    
