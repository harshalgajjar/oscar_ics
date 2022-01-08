#!/usr/bin/env python
# coding: utf-8

# In[1]:
# import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')
from flask import Flask, request, render_template, url_for, Response, send_file
#from IPython import get_ipython

import re
import uuid
from dateutil import parser
import datetime
import os


# In[4]:


app = Flask("__name__")

q = ""

@app.route("/")
def loadPage():
    return render_template('index.html', query="")

@app.route('/howto1.gif')
def get_image():
    # if request.args.get('type') == '1':
    #    filename = 'ok.gif'
    # else:
    #    filename = 'error.gif'
    return send_file('../howto1.gif', mimetype='image/gif')

@app.route("/", methods=['POST'])
def process():
   
    inputQuery1 = request.form['query1']
    
    # print(inputQuery1)

    #Normalization
    #tes2 = transformer.transform(np.array([[inputQuery1,inputQuery2,inputQuery3,inputQuery4],]))
    #output = svclassifier.predict(tes2)
    
    inputQuery1=inputQuery1.split("\n")

    #Standarization
    lines=[line.replace("\n","").replace("E-mail","") for line in inputQuery1] #.replace("\t","")
    # print(lines)

# %%
    courses=lines[0::13]
    terms=[line.replace("\t"," ") for line in lines[1::13]]
    CRNs=[line.replace("\t"," ") for line in lines[2::13]]
    status = [line.replace("\t"," ") for line in lines[3::13]]
    profs = [line.replace("\t"," ") for line in lines[4::13]]
    gradeModes = [line.replace("\t"," ") for line in lines[5::13]]
    credits = [line.replace("\t"," ") for line in lines[6::13]]
    levels = [line.replace("\t"," ") for line in lines[7::13]]
    campus = [line.replace("\t"," ") for line in lines[8::13]]

    keys=[line.split("\t") for line in lines[10::13]]
    values=[line.split("\t") for line in lines[11::13]]
    # values

    # %%
    def getDays(daysString):
        return [str(int(d)+1) for d in daysString.replace("M","0").replace("T","1").replace("W","2").replace("R","3").replace("F","4")]

    # %%
    def formattedDate(dateObj):
        return datetime.datetime.strftime(dateObj, "%Y%m%dT%H%M%S")

    # %%
    def getDaysICS(days):
        # SU,MO,TU,WE,TH,FR,SA
        return ",".join([d.replace("M","MO").replace("T","TU").replace("W","WE").replace("R","TH").replace("F","FR") for d in days])

    # %%
    eventInfos=[]

    for i in range(len(courses)):

        eventInfo={}

        firstStart=values[i][1].split("-")[0].strip()+" "+values[i][4].split("-")[0].strip()
        firstEnd=values[i][1].split("-")[1].strip()+" "+values[i][4].split("-")[0].strip()
        # print(firstStart, firstEnd)
        firstStart=parser.parse(firstStart)
        firstEnd=parser.parse(firstEnd)
        # print(firstStart.strftime("%w"))

        while(firstStart.strftime("%w") not in getDays(values[i][2])):
            # print(firstStart.strftime("%w"))
            firstStart+=datetime.timedelta(days=1)
            firstEnd+=datetime.timedelta(days=1)

        courseTill=parser.parse(values[i][4].split("-")[1].strip())

        eventInfo["SUMMARY"] = courses[i]
        eventInfo["UID"] = uuid.uuid1().__str__()
        eventInfo["LOCATION"]=values[i][3]
        eventInfo["DTSTART;TZID=America/New_York"]=formattedDate(firstStart)
        eventInfo["DTEND;TZID=America/New_York"]=formattedDate(firstEnd)
        eventInfo["RRULE"]="FREQ=WEEKLY;UNTIL="+formattedDate(courseTill)+";BYDAY="+getDaysICS(values[i][2])
        eventInfo["DESCRIPTION"]=(", ".join([re.sub('[^A-Za-z0-9 -]+', '', a[i].replace(":"," -")) for a in [terms, CRNs, status, profs, gradeModes, credits, levels, campus]]))

        eventInfos.append(eventInfo)

    # %%
    icsLines=[]
    icsLines.append("BEGIN:VCALENDAR")
    icsLines.append("VERSION:2.0")
    icsLines.append("PRODID:harshalgajjar.com")

    for i in range(len(eventInfos)):
        icsLines.append("BEGIN:VEVENT")
        for key in eventInfos[i].keys():
            icsLines.append(key+":"+eventInfos[i][key])

        icsLines.append("END:VEVENT")

    icsLines.append("END:VCALENDAR")

    # %%

    # with open('semCal_rajat.ics', 'w') as filehandle:
    #     for icsLine in icsLines:
    #         filehandle.write('%s\n' % icsLine)

    # file_handle = open('semCal_rajat.ics', 'r')

    return Response(
        "\n".join(icsLines),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=export.ics"})


    # return send_file('semCal_rajat.ics', as_attachment=True)

    # return Response(render_template('sandy1.html', output=str(12), query1 = request.form['query1'], query2 = request.form['query2'],query3 = request.form['query3'],query4 = request.form['query4']))

if __name__=='__main__':
    app.run(debug=True)


# In[ ]:




