import Web_Scraping as WS
import re


def classes(className):
    """
    Extracts the prerequisite section from a course description.
    Example:
      "Undergraduate Prerequisites: First-Year Writing Seminar (WR 120 or equivalent) - ..."
      → "First-Year Writing Seminar (WR 120 or equivalent)"
    """
    desc = WS.scrape_course_description(className)
    if not desc:
        return None
    # Broader regex — matches "Undergraduate Prerequisites", "Prereq", etc.
    match = re.search(r'Prerequisites?:\s*(.*?)\s*-\s', desc, re.IGNORECASE | re.DOTALL)
    if match:
        prereq = match.group(1).strip()
        # Remove parentheses but keep contents
        prereq = re.sub(r'[\(\)]', '', prereq)
        # Clean up multiple spaces
        prereq = re.sub(r'\s+', ' ', prereq)
        return prereq.strip()
    return None




print(classes("religion 245"))