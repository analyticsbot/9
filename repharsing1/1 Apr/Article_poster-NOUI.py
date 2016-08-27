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

parser = argparse.ArgumentParser()
parser.add_argument('atOnce', type=int,
                   help='articles to post at once')
parser.add_argument('profile',                   
                   help='profile name')

parser.add_argument('spinner',                   
                   help='spinner name')

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

def getGoodURLs(include, exclude, urls):
    return_urls = []
    if len(include)>0 and len(exclude)>0:    
        for url in urls:
            if ((any(word in url for word in include)) or (not (any(word in url for word in exclude)))):
                return_urls.append(url)
    elif len(include)>0 and len(exclude)==0:
        for url in urls:
            if ((any(word in url for word in include))):
                return_urls.append(url)
    elif len(include)==0 and len(exclude)>0:
        for url in urls:
            if (not (any(word in url for word in exclude))):
                return_urls.append(url)

    return return_urls

def getURLs4mFeed(feedurls):
    goodUrls = []
    for url in feedurls:
        response = requests.get(url)
        d = feedparser.parse(url.encode('ascii', 'ignore'))
        for i in range(len(d.entries)):
            goodUrls.append(d.entries[i].link)
    return goodUrls
    

def extractText(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    text = article.text
    title = article.title
    categories = article.keywords
    return text, title


def postToWP(title, article, url_bing):
    request = urllib2.Request(url_bing)
    request.add_header('Authorization', credentialBing)
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request)

    results = json.load(response)
    l = len(results['d']['results'])
    image = results['d']['results'][random.randint(0,l-1)]['Thumbnail']['MediaUrl']
    response = requests.get(image, stream=True)
    with open('testimage'+h+m+s+'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    url = "http://www.cloudhostingcom.com/xmlrpc.php"
    ##username: James
    ##pwd: mUFmNPvaXefAlgVTaTE#B2ku

    wp = wordpresslib.WordPressClient(url, 'admin', 'wIn$j5vG$#NryzJGGlBMd20J')
    wp.selectBlog(0)
    imageSrc = wp.newMediaObject('testimage'+h+m+s+'.jpg') #Used this format so that if i post images with the same name its unlikely they will override eachother

    img = '/wp-content/uploads/'+yr+'/'+mo+'/testimage'+h+m+s+'.jpg'

    post = wordpresslib.WordPressPost()

    post.title = title
    post.description = '<img src="'+img+'"/> \n' + article
    #post.tags = ["wordpress", "lib", "python"]

    # Set to False to save as a draft
    idPost = wp.newPost(post, True)
    print "Article Posted"
    return True

def spinArticle(articleText):
    
    url = 'http://wordai.com/users/turing-api.php'

    ## variables
    #s (Required) - The text that you would like WordAi to spin.
    s = articleText
    #quality (Required) - 'Regular', 'Readable', or 'Very Readable'
    #depending on how readable vs unique you want your spin to be
    quality ='Very Readable'

    #email (Required) - Your login email. Used to authenticate.
    email = 'swordai@butikmukena.com'

    #pass - Your password. You must either use this OR hash (see below)
    pwd = ''

    #hash - md5(substr(md5("pass"),0,15)); is the algorithm to calculate your hash.
    #It is a more secure way to send your password if you don't
    #want to use your password.
    hash_='f18b772e558e834d526a6985d009b7fc'

    ##output - Set to "json" if you want json output. Otherwise do not set
    #and you will get plaintext.
    output = ''

    #nonested - Set to "on" to turn off nested spinning (will help
    #readability but hurt uniqueness).
    nonested ='on'

    #sentence - Set to "on" if you want paragraph editing, where WordAi
    #will add, remove, or switch around the order of sentences in a paragraph (recommended!)
    sentence = 'on'

    #paragraph - Set to "on" if you want WordAi to do paragraph spinning -
    #perfect for if you plan on using the same spintax many times
    paragraph = 'on'

    #title - Set to "on" if you want WordAi to automatically spin your title
    #if there is one or add one if there isn't one
    title= 'on'

    #returnspin - Set to "true" if you want to just receive a spun version of the
    #article you provided. Otherwise it will return spintax.
    returnspin = 'true'

    #nooriginal - Set to "on" if you do not want to include the original word in
    #spintax (if synonyms are found). This is the same thing as creating a
    #"Super Unique" spin.
    nooriginal = 'on'

    #protected - Comma separated protected words (do not put spaces inbetween the words)
    protected = ''

    #synonyms - Add your own synonyms (Syntax: word1|synonym1,word two|first synonym 2|2nd syn). (comma separate the synonym sets and | separate the individuals synonyms)
    synonyms = 'word1|synonym1'

    headers = {'content-type':'application/x-www-form-urlencoded'}
    #data = {'s':s, 'quality':quality, 'email':email, 'pass':pwd,\
    #    'output':output, 'nonested':nonested, 'sentence':sentence,\
    #    'paragraph':paragraph, 'title':title,'returnspin':returnspin,\
    #    'nooriginal':nooriginal, 'protected':protected,'synonyms':synonyms}

    data = {'s':s, 'quality':quality, 'email':email, 'hash':hash_, 'returnspin':returnspin} #'pass':pwd}
    response  = requests.post(url, data=data, headers=headers)
    return response.text

def customSpin(articleText):
    headers = {'content-type':'application/x-www-form-urlencoded'}
    url = 'http://62.210.102.218:8080/spin?email=test@account.com&pass=P@ssw0rd&keywords=spolice&quality=20&y=4&s='+articleText
    response  = requests.get(url, headers=headers)
    return json.loads(response.text)['spinnedText']

profile = args.profile
#profile = 'test'
email = 'swordai@butikmukena.com'
pwd = 'J8weODTYl7'
hash_ = 'f18b772e558e834d526a6985d009b7fc'
output = 'json'
nonested = ''
sentence = ''
paragraph = ''
title = ''
returnspin = 'on'
nooriginal = ''
protected = ''
synonyms = ''
include = ''
include = [f.strip() for f in include.split(',')]
exclude = 'coupon, review, offer, sale, buy,cgi-sys, free, accessoriesfreeads'
exclude = [f.strip() for f in exclude.split(',')]
atOnce = int(args.atOnce)
#atOnce = 2
xdays = 1
DIVIDE_ARTICLE = 1000
xdaysNumPost = 1
spinner = args.spinner #'wordai'## 'custom' ##
#spinner = 'custom'
urls = ['https://flipboard.com/topic/cloudhosting.rss']
urls = [str(u.strip()) for u in urls]
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

for i in range(atOnce):
    urls_to_scrape_ = notScrapedURLs()
    if len(urls_to_scrape_) == 0:
        print ('no more articles to spin')
        c.close()
        conn.close()
        sys.exit(1)
    url = urls_to_scrape_.pop(i)
    print url
    articleText, title = extractText(url)
    articleText = articleText.replace('\n','')
    if spinner == 'wordai':
        len_article = len(articleText.split())
        if len_article>DIVIDE_ARTICLE:
            new_article = ''
            article_distributed = textwrap.wrap(articleText, DIVIDE_ARTICLE)
            for art in article_distributed:
                new_article += spinArticle(art)
            spinText = new_article
        spinText = spinArticle(articleText)
    elif spinner == 'custom':
        spinText = customSpin(articleText)
    postToWP(title, spinText, url_bing)
    print 'Posted an article to wordpress'
    updateScrapeURLs(url)
c.close()
conn.close()    
    
