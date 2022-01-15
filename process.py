import re
import uuid
from dateutil import parser
import datetime

with open('oscar_text.txt') as f:
    lines = f.readlines()


raw_lines=[line.replace("\n","").replace("\r","").replace("E-mail","") for line in lines] #.replace("\t","")

lines=[]

while(raw_lines[0]==""):
    raw_lines.pop(0)

while(raw_lines[-1]==""):
    raw_lines.pop(-1)

for line in raw_lines:
    if(("Waitlist Position" not in line) and ("Notification Expires" not in line)):
        lines.append(line)


coursesInfo={}
currentCourse=""
scheduledMeetingTimes=0

for i in range(len(lines)):
    if(lines[i].strip()==""):
        continue

    if(i==0 or lines[i-1].strip()==""):
        currentCourse=lines[i]
        coursesInfo[currentCourse]={}
        scheduledMeetingTimes=0
        coursesInfo[currentCourse]["Meetings"]=[]

    if(scheduledMeetingTimes==0):
        if("Associated Term:" in lines[i]):
            coursesInfo[currentCourse]["Associated Term"]=lines[i]
        elif("CRN:" in lines[i]):
            coursesInfo[currentCourse]["CRN"]=lines[i]
        elif("Status:" in lines[i]):
            coursesInfo[currentCourse]["Status"]=lines[i]
        elif("Assigned Instructor:" in lines[i]):
            coursesInfo[currentCourse]["Assigned Instructor"]=lines[i]
        elif("Grade Mode:" in lines[i]):
            coursesInfo[currentCourse]["Grade Mode"]=lines[i]
        elif("Credits:" in lines[i]):
            coursesInfo[currentCourse]["Credits"]=lines[i]
        elif("Level:" in lines[i]):
            coursesInfo[currentCourse]["Level"]=lines[i]
        elif("Campus:" in lines[i]):
            coursesInfo[currentCourse]["Campus"]=lines[i]
        elif("Scheduled Meeting Times" in lines[i]):
            scheduledMeetingTimes+=1
            # print("scheduledMeetingTimes++")
    elif(scheduledMeetingTimes==1):
        scheduledMeetingTimes+=1
    else:
        coursesInfo[currentCourse]["Meetings"].append(lines[i])

# courses=lines[0::13]
# terms=[line.replace("\t"," ") for line in lines[1::13]]
# CRNs=[line.replace("\t"," ") for line in lines[2::13]]
# status = [line.replace("\t"," ") for line in lines[3::13]]
# profs = [line.replace("\t"," ") for line in lines[4::13]]
# gradeModes = [line.replace("\t"," ") for line in lines[5::13]]
# credits = [line.replace("\t"," ") for line in lines[6::13]]
# levels = [line.replace("\t"," ") for line in lines[7::13]]
# campus = [line.replace("\t"," ") for line in lines[8::13]]

# keys=[line.split("\t") for line in lines[10::13]]
# values=[line.split("\t") for line in lines[11::13]]
# values


def getDays(daysString):
    return [str(int(d)+1) for d in daysString.replace("M","0").replace("T","1").replace("W","2").replace("R","3").replace("F","4")]


def formattedDate(dateObj):
    return datetime.datetime.strftime(dateObj, "%Y%m%dT%H%M%S")


def getDaysICS(days):
    # SU,MO,TU,WE,TH,FR,SA
    return ",".join([d.replace("M","MO").replace("T","TU").replace("W","WE").replace("R","TH").replace("F","FR") for d in days])


eventInfos=[]

for i in range(len(coursesInfo.keys())):
    courseName = list(coursesInfo.keys())[i]

    for j in range(len(coursesInfo[courseName]["Meetings"])):
        eventInfo={}

        values = coursesInfo[courseName]["Meetings"][j].split("\t")

        if(len(values[1].split("-"))<2):
            continue

        firstStart=values[1].split("-")[0].strip()+" "+values[4].split("-")[0].strip()
        firstEnd=values[1].split("-")[1].strip()+" "+values[4].split("-")[0].strip()

        firstStart=parser.parse(firstStart)
        firstEnd=parser.parse(firstEnd)

        while(firstStart.strftime("%w") not in getDays(values[2])):
            # print(firstStart.strftime("%w"))
            firstStart+=datetime.timedelta(days=1)
            firstEnd+=datetime.timedelta(days=1)

        courseTill=parser.parse(values[4].split("-")[1].strip())
        
        eventInfo["SUMMARY"] = courseName
        eventInfo["UID"] = uuid.uuid1().__str__()
        eventInfo["LOCATION"]=values[3]
        eventInfo["DTSTART;TZID=America/New_York"]=formattedDate(firstStart)
        eventInfo["DTEND;TZID=America/New_York"]=formattedDate(firstEnd)
        eventInfo["RRULE"]="FREQ=WEEKLY;UNTIL="+formattedDate(courseTill)+";BYDAY="+getDaysICS(values[2])

        descKeys = list(filter(lambda x:type(coursesInfo[courseName][x])==str, list(coursesInfo[courseName].keys())))
        eventInfo["DESCRIPTION"]=(", ".join([re.sub('[^A-Za-z0-9 -]+', '', coursesInfo[courseName][a].replace(":"," - ")) for a in descKeys])).strip()

        eventInfos.append(eventInfo)

        

# for i in range(len(courses)):

#     eventInfo={}

#     firstStart=values[i][1].split("-")[0].strip()+" "+values[i][4].split("-")[0].strip()
#     firstEnd=values[i][1].split("-")[1].strip()+" "+values[i][4].split("-")[0].strip()
#     # print(firstStart, firstEnd)
#     firstStart=parser.parse(firstStart)
#     firstEnd=parser.parse(firstEnd)
#     # print(firstStart.strftime("%w"))

#     while(firstStart.strftime("%w") not in getDays(values[i][2])):
#         # print(firstStart.strftime("%w"))
#         firstStart+=datetime.timedelta(days=1)
#         firstEnd+=datetime.timedelta(days=1)

#     courseTill=parser.parse(values[i][4].split("-")[1].strip())

#     eventInfo["SUMMARY"] = courses[i]
#     eventInfo["UID"] = uuid.uuid1().__str__()
#     eventInfo["LOCATION"]=values[i][3]
#     eventInfo["DTSTART;TZID=America/New_York"]=formattedDate(firstStart)
#     eventInfo["DTEND;TZID=America/New_York"]=formattedDate(firstEnd)
#     eventInfo["RRULE"]="FREQ=WEEKLY;UNTIL="+formattedDate(courseTill)+";BYDAY="+getDaysICS(values[i][2])
#     eventInfo["DESCRIPTION"]=(", ".join([re.sub('[^A-Za-z0-9 -]+', '', a[i].replace(":"," -")) for a in [terms, CRNs, status, profs, gradeModes, credits, levels, campus]]))

#     eventInfos.append(eventInfo)


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


with open('export.ics', 'w') as filehandle:
    for icsLine in icsLines:
        filehandle.write('%s\n' % icsLine)
