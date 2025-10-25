import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.bu.edu/academics/cas/courses/"

HEADERS = {
    "User-Agent": "CourseScraper/1.0 (DS-X Hackathon)"
}

DEPT_MAPPING = {
    'african american & black diaspora studies': 'aa',
    'aa': 'aa',
    'history of art & architecture': 'ah',
    'ah': 'ah',
    'asian studies': 'ai',
    'ai': 'ai',
    'american & new england studies': 'am',
    'am': 'am',
    'anthropology': 'an',
    'an': 'an',
    'archaeology': 'ar',
    'ar': 'ar',
    'astronomy': 'as',
    'as': 'as',
    'biochemistry & molecular biology': 'bb',
    'bb': 'bb',
    'biology': 'bi',
    'bi': 'bi',
    'core curriculum': 'cc',
    'cc': 'cc',
    'modern greek': 'cg',
    'cg': 'cg',
    'chemistry': 'ch',
    'ch': 'ch',
    'cinema & media studies': 'ci',
    'ci': 'ci',
    'classical studies': 'cl',
    'cl': 'cl',
    'computer science': 'cs',
    "computerscience" :"cs",
    "compsci" : "cs",
    'cs': 'cs',
    'economics': 'ec',
    'ec': 'ec',
    'earth & environment': 'ee',
    'ee': 'ee',
    'editorial studies': 'ei',
    'ei': 'ei',
    'english': 'en',
    'en': 'en',
    'geography & environment': 'ge',
    'ge': 'ge',
    'greek': 'gr',
    'gr': 'gr',
    'hebrew': 'he',
    'he': 'he',
    'history': 'hi',
    'hi': 'hi',
    'health science': 'hm',
    'hm': 'hm',
    'health studies': 'hs',
    'hs': 'hs',
    'humanities': 'hu',
    'hu': 'hu',
    'international relations': 'is',
    'is': 'is',
    'information technology': 'it',
    'it': 'it',
    'japanese': 'jp',
    'jp': 'jp',
    'jewish studies': 'jw',
    'jw': 'jw',
    'latin american studies': 'la',
    'la': 'la',
    'mathematics & statistics': 'ma',
    'ma': 'ma',
    'mechanical engineering': 'me',
    'me': 'me',
    'music': 'mu',
    'mu': 'mu',
    'near eastern languages & civilizations': 'ne',
    'ne': 'ne',
    'philosophy': 'ph',
    'ph': 'ph',
    'political science': 'pl',
    'pl': 'pl',
    'psychological & brain sciences': 'ps',
    'ps': 'ps',
    'religion': 'rn',
    'rn': 'rn',
    'science': 'sc',
    'sc': 'sc',
    'sociology': 'so',
    'so': 'so',
    'spanish': 'sp',
    'sp': 'sp',
    'theatre arts': 'th',
    'th': 'th',
    'writing': "wr",
    'wr': "wr"

}

def clean(text):
    name = ""
    for i in text:
        if i != " ":
            name += i
    return name

def normalize_course(course_name):
    course_name = clean(course_name)
    course_name = course_name.lower().strip()
    course_name = re.sub(r'\s+', ' ', course_name)

    # Extract department and number
    match = re.match(r'([a-z\s]+)\s*(\d+)', course_name)
    if not match:
        return None

    dept_name, number = match.groups()
    dept_name = dept_name.strip()

    # Lookup abbreviation
    dept_abbr = DEPT_MAPPING.get(dept_name)
    if not dept_abbr:
        return None
    return f"{dept_abbr}{number}"


def get_course_url(finding_url):
    normalized = normalize_course(finding_url)
    urlname = "cas-" + normalized[0:2] + "-" + normalized[2:]
    if normalized:
        return URL + urlname + "/"
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
    
