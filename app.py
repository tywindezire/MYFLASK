import os
from flask import Flask, render_template
import time

app = Flask('MyHerokuApp')

# Read the mailgun secret key from environment variables
mailgun_secret_key_value = os.environ.get('MAILGUN_SECRET_KEY', None)

import urllib.request
import csv
import matplotlib.pyplot as plt
import cv2
import numpy as np

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

#f = urllib2.urlopen(STATE_WISE_DAILY)
#cr = csv.reader(f)
r = urllib.request.urlretrieve(STATE_WISE_DAILY,'temp.csv')

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

#print(date)
#print(cases)

#we truncate at the very end so as to maintain the originality of data
#plot y for last n days
def plot(y,n,ax):
    x = list(range(len(y[-n:])))
    x.reverse()
    x = [i*-1 for i in x]
    ax.plot(x,y[-n:])
#plot()

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

# LAST_N_DAYS = int(input("Last N days of data, N is: "))
# N_DAY_AVG = int(input("N - Day moving average N is: "))

LAST_N_DAYS = 60
N_DAY_AVG = 20
def plotState(state,ax):
    cases = getCases(state)
    n_day = nday_moving_avg(N_DAY_AVG,cases)
    plot(n_day,LAST_N_DAYS,ax)
    ax.set_title(state)
    


fig, ax = plt.subplots(1,2)
plotState("KA",ax[0])
plotState("BR",ax[1])
#plt.show()

# redraw the canvas
fig.canvas.draw()

# convert canvas to image
img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
img  = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))

# img is rgb, convert to opencv's default bgr
img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

# display image with opencv or any operation you like
#cv2.imshow("plot",img)
#cv2.waitKey(0)

def n_fact(n):
    pro = 1
    for i in range(n):
        pro = (i+1)*pro
    return pro

# This is needed for Heroku configuration, as in Heroku our
# app will probably not run on port 5000, as Heroku will automatically
# assign a port for our application
port = int(os.environ.get("PORT", 5000))

@app.route('/')
def index():

    # We will just display our mailgun secret key, nothing more
    return render_template("index.html", value=n_fact(11))

# Route that will get the config value based on a provided key, so in
# this way we can interogate our configuration.
'''
@app.route('/<config_key>')
def key(config_key=None):
    config_value=None

    if (config_key):
        # Advice: You should make a convention to define config key upper cased.
        # otherwise you will have consistency issues when reading your keys.
        # If you know they are always upper cased, you just need to uppercase
        # what the config_key argument.
        config_key = config_key.upper()
        config_value = os.environ.get(config_key, None)

    if key and config_value:
        app.logger.info("Value of {} is {}.".format(config_key, config_value))

    # We will just display our mailgun secret key, nothing more.
    return render_template("keys.html", key=config_key, value=config_value)
'''
app.run(host='0.0.0.0', port=port, debug=True)
