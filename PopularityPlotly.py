import json
from linkedin_api import Linkedin
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import html
from dash import dcc

api = Linkedin('yunnlee@umich.edu', '1a-2b-3c-4d-')
param = input("Type in the Company you want to know of its Employees being followed: ")
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


def getAccountPopularity(id_list):

    '''
    Fetch network information for a given LinkedIn profile.
    Ex: how many followers and connections the account has
    '''
    network_info_list = []
    index = 0
    for i in id_list:
        index += 1
        print(index)
        individual = api.get_profile_network_info(i)
        network_info_list.append(individual)
    return network_info_list


def writeNetwork(network_info_list):
    with open('data\\' + param + 'Network.json', 'w') as f:
        json.dump(network_info_list, f)
        

def loadNetwork():
    
    networkLst = [param + 'Network']
    for i in networkLst:
        myfile = path + "\\" + i + ".json"
        print(myfile)
        if os.path.exists(myfile):
            if os.path.isfile(myfile):
                print(f'{i} cached!')
                # load data from json
                f = open(path + '\\' + param + 'Network.json')
                jsonStr = json.load(f)
                f.close()
    
        else:
            print("file not yet exist")
            jsonStr = getAccountPopularity(id_list)
            with open(myfile, 'w') as f:
                json.dump(jsonStr, f)
    return jsonStr


def getFolloersCount(network_info_list):
    
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
    
    df_popular = pd.DataFrame({'public Id': id_list, 'Followers Count':followerLst})
    return df_popular



if __name__ == "__main__":

    id_list = getPublicIdData()
    jsonStr = loadNetwork()
    df_popular = getFolloersCount(jsonStr)
    df_popular = df_popular[df_popular['Followers Count'] != 0]
    df_popular = df_popular.dropna()
    bin_label = ['1 to 1000', '1001 to 2000', '2001 to 3000', '3001 to 4000', '4001 to 5000', '5001 to 10000', '10001 to 20000', '20001 to 30000','30001 to 40000']
    df_popular['bins'] = pd.cut(x=df_popular['Followers Count'],
                                bins=[1, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000],
                                labels=bin_label)

    df = df_popular['bins'].value_counts().reset_index()

    # Plot 1
    fig1 = px.bar(df, x='index', y='bins', text='bins', color = 'bins')
    # Customize aspect
    fig1.update_traces(marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5, opacity=0.6)
    fig1.update_traces(texttemplate='%{text:2s}', textposition='outside')
    # Header
    fig1.update_layout(title={'text':'How many employees in ' + param + ' fall in each group of followers'},
                    uniformtext_minsize=18,uniformtext_mode='hide',
                    font=dict(size=18))
    # fig1.show()

    # Plot 2
    df_popular = df_popular.dropna()
    fig2 = px.scatter(df_popular, x="public Id", y="Followers Count", color="bins",
                    title="Follower Count Distribution @" + param)
    # fig2.show()

    # Dash
    app = dash.Dash()
    item1 = dcc.Graph(id='FollowerScatterplot',
                          figure = {'data':[go.Scatter(x = df_popular['public Id'], y = df_popular['Followers Count'], mode='markers',
                          marker = {
                              'size': 12, 'color': '#1DB954', 'symbol':'pentagon','line': {'width':2}
                          })],
                          'layout': go.Layout(title = "Follower Count Distribution @" + param, xaxis = {'title':'Linkedin User who works in' + param})}
                          )
    item2 = dcc.Graph(id='FollowerCountCategory',
                          figure = {'data':[go.Bar(x = df['index'], y = df['bins'], marker = {'color':'#1DB954'}
                          )],
                          'layout': go.Layout(title = "How many employees in " + param + " fall in each group of followers")}
                          )
    app.layout = html.Div([item1, item2])
    app.run_server()