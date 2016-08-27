# -*- coding: cp1252 -*-
import pandas as pd
from selenium import webdriver
import time, re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
from text_unidecode import unidecode

debug = True ## whether to print the updates on screen
if debug:
    print 'Successfully imported required modules'
    
driver = webdriver.Firefox()
url = 'http://www.realtor.com/'

if debug:
    print 'Successfully opened www.realtor.com'
    
filename = 'non.csv'
output_filename = 'dataoutput_non.csv'
df = pd.read_csv(filename)
df['property_status'] = ''
df['num_bed'] = ''
df['num_baths'] = ''
df['sq_ft'] = ''
df['property_date'] = ''
df['p_price'] = ''

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
        searchBox.clear()
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
        num_bed = ''
        num_baths = ''
        sq_ft = ''
        meta = driver.find_element_by_id('ldp-property-meta')
        lis = meta.find_elements_by_tag_name('li')
        for li in lis:
            if 'beds' in li.text:
                num_bed  = li.text
            elif 'bath' in li.text:
                num_baths = li.text
            elif 'sq ft' in li.text:
                sq_ft = li.text
    except Exception,e:
        print str(e)
        num_bed = ''
        num_baths = ''
        sq_ft = ''
        
    try:
        priceElem = driver.find_element_by_css_selector('.ldp-header-price')
        spans = priceElem.find_elements_by_tag_name('span')
        for span in spans:
            try:
                if span.get_attribute('itemprop') == 'price':
                    p_price = span.text
            except Exception,e:
                print str(e)
                p_price = ''
    except Exception,e:
        print str(e)
        p_price = ''
    
    if property_status == 'Recently sold':
        try:
            price = driver.find_element_by_css_selector('#ldp-history-price')
            tbody  = price.find_element_by_tag_name('tbody')
            trs = tbody.find_elements_by_tag_name('tr')
            for tr in trs:
                tds = tr.find_elements_by_tag_name('td')
                if tds[1].text == 'Sold':
                    property_date = tds[0].text
                ## try and check when the sold instance is there, else continue

        except Exception,e:
            print str(e)
            property_date = ''
        
    elif 'ACTIVE' in property_status:
        try:
            lists = driver.find_element_by_id('ldp-detail-overview').find_element_by_css_selector('.list-default')
            lists_li = lists.find_elements_by_tag_name('li')
            for li in lists_li:
                try:
                    if 'days on realtor.com' in li.text:
                        days = int(re.findall(r'(\d+)\s+days', (unidecode(li.text)))[0])
                        property_date = str(date.today() - timedelta(days=days))
                except Exception,e:
                    print str(e)
                    property_date = ''
        except Exception,e:
            print str(e)
            property_date = ''
    else:
        property_date = ''

    return property_status, num_bed, num_baths, sq_ft, property_date, p_price
	    
    

## iterate through the dataframe and add the property status
count = 0
for i, row in df.iterrows():
    address = str(row['ADDRESS'])
    if address != 'nan':
        property_status, num_bed, num_baths, sq_ft, property_date, p_price = getRecentSoldDate(address)
    else:
        property_status, num_bed, num_baths, sq_ft, property_date, p_price = 'non', 'non', 'non', 'non', 'non', 'non'
    if debug and property_status != 'non':
        count +=1
        print 'Status of property with addresss :: ', address, ' :: ', property_status, num_bed, num_baths, sq_ft, property_date, p_price
    df.ix[i, 'property_status'] = property_status
    df.ix[i, 'num_bed'] = num_bed
    df.ix[i, 'num_baths'] = num_baths
    df.ix[i, 'sq_ft'] = sq_ft
    df.ix[i, 'property_date'] = property_date
    df.ix[i, 'p_price'] = p_price

if debug:
    print 'Total number of addresses for which sold data exists', count

df.to_csv(output_filename, index = False, encoding = 'utf-8')

if debug:
    print 'Work Finished. Written the output to :: ', output_filename
   
