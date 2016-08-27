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

##AWS_Access_Key = 'PUT YOUR AWS ACCESS KEY'
##AWS_Secret_Access_Key = 'PUT YOUR AWS SECRET KEY'
##S3_BUCKET_NAME = 'S3 BUCKET NAME HERE'
##
### Connect to S3
##c = S3Connection(AWS_Access_Key, AWS_Secret_Access_Key)
##b = c.get_bucket(S3_BUCKET_NAME)
b= ''
# if debug is set as True, updates will be printed on sysout
debug = True

if not os.path.exists('reddit_jsons'):
    os.makedirs('reddit_jsons')

if not os.path.exists('reddit_issues'):
    os.makedirs('reddit_issues')

# read the id name file made after running get_research_id_name.py
# and add to a dictionary which will be used to the name of
# the research field the script is currently working on
# itertate through all the rows of the dataframe
df = pd.read_csv('subreddits.csv')
sub_reddits = df['sub_reddits']

logging.info('Read the put file containing sub-reddits')

# declare all the static variables
num_threads = 2  # number of parallel threads
valid_chars = "-_.() %s%s" % (string.ascii_letters,
                              string.digits)  # valid chars for file names

logging.info('Number of threads ' + str(num_threads))

minDelay = 3  # minimum delay between get requests to www.nist.gov
maxDelay = 7  # maximum delay between get requests to www.nist.gov

logging.info('Minimum delay between each request =  ' + str(minDelay))
logging.info('Maximum delay between each request =  ' + str(maxDelay))

# search_base_urls have the same pattern
# just need to change the research field and page on the first and
base_url = 'https://www.reddit.com/r/'

# call the getProxies function
#proxies = getProxies()
proxies = []

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

    for subreddit in subreddits:
        page = 1
        titles = []
        while True:
            url = base_url + str(subreddit).strip().replace('\t','')+ '?count=' + str(25*(page-1))
            print url
            page+=1
            if page%3==0:
                titles = []
            if debug:
                sys.stdout.write('Visting reddit url :: ' + url + '\n' + '\n')

            logging.info('Visting reddit url :: ' + url + '\n' + '\n')
            br = mechanize.Browser()
            
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                'Referer': 'http://www.reddit.com'}
            #Cookie Jar
            cj = cookielib.LWPCookieJar()
             
            #Browser Options
            br.set_cookiejar(cj)
            br.set_handle_equiv(True)
            br.set_handle_redirect(True)
            br.set_handle_referer(True)
            br.set_handle_robots(False)
            br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

            # wrap the request.
            request = urllib2.Request(url, None, header)
            br.open(request)
            html = br.response().read()
            soup = BeautifulSoup(html, 'lxml')

            siteTable = soup.find(attrs = {'id':'siteTable'})
            divs = siteTable.findAll('div')

            for div in divs:
                try:
                    timestamp = div['data-timestamp']
                    time_post = str(datetime.fromtimestamp(int(timestamp)/1000))
                    title = unidecode(div.find(attrs = {'class':'title'}).find('a').getText())
                    rank = div.find(attrs = {'class':'rank'}).getText()
                    link = div.find(attrs = {'class':'title'}).find('a')['href']
                    if '/r/' in link:
                        link = base_url + link[1:]
                    
                    if title in titles:
                        break

                    titles.append(title)
                    
                    # write the fellow summary to file
                    file_name = title.replace(' ', '_') + '.json'
                    file_name = ''.join(c for c in file_name if c in valid_chars)
                    
                    f = open('reddit_jsons//' + file_name, 'wb')
                    folder = 'reddit_jsons'
                    logging.info(
                        'Opened ' +
                        'reddit_jsons//' +
                        file_name +
                        '.json' +
                        ' for writing')
                    

                    data = {
                        'date': time_post,
                        'title': title,
                        'rank': rank,
                        'link': link,
                        'url': url
                        }

                    f.write(json.dumps(data))
                    f.close()
                    logging.info('File written ' + file_name + '.json' + '')
                    if os.name == 'nt':
                        uploadDataS3(folder + '//' + file_name, b)
                    else:
                        uploadDataS3(folder + '/' + file_name, b)

                    if debug:
                        sys.stdout.write(file_name + ' written' + '\n')
                        
                except Exception,e:
                    #print str(e)
                    pass
            
            wait_time = random.randint(minDelay, maxDelay)
            sys.stdout.write('Sleeping for :: ' + str(wait_time) + '\n')
            logging.info('Sleeping for :: ' + str(wait_time) + '\n')
            sys.stdout.write(
                '******************************************' + '\n')
            sys.stdout.write(
                '******************************************' + '\n')
            time.sleep(wait_time)

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
        for worker in dataThreads:
            worker.terminate()
            worker.join(10)
