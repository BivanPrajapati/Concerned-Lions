import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.bu.edu/academics/cas/courses/"

HEADERS = {
    "User-Agent": "CourseScraper/1.0 (DS-X Hackathon)"
}

DEPT_MAPPING = {
    # --- Writing ---
    'writing': 'wr', 'wr': 'wr', 'WRITING': 'wr', 'WR': 'wr',

    # --- Computer Science ---
    'computer science': 'cs', 'computerscience': 'cs', 'compsci': 'cs', 'cs': 'cs',
    'COMPUTER SCIENCE': 'cs', 'COMPUTERSCIENCE': 'cs', 'COMPSCI': 'cs', 'CS': 'cs',

    # --- History of Art & Architecture ---
    'history of art & architecture': 'ah', 'ah': 'ah', 'HISTORY OF ART & ARCHITECTURE': 'ah', 'AH': 'ah',

    # --- Languages ---
    'african languages': 'ly', 'chinese': 'lc', 'french': 'lf', 'german': 'lg',
    'hindi-urdu': 'lh', 'italian': 'li', 'korean': 'lk', 'persian': 'ln',
    'portuguese': 'lp', 'russian': 'lr', 'swahili': 'ls', 'vietnamese': 'lv',
    'yiddish': 'ly', 'african american & black diaspora studies': 'aa', 'aa': 'aa',

    # --- Linguistics ---
    'linguistics': 'lx', 'lx': 'lx', 'LINGUISTICS': 'lx',

    # --- Sciences ---
    'biology': 'bi', 'bi': 'bi', 'BIOLOGY': 'bi', 'BI': 'bi',
    'chemistry': 'ch', 'ch': 'ch', 'CHEMISTRY': 'ch', 'CH': 'ch',
    'physics': 'py', 'py': 'py', 'PHYSICS': 'py', 'PY': 'py',
    'earth & environment': 'ee', 'ee': 'ee', 'EARTH & ENVIRONMENT': 'ee', 'EE': 'ee',
    'biochemistry & molecular biology': 'bb', 'bb': 'bb', 'BIOCHEMISTRY & MOLECULAR BIOLOGY': 'bb', 'BB': 'bb',
    'marine science': 'ms', 'ms': 'ms', 'MARINE SCIENCE': 'ms',
    # --- Mathematics ---
    "neuroscience":"ne","ne":"ne", "NE":"ne",
    'mathematics': 'ma', 'math': 'ma', 'ma': 'ma', 'MATHEMATICS': 'ma', 'MATH': 'ma', 'MA': 'ma',

    # --- Social Sciences ---
    'anthropology': 'an', 'an': 'an', 'ANTHROPOLOGY': 'an', 'AN': 'an',
    'sociology': 'so', 'so': 'so', 'SOCIOLOGY': 'so', 'SO': 'so',
    'economics': 'ec', 'ec': 'ec', 'ECONOMICS': 'ec', 'EC': 'ec',
    'political science': 'pl', 'pl': 'pl', 'POLITICAL SCIENCE': 'pl', 'PL': 'pl',
    'psychological & brain sciences': 'ps', 'ps': 'ps', 'PSYCHOLOGICAL & BRAIN SCIENCES': 'ps', 'PS': 'ps',
    'international relations': 'is', 'is': 'is', 'INTERNATIONAL RELATIONS': 'is', 'IS': 'is',

    # --- Humanities ---
    'philosophy': 'ph', 'ph': 'ph', 'PHILOSOPHY': 'ph', 'PH': 'ph',
    'religion': 'rn', 'rn': 'rn', 'RELIGION': 'rn', 'RN': 'rn',
    'classical studies': 'cl', 'cl': 'cl', 'CLASSICAL STUDIES': 'cl', 'CL': 'cl',
    'humanities': 'hu', 'hu': 'hu', 'HUMANITIES': 'hu', 'HU': 'hu',
    'modern greek': 'cg', 'cg': 'cg', 'MODERN GREEK': 'cg', 'CG': 'cg',
    'greek': 'gr', 'gr': 'gr', 'GREEK': 'gr', 'GR': 'gr',
    'hebrew': 'he', 'he': 'he', 'HEBREW': 'he', 'HE': 'he',
    'latin american studies': 'la', 'la': 'la', 'LATIN AMERICAN STUDIES': 'la', 'LA': 'la',
    'asian studies': 'ai', 'ai': 'ai', 'ASIAN STUDIES': 'ai', 'AI': 'ai',
    'american & new england studies': 'am', 'am': 'am', 'AMERICAN & NEW ENGLAND STUDIES': 'am', 'AM': 'am',
    'jewish studies': 'jS', 'jS': 'js', 'JEWISH STUDIES': 'jS', 'JS': 'js',
    'js': 'js', 'JS': 'js',  # alternate mapping

    # --- Music, Theatre, Arts ---
    'music': 'mu', 'mu': 'mu', 'MUSIC': 'mu', 'MU': 'mu',
    'theatre arts': 'th', 'th': 'th', 'THEATRE ARTS': 'th', 'TH': 'th',
    'cinema & media studies': 'ci', 'ci': 'ci', 'CINEMA & MEDIA STUDIES': 'ci', 'CI': 'ci',
    'editorial studies': 'ei', 'ei': 'ei', 'EDITORIAL STUDIES': 'ei', 'EI': 'ei',

    # --- Engineering ---
    'mechanical engineering': 'me', 'me': 'me', 'MECHANICAL ENGINEERING': 'me', 'ME': 'me',

    # --- Core Curriculum ---
    'core curriculum': 'cc', 'cc': 'cc', 'CORE CURRICULUM': 'cc', 'CC': 'cc',

    # --- Languages (extra variations) ---
    'turkish': 'lt', 'lt': 'lt', 'LT': 'lt',
    'japanese': 'jp', 'jp': 'jp', 'JAPANESE': 'jp', 'JP': 'jp',
    'portuguese': 'lp', 'lp': 'lp', 'PORTUGUESE': 'lp',
    'russian': 'lr', 'lr': 'lr', 'RUSSIAN': 'lr',
    'vietnamese': 'lv', 'lv': 'lv', 'VIETNAMESE': 'lv',
    'swahili': 'ls', 'ls': 'ls', 'SWAHILI': 'ls',
    'french': 'lf', 'lf': 'lf', 'FRENCH': 'lf',
    'german': 'lg', 'lg': 'lg', 'GERMAN': 'lg',
    'italian': 'li', 'li': 'li', 'ITALIAN': 'li',
    'korean': 'lk', 'lk': 'lk', 'KOREAN': 'lk',
    'hindi-urdu': 'lh', 'lh': 'lh', 'HINDI-URDU': 'lh',
    'chinese': 'lc', 'lc': 'lc', 'CHINESE': 'lc',
    'yiddish': 'ly', 'ly': 'ly', 'YIDDISH': 'ly',
    'african american & black diaspora studies': 'aa', 'aa': 'aa', 'AFRICAN AMERICAN & BLACK DIASPORA STUDIES': 'aa', 'AA': 'aa',
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