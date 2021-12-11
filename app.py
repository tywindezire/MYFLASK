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

def plot(y,n,ax):
    x = list(range(len(y[-n:])))
    x.reverse()
    x = [i*-1 for i in x]
    ax.plot(x,y[-n:])
    return y[-n:]

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

def plotState(state_code,state_name,ax,n,nma):
    cases = getCases(state_code)
    n_day = nday_moving_avg(nma,cases)
    retval = plot(n_day,n,ax)
    ax.set_title(state_name)

def main_covid(state1,state2,n,nma):
    r = urllib.request.urlretrieve(STATE_WISE_DAILY,'temp.csv')
    
    filename ="india-states.csv"
    mydict = []
    with open(filename, 'r') as data:
        reader = csv.reader(data)
        mydict = {rows[0]:rows[1] for rows in reader}
    state_name_1 = mydict[state1]
    state_name_2 = mydict[state2]
    
    fig, ax = plt.subplots(1,2)
    plotState(state1,state_name_1,ax[0],n,nma)
    plotState(state2,state_name_2,ax[1],n,nma)


    # redraw the canvas
    fig.canvas.draw()

    # convert canvas to image
    img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    img  = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    # img is rgb, convert to opencv's default bgr
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.getcwd()+"/static/graph.jpg", img)

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
    print(state1,state2)
    return render_template("index.html", value=main_covid(state1,state2,LAST_N_DAYS,N_DAY_AVG))


app.run(host='0.0.0.0', port=port, debug=True)
