import re
import Web_Scraping as ws


def display_course(course):
    return re.sub(r'^CAS', '', course, flags=re.IGNORECASE)

def normalize_separators(prereq_string):
    prereq_string = re.sub(r'\s*[,;]\s*', ' and ', prereq_string, flags=re.IGNORECASE)
    prereq_string = re.sub(r'(and\s+)+and', 'and', prereq_string, flags=re.IGNORECASE)
    prereq_string = re.sub(r'\s+', ' ', prereq_string)
    return prereq_string.strip()

def extract_prereqs(course_name):
    normalized_course = ws.normalize_course(course_name)
    if not normalized_course:
        return ""
    description = ws.scrape_course_description(course_name)
    if not description:
        return ""
    match = re.search(r'Prerequisites\s*:?\s*(.*?)\s*(?:-|\.|\n|$)',
                      description, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    prereq_text = match.group(1)
    prereq_text = ws.clean_text(prereq_text)
    prereq_text = re.sub(r'\bCAS', '', prereq_text, flags=re.IGNORECASE)
    prereq_text = normalize_separators(prereq_text)
    return prereq_text

# --- Extract all course codes from a string, including slash/or ---
def extract_course_codes(prereq_string):
    # Match normal course codes
    codes = re.findall(r'\b[A-Z]{2,4}\s*\d{3}[A-Z]?\b', prereq_string)
    # Match slash-separated pairs like CS132/MA242
    slash_codes = re.findall(r'\b([A-Z]{2,4}\d{3})/([A-Z]{2,4}\d{3})\b', prereq_string)
    for c1, c2 in slash_codes:
        codes.append(c1)
        codes.append(c2)
    return list(set(codes))  # remove duplicates

def get_prereqs_for_courses(course_list, visited=None, level=0):
    if visited is None:
        visited = set()
    results = []
    indent = "    " * level

    for course in course_list:
        normalized_course = ws.normalize_course(course)
        if not normalized_course:
            results.append(f"{indent}{course} (cannot normalize)")
            continue
        if normalized_course in visited:
            continue
        visited.add(normalized_course)

        course_disp = display_course(normalized_course)
        prereq_string = extract_prereqs(course)
        if prereq_string:
            results.append(f"{indent}{course_disp} prerequisites: {prereq_string}")

            # Recursively expand all courses in the prereq string
            prereq_codes = extract_course_codes(prereq_string)
            if prereq_codes:
                results.extend(get_prereqs_for_courses(prereq_codes, visited=visited, level=level+1))
        else:
            results.append(f"{indent}{course_disp} has no prerequisites")

    return results

def classes_used(course_list):
    if isinstance(course_list, str):
        course_list = [course_list]
    return "\n".join(get_prereqs_for_courses(course_list))

print(classes_used("cs330"))