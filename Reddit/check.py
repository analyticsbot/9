##import requests
##
##url = 'https://www.reddit.com/r/gifs'
##
##from bs4 import BeautifulSoup
##resp = requests.get(url)
##soup = BeautifulSoup(resp.content)
##siteTable = soup.find(attrs = {'id':'siteTable'})


import mechanize
from bs4 import BeautifulSoup
import cookielib
url = 'https://www.reddit.com/r/funny?count=0'
url = 'https://www.reddit.com/r/movies/comments/4n0i8t/whats_an_ip_you_want_to_see_get_a_movie_one_thats/'
#Browser
br = mechanize.Browser()
 
#Cookie Jar
cj = cookielib.LWPCookieJar()
 
#Browser Options
br.set_cookiejar(cj)
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
 
 
#Adding request headers
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'),
                              ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                              ('Accept-Language', 'en-gb,en;q=0.5'),
                              ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')]

br.open(url)
html = br.response().read()
soup = BeautifulSoup(html, 'lxml')

siteTable = soup.find(attrs = {'id':'siteTable'})
divs = siteTable.findAll('div')
