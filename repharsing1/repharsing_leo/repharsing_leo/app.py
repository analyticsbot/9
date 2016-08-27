# import the Flask class from the flask module and other required modules
from flask import Flask, render_template, request, make_response, session, url_for, jsonify
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys, sqlite3
import requests, feedparser
from newspaper import Article
import wordpresslib
import urllib2, json, shutil, requests
import time
import wordpresslib
from PIL import Image
from datetime import datetime

time = datetime.now()

h = str(time.strftime('%H'))
m = str(time.strftime('%M'))
s = str(time.strftime('%S'))
mo = str(time.strftime('%m'))
yr = str(time.strftime('%Y'))

keyBing = 'oe+UNVTEf8jvNUB+RasqpDY8RkC5cVeAIP0s9I2AvQ8='        # get Bing key from: https://datamarket.azure.com/account/keys
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
searchString = '%27Xbox+One%27'
top = 20
offset = 0

url = 'https://api.datamarket.azure.com/Bing/Search/Image?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % (searchString, top, offset)


reload(sys)
sys.setdefaultencoding('utf-8')

# create the application object
app = Flask(__name__)
app.secret_key = "/\xfa-\x84\xfeW\xc3\xda\x11%/\x0c\xa0\xbaY\xa3\x89\x93$\xf5\x92\x9eW}"
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.WTF_CSRF_SECRET_KEY  = "spinningbot"
app.CSRF_ENABLED = True
app.debug = True


@app.route('/', methods=['GET'])
def home():
    """ flask view for the home page"""
    return render_template('index_2.html')

def getGoodURLs(include, exclude, urls):
    return_urls = []
    for url in urls:
        if ((any(word in url for word in include)) and (not (any(word in url for word in exclude)))):
            return_urls.append(url)

    return return_urls

def extractText(url):
    article = Article(url)
    article.download()
    article.parse()
    text = article.text
    return text

def getURLs4mFeed(feedurls):
    goodUrls = []
    for url in feedurls:
        response = requests.get(url)
        d = feedparser.parse(response.text.encode('ascii', 'ignore'))
        for i in range(len(d.entries)):
            goodUrls.append( d.entries[i].link)
    return goodUrls

def posttoWP(title, article):
    request = urllib2.Request(url)
    request.add_header('Authorization', credentialBing)
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request) 

    results = json.load(response)
    image = results['d']['results'][0]['Thumbnail']['MediaUrl']
    response = requests.get(image, stream=True)
    with open('testimage'+h+m+s+'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    print image

    url = "http://www.easyinjury.com/xmlrpc.php"
    ##URL: www.easyinjury.com
    ##username: James
    ##pwd: mUFmNPvaXefAlgVTaTE#B2ku

    wp = wordpresslib.WordPressClient(url, 'James', 'mUFmNPvaXefAlgVTaTE#B2ku')
    wp.selectBlog(0)
    imageSrc = wp.newMediaObject('testimage'+h+m+s+'.jpg') #Used this format so that if i post images with the same name its unlikely they will override eachother

    img = '/wp-content/uploads/'+yr+'/'+mo+'/testimage'+h+m+s+'.jpg'

    post = wordpresslib.WordPressPost()

    post.title = 'Title'
    post.description = '<img src="'+img+'"/>' + 'Content'
    post.tags = ["wordpress", "lib", "python"]

    # Set to False to save as a draft
    idPost = wp.newPost(post, True)

def spinArticle():
    ## variables
    #s (Required) - The text that you would like WordAi to spin.
    s = 'The text that you would like WordAi to spin.'
    #quality (Required) - 'Regular', 'Readable', or 'Very Readable'
    #depending on how readable vs unique you want your spin to be
    quality ='Very Readable'

    #email (Required) - Your login email. Used to authenticate.
    email = 'swordai@butikmukena.com'

    #pass - Your password. You must either use this OR hash (see below)
    pwd = 'J8weODTYl7'

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
    data = {'s':s, 'quality':quality, 'email':email, 'pass':pwd,\
            'output':output, 'nonested':nonested, 'sentence':sentence,\
            'paragraph':paragraph, 'title':title,'returnspin':returnspin,\
            'nooriginal':nooriginal, 'protected':protected,'synonyms':synonyms}

    data = {'s':s, 'quality':quality, 'email':email, 'hash':hash_} #'pass':pwd}
    ##data = {'s':s, 'quality':quality, 'email':email, 'hash':hash_,
    ##        'returnspin':returnspin} #'pass':pwd}
    response  = requests.post(url, data = data, headers=headers)
    print response.text
    
@app.route('/go', methods=['POST'])
def postWP(numrows=10):
    """ flask view for the search page"""
    if request.method == "POST":
        errors = {}
        profile = request.form['profile']
        email = request.form['email']
        pwd = request.form['pwd']
        hash_ = request.form['hash']
        output = request.form['output']
        nonested = request.form['nonested']
        sentence = request.form['sentence']
        paragraph = request.form['paragraph']
        title = request.form['title']
        returnspin = request.form['returnspin']
        nooriginal = request.form['nooriginal']
        protected = request.form['protected']
        synonyms = request.form['synonyms']
        include = request.form['include']
        include = [f.strip().split(',') for f in include]
        exclude = request.form['exclude']
        exclude = [f.strip().split(',') for f in exclude]
        emailwp = request.form['emailwp']
        pwdwp = request.form['pwdwp']
        atonce = request.form['atonce']
        xdays = request.form['xdays']
        xdaysNumPost = request.form['xdaysNumPost']
        urls = request.form['urls']
        urls = [str(u.strip()) for u in urls]
        goodUrls = getURLs4mFeed(urls)
        urls_to_scrape = getGoodURLs(include, exclude, goodUrls)
            
        
                    

        return render_template('index.html', url = url, message = "Please Wait...", profile=profile,\
                               email=email,pwd=pwd,hash=hash,output=output,nonested=nonested,\
                               sentence=sentence,paragraph=paragraph,title=title,returnspin=returnspin,\
                               nooriginal=nooriginal,protected=protected,synonyms=synonyms,include=include,\
                               exclude=exclude,emailwp=emailwp,pwdwp=pwdwp,atonce=atonce,xdaysNumPost=xdaysNumPost)

if __name__ == '__main__':
        app.run(debug=True)
