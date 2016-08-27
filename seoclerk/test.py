import requests
from BeautifulSoup import BeautifulSoup
from text_unidecode import unidecode

profileUrl = 'https://www.seoclerk.com/user/Ahove'
rr = requests.get(profileUrl)
soup1 = BeautifulSoup(rr.content)
data = []
skills = soup1.findAll(attrs = {'class':'tm-tag tm-tag-inverse tm-tag-small'})
userSkills = []
skillCount = 0
for skill in skills:
    userSkills.append(str(skill.getText()))
    skillCount+=1

for i in range(skillCount, 50):
    userSkills.append('')

ps = soup1.findAll('p')
logged_in = ''
for p in ps:
    try:
            if 'logged' in p.getText():
                    logged_in = p.getText().replace('last logged in','')
    except:
            pass


wtb = soup1.find(attrs = {'id':'wtb'})
wants = []
wantsCount = 0
lis = wtb.findAll('li')
for li in lis:
    try:
        wants.append(li.getText())
        wantsCount+=1
    except:
        pass
for i in range(wantsCount, 50):
    wants.append('')
        
data.extend(userSkills)
data.extend([logged_in])
data.extend(wants)
