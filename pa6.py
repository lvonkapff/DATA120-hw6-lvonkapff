#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bs4
import time
from time import sleep
import pandas as pd
from io import StringIO
import pandas as pd
import re
import requests

def scrape_course(page):
    soup = bs4.BeautifulSoup(page.text)
    course_numbers = []
    descriptions = []
    terms_offered = []
    equivalent_courses = []
    prerequisites = []
    instructors = []
    
    course_blocks = soup.find_all("div", class_="courseblock main")
    subsequence_blocks = soup.find_all("div", class_="courseblock subsequence")
    
    for course in course_blocks+subsequence_blocks:
        if course.find("p", class_="courseblockdetail"):
            course_number = course.find("p", class_="courseblocktitle").strong.text.split('.')[0]
            if len(course_number) == 10:
                course_numbers.append(course_number[:4]+ " " + course_number[-5:])
            else:
                course_number.append(course_number[:4]+ ' ' + course_number[5:])
            description = course.find("p", class_="courseblockdesc")
            if description:
                course_description = description.text.strip()
                descriptions.append(course_description)
            else:
                descriptions.append(None)
            course_details = course.find("p", class_="courseblockdetail").text.strip()
            term_offered = re.findall(r"Terms Offered: (.+)", course_details)
            if term_offered:
                terms_offered.append(term_offered[0])
            else:
                terms_offered.append(None)
            instructor = re.findall(r"Instructor\(s\): ([^\s][^:]+?)(?:\s*(?:Terms Offered|Prerequisite|Equivalent Course)\(s\)|$)", course_details)
            if instructor:
                instructors.append(instructor[0])
            else:
                instructors.append(None)
            equivalent_course = re.findall(r"Equivalent Course\(s\): (.+?)(?:\n|$)", course_details)
            if equivalent_course:
                equivalent_courses.append(equivalent_course[0])
            else:
                equivalent_courses.append(None)
            prerequisite = re.findall(r"Prerequisite\(s\): (.+?)\n", course_details)
            if prerequisite:
                prerequisites.append(prerequisite[0])
            else:
                prerequisites.append(None)
    df = pd.DataFrame({
        'Course Number': course_numbers,
        'Description': descriptions,
        'Terms Offered': terms_offered,
        'Equivalent Courses': equivalent_courses,
        'Prerequisites': prerequisites,
        'Instructors': instructors
    })
    return df

def process_li(li):
    href = li.find('a')['href']
    full_url = "http://collegecatalog.uchicago.edu" + href
    print(full_url)
    page = requests.get(full_url)
    if page.status_code == 200:
        return scrape_course(page)
    else:
        print(f"Failed to retrieve page: {full_url}")
        return pd.DataFrame()
    
page = requests.get("http://collegecatalog.uchicago.edu/thecollege/programsofstudy/")
soup = bs4.BeautifulSoup(page.text)
li_elements = soup.find_all('li')
dfs = []
for li in li_elements[6:-28]:
    df = process_li(li)
    if not df.empty:
        dfs.append(df)
    sleep(3)
final_df = pd.concat(dfs, ignore_index=True)
final_df

final_df["Department"]=final_df["Course Number"].str[:4]
final_df.groupby("Department")["Course Number"].count().idxmax()

final_df['Terms Offered'] = final_df['Terms Offered'].fillna('None')
quarters = final_df['Terms Offered'].str.split(',').explode().str.strip()
quarter_counts = quarters.value_counts()
quarter_counts

final_df.to_csv('HW6_dataframe.csv', index=False)

