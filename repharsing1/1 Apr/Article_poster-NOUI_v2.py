# import the Flask class from the flask module and other required modules
#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys, sqlite3, wordpresslib, time, argparse, textwrap, random
from newspaper import Article
import urllib2, json, shutil, requests, logging, time, random, feedparser
from PIL import Image
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import os


parser = argparse.ArgumentParser()
parser.add_argument('atOnce', type=int,
                   help='articles to post at once')
parser.add_argument('profile',                   
                   help='profile name')

parser.add_argument('spinner',                   
                   help='spinner name')
parser.add_argument('topic',                   
                   help='topic name')

args = parser.parse_args()

time1 = datetime.now()

h = str(time1.strftime('%H'))
m = str(time1.strftime('%M'))
s = str(time1.strftime('%S'))
mo = str(time1.strftime('%m'))
yr = str(time1.strftime('%Y'))

keyBing = 'oe+UNVTEf8jvNUB+RasqpDY8RkC5cVeAIP0s9I2AvQ8='        # get Bing key from: https://datamarket.azure.com/account/keys
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
searchString = '%27Cloud+Computing%27'
top = 20
offset = 0
url_bing = 'https://api.datamarket.azure.com/Bing/Search/Image?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % (searchString, top, offset)

def getGoodURLs(include, exclude, urls, titles):
    return_urls = []
    if len(include)>0 and len(exclude)>0:    
        for url in urls:
            ix = urls.index(url)
            title_ = titles[ix]
            if ((any(word in url for word in include)) or (not (any(word in url for word in exclude))))\
               or ((any(word in title_.lower() for word in include)) or (not (any(word in title_.lower() for word in exclude)))):
                return_urls.append(url)
    elif len(include)>0 and len(exclude)==0:
        for url in urls:
            ix = urls.index(url)
            title_ = titles[ix]
            if ((any(word in url for word in include))) or ((any(word in title_.lower() for word in include))):
                return_urls.append(url)
    elif len(include)==0 and len(exclude)>0:
        for url in urls:
            ix = urls.index(url)
            title_ = titles[ix]
            if (not (any(word in url for word in exclude))) or (not (any(word in title_.lower() for word in exclude))):
                return_urls.append(url)

    return return_urls

def getURLs4mFeed(feedurls):
    goodUrls = []
    titles = []
    for url in feedurls:
        response = requests.get(url)
        d = feedparser.parse(url.encode('ascii', 'ignore'))
        for i in range(len(d.entries)):
            goodUrls.append(d.entries[i].link)
            titles.append(d.entries[i].title)
    return goodUrls, titles
    
def extractText(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    text = article.text
    title = article.title
    categories = article.keywords
    return text, title, categories
   
def postToWP(title, article, url_bing):
    request = urllib2.Request(url_bing)
    request.add_header('Authorization', credentialBing)
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request)
    results = json.load(response)
    l = len(results['d']['results'])
    image = results['d']['results'][random.randint(0,l-1)]['Thumbnail']['MediaUrl']
    response = requests.get(image, stream=True)
    with open('image'+h+m+s+'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    filename = 'image'+h+m+s+'.jpg'
    url = "http://www.cloudhostingcom.com/xmlrpc.php"
    wp = Client(url, 'admin', 'wIn$j5vG$#NryzJGGlBMd20J')
    # prepare metadata
    data = {
        'name': 'image'+h+m+s+'.jpg',
        'type': 'image/jpeg',  # mimetype
    }
    with open(filename, 'rb') as img:
        data['bits'] = xmlrpc_client.Binary(img.read())
    response = wp.call(media.UploadFile(data))
    
    img = '/wp-content/uploads/'+yr+'/'+mo+'/image'+h+m+s+'.jpg'
    post = WordPressPost()
    post.title = title
    post.content = '<img class="alignleft" src="'+img+'" width="341" height="341"/> \n' + article
    post.terms_names = {
        'category': categories[:2]
    }
    
    post.post_status = 'publish'
    wp.call(NewPost(post))
    return True
    
def spinArticle(articleText):    
    url = 'http://wordai.com/users/turing-api.php'
    ## variables
    s = articleText
    quality ='Very Readable'
    email = 'leo@adgency.ca'
    pwd = ''
    hash_='668d35909fd68cdf9f071545246ecd50'
    output = ''
    nonested ='on'
    sentence = 'on'
    paragraph = 'on'
    title= 'on'
    returnspin = 'true'
    nooriginal = 'on'
    protected = ''
    synonyms = 'word1|synonym1'
    headers = {'content-type':'application/x-www-form-urlencoded'}
    data = {'s':s, 'quality':quality, 'email':email, 'hash':hash_, 'returnspin':returnspin} #'pass':pwd}
    response  = requests.post(url, data=data, headers=headers)
    return response.text

def customSpin(articleText):
    headers = {'content-type':'application/x-www-form-urlencoded'}
    url = 'http://62.210.102.218:8080/spin?email=test@account.com&pass=P@ssw0rd&keywords=spolice&quality=20&y=4&s='+articleText
    response  = requests.get(url, headers=headers)
    return json.loads(response.text)['spinnedText']

profile = args.profile
topic = args.topic
include = ''
include = [f.strip() for f in include.split(',')]
exclude = 'coupon, review, offer, sale, buy,cgi-sys, free, accessoriesfreeads'
exclude = [f.strip() for f in exclude.split(',')]
atOnce = int(args.atOnce)
xdays = 1
DIVIDE_ARTICLE = 500
xdaysNumPost = 1
spinner = args.spinner #'wordai' OR 'custom' #
urls = ['https://flipboard.com/topic/' + topic + '.rss']
urls = [str(u.strip()) for u in urls]
time.sleep(2)
goodUrls, titles = getURLs4mFeed(urls)
urls_to_scrape = getGoodURLs(include, exclude, goodUrls, titles)
conn = sqlite3.connect('spinnerData.db')
c = conn.cursor()

def insertURLs(profile, urls_to_scrape):
    query = 'SELECT name FROM sqlite_master WHERE name="' + profile +'"'
    c.execute(query)
    rows = c.fetchone()
    if rows is None:
        create_table_query = 'CREATE TABLE ' + str(profile) + '( ID INTEGER PRIMARY KEY AUTOINCREMENT, URL CHAR(500000), SCRAPED INT);'
        c.execute(create_table_query)
        conn.commit()
        for url in urls_to_scrape:
            insert_url_query = 'INSERT INTO ' + str(profile) + ' (URL, SCRAPED)  VALUES ("' + str(url) +'",0);'
            c.execute(insert_url_query)
        conn.commit()

insertURLs(profile, urls_to_scrape)

def updateScrapeURLs(url):
    update_url_query = 'UPDATE ' + str(profile) + ' SET SCRAPED = 1 WHERE URL = "' + str(url)+ '";'
    c.execute(update_url_query)
    conn.commit()

def notScrapedURLs():
    query = 'SELECT url FROM ' + str(profile) + ' WHERE scraped=0'
    c.execute(query)
    rows = c.fetchall()
    rows = [r[0] for r in rows]
    return rows

def trimArticle(articleText, DIVIDE_ARTICLE):
    article_distributed = articleText.split()
    len_article = len(article_distributed)
    if len_article>DIVIDE_ARTICLE:
        new_article = ''
        for i in range(DIVIDE_ARTICLE):
            new_article = new_article + ' ' + article_distributed[i]
        
        while True:
            i+=1
            new_article = new_article + ' ' + article_distributed[i]
            if new_article.endswith('.'):
                break
    else:
        new_article = articleText
    return new_article.strip()

for i in range(atOnce):
    urls_to_scrape_ = notScrapedURLs()
    if len(urls_to_scrape_) == 0:
        print ('no more articles to spin')
        c.close()
        conn.close()
        sys.exit(1)
    url = urls_to_scrape_.pop(i)
    print url
    articleText, title, categories = extractText(url)
    articleText = articleText.replace('\n','\\n\\')
    articleText = trimArticle(articleText, DIVIDE_ARTICLE)
    articleText = articleText.replace('\\n\\','\n')
    '''
    if spinner == 'wordai':
        spinText = spinArticle(articleText)
    elif spinner == 'custom':
        spinText = customSpin(articleText)
    '''
    postToWP(title, articleText, url_bing)
    print 'Posted an article to wordpress'
    updateScrapeURLs(url)

c.close()
conn.close()    
    
