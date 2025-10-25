from bs4 import BeautifulSoup
import requests
import re
import pandas as pd # 1. Import pandas

url = 'https://www.bu.edu/academics/cas/courses/'

page = requests.get(url)

def parse_course_data(html_content):
    """
    Parses course data, extracting the Title (from <strong>) and
    the Description (text immediately following the <a> tag).
    """
    # html_content must be a string of HTML
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

# Run the function to get the list of dictionaries
parsed_data = parse_course_data(page.text)

# 2. Convert the list of course dictionaries into a Pandas DataFrame
df_courses = pd.DataFrame(parsed_data)

# Print the first few rows of the DataFrame to verify the data
print("--- Pandas DataFrame Output ---")
print(df_courses.head())
print("\nDataFrame Shape:", df_courses.shape)
print("-----------------------------")

df_courses.to_csv('bu_cas_courses.csv', index=False)

# You can now save the data to a CSV file if needed:
# df_courses.to_csv('bu_cas_courses.csv', index=False)