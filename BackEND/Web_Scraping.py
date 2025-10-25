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
    'AFRICAN AMERICAN & BLACK DIASPORA STUDIES': 'aa',
    'AA': 'aa',

    'history of art & architecture': 'ah',
    'ah': 'ah',
    'HISTORY OF ART & ARCHITECTURE': 'ah',
    'AH': 'ah',
    'arabic': 'aa',
    'aa': 'aa',
    'AA': 'aa',
    'asian studies': 'ai',
    'ai': 'ai',
    'ASIAN STUDIES': 'ai',
    'AI': 'ai',

    'american & new england studies': 'am',
    'am': 'am',
    'AMERICAN & NEW ENGLAND STUDIES': 'am',
    'AM': 'am',

    'anthropology': 'an',
    'an': 'an',
    'ANTHROPOLOGY': 'an',
    'AN': 'an',

    'archaeology': 'ar',
    'ar': 'ar',
    'ARCHAEOLOGY': 'ar',
    'AR': 'ar',

    'astronomy': 'as',
    'as': 'as',
    'ASTRONOMY': 'as',
    'AS': 'as',

    'biochemistry & molecular biology': 'bb',
    'bb': 'bb',
    'BIOCHEMISTRY & MOLECULAR BIOLOGY': 'bb',
    'BB': 'bb',

    'biology': 'bi',
    'bi': 'bi',
    'BIOLOGY': 'bi',
    'BI': 'bi',

    'core curriculum': 'cc',
    'cc': 'cc',
    'CORE CURRICULUM': 'cc',
    'CC': 'cc',

    'modern greek': 'cg',
    'cg': 'cg',
    'MODERN GREEK': 'cg',
    'CG': 'cg',

    'chemistry': 'ch',
    'ch': 'ch',
    'CHEMISTRY': 'ch',
    'CH': 'ch',

    'cinema & media studies': 'ci',
    'ci': 'ci',
    'CINEMA & MEDIA STUDIES': 'ci',
    'CI': 'ci',

    'classical studies': 'cl',
    'cl': 'cl',
    'CLASSICAL STUDIES': 'cl',
    'CL': 'cl',

    'computer science': 'cs',
    'computerscience': 'cs',
    'compsci': 'cs',
    'cs': 'cs',
    'COMPUTER SCIENCE': 'cs',
    'COMPUTERSCIENCE': 'cs',
    'COMPSCI': 'cs',
    'CS': 'cs',

    'economics': 'ec',
    'ec': 'ec',
    'ECONOMICS': 'ec',
    'EC': 'ec',

    'earth & environment': 'ee',
    'ee': 'ee',
    'EARTH & ENVIRONMENT': 'ee',
    'EE': 'ee',

    'editorial studies': 'ei',
    'ei': 'ei',
    'EDITORIAL STUDIES': 'ei',
    'EI': 'ei',

    'english': 'en',
    'en': 'en',
    'ENGLISH': 'en',
    'EN': 'en',

    'geography & environment': 'ge',
    'ge': 'ge',
    'GEOGRAPHY & ENVIRONMENT': 'ge',
    'GE': 'ge',

    'greek': 'gr',
    'gr': 'gr',
    'GREEK': 'gr',
    'GR': 'gr',

    'hebrew': 'he',
    'he': 'he',
    'HEBREW': 'he',
    'HE': 'he',

    'history': 'hi',
    'hi': 'hi',
    'HISTORY': 'hi',
    'HI': 'hi',

    'health science': 'hm',
    'hm': 'hm',
    'HEALTH SCIENCE': 'hm',
    'HM': 'hm',

    'health studies': 'hs',
    'hs': 'hs',
    'HEALTH STUDIES': 'hs',
    'HS': 'hs',

    'humanities': 'hu',
    'hu': 'hu',
    'HUMANITIES': 'hu',
    'HU': 'hu',

    'international relations': 'is',
    'is': 'is',
    'INTERNATIONAL RELATIONS': 'is',
    'IS': 'is',

    'information technology': 'it',
    'it': 'it',
    'INFORMATION TECHNOLOGY': 'it',
    'IT': 'it',

    'japanese': 'jp',
    'jp': 'jp',
    'JAPANESE': 'jp',
    'JP': 'jp',

    'jewish studies': 'jw',
    'jw': 'jw',
    'JEWISH STUDIES': 'jw',
    'JW': 'jw',

    'latin american studies': 'la',
    'la': 'la',
    'LATIN AMERICAN STUDIES': 'la',
    'LA': 'la',

    'mathematics & statistics': 'ma',
    'ma': 'ma',
    'MATHEMATICS & STATISTICS': 'ma',
    'MA': 'ma',

    'mechanical engineering': 'me',
    'me': 'me',
    'MECHANICAL ENGINEERING': 'me',
    'ME': 'me',

    'music': 'mu',
    'mu': 'mu',
    'MUSIC': 'mu',
    'MU': 'mu',

    'near eastern languages & civilizations': 'ne',
    'ne': 'ne',
    'NEAR EASTERN LANGUAGES & CIVILIZATIONS': 'ne',
    'NE': 'ne',

    'philosophy': 'ph',
    'ph': 'ph',
    'PHILOSOPHY': 'ph',
    'PH': 'ph',

    'political science': 'pl',
    'pl': 'pl',
    'POLITICAL SCIENCE': 'pl',
    'PL': 'pl',

    'psychological & brain sciences': 'ps',
    'ps': 'ps',
    'PSYCHOLOGICAL & BRAIN SCIENCES': 'ps',
    'PS': 'ps',
    "physics":"py",
    "py":"py",
    "PY":"py", 
    'religion': 'rn',
    'rn': 'rn',
    'RELIGION': 'rn',
    'RN': 'rn',

    'science': 'sc',
    'sc': 'sc',
    'SCIENCE': 'sc',
    'SC': 'sc',

    'sociology': 'so',
    'so': 'so',
    'SOCIOLOGY': 'so',
    'SO': 'so',

    'spanish': 'sp',
    'sp': 'sp',
    'SPANISH': 'sp',
    'SP': 'sp',

    'theatre arts': 'th',
    'th': 'th',
    'THEATRE ARTS': 'th',
    'TH': 'th',

    'writing': 'wr',
    'wr': 'wr',
    'WRITING': 'wr',
    'WR': 'wr',
}

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def normalize_course(course_name):
    """Normalize a course name to short form like cs112"""
    course_name = course_name.upper().replace("CAS", "").strip()
    match = re.match(r'([A-Z &]+)\s*(\d+)', course_name)
    if not match:
        return None
    dept_name, number = match.groups()
    dept_abbr = DEPT_MAPPING.get(dept_name.lower().strip())
    if not dept_abbr:
        return None
    return f"{dept_abbr}{number}"

def get_course_url(course_name):
    normalized = normalize_course(course_name)
    if not normalized:
        return None
    return URL + f"cas-{normalized[:2]}-{normalized[2:]}/"
def scrape_course_description(course_name):
    course_url = get_course_url(course_name)
    if not course_url:
        return None
    try:
        response = requests.get(course_url, headers=HEADERS)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.find("main") or soup

        exclude_text = "Boston University is accredited by the New England Commission of Higher Education(NECHE)."
        description_parts = []

        for p in content.find_all("p"):
            text = p.get_text(strip=True)
            if text and not text.startswith("Note") and exclude_text not in text:
                description_parts.append(text)

        # Include info boxes if any
        info_boxes = content.find_all(class_="content")
        for box in info_boxes:
            for p in box.find_all("p"):
                text = p.get_text(strip=True)
                if text:
                    description_parts.append(text)

        if description_parts:
            return "\n".join(description_parts)
        else:
            return None
    except:
        return None