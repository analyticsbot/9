from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulSoup
from textblob import TextBlob
import pandas as pd
import dateutil.parser as dparser
from text_unidecode import unidecode

df = pd.DataFrame(columns = ['Email_Body', 'polarity', 'subjectivity', 'num_words_doc', 'email_title'])
## this is the input html file.  Need to change that
f = open('Nike1991.HTML', 'r')
data = f.read()
soup = BeautifulSoup(data)
emails = soup.findAll(attrs = {'class':'c5'})

counter = 0
for email in emails:
    try:
        text = email.getText().lower().strip()
        if 'length' in text:
            num_words = text.replace('length:','').strip()
        soup1 = BeautifulSoup(str(email))
        if (soup1.findAll(attrs = {'class':'c7'})):# and soup1.findAll(attrs = {'class':'c8'})):
            title = email.getText().strip()
            
        if ((len(soup1.findAll(attrs = {'class':'c4'}))>0) and (len(soup1.findAll(attrs = {'class':'c2'})) >=0) and\
            (len(soup1.findAll(attrs = {'class':'c9'}))==0) or (len(soup1.findAll(attrs = {'class':'c12'}))>=0)):
            body = str(unidecode(email.getText())).strip().replace('&nbsp;',' ').replace('\n','')
##            index = emails.index(email)
            siblings = email.fetchNextSiblings()[:4]
            cc = 0
            for s in siblings:
                if s.name=='table':
                    body +=str(unidecode(s.getText())).strip().replace('&nbsp;',' ').replace('\n','')
##                elif (s.name == 'div') and ('$' in s.getText()) :
##                    cc+=1
##                    emails.pop(index+cc)
                    
            blob = TextBlob(body)
            sentiment_polarity = blob.sentiment.polarity
            sentiment_subjectivity = blob.sentiment.subjectivity
            num_words_doc = num_words
            email_title = title
            df.loc[counter] = [body, sentiment_polarity, sentiment_subjectivity, num_words_doc, email_title]
            counter +=1
    except:
        pass
    
print counter
##date_column = []
##dates = soup.findAll(attrs = {'class':'c1'})
##c =0
##for date in dates:
##    try:
##        date_time = ''
##        date_time += date.find(attrs = {'class':'c4'}).getText() + ' '
##        date_time += date.find(attrs = {'class':'c2'}).getText()
##        date_column.append(date_time)
##        c+=1
##    except:
##        pass   
##    
##print len(date_column)
##document_idx = []
##docs = soup.findAll(attrs = {'class':'c0'})
##for d in docs:
##    text = d.getText().strip()
##    if 'DOCUMENT' in text:
##        document_idx.append(text)
##print len(document_idx)
#### this is the outputfile name ==  parsed_data1.csv. You can change that
#### to whatever you want.
##temp = pd.DataFrame(columns = ['date'])
##temp['date'] = date_column
##df = pd.concat([df, temp], axis =1)
##temp = pd.DataFrame(columns = ['docIndex'])
##temp['docIndex'] = (document_idx)
##df = pd.concat([df, temp], axis =1)
df.to_csv('parsed_data6.csv', index = False, encoding = 'utf-8')
