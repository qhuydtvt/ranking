# import requests
# from user_agent import generate_user_agent
# url = 'https://www.usnews.com/best-colleges/university-of-chicago-1774/paying'
#
# headers = {'User-Agent': generate_user_agent()}
#
# response = requests.get(url, headers=headers)
# print(response.text)

from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

opts = Options()
# opts.set_headless()
profile = FirefoxProfile()
profile.set_preference("javascript.enabled", False)
browser = Firefox(firefox_profile=profile, options=opts, executable_path=os.path.join(dir_path, 'geckodriver'))
print("Getting page...")
browser.get('https://www.usnews.com/best-colleges/university-of-chicago-1774/paying')

widget_class_name = 'hero-stats-widget-stats'
print("Finding stats section...")
stats_wrapper = browser.find_element_by_xpath('//section[@class="hero-stats-widget-stats"]')
print("Finding stats list region")
stats_ul = stats_wrapper.find_element_by_tag_name('ul')
stats_li_list = stats_ul.find_elements_by_tag_name('li')
for li in stats_li_list:
    span_title = li.find_element_by_tag_name("span").text
    strong_content = li.find_element_by_tag_name("strong")
    if span_title is not None:
        if span_title.strip() == "ROOM AND BOARD":
            print(strong_content.text)
        elif span_title.strip() == "APPLICATION DEADLINE":
            print(strong_content.text)
