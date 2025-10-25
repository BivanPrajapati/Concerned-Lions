import requests
from bs4 import BeautifulSoup
import time
import csv

URL = "https://www.bu.edu/academics/cas/courses/"
HEADERS = {
    "User-Agent": "CourseScraper/1.0 (DS-X Hackathon)"
}

