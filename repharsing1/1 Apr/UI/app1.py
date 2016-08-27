# import the Flask class from the flask module and other required modules
from flask import Flask, render_template, request, make_response, session, url_for, jsonify
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys, sqlite3, requests, feedparser 
from newspaper import Article 
import urllib2, json, shutil, requests, wordpresslib, time
from PIL import Image
from datetime import datetime
from threading import Thread



keyBing = 'oe+UNVTEf8jvNUB+RasqpDY8RkC5cVeAIP0s9I2AvQ8='        # get Bing key from: https://datamarket.azure.com/account/keys
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
top = 20
offset = 0

def insertImages(profile, imagename):
    query = 'SELECT name FROM sqlite_master WHERE name="' + profile +'_images"'
    c.execute(query)
    rows = c.fetchone()
    if rows is None:
        create_table_query = 'CREATE TABLE ' + str(profile) + '_images ( ID INTEGER PRIMARY KEY AUTOINCREMENT, imagename CHAR(500000));'
        c.execute(create_table_query)
        conn.commit()

    query = 'SELECT ' + *  + ' FROM "' + profile +'_images" where imagename = "'+imagename+'"'
    c.execute(query)
    present = 1
    rows = c.fetchone()
    if rows is None:
        insert_url_query = 'INSERT INTO ' + str(profile) + '_images (imagename)  VALUES ("' + str(imagename) +'");'
        c.execute(insert_url_query)
        present = 0
    conn.commit()
    return present

def getGoodURLs(include, exclude, urls, titles):
    return_urls = []
    if len(include)>1 and len(exclude)>1:    
        for url in urls:
            ix = urls.index(url)
            title_ = titles[ix]
            if ((any(word in url for word in include)) and (not (any(word in url for word in exclude))))\
               and ((any(word in title_.lower() for word in include)) and (not (any(word in title_.lower() for word in exclude)))):
                return_urls.append(url)
    elif len(include)>1 and len(exclude)==1:
        for url in urls:
            ix = urls.index(url)
            title_ = titles[ix]
            if ((any(word in url for word in include))) and ((any(word in title_.lower() for word in include))):
                return_urls.append(url)
    elif len(include)==1 and len(exclude)>1:
        for url in urls:
            ix = urls.index(url)
            title_ = titles[ix]
            if (not (any(word in url for word in exclude))) and (not (any(word in title_.lower() for word in exclude))):
                return_urls.append(url)

    return return_urls

def extractText(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    text = article.text
    title = article.title
    categories = article.keywords
    return text, title, categories

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

def spinArticle(articleText, email, hash_):    
    url = 'http://wordai.com/users/turing-api.php'
    ## variables
    s = articleText
    quality ='Very Readable'
    email = email
    pwd = ''
    hash_= hash_
    output = 'json'
    nonested ='on'
    sentence = 'on'
    paragraph = 'on'
    title= 'on'
    returnspin = 'true'
    headers = {'content-type':'application/x-www-form-urlencoded'}
    data = {'output':output, 's':s, 'quality':quality, 'email':email, 'hash':hash_, 'returnspin':returnspin} #'pass':pwd}
    while True:
        response  = requests.post(url, data=data, headers=headers, timeout=25)
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

def insertURLs(profile, urls_to_scrape):
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()
    query = 'SELECT name FROM sqlite_master WHERE name="' + profile +'"'
    c.execute(query)
    rows = c.fetchone()
    if rows is None:
        create_table_query = 'CREATE TABLE ' + str(profile) + '( ID INTEGER PRIMARY KEY AUTOINCREMENT, URL CHAR(500000), SCRAPED INT);'
        c.execute(create_table_query)
        conn.commit()
        for url in urls_to_scrape:
            print url
            insert_url_query = 'INSERT INTO ' + str(profile) + ' (URL, SCRAPED)  VALUES ("' + str(url) +'", 0);'
            c.execute(insert_url_query)
        conn.commit()
    else:
        for url in urls_to_scrape:
            check_url = 'SELECT url FROM ' + str(profile) + ' WHERE url="'+str(url)+'";'
            c.execute(check_url)
            row = c.fetchone()
            if row is None:
                insert_url_query = 'INSERT INTO ' + str(profile) + ' (URL, SCRAPED)  VALUES ("' + str(url) +'", 0);'
                c.execute(insert_url_query)
        conn.commit()

    c.close()
    conn.close()

def updateScrapeURLs(profile, url):
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()
    update_url_query = 'UPDATE ' + str(profile) + ' SET SCRAPED = 1 WHERE URL = "' + str(url)+ '";'
    c.execute(update_url_query)
    conn.commit()
    c.close()
    conn.close()

def notScrapedURLs(profile):
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()
    query = 'SELECT url FROM ' + str(profile) + ' WHERE scraped=0'
    c.execute(query)
    rows = c.fetchall()
    rows = [r[0] for r in rows]
    c.close()
    conn.close()
    return rows
    

def work(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, urls, spinner,url_bing,keyword,split):
    urls = [str(u.strip()) for u in urls]
    goodUrls, titles = getURLs4mFeed(urls)
    urls_to_scrape = getGoodURLs(include, exclude, goodUrls, titles)
    insertURLs(profile, urls_to_scrape)
    for i in range(int(atonce)):
        urls_to_scrape_ = notScrapedURLs(profile)
        if len(urls_to_scrape_) == 0:
            print ('no more articles to spin')
            sys.exit(1)
        url = urls_to_scrape_.pop(i)
        print url
        articleText, title, categories = extractText(url)
        articleText = articleText.replace('\n','\\n\\')
        articleText = trimArticle(articleText, split)
        articleText = articleText.replace('\\n\\','\n')
        
        if spinner == 'wordai':
            spinText = spinArticle(articleText, email, hash_)
        elif spinner == 'custom':
            spinText = customSpin(articleText)

        time.sleep(20)
        postToWP(title, articleText, url_bing, bing_image_list, profile)
        print 'Posted an article to wordpress'
        updateScrapeURLs(profile, url)

def createProfile(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                                returnspin, nooriginal, protected, synonyms, include, exclude,\
                                emailwp, pwdwp, atonce, urls, spinner,keyword,split, conn, c):
    c.execute("INSERT INTO data profile = '" + str(profile) + \
              "', email = '" + str(email) +  \
              "', pwd = '" + str(pwd) + "', hash_ = '" + str(hash_) +\
              "', output = '" + str(output) + "', nonested = '" + str(nonested) +\
              "', sentence = '" + str(sentence) + "', paragraph = '" + str(paragraph) +\
              "', title = '" + str(title) + "', returnspin = '" + str(returnspin) +\
              "', nooriginal = '" + str(nooriginal) + "', protected = '" + str(protected) +\
              "', synonyms = '" + str(synonyms) + "', include = '" + str(include)+", exclude = '" + str(exclude)+\
              "', emailwp = '" + str(emailwp)+ "', pwdwp = '" + str(pwdwp)+ "', atonce = " + str(atonce)\
              +", urls = '" + str(urls)\
              +"', spinner = '" + str(spinner) + "' ;")
    conn.commit()

def updateVariables(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                                returnspin, nooriginal, protected, synonyms, include, exclude,\
                                emailwp, pwdwp, atonce, urls, spinner,keyword,split, conn, c):
    """Function to update the variables"""
    c.execute("UPDATE data SET email = '" + str(email) + \
              "', pwd = '" + str(pwd) + "', hash_ = '" + str(hash_) +\
              "', output = '" + str(output) + "', nonested = '" + str(nonested) +\
              "', sentence = '" + str(sentence) + "', paragraph = '" + str(paragraph) +\
              "', title = '" + str(title) + "', returnspin = '" + str(returnspin) +\
              "', nooriginal = '" + str(nooriginal) + "', protected = '" + str(protected) +\
              "', synonyms = '" + str(synonyms) + "', include = '" + str(include)+"', exclude = '" + str(exclude)+\
              "', emailwp = '" + str(emailwp)+"', pwdwp = '" + str(pwdwp)+"', atonce = " + str(atonce)\
              +", urls = '" + str(urls)\
              +"' , spinner = '" + str(spinner) + "' WHERE profile = '"+str(profile)+"';")
    conn.commit()
    
def getDefaultProfile(conn, c):
    """Function to get the default profile"""
    c.execute("SELECT profile from data where defaultProfile = 1")
    profile = c.fetchone()
    return profile    

def getParams(c, conn, profile):
    """Function to get the parameter"""
    c.execute("SELECT email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, urls, spinner, keyword, split from data where profile ='" + str(profile)+"';")
    params = c.fetchone()
    return params
  
# create the application object
app = Flask(__name__)
app.secret_key = "/\xfa-\x84\xfeW\xc3\xda\x11%/\x0c\xa0\xbaY\xa3\x89\x93$\xf5\x92\x9eW}"
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.WTF_CSRF_SECRET_KEY  = "spinningbot"
app.CSRF_ENABLED = True
app.debug = True

@app.route('/profile/<profile>', methods=['GET'])
@app.route('/', methods=['GET'])
def home(profile=None):
    """ flask view for the home page"""
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()

    if not profile:
        profile = getDefaultProfile(conn, c)[0]
        
    params = getParams(c, conn, profile)
    email, pwd, hash_, output, nonested, sentence, paragraph, title,\
    returnspin, nooriginal, protected, synonyms, include, exclude,\
    emailwp, pwdwp, atonce, urls, spinner, keyword, split = params[0],params[1],params[2],params[3],params[4],\
    params[5],params[6],params[7],params[8],params[9],params[10],params[11],params[12],params[13],params[14],\
    params[15],params[16],params[17],params[18],params[19],params[20]

    return render_template('index_2.html', urls = urls, profile=profile,\
                               email=email,pwd=pwd,hash1=hash_,output=output,nonested=nonested,\
                               sentence=sentence,paragraph=paragraph,title=title,returnspin=returnspin,\
                               nooriginal=nooriginal,protected=protected,synonyms=synonyms,include=include,\
                               exclude=exclude,emailwp=emailwp,pwdwp=pwdwp,atonce=atonce,\
                               spinner=spinner, keyword=keyword, split=split)

@app.route('/go', methods=['POST'])
def postWP(numrows=10):
    """ flask view for the search page"""
    if request.method == "POST":
        errors = {}
        profile = request.form['profile']
        email = request.form['email']
        pwd = request.form['pwd']
        hash_ = request.form['hash1']
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
        
        exclude = request.form['exclude']
        
        emailwp = request.form['emailwp']
        pwdwp = request.form['pwdwp']
        atonce = request.form['atonce']

        urls = request.form['urls']
        spinner = request.form['spinner']
        keyword = request.form['keyword']
        split = request.form['split']

        conn = sqlite3.connect('profile.db')
        c = conn.cursor()
        print profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, include, exclude,\
                            emailwp, pwdwp, atonce, urls, spinner, keyword,split
        c.execute("SELECT * from data where profile = '" + str(profile) + "'")
        exists = c.fetchone()
        if exists == None:
            createProfile(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                                returnspin, nooriginal, protected, synonyms, include, exclude,\
                                emailwp, pwdwp, atonce, urls, spinner,keyword,split, conn, c)
        else:
            updateVariables(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                                returnspin, nooriginal, protected, synonyms, include, exclude,\
                                emailwp, pwdwp, atonce, urls, spinner,keyword,split, conn, c)
        urls = [u.strip() for u in urls.split(',')]
        includes = [f.strip() for f in include.split(',')]
        excludes = [f.strip() for f in exclude.split(',')]
        searchString = '%27'+'+'.join(keyword.split())+'%27'
        url_bing = 'https://api.datamarket.azure.com/Bing/Search/Image?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % (searchString, top, offset)
        t1 = Thread(target = work, args=(profile, email, pwd, hash_, output, nonested, sentence, paragraph, title,\
                            returnspin, nooriginal, protected, synonyms, includes, excludes,\
                            emailwp, pwdwp, atonce, urls, spinner,url_bing,keyword,split, ))
        t1.start()       
        if len(urls)==1:
            urls = urls[0]
        else:
            urls = ', '.join(urls)
        return render_template('index_2.html', urls = urls, message = "Please Wait...", profile=profile,\
                               email=email,pwd=pwd,hash1=hash,output=output,nonested=nonested,\
                               sentence=sentence,paragraph=paragraph,title=title,returnspin=returnspin,\
                               nooriginal=nooriginal,protected=protected,synonyms=synonyms,include=include,\
                               exclude=exclude,emailwp=emailwp,pwdwp=pwdwp,atonce=atonce,\
                               spinner=spinner, keyword = keyword, split=split)

## view for load all profiles
@app.route('/loadProfiles', methods=['GET'])
def loadProfiles():
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()
    c.execute("select profile, urls, defaultProfile from data")
    data = c.fetchall()
    return render_template('profile.html', profiles = data)

## view for making a profile default   
@app.route('/makedefault/<profile>', methods=['GET', 'POST'])
def makeDefault(profile):
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile.db')
    c = conn.cursor()
    c.execute("UPDATE data SET defaultProfile=0")
    conn.commit()
    c.execute("UPDATE data SET defaultProfile = 1 where profile = '" + str(profile) + "'")
    conn.commit()
    c.execute("select profile, urls, defaultProfile from data")
    data = c.fetchall()
    return render_template('profile.html', profiles = data)

if __name__ == '__main__':
        app.run(debug=True)
