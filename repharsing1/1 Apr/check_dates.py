import urllib2, json, shutil, requests, logging, time, random, feedparser
from datetime import datetime

keyword='books'

keyBing = 'oe+UNVTEf8jvNUB+RasqpDY8RkC5cVeAIP0s9I2AvQ8='        # get Bing key from: https://datamarket.azure.com/account/keys
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
searchString = '%27'+'+'.join(keyword.split())+'%27'
top = 50
offset = 0
url_bing = 'https://api.datamarket.azure.com/Bing/Search/Image?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % (searchString, top, offset)

time1 = datetime.now()
bing_image_list = []
h = str(time1.strftime('%H'))
m = str(time1.strftime('%M'))
s = str(time1.strftime('%S'))
mo = str(time1.strftime('%m'))
yr = str(time1.strftime('%Y'))


request = urllib2.Request(url_bing)
request.add_header('Authorization', credentialBing)
requestOpener = urllib2.build_opener()
response = requestOpener.open(request)
results = json.load(response)
l = len(results['d']['results'])
print l
while True:
    ran_num = random.randint(0,l-1)
    if ran_num not in bing_image_list:
        bing_image_list.append(ran_num)
        break
image = results['d']['results'][ran_num]['Thumbnail']['MediaUrl']
print image
response = requests.get(image, stream=True)
with open('image'+h+m+s+'.jpg', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
del response
filename = 'image'+h+m+s+'.jpg'
print filename
