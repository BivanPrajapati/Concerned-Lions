from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

url = 'https://www.bu.edu/academics/cas/courses/'

page = requests.get(url)

# This line is now unnecessary as the function will handle finding the list:
# soup = BeautifulSoup(page.text, 'html.parser')
# html_data = soup.find_all('ul', class_ = 'course-feed')


def parse_course_data(html_content):
    """
    Parses course data, extracting the Title (from <strong>) and
    the Description (text immediately following the <a> tag).
    """
    # FIX: html_content must be a string of HTML
    soup = BeautifulSoup(html_content, 'lxml')
    courses = []

    # Find the main course feed container
    course_list = soup.find('ul', class_='course-feed')
    if not course_list:
        return []

    # Iterate over each course item
    for course_item in course_list.find_all('li', recursive=False):
        # 1. Extract the Title Data (from <strong> inside <a>)
        title_tag = course_item.find('strong')
        title = title_tag.text.strip() if title_tag else "N/A"

        # 2. Extract the Description Data
        description_text = ''

        # Get all siblings of the <a> tag (including text and other tags)
        a_tag = course_item.find('a')
        if a_tag:
            # The description starts after the <a> tag (and sometimes a <br/>)
            current_element = a_tag.next_sibling
            while current_element:
                # Stop when we hit the BU Hub details div
                if current_element.name == 'div' and 'cf-hub-ind' in current_element.get('class', []):
                    break

                # If it's a NavigableString (text node), append it
                if isinstance(current_element, str):
                    description_text += str(current_element)

                # If it's a <br/> tag, replace it with a space or nothing
                elif current_element.name == 'br':
                    description_text += ' '

                current_element = current_element.next_sibling

        # Clean up the description text (remove leading/trailing whitespace and multiple newlines/spaces)
        description = re.sub(r'\s+', ' ', description_text).strip()

        courses.append({
            "Title": title,
            "Description": description
        })

    return courses

# Run the function and print the results
# Pass the raw HTML content (a string) from the page request
parsed_data = parse_course_data(page.text)

for course in parsed_data:
    print("---")
    print(f"Title: {course['Title']}")
    print(f"Description: {course['Description']}")
    print("---")