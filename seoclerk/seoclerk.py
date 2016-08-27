from BeautifulSoup import BeautifulSoup
import requests, sys
import pandas as pd
import time, random

columns = ['URL', 'Skill_1', 'Skill_2', 'Skill_3', 'Skill_4', 'Skill_5', 'Skill_6', 'Skill_7', 'Skill_8', 'Skill_9', 'Skill_10', 'Skill_11', 'Skill_12', 'Skill_13', 'Skill_14', 'Skill_15', 'Skill_16', 'Skill_17', 'Skill_18', 'Skill_19', 'Skill_20', 'Skill_21', 'Skill_22', 'Skill_23', 'Skill_24', 'Skill_25', 'Last_Logged_in', 'Wants_1', 'Wants_2', 'Wants_3', 'Wants_4', 'Wants_5', 'Wants_6', 'Wants_7', 'Wants_8', 'Wants_9', 'Wants_10', 'Wants_11', 'Wants_12', 'Wants_13', 'Wants_14', 'Wants_15', 'Wants_16', 'Wants_17', 'Wants_18', 'Wants_19', 'Wants_20', 'Wants_21', 'Wants_22', 'Wants_23', 'Wants_24', 'Wants_25', 'Wants_26', 'Wants_27', 'Wants_28', 'Wants_29', 'Wants_30', 'Wants_31', 'Wants_32', 'Wants_33', 'Wants_34', 'Wants_35', 'Wants_36', 'Wants_37', 'Wants_38', 'Wants_39', 'Wants_40','Wants_41', 'Wants_42', 'Wants_43', 'Wants_44', 'Wants_45', 'Wants_46', 'Wants_47', 'Wants_48', 'Wants_49', 'Wants_50']
NUM_PROFILES = 40
minDelay = 1
maxDelay = 2

df = pd.DataFrame(columns=columns)

def getUserData(profileUrl):
    rr = requests.get(profileUrl)
    soup1 = BeautifulSoup(rr.content)
    data = []
    skills = soup1.findAll(attrs = {'class':'tm-tag tm-tag-inverse tm-tag-small'})
    userSkills = []
    skillCount = 0
    for skill in skills:
        userSkills.append(str(skill.find('span').getText()))
        skillCount+=1

    for i in range(skillCount,25):
            userSkills.append('')
    
    ps = soup1.findAll('p')
    logged_in = ''
    for p in ps:
        try:
                if 'logged' in p.getText():
                        logged_in = p.getText().replace('last logged in','').replace('\t','').replace('\n',' ')
        except:
                pass


    wtb = soup1.find(attrs = {'id':'wtb'})
    wants = []
    wantsCount = 0
    lis = wtb.findAll('li')
    for li in lis:
        try:
                if li.getText() in [1, '1']:
                        wants = wants[:-1]
                        wantsCount = wantsCount-1
                        break
                wants.append(li.getText())
                wantsCount+=1
        except:
                pass
    for i in range(wantsCount, 50):
            wants.append('')
            
    data.extend(userSkills)
    data.extend([logged_in])
    data.extend(wants)
    return data
    
start_url = 'https://www.seoclerk.com/freelancers?page={page}'
numProfiles = 0
for i in range(1, 11707):
        time.sleep(random.randint(minDelay, maxDelay))
        
        url = start_url.replace('{page}', str(i))
        print 'Visiting url == ', url
        resp = requests.get(url)
        soup= BeautifulSoup(resp.content)
        table = soup.find('table')
        trs = table.findAll('tr')

        for tr in trs:
                tds = tr.findAll('td')
                try:
                        profileUrl = tds[0].find('a')['href']
                        print 'Visiting user profile url == ', profileUrl
                        userData = getUserData(profileUrl)
                        df.loc[numProfiles] = [profileUrl] + userData
                        #print 'Successfully scraped profile data for url == ' , profileUrl
                        #print [profileUrl] + userData
                        #print len([profileUrl] + userData)
                        numProfiles+=1
                        if numProfiles%10==0:
                                print 'Number of Profiles scraped == ', numProfiles
                        if (numProfiles == NUM_PROFILES) and NUM_PROFILES!=0:
                                df = df.drop_duplicates()
                                df.to_csv('seoclerk40.csv', index = False, encoding='utf-8')
                                print 'Successfully output to csv'
                                sys.exit(1)
                except Exception,e:
                        pass

print 'Successfully output to csv'
df = df.drop_duplicates()
df.to_csv('seoclerk10.csv', index = False)


