import requests
from user_agent import generate_user_agent
import json

import pyexcel
from addict import Dict

from random import randint
from time import sleep


def crawl_one_uni_in_list():
    # ua.update()
    headers = {'User-Agent': generate_user_agent()}

    #
    #
    url_format = "https://www.usnews.com/best-colleges/rankings/national-universities?_page={0}&format=json"
    # #
    # #
    page_no = 14
    url = url_format.format(page_no)
    # #
    # #
    response_text = None

    while response_text is None:
        response = requests.get(url, headers=headers)
        if "You don't have permission to access" not in response.text:
            response_text = response.text
            print("Xin roi")
        else:
            print("Huhu")
            seconds_to_sleep = randint(10, 20)
            print("Seconds to sleep", seconds_to_sleep)
            for i in range(seconds_to_sleep):
                print(i)
                sleep(1)

    with open("national_{0}.json".format(page_no), "w") as f:
        f.write(response_text)

def extract(item):
    institution = item['institution']
    searchData = item['searchData']
    name = institution['displayName']
    ranking = institution['rankingSortRank']
    state = institution['state']
    tuition = searchData['tuition']['rawValue']
    acceptance_rate = searchData['acceptance-rate']['rawValue']
    sat_avg = searchData['sat-avg']['rawValue']

    return {
        'name': name,
        'ranking': ranking,
        'state': state,
        'tuition': tuition,
        'acceptance_rate': acceptance_rate,
        'sat_avg': sat_avg
    }


def extract_page(page):
    uni_json_string = open("national_{0}.json".format(page)).read()
    uni_dict = json.loads(uni_json_string)
    items = uni_dict['data']['items']
    colleges_at_page = [extract(item) for item in items]
    return colleges_at_page

crawl_one_uni_in_list()

# college_list = []
# for i in range(1, 16):
#     college_list.extend(extract_page(i))
#
#
# pyexcel.save_as(records=college_list, dest_file_name="national.xlsx")
