import mysqlCnx
import json
import uvicorn
import datetime
import csv
import pandas as pd
import codecs
import pdfkit
from io import StringIO
import os, sys
from models import *

def convertTo24Time(time):
    time12Hour = datetime.datetime.strptime(time,'%I%M%p')
    return int(time12Hour.strftime("%H%M"))

if __name__ == "__main__":
    with open('2022_spring_schedule.json') as data_file:
        data= json.load(data_file)
        print(type(data[0]))
        index = 0
        numErrors = 0
        for dict in data:
            print(index)
            newClass = {}
            try:
                newClass['crn'] = int(dict["Crn"])
                newClass['college'] = dict["Col"]
                newClass['subject'] = dict["Subj"].replace("'","")
                newClass['courseNumber'] = int(dict["Crse"])
                newClass['section'] = dict["Sect"].replace("'","")
                newClass['title'] = dict["Title"].replace("'","")
                newClass['primaryInstructor'] = dict["PrimaryInstructor"].replace("'","")
                newClass['maxNumber'] = int(dict["Max"])
                newClass['currentlyEnrolled'] = int(dict["Curr"])
                newClass['days'] = dict["Days"]
                newClass['startTime'] = dict["Begin"]
                newClass['endTime'] = dict["End"]
                newClass['building'] = dict["Bldg"].replace("'","")
                newClass['room'] = dict["Room"].replace("'","")

                startTime = convertTo24Time(newClass['startTime'])
                endTime = convertTo24Time(newClass['endTime'])
                sql = f"""
                INSERT INTO `courses` (crn,col,subj,crse,sect,title,primaryInstructor,maxNum,currEnrolled,days,startTime,endTime,hours,bldg,room)
                VALUES({newClass['crn']},'{newClass['college']}','{newClass['subject']}',{newClass['courseNumber']},
                '{newClass['section']}','{newClass['title']}','{newClass['primaryInstructor']}',{newClass['maxNumber']},
                {newClass['currentlyEnrolled']},'{newClass['days']}',{startTime},
                {endTime},{newClass['courseNumber']},'{newClass['building']}','{newClass['room']}')
                """

                result = mysqlCnx.query('advising',sql,'insert')
            except:
                numErrors += 1
            index+=1

        print(f"Number of Errors: {numErrors}")

            
            