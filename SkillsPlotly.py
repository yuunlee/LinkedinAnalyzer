import json
from linkedin_api import Linkedin
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import html
from dash import dcc
import re

api = Linkedin('yunnlee@umich.edu', '1a-2b-3c-4d-')
param = input("Type in the Company you want to know: ")
path = r'C:\Users\YunL\OneDrive - Umich\桌面\SI507\2021fall\final\yunlee\data'


def loadPublicIdList():

    # load data from json
    f = open(path + '\workIn' + param + '.json')
    data = json.load(f)
    f.close()

    id_list = []
    for i in range(len(data)):
        id_list.append(data[i]['public_id'])
    return id_list


def getInitialSkills(public_id_list):

    '''
    get_profile_skills API returns the skills listed on a given LinkedIn profile.
    The returned result are in dictionary format, so we are only getting the value, which is the skills of the dictionary.
    Since there might be skills presented in different languages,
    here, we will use regex to considered only those that are in English for simplicity.
    '''

    initialList = []
    index = 0
    for i in public_id_list:
        index += 1
        print(index)
        skillSet = api.get_profile_skills(i)
        initialList.append(skillSet)
    return initialList


def loadSkills():

    preParseSkillList = [param + 'Skills']
    for i in preParseSkillList:
        myfile = path + "\\" + i + ".json"
        print(myfile)
        if os.path.exists(myfile):
            if os.path.isfile(myfile):
                print(f'{i} cached!')
                # load data from json
                f = open(path + '\\' + param + 'Skills.json')
                jsonStr = json.load(f)
                if type(jsonStr) == str:
                    aList = json.loads(jsonStr)
                elif type(jsonStr) == list:
                    aList = json.dumps(jsonStr)
                f.close()

        else:
            print("file not yet exist")
            aList = getInitialSkills(public_id_list)
            with open(myfile, 'w') as f:
                json.dump(aList, f)
    return aList
            
            
def GetSkills(initialList):

    '''
    get_profile_skills API returns the skills listed on a given LinkedIn profile.
    The returned result are in dictionary format, so we are only getting the value, which is the skills of the dictionary.
    Since there might be skills presented in different languages,
    here, we will use regex to considered only those that are in English for simplicity.
    '''
    if type(initialList) == list:
        test_list = []
        for personSkill in initialList:
            for itemSkill in personSkill:
                test_list.append(itemSkill.get('name'))
                
        skillList = []
        for item in test_list:
            skillList.append(re.sub("[^a-zA-Z0-9 ]+", "",item))
        skillList = list(filter(None,skillList))
    elif type(initialList) == str:
        initialList = initialList.replace('"','').replace('[','').replace(']','')
        skillList = list(initialList.split(", "))

    return skillList


def CountSkillFrequency(skillList):

    '''
    This function counts the frequency of each skills
    The skillCountList returns the frequency of each skill in descending order
    '''

    skillCountList = []
    freq = {}
    for items in skillList:
        # print(items)
        freq[items] = skillList.count(items)
     
    for key, value in freq.items():
        skillCountList.append([key, value])
    
    return skillCountList


# sort and choose the top skills
def Sort(skillCountList):

    '''reverse = None (Sorts in Ascending order)
    key is set to sort using second element of
    sublist lambda has been used
    reverse=True so that the list is returned in descending order
    '''

    return(sorted(skillCountList, key = lambda x: x[1], reverse=True))


mapping = {'C':'Programming',
           'Python':'Programming',
           'Python Programming Language':'Programming',
           'JavaScript':'Programming',
           'Java':'Programming',
           'Programming':'Programming',
           'Matlab':'Programming',
           'Git':'Programming',
           'Linux':'Programming',
           'Software Development':'Programming',
           'HTML':'Programming',
           'CSS':'Programming',
           'Cascading Style Sheets CSS':'Programming',
           'R':'Analytics',
           'SQL':'Analytics',
           'Statistics':'Analytics',
           'MySQL':'Analytics',
           'Machine Learning': 'Analytics',
           'Data Analysis':'Analytics',
           'Microsoft PowerPoint':'Admin',
           'PowerPoint':'Admin',
           'Microsoft Word':'Admin',
           'Microsoft Excel':'Admin',
           'Microsoft Office':'Admin',
           'Project Management': 'Product',
           'Product Management':'Product',
           'User Experience UX': 'Product',
           'Agile Methodologies':'Product',
           'Customer Service':'Product',
           'Marketing':'Marketing',
           'Marketing Strategy': 'Marketing',
           'Event Planning':'Marketing',
           'Social Media Marketing': 'Marketing',
           'Sales':'Marketing',
           'Retail':'Marketing',
           'Advertising':'Marketing',
           'Adobe Photoshop':'Design',
           'Graphic Design':'Design',
           'User Interface Design':'Design',
           'Adobe Creative Suite':'Design',
           'Interaction Design':'Design',
           'Adobe Illustrator':'Design',
           'Public Speaking':'Soft Skills',
           'Teamwork':'Soft Skills',
           'Management':'Soft Skills',
           'Strategy':'Soft Skills',
           'Strategic Planning':'Soft Skills',
           'Business Strategy':'Soft Skills',
           'Leadership': 'Soft Skills',
           'Team Leadership':'Soft Skills',
           'Crossfunctional Team Leadership':'Soft Skills',
           'Research':'Research',
           'Clinical Research':'Research',
           'Social Media':'Digital',
           'Digital Marketing':'Digital',
           'Pharmaceutical Industry':'Domain Knowledge',
           'Healthcare':'Domain Knowledge',
           'Clinical Trials':'Domain Knowledge',
           'Life Sciences':'Domain Knowledge',
           'Lifesciences':'Domain Knowledge',
           'Oncology':'Domain Knowledge',
           'Drug Development':'Domain Knowledge',
           'Clinical Development':'Domain Knowledge',
           'Molecular Biology':'Domain Knowledge',
           'Drug Discovery':'Domain Knowledge',
           'Cell Culture':'Domain Knowledge',
           'Biochemistry':'Domain Knowledge',
           'Biotechnology':'Domain Knowledge'}

if __name__ == "__main__":

    public_id_list = loadPublicIdList()
    aList = loadSkills()
    skillList = GetSkills(aList)
    skillCountList = CountSkillFrequency(skillList)
    Top30Skills = Sort(skillCountList)[:30]
    dfSkills = pd.DataFrame(Top30Skills, columns = ['Skill', 'Frequency'])
    dfSkills['Skill_Type'] = ''
    dfSkills['Skill_Type'] = dfSkills['Skill'].map(mapping)

    # plot
    fig = px.bar(dfSkills, x='Skill', y='Frequency', text='Frequency', color="Skill_Type")
    # Customize aspect
    fig.update_traces(marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5, opacity=0.6)
    fig.update_traces(texttemplate='%{text:2s}', textposition='outside')
    # Header
    fig.update_layout(title={'text':'Top 30 Skills ' + param + ' Employees have' + "<br><sub>This information came from the 'Skills' section on user Linkedin proile.</sub>" + "<br><sub>I classified the top 30 skills into certain categories based on my own knowledge.</sub>" + "<br><sub>You can click on the skill type labels on the right side to exclude certain skills</sub>", 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                    uniformtext_minsize=14,uniformtext_mode='hide',
                    font=dict(family="Courier New, monospace",
                                size=12))
    fig.show()


