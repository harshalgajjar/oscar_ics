import re
import uuid
from dateutil import parser
import datetime
# %%
with open('oscar_text.txt') as f:
    lines = f.readlines()

# %%
lines=[line.replace("\n","").replace("\r","").replace("E-mail","") for line in lines] #.replace("\t","")

while(lines[0]==""):
    lines.pop(0)

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
with open('export.ics', 'w') as filehandle:
    for icsLine in icsLines:
        filehandle.write('%s\n' % icsLine)

# %%



