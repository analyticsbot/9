import requests, json

url = 'http://wordai.com/users/turing-api.php'

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
