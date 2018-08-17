import requests
import json
from bs4 import BeautifulSoup
from agents import desktop_agents

import pyexcel

import os
import datetime

from time import sleep
from random import randint, choice

NATIONAL_UNI_TYPE = "national-universities"
LIBERAL_UNI_TYPE = "national-liberal-arts-colleges"

REGIONAL_NORTH = "regional-universities-north"
REGIONAL_SOUTH = "regional-universities-south"
REGIONAL_MIDWEST = "regional-universities-midwest"
REGIONAL_WEST = "regional-universities-west"



def extract(item):
    institution = item['institution']
    searchData = item['searchData']
    name = institution['displayName']
    ranking = institution['rankingSortRank']
    state = institution['state']
    tuition = searchData['tuition']['rawValue']
    acceptance_rate = searchData['acceptance-rate']['rawValue']
    sat_avg = searchData['sat-avg']['rawValue']
    act_avg = searchData['sat-avg']['rawValue']
    gpa_avg = searchData['hs-gpa-avg']['rawValue']

    return {
        'name': name,
        'ranking': ranking,
        'state': state,
        'tuition': tuition,
        'acceptance_rate': acceptance_rate,
        'sat_avg': sat_avg,
        'act_avg': act_avg,
        'gpa_avg': gpa_avg,
        'url': 'https://www.usnews.com/best-colleges/{0}-{1}'.format(institution['urlName'], institution['primaryKey']),
        'primary_key': institution['primaryKey'],
    }


def extract_page(page, ranking_type_url=NATIONAL_UNI_TYPE):
    uni_json_string = open("{0}/{1}.json".format(ranking_type_url, page)).read()
    uni_dict = json.loads(uni_json_string)
    items = uni_dict['data']['items']
    colleges_at_page = [extract(item) for item in items]
    return colleges_at_page

def get_detail(college, ranking_type_url=NATIONAL_UNI_TYPE):
    print("Getting detail of {0}".format(college['name']))
    url = college['url']
    primary_key = college['primary_key']
    html_file_url = "{0}/{1}.html".format(ranking_type_url, primary_key)

    if os.path.exists(html_file_url):
        print("HTML alreay exists")
        return
    # #
    response_text = None

    while response_text is None:
        headers = {'User-Agent': choice(desktop_agents)}
        response = requests.get(url, headers=headers)
        if "You don't have permission to access" in response.text:
            response_text = None
            print("No permissions, retrying...")
            time_to_sleep = randint(1, 5) * 10
            print("Sleeping for", time_to_sleep, "seconds") 
            for i in range(time_to_sleep):
                print(i)
                sleep(1)
        else:
            response_text = response.text
    
    with open(html_file_url, "w") as f:
        f.write(response_text)

def read_college_list(ranking_type_url=NATIONAL_UNI_TYPE, page_max=15):
    college_list = []
    for i in range(1, page_max + 1):
        college_list.extend(extract_page(i, ranking_type_url))
    return college_list

def crawl_college_details(college_list, ranking_type_url=NATIONAL_UNI_TYPE):
    for college in college_list:
        get_detail(college, ranking_type_url)

def fill_college_details(college_list, ranking_type_url=NATIONAL_UNI_TYPE):
    for index, college in enumerate(college_list):
        print("Filling college {0}-{1}:{2}.html, {3}".format(index, college['name'], college['primary_key'], college['url']))
        fill_college_detail(college, ranking_type_url)

def fill_college_detail(college, ranking_type_url=NATIONAL_UNI_TYPE):
    html_file_url = "{0}/{1}.html".format(ranking_type_url, college['primary_key'])

    detail_html_content = ""
    with open(html_file_url) as f:
        detail_html_content = f.read()
    soup = BeautifulSoup(detail_html_content, 'html.parser')
    general_section = soup.find("section", "hero-stats-widget-stats")
    li_list = general_section.find_all("li")
    for li in li_list:
        title = li.span.text
        if title == 'Room and Board':
            college['room-and-board'] = li.strong.text
        elif title == 'Application Deadline':
            college['application-deadline'] = li.strong.text
    blocks = soup.find('h3', text="General Information").parent.find_all('span')
    for block in blocks:
        if "setting" in block.text:
            setting = block.find_previous_sibling('span').text
            college['setting'] = setting

    starting_salaries_secion = soup.find(id='Alumni Starting Salaries-section')
    if starting_salaries_secion is not None:
        major_container = starting_salaries_secion.parent.find('p', 'text-coal').parent
        majors = []
        for div in major_container.find_all('div', 'show-for-medium-up'):
            majors.append(div.span.text.strip())
        college['majors'] = "\n".join(majors)
    else:
        college['majors'] = "N/A"

def export_college_list(ranking_type_url=NATIONAL_UNI_TYPE):
    college_list = read_college_list()
    
    for college in college_list:
        get_detail(college)

    detail_html_content = ""
    for index, college in enumerate(college_list):
        print("Processing college {0}:{1}".format(index + 1, college['name']))
        with open("{0}.html".format(college['primary_key'])) as f:
            detail_html_content = f.read()
        soup = BeautifulSoup(detail_html_content, 'html.parser')
        general_section = soup.find("section", "hero-stats-widget-stats")
        li_list = general_section.find_all("li")
        for li in li_list:
            title = li.span.text
            if title == 'Room and Board':
                college['room-and-board'] = li.strong.text
            elif title == 'Application Deadline':
                college['application-deadline'] = li.strong.text
        blocks = soup.find('h3', text="General Information").parent.find_all('span')
        for block in blocks:
            if "setting" in block.text:
                setting = block.find_previous_sibling('span').text
                college['setting'] = setting

        major_container = soup.find(id='Alumni Starting Salaries-section').parent.find('p', 'text-coal').parent
        majors = []
        for div in major_container.find_all('div', 'show-for-medium-up'):
            majors.append(div.span.text.strip())
        college['majors'] = "\n".join(majors)
    pyexcel.save_as(records=college_list, dest_file_name="results/national_2018_08_17_2.xlsx")

## Crawl Uni page
def crawl_uni_pages(ranking_type_url=NATIONAL_UNI_TYPE, page_max=15):
    for i in range(1, page_max + 1):
        print("Crawling {0}: {1}".format(ranking_type_url, i))
        crawl_uni_page(i, ranking_type_url)

def crawl_uni_page(page_no=1, ranking_type_url=NATIONAL_UNI_TYPE):
    
    json_file_url = "{0}/{1}.json".format(ranking_type_url, page_no)
    if os.path.exists(json_file_url):
        print("Data is already present")
        return
    #
    #
    url_format = "https://www.usnews.com/best-colleges/rankings/{0}?_page={1}&format=json"
    # #
    # #
    url = url_format.format(ranking_type_url, page_no)
    # #
    # #
    response_text = None

    while response_text is None:
        user_agent = choice(desktop_agents)
        headers = {'User-Agent': user_agent}
        print("Useragent:", user_agent)
        response = requests.get(url, headers=headers)
        if "You don't have permission to access" not in response.text:
            response_text = response.text
            print("Access was successful")
        else:
            print("Access was NOT successful, retrying...")
            seconds_to_sleep = randint(10, 20)
            print("Seconds to sleep", seconds_to_sleep)
            for i in range(seconds_to_sleep):
                print(i)
                sleep(1)
    if not os.path.exists(ranking_type_url):
        os.mkdir(ranking_type_url)
    with open(json_file_url, "w") as f:
        f.write(response_text)

for ranking_type_url in [REGIONAL_NORTH, REGIONAL_SOUTH, REGIONAL_MIDWEST, REGIONAL_WEST]:
    page_max = 5
    crawl_uni_pages(ranking_type_url, page_max)
    college_list = read_college_list(ranking_type_url, page_max)
    crawl_college_details(college_list, ranking_type_url)
    fill_college_details(college_list, ranking_type_url)


    now_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pyexcel.save_as(records=college_list, dest_file_name="{0}/{0}_uni_{1}.xlsx".format(ranking_type_url, now_string))