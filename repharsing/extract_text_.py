import xml.etree.ElementTree as ET
import requests

from newspaper import Article

url ='https://flipboard.com/topic/cloudcomputing.rss'

response = requests.get(url)
e = ET.fromstring(response.text.encode('ascii', 'ignore'))
elements = e.getiterator()

urls = []

for element in elements:
    if element.tag == 'link':
        urls.append(element.text)

    elif element.tag == 'item':
        children = element.getchildren()
        for child in children:
            if child.tag == 'link':
                urls.append(child.text)

articles = {}

for url in urls:
    article = Article(url)
    article.download()
    article.parse()
    text = article.text
    articles[url] = text
