import os
from flask import Flask, render_template, request
import time
import urllib.request
import csv
import matplotlib.pyplot as plt
import cv2
import numpy as np

app = Flask('MyHerokuApp')

# Read the mailgun secret key from environment variables
mailgun_secret_key_value = os.environ.get('MAILGUN_SECRET_KEY', None)

BASE_URL = "https://data.incovid19.org/"
CASE_TIME_SERIES = BASE_URL+"csv/latest/case_time_series.csv"
STATES = BASE_URL+"csv/latest/states.csv"
DISTRICTS	= BASE_URL+"csv/latest/districts.csv"
SOURCES_LIST	= BASE_URL+"csv/latest/sources_list.csv"
COWIN_VACCINE_DATA_STATEWISE	= BASE_URL+"csv/latest/cowin_vaccine_data_statewise.csv"
COWIN_VACCINE_DATA_DISTRICTWISE	= BASE_URL+"csv/latest/cowin_vaccine_data_districtwise.csv"
STATE_WISE_DAILY	= BASE_URL+"csv/latest/state_wise_daily.csv"
STATE_WISE	= BASE_URL+"csv/latest/state_wise.csv"
DISTRICT_WISE	= BASE_URL+"csv/latest/district_wise.csv"

def n_fact(n):
    pro = 1
    for i in range(n):
        pro = (i+1)*pro
    return pro

def getCases(state_code):
    with open('temp.csv','r') as csvfile:
        date = []
        cases = []
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        state = -1
        state = fields.index(state_code)
        
        for row in csvreader:
            if('Confirmed' in row):
                date.append(str(row[0]))
                cases.append(int(row[state]))
        
        return cases

def generateCSV(state_name,y,n):
    str_y = state_name
    y = y[-n:]
    for items in y:
        str_y = str_y + ","+str(items)
    with open("./static/chart0.csv",'a+') as charts:
        charts.write(str_y+"\n")

def generateCSVAll(state_name,y,n,index):
    str_y = state_name
    y = y[-n:]
    for items in y:
        str_y = str_y + ","+str(items)
    with open("./static/chart"+str(index)+".csv",'a+') as charts:
        charts.write(str_y+"\n")

def generateCSVHeader(n,y):
    x = list(range(len(y[-n:])))
    x.reverse()
    x = [i*-1 for i in x]
    str_x = ""
    for items in x:
        str_x=str_x +","+str(items)
    with open("./static/chart0.csv",'w') as charts:
        charts.write(str_x+"\n")

def generateCSVHeaderAll(n,y,index):
    x = list(range(len(y[-n:])))
    x.reverse()
    x = [i*-1 for i in x]
    str_x = ""
    for items in x:
        str_x=str_x +","+str(items)
    with open("./static/chart"+str(index)+".csv",'w') as charts:
        charts.write(str_x+"\n")

def nday_moving_avg(n,mylist):
    ret = []
    count = 0
    first_avg = 0
    list_len = len(mylist)
    for i in range(n):
        first_avg = first_avg + mylist[i]
    first_avg = first_avg/n
    for i in range(len(mylist)):
        if(count < n):
            count = count + 1
        else:
            #print(first_avg)
            ret.append(first_avg)
            first_avg = (first_avg*n - mylist[i-n]+mylist[i])/n
    ret.append(first_avg)
    return ret

def plotState2(state_codes,state_names,n,nma):
    cases = []
    n_day = []
    cases.append(getCases(state_codes[0]))
    cases.append(getCases(state_codes[1]))
    n_day.append(nday_moving_avg(nma,cases[0]))
    n_day.append(nday_moving_avg(nma,cases[1]))
    generateCSVHeader(n,cases[0])
    generateCSV(state_names[0],n_day[0],n)
    generateCSV(state_names[1],n_day[1],n)
    #ax.set_title(state_name)

def plotStateAll(state_codes,state_names,n,nma):
    cases = []
    n_day = []
    NO_OF_STATES = len(state_codes)
    for index in range(NO_OF_STATES):
        cases.append(getCases(state_codes[index]))

    for index in range(NO_OF_STATES):    
        n_day.append(nday_moving_avg(nma,cases[index]))
    

    for index in range(NO_OF_STATES):
        generateCSVHeaderAll(n,cases[index],index)
        generateCSVAll(state_names[index],n_day[index],n,index)

    #ax.set_title(state_name)

def main_covid(state_code_list,n,nma):
    r = urllib.request.urlretrieve(STATE_WISE_DAILY,'temp.csv')
    
    filename ="india-states.csv"
    mydict = []
    with open(filename, 'r') as data:
        reader = csv.reader(data)
        mydict = {rows[0]:rows[1] for rows in reader}
    all_states = 0
    state_names = []
    state_codes = state_code_list
    dimension = len(state_code_list)

    for codes in state_codes:
        state_names.append(mydict[codes])

    if(dimension < 3):
        plotState2(state_codes,state_names,n,nma)
    else:
        plotStateAll(state_codes,state_names,n,nma)


# This is needed for Heroku configuration, as in Heroku our
# app will probably not run on port 5000, as Heroku will automatically
# assign a port for our application
port = int(os.environ.get("PORT", 5000))

@app.route('/index')
def index():

    # We will just display our mailgun secret key, nothing more
    return render_template("index.html", value=main_covid(1,1))
 
@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    LAST_N_DAYS = int(request.form['n-day'])
    N_DAY_AVG = int(request.form['n-day-ma'])
    state1 = request.form['state1']
    state2 = request.form['state2']
    all_switch = "off"
    try:
        all_switch = request.form['mycheckbox']
    except:
        pass
    #print("------------------->"+(all_switch))
    state_code_list= []
    if(all_switch == "on"):
            state_code_list = ["AP","AR","AS","BR","CT","GA","GJ","HR","HP","JK","JH","KA","KL","MP","MH","MN","ML","MZ","NL","OR","PB","RJ","SK","TN","TG","TR","UT","UP","WB","AN","CH","DN","DL","LD","PY"]
            #state_code_list = ["AP","AR","AS","BR","CT","GA","GJ","HR","HP","JK","JH","KA","KL","MP","MH","MN","ML","MZ","NL","OR","PB","RJ","SK","TN","TG","TR","UT","UP","WB","AN","CH","DN","DL","LD","PY"]
    else:
            state_code_list = [state1,state2]
    return render_template("index.html", value=main_covid(state_code_list,LAST_N_DAYS,N_DAY_AVG),pass_val_switch = all_switch)


app.run(host='0.0.0.0', port=port, debug=True)
