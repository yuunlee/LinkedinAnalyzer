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
param = input('Type in the company you want to know about (GeoGrahic Distribution): ')
path = r'C:\Users\YunL\OneDrive - Umich\桌面\SI507\2021fall\final\yunlee\data'

def getPublicIdData():

    '''
    load data from json
    '''

    f = open(path + '\workIn' + param + '.json')
    data = json.load(f)
    f.close()

    id_list = []
    for i in range(len(data)):
        id_list.append(data[i]['public_id'])

    return id_list

public_id_list = getPublicIdData()


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


def loadProfile():
    
    ProfileLst = [param + 'Profile']
    for i in ProfileLst:
        myfile = path + "\\" + i + ".json"
        print(myfile)
        if os.path.exists(myfile):
            if os.path.isfile(myfile):
                print(f'{i} cached!')
                # load data from json
                f = open(path + '\\' + param + 'Profile.json')
                jsonStr = json.load(f)
                f.close()
        else:
            print("file not yet exist")
            jsonStr = getProfileInfo(public_id_list)
            with open(myfile, 'w') as f:
                json.dump(jsonStr, f)
    return jsonStr

jsonStr = loadProfile()

def getGeoLocationLst():

    geoLst = []
    for i in range(len(jsonStr)):
        try:
            geoLst.append(jsonStr[i]['geoLocationName'])
        except:
            pass
    return geoLst


def getGeoCountryLst(jsonStr):
    geoCountryLst = []
    for i in range(len(jsonStr)):
        try:
            geoCountryLst.append(jsonStr[i]['geoCountryName'])
        except:
            pass
    return geoCountryLst

geoCountryLst = getGeoCountryLst(jsonStr)


def getEntireData(jsonStr):
    degreeLst = []
    schoolLst = []
    gradeLst = []
    fieldOfStudyLst = []
    companyNameLst = []
    titleLst = []
    timePeriodLst = []
    for i in range(len(jsonStr)):
        try:
            degreeLst.append(jsonStr[i]['education'][0]['degreeName'])
        except:
            degreeLst.append('')
        try:
            schoolLst.append(jsonStr[i]['education'][0]['schoolName'])
        except:
            schoolLst.append('')
        try:
            gradeLst.append(jsonStr[i]['education'][0]['grade'])
        except:
            gradeLst.append('')
        try:
            fieldOfStudyLst.append(jsonStr[i]['education'][0]['fieldOfStudy'])
        except:
            fieldOfStudyLst.append('')
        try:
            companyNameLst.append(jsonStr[i]['experience'][0]['companyName'])
        except:
            companyNameLst.append('')
        try:
            titleLst.append(jsonStr[i]['experience'][0]['title'])
        except:
            titleLst.append('')
        try:
            timePeriodLst.append(jsonStr[i]['experience'][0]['timePeriod'])
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
    df_ = df[df['Company'] == param].reset_index(drop=True)
    return df_


def getGeoFrequency(geoLst):
    
    # get location frequency
    d = {ele:geoLst.count(ele) for ele in set(geoLst)}
    
    # sort
    return (dict(sorted(d.items(), key=lambda item: item[1], reverse=True)))



df_geoCountry = pd.DataFrame(geoCountryLst)
df_geoCountry = pd.DataFrame(df_geoCountry.rename(columns={0: "country"}))
df_geoCountry = pd.DataFrame(df_geoCountry.rename(columns={'country':'Number of people working at the company'}))
df_country = df_geoCountry['Number of people working at the company'].value_counts().reset_index()
df_country = pd.DataFrame(df_country.rename(columns={'index': "country"}))

mapping = {'Hong Kong SAR':'HKG',
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
df_country['iso_alpha'] = df_country['country'].map(mapping)

# plot
fig = px.scatter_geo(df_country, locations="iso_alpha", color="country", text="country",
                     title = "Geographic Distribution of Employees Working @" + param + "<br><sup>Hover on each country on the map to take a closer look on the number of employees in each country. (According to the data API returns)</sup>" + "<br><sub>Click on the country labels on the right side to exclude selected countries</sub>",
                     size = "Number of people working at the company", # size of markers
                     projection="natural earth")
# fig.update_traces(marker=dict(size=25))
fig.show()