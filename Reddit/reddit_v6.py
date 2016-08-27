# import all necessary modules
import mechanize
import json
import urllib2
import os
import sys
import string
import time
import random
import re
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing import Process, Queue
from text_unidecode import unidecode
import logging
import multiprocessing
import math
import os
import boto
from filechunkio import FileChunkIO
from boto.s3.connection import S3Connection
import cookielib
from datetime import datetime

logging.basicConfig(
    filename='reddit.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

AWS_Access_Key = ''
AWS_Secret_Access_Key = ''
S3_BUCKET_NAME = ''

# Connect to S3
##c = S3Connection(AWS_Access_Key, AWS_Secret_Access_Key)
##b = c.get_bucket(S3_BUCKET_NAME)
b=''
# if debug is set as True, updates will be printed on sysout
debug = True

if not os.path.exists('reddit_jsons'):
    os.makedirs('reddit_jsons')

if not os.path.exists('reddit_issues'):
    os.makedirs('reddit_issues')

# read the subreddits from an input csv file
df = pd.read_csv('subreddits.csv')
sub_reddits = df['sub_reddits']

logging.info(
    'Read the put file containing sub-reddits. Total subreddits : ' + str(df.shape[0]))

# declare all the static variables
num_threads = 2  # number of parallel threads
valid_chars = "-_.() %s%s" % (string.ascii_letters,
                              string.digits)  # valid chars for file names

logging.info('Number of threads ' + str(num_threads))

minDelay = 3  # minimum delay between get requests to www.nist.gov
maxDelay = 7  # maximum delay between get requests to www.nist.gov

logging.info('Minimum delay between each request =  ' + str(minDelay))
logging.info('Maximum delay between each request =  ' + str(maxDelay))

# reddit urls have the same pattern
base_url = 'https://www.reddit.com/r/'

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


def uploadDataS3(source_path, b):
    # Get file info
    source_size = os.stat(source_path).st_size

    # Create a multipart upload request
    mp = b.initiate_multipart_upload(os.path.basename(source_path))

    # Use a chunk size of 50 MiB (feel free to change this)
    chunk_size = 52428800
    chunk_count = int(math.ceil(source_size / float(chunk_size)))

    # Send the file parts, using FileChunkIO to create a file-like object
    # that points to a certain byte range within the original file. We
    # set bytes to never exceed the original file size.
    for i in range(chunk_count):
        offset = chunk_size * i
        bytes = min(chunk_size, source_size - offset)
        with FileChunkIO(source_path, 'r', offset=offset,
                         bytes=bytes) as fp:
            mp.upload_part_from_file(fp, part_num=i + 1)

    # Finish the upload
    mp.complete_upload()


def split(a, n):
    """Function to split data evenly among threads"""
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
            for i in xrange(n))


def redditData(i, subreddits, debug, minDelay, maxDelay, b):
    """Function to scrape data from reddit subreddits
    subreddits = list of subreddits
    debug = print updates on screen
    minDelay = minimum delay between each scrape
    maxDelay = maximum delay between each scrape
    b = connection to AWS bucket
    """

    # intantiate an instance of mechanize with headers

    br = mechanize.Browser()

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
        'Referer': 'http://www.reddit.com'}
    # Cookie Jar
    cj = cookielib.LWPCookieJar()

    # Browser Options
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # iterate through the subreddits. Stop the program when the user
    # terminates of no more data
    for subreddit in subreddits:
        page = 1
        titles = []
        while True:
            url = base_url + str(subreddit).strip().replace('\t',
                                                            '') + '?count=' + str(25 * (page - 1))
            page += 1
            if page % 3 == 0:
                titles = []
            if debug:
                sys.stdout.write('Visting reddit url :: ' + url + '\n' + '\n')

            logging.info('Visting reddit url :: ' + url + '\n' + '\n')

            # wrap the request.
            request = urllib2.Request(url, None, header)
            br.open(request)
            html = br.response().read()
            soup = BeautifulSoup(html, 'lxml')

            siteTable = soup.find(attrs={'id': 'siteTable'})
            divs = siteTable.findAll('div')

            for div in divs:
                try:
                    timestamp = div['data-timestamp']
                    date_time =  str(parser.parse(div.find('time')['datetime']).replace(second=0).isoformat()).replace(':00+00:00', '+00:00')
                    day = str(
                        datetime.fromtimestamp(
                            int(timestamp) / 1000).date())
                    time_post = str(
                        datetime.fromtimestamp(
                            int(timestamp) / 1000).isoformat())
                    title = unidecode(
                        div.find(
                            attrs={
                                'class': 'title'}).find('a').getText())
                    rank = div.find(attrs={'class': 'rank'}).getText()
                    link = div.find(attrs={'class': 'title'}).find('a')['href']
                    comment_link = div.find(
                        attrs={'class': 'flat-list buttons'}).find('a')['href']

                    logging.info(
                        'Visting reddit comment url :: ' +
                        comment_link +
                        '\n' +
                        '\n')

                    # wrap the request.
                    request_comment = urllib2.Request(
                        comment_link, None, header)
                    br.open(request_comment)
                    html_comment = br.response().read()
                    soup_comment = BeautifulSoup(html_comment, 'lxml')

                    comment_dict = {}
                    words = title

                    comments = soup_comment.findAll(attrs={'class': 'comment'})

                    # get comment 1 and 3 children
                    comment_dict['commentary_1'] = {}
                    comment_dict['commentary_1']['child_comments'] = {}
                    comment_dict['commentary_2'] = {}
                    comment_dict['commentary_2']['child_comments'] = {}
                    comment_dict['commentary_3'] = {}
                    comment_dict['commentary_3']['child_comments'] = {}
                    try:
                        comment_dict['commentary_1']['words'] = unidecode(comments[0].find(
                            attrs={'class': 'usertext warn-on-unload'}).getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(comments[0].find(
                            attrs={'class': 'usertext warn-on-unload'}).getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_1']['words'] = ''
                    try:
                        comment_dict['commentary_1']['points'] = unidecode(
                            comments[0].find(attrs={'class': 'score likes'}).getText())
                    except:
                        comment_dict['commentary_1']['points'] = ''
                    try:
                        comment_dict['commentary_1']['time'] = unidecode(
                            comments[0].find(attrs={'class': 'tagline'}).find('time')['title'])
                    except:
                        comment_dict['commentary_1']['time'] = ''
                    try:
                        comment_dict['commentary_1']['user'] = unidecode(comments[0].find(
                            attrs={'class': 'tagline'}).findAll('a')[1].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_1']['user'] = ''

                    try:
                        children = comments[0].findAll(
                            attrs={'class': 'usertext warn-on-unload'})
                    except:
                        pass
                    try:
                        comment_dict['commentary_1']['child_comments'][
                            'comment_1'] = unidecode(children[1].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[1].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_1'][
                            'child_comments']['comment_1'] = ''

                    try:
                        comment_dict['commentary_1']['child_comments'][
                            'comment_2'] = unidecode(children[2].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[2].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_1'][
                            'child_comments']['comment_2'] = ''

                    try:
                        comment_dict['commentary_1']['child_comments'][
                            'comment_3'] = unidecode(children[3].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[3].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_1'][
                            'child_comments']['comment_3'] = ''

                    # get comment 2 and 3 children
                    try:
                        comment_dict['commentary_2']['words'] = unidecode(
                            comments[1].find(attrs={'class': 'usertext warn-on-unload'}).getText())
                        words = words + ' ' + unidecode(
                            comments[1].find(attrs={'class': 'usertext warn-on-unload'}).getText())
                    except:
                        comment_dict['commentary_2']['words'] = ''
                    try:
                        comment_dict['commentary_2']['points'] = unidecode(
                            comments[1].find(attrs={'class': 'score likes'}).getText())
                    except:
                        comment_dict['commentary_2']['points'] = ''
                    try:
                        comment_dict['commentary_2']['time'] = unidecode(
                            comments[1].find(attrs={'class': 'tagline'}).find('time')['title'])
                    except:
                        comment_dict['commentary_2']['time'] = ''
                    try:
                        comment_dict['commentary_2']['user'] = unidecode(comments[1].find(
                            attrs={'class': 'tagline'}).findAll('a')[1].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_2']['user'] = ''

                    try:
                        children = comments[0].findAll(
                            attrs={'class': 'usertext warn-on-unload'})
                    except:
                        children = []
                    try:
                        comment_dict['commentary_2']['child_comments'][
                            'comment_1'] = unidecode(children[1].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[1].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_2'][
                            'child_comments']['comment_1'] = ''

                    try:
                        comment_dict['commentary_2']['child_comments'][
                            'comment_2'] = unidecode(children[2].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[2].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_2'][
                            'child_comments']['comment_2'] = ''

                    try:
                        comment_dict['commentary_2']['child_comments'][
                            'comment_3'] = unidecode(children[3].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[3].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_2'][
                            'child_comments']['comment_3'] = ''

                    # get comment 3 and 3 children
                    try:
                        comment_dict['commentary_3']['words'] = unidecode(comments[2].find(
                            attrs={'class': 'usertext warn-on-unload'}).getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(comments[2].find(
                            attrs={'class': 'usertext warn-on-unload'}).getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_3']['words'] = ''
                    try:
                        comment_dict['commentary_3']['points'] = unidecode(
                            comments[2].find(attrs={'class': 'score likes'}).getText())
                    except:
                        comment_dict['commentary_3']['points'] = ''
                    try:
                        comment_dict['commentary_3']['time'] = unidecode(
                            comments[2].find(attrs={'class': 'tagline'}).find('time')['title'])
                    except:
                        comment_dict['commentary_3']['time'] = ''
                    try:
                        comment_dict['commentary_3']['user'] = unidecode(comments[2].find(
                            attrs={'class': 'tagline'}).findAll('a')[1].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_3']['user'] = ''

                    try:
                        children = comments[2].findAll(
                            attrs={'class': 'usertext warn-on-unload'})
                    except:
                        children = []
                    try:
                        comment_dict['commentary_3']['child_comments'][
                            'comment_1'] = unidecode(children[1].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[1].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_3'][
                            'child_comments']['comment_1'] = ''

                    try:
                        comment_dict['commentary_3']['child_comments'][
                            'comment_2'] = unidecode(children[2].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[2].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_3'][
                            'child_comments']['comment_2'] = ''

                    try:
                        comment_dict['commentary_3']['child_comments'][
                            'comment_3'] = unidecode(children[3].getText().replace('\n', ' '))
                        words = words + ' ' + unidecode(children[3].getText().replace('\n', ' '))
                    except:
                        comment_dict['commentary_3'][
                            'child_comments']['comment_3'] = ''
                    abstract = trimArticle(words, 50)

                    if '/r/' in link:
                        link = base_url + link[1:]

                    logging.info(
                        'Successfully got 3 comments from reddit comment url :: ' +
                        comment_link +
                        '\n' +
                        '\n')

                    if title in titles:
                        logging.info(
                            'Scraped all posts from sub reddit :: ' + url + '\n' + '\n')
                        break

                    titles.append(title)

                    # write the fellow summary to file
                    file_name = title.replace(' ', '_') + '.json'
                    file_name = ''.join(
                        c for c in file_name if c in valid_chars)
                    
                    if os.name == 'nt':
                        f = open('reddit_jsons//' + file_name, 'wb')
                    else:
                        f = open('reddit_jsons/' + file_name, 'wb')
                    folder = 'reddit_jsons'
                    logging.info(
                        'Opened ' +
                        'reddit_jsons//' +
                        file_name +
                        '.json' +
                        ' for writing')

                    data = {
                        'abstract':abstract,
                        'external_id': 'reddit_' + title.replace(' ', '-'),
                        'date': time_post,
                        'words': words,
                        'meta': {
                                'reddit' : {
                                    'comments' : str(comment_dict),
                                    'link' : link, 
                                    'rank' : rank
                                    }
                            },
                        'url': comment_link
                    }
                    

                    f.write(json.dumps(data))
                    f.close()
                    logging.info('File written ' + file_name + '.json' + '')
##                    if os.name == 'nt':
##                        uploadDataS3(folder + '//' + file_name, b)
##                    else:
##                        uploadDataS3(folder + '/' + file_name, b)
                    

                    if debug:
                        sys.stdout.write(file_name + ' written' + '\n')

                except Exception as e:
                    # print str(e)
                    pass

            wait_time = random.randint(minDelay, maxDelay)
            sys.stdout.write('Sleeping for :: ' + str(wait_time) + '\n')
            logging.info('Sleeping for :: ' + str(wait_time) + '\n')
            sys.stdout.write(
                '******************************************' + '\n')
            sys.stdout.write(
                '******************************************' + '\n')
            time.sleep(wait_time)

# split the subreddits evenly among the threads

distributed_ids = list(split(list(sub_reddits), num_threads))

if __name__ == "__main__":
    # declare an empty queue which will hold the publication ids

    dataThreads = []
    for i in range(num_threads):
        data = distributed_ids[i]
        dataThreads.append(
            Process(
                target=redditData,
                args=(
                    i + 1,
                    data,
                    debug,
                    minDelay,
                    maxDelay,
                    b,

                )))
    j = 1
    for thread in dataThreads:
        sys.stdout.write('starting reddit scraper ##' + str(j) + '\n')
        logging.info('starting reddit scraper ##' + str(j) + '\n')
        j += 1
        thread.start()

    try:
        for worker in dataThreads:
            worker.join(10)
    except KeyboardInterrupt:
        print 'Received ctrl-c'
        logging.info('Received ctrl-c' + '\n' + '\n')
        for worker in dataThreads:
            worker.terminate()
            worker.join(10)
