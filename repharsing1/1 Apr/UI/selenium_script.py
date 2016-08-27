from selenium import webdriver
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('atOnce', type=int,
                   help='articles to post at once')
parser.add_argument('profile',                   
                   help='profile name')

parser.add_argument('spinner',                   
                   help='spinner name')
parser.add_argument('url',                   
                   help='Enter RSS URL topic name')
parser.add_argument('keyword',                  
                   help='Enter keyword for Image')
args = parser.parse_args()

driver = webdriver.Firefox()

atonce = args.atOnce
profile = args.profile
spinner = args.spinner
url = args.topic
keyword = args.keyword

try:
    driver.find_element_by_id('profile').clear()
    driver.find_element_by_id('profile').send_keys(profile)
except:
    pass
try:
    driver.find_element_by_id('atonce').clear()
    driver.find_element_by_id('atonce').send_keys(atonce)
except:
    pass
try:
    driver.find_element_by_id('spinner').clear()
    driver.find_element_by_id('spinner').send_keys(spinner)
except:
    pass
try:
    driver.find_element_by_id('keyword').clear()
    driver.find_element_by_id('keyword').send_keys(keyword)
except:
    pass

try:
    driver.find_element_by_id('urls').clear()
    driver.find_element_by_id('urls').send_keys(url)
except:
    pass

driver.find_element_by_id('btn_submit').click()
