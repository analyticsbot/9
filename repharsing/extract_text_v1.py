import xml.etree.ElementTree as ET
import requests, feedparser

from newspaper import Article

url ='https://flipboard.com/topic/cloudcomputing.rss'

response = requests.get(url)
d = feedparser.parse(response.text.encode('ascii', 'ignore'))

urls = []

for i in range(len(d.entries)):
    urls.append( d.entries[i].link)
	
articles = {}

for url in urls:
    article = Article(url)
    article.download()
    article.parse()
    text = article.text
    articles[url] = text
