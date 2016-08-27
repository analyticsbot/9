import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

debug = True ## whether to print the updates on screen
if debug:
    print 'Successfully imported required modules'
    
driver = webdriver.Firefox()
url = 'http://www.realtor.com/'

if debug:
    print 'Successfully opened www.realtor.com'
    
filename = 'dataoutput_Affidavit_of_Death_5.2_2016.csv'
output_filename = 'dataoutput.csv'
df = pd.read_csv(filename)
df['property_status'] = ''
df['property'] = ''

if debug:
    print 'Successfully read input file', filename,' . Total number of rows', df.shape[0]

def getRecentSoldDate(address):
    """Function to get the property status from realtor.com
    input =  address of the property
    """
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.ID, "searchBox")) )
        searchBox = driver.find_element_by_css_selector('#searchBox')
        searchBox.send_keys(address)
        driver.find_element_by_css_selector('.btn.btn-primary.js-searchButton').click()
    except:
        pass
    try:
        WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.ID, "ldp-history-price")) )
    except:
        pass
    try:
        property_status = driver.find_element_by_css_selector('.listing-header')\
                          .find_element_by_css_selector('.col-sm-6').text
    except:
        property_status = 'non'
    try:
        price = driver.find_element_by_css_selector('#ldp-history-price')
        tbody  = price.find_element_by_tag_name('tbody')
        trs = tbody.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            if tds[1].text == 'Sold':
                return tds[0].text, property_status
            ## try and check when the sold instance is there, else continue

        return 'non', property_status

    except:
        return 'non', property_status

## iterate through the dataframe and add the property status
count = 0
for i, row in df.iterrows():
    address = str(row['ADDRESS'])
    if address != 'nan':
        status,property_status = getRecentSoldDate(address)
    else:
        status, property_status = 'non', 'non'
    if debug and status != 'non':
        count +=1
        print 'Status of property with addresss :: ', address, ' :: ', status
    df.ix[i, 'property_status'] = status
    df.ix[i, 'property'] = property_status

if debug:
    print 'Total number of addresses for which sold data exists', count

df.to_csv(output_filename, index = False, encoding = 'utf-8')

if debug:
    print 'Work Finished. Written the output to :: ', output_filename
    
