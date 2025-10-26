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
        return None

    description = ws.scrape_course_description(course_name)
    if not description:
        # course not available on BU site
        return "COURSE_NOT_FOUND"

    match = re.search(
        r'Prerequisites\s*:?\s*(.*?)\s*(?:-|\.|\n|$)',
        description,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        # course exists, but has no prereqs
        return ""

    prereq_text = match.group(1)
    prereq_text = ws.clean_text(prereq_text)
    prereq_text = re.sub(r'\bCAS', '', prereq_text, flags=re.IGNORECASE)
    prereq_text = normalize_separators(prereq_text)
    return prereq_text


def extract_course_codes(prereq_string):
    codes = re.findall(r'\b[A-Z]{2,4}\s*\d{3}[A-Z]?\b', prereq_string)
    slash_codes = re.findall(r'\b([A-Z]{2,4}\d{3})/([A-Z]{2,4}\d{3})\b', prereq_string)
    for c1, c2 in slash_codes:
        codes.append(c1)
        codes.append(c2)
    return list(set(codes))


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

        if prereq_string == "COURSE_NOT_FOUND":
            results.append(f"{indent}{course_disp} (course not available)")
            continue

        if prereq_string:
            results.append(f"{indent}{course_disp} prerequisites: {prereq_string}")
            prereq_codes = extract_course_codes(prereq_string)
            if prereq_codes:
                results.extend(
                    get_prereqs_for_courses(prereq_codes, visited=visited, level=level + 1)
                )
        else:
            results.append(f"{indent}{course_disp} has no prerequisites")

    return results


def classes_used(course_list):
    if isinstance(course_list, str):
        course_list = [course_list]
    return "\n".join(get_prereqs_for_courses(course_list))


def extract_hub(course_name):
    normalized_course = ws.normalize_course(course_name)
    if not normalized_course:
        return None

    description = ws.scrape_course_description(course_name)
    if not description:
        return "COURSE_NOT_FOUND"

    match = re.search(
        r"this course fulfills.*?BU Hub area[s]*:?\s*(.*?)\.",
        description,
        re.IGNORECASE | re.DOTALL
    )
    if not match:
        return ""

    hub_text = match.group(1)
    hub_text = ws.clean_text(hub_text)
    return hub_text.strip()


def get_hubs_for_courses(course_list, visited=None):
    if visited is None:
        visited = set()

    results = []

    for course in course_list:
        normalized_course = ws.normalize_course(course)
        if not normalized_course:
            results.append(f"{course} (cannot normalize)")
            continue

        if normalized_course in visited:
            continue
        visited.add(normalized_course)

        course_disp = re.sub(r'^CAS', '', normalized_course, flags=re.IGNORECASE)
        hub_text = extract_hub(course)

        if hub_text == "COURSE_NOT_FOUND":
            results.append(f"{course_disp}: Course not available")
        elif hub_text:
            results.append(f"{course_disp}: {hub_text}")
        else:
            results.append(f"{course_disp}: No Hub requirement")

    return "\n".join(results)


def hubs_used(course_list):
    if isinstance(course_list, str):
        course_list = [course_list]
    return get_hubs_for_courses(course_list)

