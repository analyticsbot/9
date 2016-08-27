# import the Flask class from the flask module and other required modules
#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys, sqlite3, wordpresslib, time, argparse, textwrap, random
import newspaper
from newspaper import Config, Article, Source, ArticleException
import urllib2, json, shutil, requests, logging, time, random, feedparser
from PIL import Image
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import os, json, time

'''
username = 'lum-customer-senexx-zone-gen-country-us'
password = '2634d932928f'
port = 22225
session_id = random.random()
super_proxy_url = ('http://%s-session-%s:%s@zproxy.luminati.io:%d' %
    (username, session_id, password, port))
proxy_handler = urllib2.ProxyHandler({
    'http': super_proxy_url,
    'https': super_proxy_url,
})
opener = urllib2.build_opener(proxy_handler)
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')]
urllib2.install_opener(opener)
'''
parser = argparse.ArgumentParser()
parser.add_argument('atOnce', type=int,
                   help='articles to post at once')
parser.add_argument('profile',                   
                   help='profile name')

#parser.add_argument('spinner',                   
#                   help='spinner name')
parser.add_argument('topic',                   
                   help='Enter RSS URL topic name')
parser.add_argument('keyword',                  
                   help='Enter keyword for Image')
args = parser.parse_args()

keyBing = 'oe+UNVTEf8jvNUB+RasqpDY8RkC5cVeAIP0s9I2AvQ8='        # get Bing key from: https://datamarket.azure.com/account/keys
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
searchString = '%27'+'+'.join(args.keyword.split())+'%27'
top = 50
offset = 0
url_bing = 'https://api.datamarket.azure.com/Bing/Search/Image?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % (searchString, top, offset)


config = Config()
config.memoize_articles = False

def insertImages(profile, imagename):
    query = 'SELECT name FROM sqlite_master WHERE name="' + profile +'_images"'
    c.execute(query)
    rows = c.fetchone()
    print 'aa', rows
    if rows is None:
        create_table_query = 'CREATE TABLE ' + str(profile) + '_images ( ID INTEGER PRIMARY KEY AUTOINCREMENT, imagename CHAR(500000));'
        print create_table_query
        c.execute(create_table_query)
        conn.commit()

    query = 'SELECT imagename '  + ' FROM "' + profile +'_images" where imagename = "'+imagename+'"'
    c.execute(query)
    present = 1
    rows = c.fetchone()
    if rows is None:
        insert_url_query = 'INSERT INTO ' + str(profile) + '_images (imagename)  VALUES ("' + str(imagename) +'");'
        c.execute(insert_url_query)
        present = 0
    conn.commit()
    return present

def getGoodURLs(include, exclude, urls):
    return_urls = []
    if len(include)>1 and len(exclude)>1:    
        for url in urls:
            ix = urls.index(url)
            if ((any(word in url for word in include)) and (not (any(word in url for word in exclude)))):
                return_urls.append(url)
        
    elif len(include)>1 and len(exclude)==1:
        for url in urls:
            ix = urls.index(url)
            if ((any(word in url for word in include))):
                return_urls.append(url)
        
    elif len(include)==1 and len(exclude)>1:
        for url in urls:
            ix = urls.index(url)
            if (not (any(word in url for word in exclude))):
                return_urls.append(url)
        
    elif len(include)==1 and len(exclude)==1:
        for url in urls:
            ix = urls.index(url)
            return_urls.append(url)
    return return_urls
   
'''
def getURLs4mFeed(feedurls):
    goodUrls = []
    titles = []
    for url in feedurls:
        response = requests.get(url)
        d = feedparser.parse(url.encode('ascii', 'ignore'))
        for i in range(len(d.entries)):
            goodUrls.append(d.entries[i].link)
            titles.append(d.entries[i].title)
    print goodUrls, titles
    return goodUrls, titles
'''

def getURLs4mFeed(feedurls):
    goodUrls = [] 
    blog = newspaper.build(feedurls, config=config)
    for article in blog.articles:
        goodUrls.append(article.url) 
    return goodUrls
       
def extractText(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    text = article.text
    title = article.title
    categories = article.keywords
    return text, title, categories
   
def postToWP(title, article, url_bing, bing_image_list, profile):
    while True:
        try:
            request = urllib2.Request(url_bing)
            request.add_header('Authorization', credentialBing)
            requestOpener = urllib2.build_opener()
            response = requestOpener.open(request)
            results = json.load(response)
            l = len(results['d']['results'])
        
            ran_num = random.randint(0,l-1)
            
            image = results['d']['results'][ran_num]['Thumbnail']['MediaUrl']
            present = insertImages(profile, image)
        except:
            pass
        if present == 0:
            break
    time1 = datetime.now()

    h = str(time1.strftime('%H'))
    m = str(time1.strftime('%M'))
    s = str(time1.strftime('%S'))
    mo = str(time1.strftime('%m'))
    yr = str(time1.strftime('%Y'))
    
    response = requests.get(image, stream=True)
    with open('image'+h+m+s+'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    filename = 'image'+h+m+s+'.jpg'
    url = 'http://www.'+args.profile+'.com/xmlrpc.php'
##    wp = Client(url, 'admin', 'wIn$j5vG$#NryzJGGlBMd20J')
##    # prepare metadata
##    data = {
##        'name': 'image'+h+m+s+'.jpg',
##        'type': 'image/jpeg',  # mimetype
##    }
##    with open(filename, 'rb') as img:
##        data['bits'] = xmlrpc_client.Binary(img.read())
##    response = wp.call(media.UploadFile(data))
    
    img = '/wp-content/uploads/'+yr+'/'+mo+'/image'+h+m+s+'.jpg'
##    post = WordPressPost()
##    post.title = title
##    post.content = '<img class="alignleft" src="'+img+'" width="341" height="341"/> \n' + article
##    post.terms_names = {
##        'category': categories[:2]
##    }
##    
##    post.post_status = 'publish'
##    wp.call(NewPost(post))
    return True, bing_image_list
    
def spinArticle(articleText):    
    url = 'http://wordai.com/users/turing-api.php'
    ## variables
    s = articleText
    quality ='Very Readable'
    email = 'leo@adgency.ca'
    pwd = ''
    hash_='668d35909fd68cdf9f071545246ecd50'
    output = 'json'
    nonested ='on'
    sentence = 'on'
    paragraph = 'off'
    title= 'off'
    returnspin = 'true'
    nooriginal = 'on'
    protected = ''
    synonyms = 'word1|synonym1'
    headers = {'content-type':'application/x-www-form-urlencoded'}
    data = {'output':output, 's':s, 'quality':quality, 'email':email, 'hash':hash_, 'returnspin':returnspin} #'pass':pwd}

    s = requests.Session()
    
    while True:
        response  = s.post(url, data=data, headers=headers, timeout=600)
        job_status = json.loads(response.text)
        if job_status['status'] == 'Success':
            break
        elif job_status['status'] == 'Failure':
            time.sleep(random.randint(15, 40))
    return job_status['text']

def customSpin(articleText):
    headers = {'content-type':'application/x-www-form-urlencoded'}
    url = 'http://62.210.102.218:8080/spin?email=test@account.com&pass=P@ssw0rd&keywords=spolice&quality=20&y=4&s='+articleText
    response  = requests.get(url, headers=headers)
    return json.loads(response.text)['spinnedText']

profile = args.profile
topic = args.topic
include = ''
include = [f.strip() for f in include.split(',')]
exclude = 'resources, forbes, washingtonpost, coupon, review, offer, sale, deal, buy,cgi-sys, free, accessoriesfreeads, discount, coupons, podcast, radio, subscribe, quickbooks, fuck, hostgator'
#exclude = ''
exclude = [f.strip() for f in exclude.split(',')]
atOnce = int(args.atOnce)
xdays = 1
DIVIDE_ARTICLE = 500
xdaysNumPost = 1
#spinner = args.spinner #'wordai' OR 'custom' #
spinner = "wordai"
urls = [args.topic]
urls = (urls[0])
#urls = [str(u.strip()) for u in urls]

time.sleep(2)
goodUrls = getURLs4mFeed(urls)
urls_to_scrape = getGoodURLs(include, exclude, goodUrls)
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

bing_image_list = []

for i in range(atOnce):
    urls_to_scrape_ = notScrapedURLs()
    if len(urls_to_scrape_) == 0:
        print ('no more articles to spin')
        c.close()
        conn.close()
        sys.exit(1)
    url = urls_to_scrape_.pop(i)
    articleText, title, categories = extractText(url)
    articleText = articleText.replace('\n','\\n\\')
    try:
        articleText = trimArticle(articleText, DIVIDE_ARTICLE)
    except:
        pass
    articleText = articleText.replace('\\n\\','\n')
    
    #print articleText
    
    #if spinner == 'wordai':
    #    spinText = spinArticle(articleText)
    #elif spinner == 'custom':
    #    spinText = customSpin(articleText)
    #time.sleep(20)

    spinText = articleText
    
    status, bing_image_list = postToWP(title, spinText, url_bing, bing_image_list, profile)
    print 'Posted an article to wordpress'
    updateScrapeURLs(url)
 
c.close()
conn.close()    
 
