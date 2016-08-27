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

