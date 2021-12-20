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
import secrets

api = Linkedin(secrets.EMAIL, secrets.PWD)
param = input("Type in one of the three companies you want to know about: ")
path = r'C:\Users\YunL\OneDrive - Umich\桌面\SI507\2021fall\final\yunlee\data'

def getPublicIdData():

    '''
    load data from json
    '''

    f = open(path + '\workIn' + param + '.json')
    data = json.load(f)
    f.close()

    public_id_list = []
    for i in range(len(data)):
        public_id_list.append(data[i]['public_id'])

    return public_id_list


def getAccountPopularity(public_id_list):

    '''
    Fetch network information for a given LinkedIn profile.
    Ex: how many followers and connections the account has
    '''
    network_info_list = []
    index = 0
    for i in public_id_list:
        index += 1
        print(index)
        individual = api.get_profile_network_info(i)
        network_info_list.append(individual)
    return network_info_list


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


def getProfileInfo(public_id_list):

    '''
    The get_profile API will return the profile information of LinkedIn user.
    I passed in the public_id_list from previous step,
    so the profile_list will return the profile of my connections.
    (as long as their page is public)
    '''

    index = 0
    profile_list = []
    for i in public_id_list:
        index += 1
        print(index)
        profile = api.get_profile(i)
        profile_list.append(profile)
    return profile_list


def writeProfile(profile_list):
    with open('data\\' + param + 'Profile.json', 'w') as f:
        json.dump(profile_list, f)


def writeNetwork(network_info_list):
    with open('data\\' + param + 'Network.json', 'w') as f:
        json.dump(network_info_list, f)


def writeSkills(initialList):
    with open('data\\' + param + 'Skills.json', 'w') as f:
        json.dump(initialList, f)


def loadNetwork(public_id_list):

    '''
    check if the cache exist, if exist then load the data,
    if it does not exist, then call the API and save it into json
    '''
    
    networkLst = [param + 'Network']
    for i in networkLst:
        myfile = path + "\\" + i + ".json"
        print(myfile)
        if os.path.exists(myfile):
            if os.path.isfile(myfile):
                print(f'{i} cached!')
                f = open(path + '\\' + param + 'Network.json')
                jsonStrNetwork = json.load(f)
                f.close()
    
        else:
            print("file not yet exist")
            jsonStrNetwork = getAccountPopularity(public_id_list)
            with open(myfile, 'w') as f:
                json.dump(jsonStrNetwork, f)
    return jsonStrNetwork


def loadSkills(public_id_list):

    '''
    check if the cache exist, if exist then load the data,
    if it does not exist, then call the API and save it into json
    '''

    preParseSkillList = [param + 'Skills']
    for i in preParseSkillList:
        myfile = path + "\\" + i + ".json"
        print(myfile)
        if os.path.exists(myfile):
            if os.path.isfile(myfile):
                print(f'{i} cached!')
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


def loadProfile(public_id_list):
    
    '''
    check if the cache exist, if exist then load the data,
    if it does not exist, then call the API and save it into json
    '''

    ProfileLst = [param + 'Profile']
    for i in ProfileLst:
        myfile = path + "\\" + i + ".json"
        print(myfile)
        if os.path.exists(myfile):
            if os.path.isfile(myfile):
                print(f'{i} cached!')
                f = open(path + '\\' + param + 'Profile.json')
                jsonStrProfile = json.load(f)
                f.close()
        else:
            print("file not yet exist")
            jsonStrProfile = getProfileInfo(public_id_list)
            with open(myfile, 'w') as f:
                json.dump(jsonStrProfile, f)
    return jsonStrProfile


def getFolloersCount(network_info_list, public_id_list):
    
    '''
    get follower count from the API and append it into a list
    combine list of id and list of followers into dataframe
    
    '''
    followerLst = []
    for index in network_info_list:
        try:
            followerLst.append(index['followersCount'])
        except:
            followerLst.append(0)
    
    df_popular = pd.DataFrame({'public Id': public_id_list, 'Followers Count':followerLst})
    return df_popular


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
        freq[items] = skillList.count(items)
     
    for key, value in freq.items():
        skillCountList.append([key, value])
    
    return skillCountList


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


def getGeoLocationLst(jsonStrProfile):

    geoLst = []
    for i in range(len(jsonStrProfile)):
        try:
            geoLst.append(jsonStrProfile[i]['geoLocationName'])
        except:
            pass
    return geoLst


def getGeoCountryLst(jsonStrProfile):
    geoCountryLst = []
    for i in range(len(jsonStrProfile)):
        try:
            geoCountryLst.append(jsonStrProfile[i]['geoCountryName'])
        except:
            pass
    return geoCountryLst


def getEntireData(jsonStrProfile):
    degreeLst = []
    schoolLst = []
    gradeLst = []
    fieldOfStudyLst = []
    companyNameLst = []
    titleLst = []
    timePeriodLst = []
    for i in range(len(jsonStrProfile)):
        try:
            degreeLst.append(jsonStrProfile[i]['education'][0]['degreeName'])
        except:
            degreeLst.append('')
        try:
            schoolLst.append(jsonStrProfile[i]['education'][0]['schoolName'])
        except:
            schoolLst.append('')
        try:
            gradeLst.append(jsonStrProfile[i]['education'][0]['grade'])
        except:
            gradeLst.append('')
        try:
            fieldOfStudyLst.append(jsonStrProfile[i]['education'][0]['fieldOfStudy'])
        except:
            fieldOfStudyLst.append('')
        try:
            companyNameLst.append(jsonStrProfile[i]['experience'][0]['companyName'])
        except:
            companyNameLst.append('')
        try:
            titleLst.append(jsonStrProfile[i]['experience'][0]['title'])
        except:
            titleLst.append('')
        try:
            timePeriodLst.append(jsonStrProfile[i]['experience'][0]['timePeriod'])
        except:
            timePeriodLst.append('')
    
    
    df = pd.DataFrame({'Degree':degreeLst,
                       'School':schoolLst,
                       'GPA':gradeLst,
                       'Field of Study':fieldOfStudyLst,
                       'Company':companyNameLst,
                       'Title':titleLst,
                       'Time Period':timePeriodLst})
    
    # For simplicity, include only the user that are currently working at the company
    df_profile = df[df['Company'] == param].reset_index(drop=True)
    return df_profile


def getGeoFrequency(geoLst):
    
    # get location frequency
    d = {ele:geoLst.count(ele) for ele in set(geoLst)}
    
    # sort
    return (dict(sorted(d.items(), key=lambda item: item[1], reverse=True)))


mapping_country = {'Hong Kong SAR':'HKG',
                    'India':'IND',
                    'Taiwan':'TWN',
                    'Japan':'JPN',
                    'United States':'USA',
                    'Singapore':'SGP',
                    'China':'CHN',
                    'Romania':'ROU',
                    'Germany':'DEU',
                    'Netherlands':'NLD',
                    'Australia':'AUS',
                    'Spain':'ESP',
                    'Sweden':'SWE',
                    'United Kingdom':'GBR',
                    'France':'FRA',
                    'Denmark':'DNK',
                    'Indonesia':'IDN',
                    'South Korea':'KOR',
                    'Morocco':'MAR',
                    'Greece':'GRC',
                    'Philippines':'PHL',
                    'Brazil':'BRA',
                    'Canada':'CAN',
    }


if __name__ == '__main__':
    
    # Popularity
    public_id_list = getPublicIdData()
    jsonStrNetwork = loadNetwork(public_id_list)
    df_popular = getFolloersCount(jsonStrNetwork, public_id_list)
    df_popular = df_popular[df_popular['Followers Count'] != 0]
    df_popular = df_popular.dropna()
    bin_label = ['1 to 1000', '1001 to 2000', '2001 to 3000', '3001 to 4000', '4001 to 5000', '5001 to 10000', '10001 to 20000', '20001 to 30000','30001 to 40000']
    df_popular['bins'] = pd.cut(x=df_popular['Followers Count'],
                                bins=[1, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000],
                                labels=bin_label)

    df = df_popular['bins'].value_counts().reset_index()
    df_popular = df_popular.dropna()

    # Skills
    public_id_list = getPublicIdData()
    aList = loadSkills(public_id_list)
    skillList = GetSkills(aList)
    skillCountList = CountSkillFrequency(skillList)
    Top30Skills = Sort(skillCountList)[:30]
    dfSkills = pd.DataFrame(Top30Skills, columns = ['Skill', 'Frequency'])
    dfSkills['Skill_Type'] = ''
    dfSkills['Skill_Type'] = dfSkills['Skill'].map(mapping)

    # Profile
    public_id_list = getPublicIdData()
    jsonStrProfile = loadProfile(public_id_list)
    geoCountryLst = getGeoCountryLst(jsonStrProfile)
    df_geoCountry = pd.DataFrame(geoCountryLst)
    df_geoCountry = pd.DataFrame(df_geoCountry.rename(columns={0: "country"}))
    df_geoCountry = pd.DataFrame(df_geoCountry.rename(columns={'country':'Number of people working at the company'}))
    df_country = df_geoCountry['Number of people working at the company'].value_counts().reset_index()
    df_country = pd.DataFrame(df_country.rename(columns={'index': "country"}))
    df_country['iso_alpha'] = df_country['country'].map(mapping_country)
    df_profile = getEntireData(jsonStrProfile)




    # Dash
    app = dash.Dash()
    # Popularity
    fig1 = px.bar(df, x='index', y='bins', text='bins', color = 'bins')
    # Customize aspect
    fig1.update_traces(marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5, opacity=0.6)
    fig1.update_traces(texttemplate='%{text:2s}', textposition='outside')
    # Header
    fig1.update_layout(title={'text':'How many employees in ' + param + ' fall in each group of followers'+ "<br><sub>I categorized the followers' amount into 9 groups, to visualize how many followers should an employee working in one of my dream companies have</sub>"},
                    uniformtext_minsize=14,uniformtext_mode='hide',
                    font=dict(size=12))
    item1 = dcc.Graph(id = 'Popularity1',
                    figure = fig1
                    )

    df_popular = df_popular.dropna()
    fig2 = px.scatter(df_popular, x="public Id", y="Followers Count", color="bins",
                    title="Follower Count Distribution @" + param + "<br><sub>The x-axis is the individual working in the company, and the y-axis is the respective followers the individual has." + "<br><sub>As you can see from the scatter plot, most of the employees have more than 1k followers, only a few of them have more than 10k followers.</sub>" + "<br><sub>Hover over the dots to get more information</sub>")
    item2 = dcc.Graph(id = 'Popularity2',
                    figure = fig2
                    )

    # Skills
    fig3 = px.bar(dfSkills, x='Skill', y='Frequency', text='Frequency', color="Skill_Type")
    # Customize aspect
    fig3.update_traces(marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5, opacity=0.6)
    fig3.update_traces(texttemplate='%{text:2s}', textposition='outside')
    # Header
    fig3.update_layout(title={'text':'Top 30 Skills ' + param + ' Employees have' + "<br><sub>This information came from the 'Skills' section on the user's Linkedin profile.</sub>" + "<br><sub>I classified the top 30 skills into certain categories based on my own knowledge.</sub>" + "<br><sub>You can click on the skill type labels on the right side to exclude certain skills</sub>", 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                    uniformtext_minsize=14,uniformtext_mode='hide',
                    font=dict(size=12))
    item3 = dcc.Graph(id = 'SkillGraph',
                    figure = fig3
                    )
    # Profile
    fig4 = px.scatter_geo(df_country, locations="iso_alpha", color="country", text="country",
                            title = "Geographic Distribution of Employees Working @" + param + "<br><sup>Hover on each country on the map to take a closer look on the number of employees in each country. (According to the data API returns)</sup>" + "<br><sub>Click on the country labels on the right side to exclude selected countries</sub>",
                            size = "Number of people working at the company", # size of markers
                            projection="natural earth")
    item4 = dcc.Graph(id = 'geoLocation',
                    figure = fig4
                    )

    app.layout = html.Div([item1, item2, item3, item4])
    app.run_server()