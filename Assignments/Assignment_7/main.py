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

from fastapi import FastAPI,File,UploadFile,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

app = FastAPI()

def compVal(operator):
    #Will work come release of Python 3.10
    # match operator:
    #     case 0:
    #         return "="
    #     case 1:
    #         return ">"
    #     case 2:
    #         return ">="
    #     case 3:
    #         return "<"
    #     case 4:
    #         return "<="
    #     case 5:
    #         return "<>"
    #     default:
    #         raise ValueError('Invalid operator')
    print(operator)
    if operator == Operator.equals:
        return "="
    elif operator == Operator.greater_than:
        return ">"
    elif operator == Operator.greater_than_or_equal_to:
        return ">="
    elif operator == Operator.less_than:
        return "<"
    elif operator == Operator.less_than_or_equal_to:
        return "<="
    elif operator == Operator.not_equals:
        return "<>"
    else:
        raise ValueError('Invalid operator')

def comp2Vals(operator):
    #Will work come release of Python 3.10
    # match operator:
    #     case 1:
    #         return (">","<")
    #     case 2:
    #         return (">=","<=")
    #     case 3:
    #         return ("<",">")
    #     case 4:
    #         return ("<=",">=")
    #     default:
    #         raise ValueError('Invalid operator with 2 values')
    if operator == Operator.greater_than:
        return (">","<")
    elif operator == Operator.greater_than_or_equal_to:
        return (">=","<=")
    elif operator == Operator.less_than:
        return ("<",">")
    elif operator == Operator.less_than_or_equal_to:
        return ("<=",">=")
    else:
        raise ValueError('Invalid operator with 2 values')
        return

def convertTo24Time(time):
    time12Hour = datetime.datetime.strptime(time,'%I%M%p')
    return int(time12Hour.strftime("%H%M"))

def convertFrom24Time(time):
    timeString = str(time).zfill(4)
    time12Hour = datetime.time(hour=int(timeString[0:2]),minute=int(timeString[2:4]))
    return time12Hour.strftime("%I:%M%P")

def dropPreviousAdvising(mNumber,semester,year):
    params = (mNumber,semester,year,)
    result = mysqlCnx.sprocQuery('advising',params,'DropAdvisingForm','delete')
    return result

def enrollInCourse(mNumber,semester,year,courseCRN):
    newCourse = getCourseByCRN(courseCRN)[0]
    newDays = list(newCourse['days'])
    if newCourse['maxNum'] == newCourse['currEnrolled']:
        return {"Result":"Class is full"}
    currentEnrolled = getAdvisingForm(mNumber,semester,year)
    for course in currentEnrolled:
        c = getCourseByCRN(course['courseCRN'])[0]
        cDays = list(c['days'])
        for d in cDays:
            if d in newDays:
                if (c['startTime'] <= newCourse['startTime'] <= c['endTime']) or (c['startTime'] <= newCourse['endTime'] <= c['endTime']):
                    return {"Result":"Conflicting time with currently enrolled classes"}
    params = (mNumber,semester,year,courseCRN,)
    result = mysqlCnx.sprocQuery('advising',params,'AddAdvisingLink','insert')
    print(f"Result is {result}")
    #return result

def dropCourse(mNumber,semester,year,courseCRN):
    params = (mNumber,semester,year,courseCRN,)
    result = mysqlCnx.sprocQuery('advising',params,'DropAdvisingLink','delete')
    return result

def getCourseByCRN(crn):
    params = (crn,)
    result = mysqlCnx.sprocQuery('advising',params,'GetCourse','select')
    return result

def getStudentByMNumber(mNumber):
    params = (mNumber,)
    result = mysqlCnx.sprocQuery('advising',params,'GetStudent','select')
    return result

def getAdvisingForm(mNumber,semester,year):
    params = (mNumber,semester,year,)
    result = mysqlCnx.sprocQuery('advising',params,'GetAdvisingForm','select')
    return result

@app.get("/",response_class=HTMLResponse)
async def root():
    html = """
    <html>
        <body>
            <h1>Assignment 7 API</h1>
            <h3>Daniel Bowen</h3>
            </br>
            <div>
                <p>
                    <a href="http://143.198.60.31:8004/docs">API Swagger</a>
                </p>
            </div>
        </body>
    </html>
    """
    return html

@app.get("/course/{crn}")
async def getCourse(crn:int):
    result = getCourseByCRN(crn)
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/course/")
async def getCourses(item: CourseGet):
    sql = """
    SELECT * FROM `courses`
    """
    whereQuery = "WHERE "
    numWhereQueries = 0
    numAnds = 0
    try:
        subject = item.subject
        if subject != None:
            numWhereQueries += 1
            subjectQuery = f" (subj = '{subject}')"
            whereQuery += subjectQuery
    except:
        pass
    
    try:
        courseNumber = item.courseNumber
        if courseNumber != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            courseNumberQuery = f" (crse = {courseNumber})"
            whereQuery += courseNumberQuery
    except:
        pass

    try:
        title = item.title
        if title != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            titleQuery = f" (title LIKE '{title}')"
            whereQuery += titleQuery
    except:
        pass
    
    try:
        primaryInstructor = item.primaryInstructor
        if primaryInstructor != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            primaryInstructorQuery = f" (primaryInstructor = '{primaryInstructor}')"
            whereQuery += primaryInstructorQuery
    except:
        pass
    try:
        building = item.building
        if building != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            buildingQuery = f" (bldg = '{building}')"
            whereQuery += buildingQuery
    except:
        pass

    try:
        room = item.room
        if room != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            roomQuery = f" (room = '{room}')"
            whereQuery += roomQuery
    except:
        pass
    try:
        betweenTimes = item.betweenTimes
        if betweenTimes != None:
            val1 = convertTo24Time(betweenTimes.startTime)
            val2 = convertTo24Time(betweenTimes.endTime)
            if val2 != None and val1 != None:
                numWhereQueries += 1
                if(numWhereQueries - 1 != numAnds):
                    whereQuery += " AND "
                    numAnds += 1
                
                betweenTimesQuery =f"(startTime >= {val1} AND startTime <= {val2}) AND (endTime >= {val1} AND endTime <= {val2})"
                whereQuery += betweenTimesQuery
    except:
        pass
    sql += whereQuery
    result = mysqlCnx.query('advising',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/courses/all")
async def getAllCourses():
    print("AHHHHHHH")
    sql = """
    SELECT * FROM `courses`
    """
    result = mysqlCnx.query('advising',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/courses/closed")
async def getClosedCourses():
    sql = """
    SELECT * FROM `courses` WHERE maxNum = currEnrolled
    """
    result = mysqlCnx.query('advising',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.post("/course/")
async def addCourse(item:Course):
    startTime = convertTo24Time(item.startTime)
    endTime = convertTo24Time(item.endTime)
    sql = f"""
    INSERT INTO `courses` (crn,col,subj,crse,sect,title,primaryInstructor,maxNum,currEnrolled,days,startTime,endTime,hours,bldg,room)
    VALUES({item.crn},'{item.college}','{item.subject}',{item.courseNumber},
    '{item.section}','{item.title}','{item.primaryInstructor}',{item.maxNumber},
    {item.currentlyEnrolled},'{item.days}',{startTime},
    {endTime},{item.courseNumber},'{item.building}','{item.room}')
    """

    result = mysqlCnx.query('advising',sql,'insert')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.put("/course/")
async def editCourse(item:Course):
    sql = f"""
    UPDATE `courses` 
    SET
    col = '{item.college}',
    subj = '{item.subject}',
    crse = {item.courseNumber},
    sect = '{item.section}',
    title = '{item.title}',
    primaryInstructor = '{item.primaryInstructor}',
    maxNum = {item.maxNumber},
    currEnrolled = {item.currentlyEnrolled},
    days = '{item.days}',
    startTime = {convertTo24Time(item.startTime)},
    endTime = {convertTo24Time(item.endTime)},
    hours = {item.courseNumber % 10},
    bldg = '{item.building}',
    room = '{item.room}'
    WHERE crn = {item.crn}
    """

    result = mysqlCnx.query('advising',sql,'update')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.post("/student/")
async def addStudent(item:Student):
    try:
        gpa = item.gpa
    except:
        gpa = None
    try:
        githubUserName = item.githubUserName
    except:
        githubUserName = None

    params = (item.firstName,item.lastName,item.mNumber,item.classification,item.email,gpa,githubUserName)
    result = mysqlCnx.sprocQuery('advising',params,'AddOrUpdateStudent','insert')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.put("/student/")
async def updateStudent(item:Student):
    try:
        gpa = item.gpa
    except:
        gpa = None
    try:
        githubUserName = item.githubUserName
    except:
        githubUserName = None

    params = (item.firstName,item.lastName,item.mNumber,item.classification,item.email,gpa,githubUserName)
    result = mysqlCnx.sprocQuery('advising',params,'AddOrUpdateStudent','insert')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/student/")
async def getStudent(item: StudentGet):
    sql = """
    SELECT * FROM `student`
    """
    whereQuery = "WHERE "
    numWhereQueries = 0
    numAnds = 0
    try:
        firstName = item.firstName
        if firstName != None:
            numWhereQueries += 1
            fNameQuery = f" (firstName = '{firstName}')"
            whereQuery += fNameQuery
    except:
        pass
    
    try:
        lastName = item.lastName
        if lastName != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            lNameQuery = f" (lastName = '{lastName}')"
            whereQuery += lNameQuery
    except:
        pass

    try:
        mNumber = item.mNumber
        if mNumber != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            mNumberQuery = f" (mNumber = '{mNumber}')"
            whereQuery += mNumberQuery
    except:
        pass
    try:
        gpa = item.gpa
        if gpa != None:
            val1 = gpa.valuea
            operator = gpa.operator
            numWhereQueries += 1
            if(numWhereQueries - 1 != numAnds):
                whereQuery += " AND "
                numAnds += 1

            gpaQuery = "("
            try:#if two release date values have been passed in
                val2 = gpa.valueb
                if val2 != None:
                    ops = comp2Vals(operator)
                    gpaQuery += f"gpa {ops[0]} {val1} AND gpa {ops[1]} {val2}"
                else:
                    raise ValueError("Second value not present")
            except:#if doing a single release date comparison
                op = compVal(operator)
                gpaQuery += f"gpa {op} {val1}"
            whereQuery += gpaQuery + ") "
    except:
        pass

    sql += whereQuery
    result = mysqlCnx.query('advising',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/student/all")
async def getAllStudents():
    result = mysqlCnx.sprocQuery('advising',(),'GetAllStudents','select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/advising_form/template")
async def getAdvisingFormTemplate():
    return FileResponse('advising_form.csv',filename='advising_form.csv')

@app.get("/advising_form/")
async def getAdvisingForms(item: AdvisingFormGet):
    sql = """
    SELECT
    s.firstName, s.lastName, studentMNumber,semester,year,
    courseCRN,c.crse,c.sect,c.title,c.days,c.startTime,c.endTime,c.bldg,
    c.room,c.primaryInstructor
    FROM `enrolled_class`
    LEFT JOIN `student` AS s ON s.mNumber = studentMNumber
    LEFT JOIN `courses` AS c ON c.crn = courseCRN
    """
    sqlGroupAndOrder = """
    GROUP BY s.firstName, s.lastName,studentMNumber,semester,year,courseCRN
    ORDER BY s.firstName, s.lastName, studentMNumber,semester,year
    """

    whereQuery = "WHERE "
    numWhereQueries = 0
    numAnds = 0
    try:
        mNumber = item.studentMNumber
        if mNumber != None:
            numWhereQueries += 1
            mNumberQuery = f" (studentMNumber = '{mNumber}')"
            whereQuery += mNumberQuery
    except:
        pass
    
    try:
        semester = item.semester
        if semester != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            semesterQuery = f" (semester = '{semester}')"
            whereQuery += semesterQuery
    except:
        pass

    try:
        year = item.year
        if year != None:
            numWhereQueries += 1
            if numWhereQueries - 1 != numAnds:
                whereQuery += " AND "
                numAnds += 1
            yearQuery = f" (year = {year})"
            whereQuery += yearQuery
    except:
        pass
    
    sql += whereQuery + " " + sqlGroupAndOrder
    result = mysqlCnx.query('advising',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/advising_form/all")
async def getAllAdvisingForms():
    params = None
    result = mysqlCnx.sprocQuery('advising',params,'GetAllAdvisingForms','select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/advising_form/export/csv")
async def exportAdvisingForm(item: AdvisingIdentifier):
    result = getAdvisingForm(item.studentMNumber, item.semester,item.year)

    if result == None:
        raise HTTPException(status_code=404, detail="Item not found")
        return
    
    filename = "temp.csv"
    student = getStudentByMNumber(item.studentMNumber)[0]
    with open(filename,'w',encoding='utf-8') as t:
        t.write('\ufeff')
        cWriter = csv.writer(t,quoting=csv.QUOTE_MINIMAL)
        cWriter.writerow(['Student First Name','Student Last Name','Student M Number','','Semester','Year','','','',''])
        cWriter.writerow([student['firstName'],student['lastName'],item.studentMNumber,'',item.semester,item.year,'','','',''])
        cWriter.writerow(['','','','','','','','','',''])
        cWriter.writerow(['CRN','CRSE','SECT','TITLE','DAYS','START','END','BLDG','ROOM','INSTRUCTOR'])

        hours = 0
        for rowT in result:
            row = getCourseByCRN(rowT["courseCRN"])[0]
            start = convertFrom24Time(row['startTime'])
            end = convertFrom24Time(row['endTime'])
            hours += row['hours']
            cWriter.writerow([row['crn'],row['crse'],row['sect'],row['title'],row['days'],start,end,row['bldg'],row['room'],row['primaryInstructor']])
        cWriter.writerow(['','','','','','','','','',''])
        cWriter.writerow(['','','','','','','','','Total Hours',hours])
    
    returnFileName = item.studentMNumber + '-' + item.semester + '-' + str(item.year) + '.csv'
    fileResponse = FileResponse(filename,filename=returnFileName)
    #os.unlink(filename)

    return fileResponse

@app.get("/advising_form/export/pdf")
async def exportAdvisingFormPDF(item: AdvisingIdentifier):
    result = getAdvisingForm(item.studentMNumber, item.semester,item.year)

    if result == None:
        raise HTTPException(status_code=404, detail="Item not found")
        return
    
    filename = "temp.csv"
    htmlFileName = "temp.html"
    pdfFileName = "temp.pdf"
    student = getStudentByMNumber(item.studentMNumber)[0]
    with open(filename,'w',encoding='utf-8') as t:
        t.write('\ufeff')
        cWriter = csv.writer(t,quoting=csv.QUOTE_MINIMAL)
        cWriter.writerow(['Student First Name','Student Last Name','Student M Number','','Semester','Year','','','',''])
        cWriter.writerow([student['firstName'],student['lastName'],item.studentMNumber,'',item.semester,item.year,'','','',''])
        cWriter.writerow(['','','','','','','','','',''])
        cWriter.writerow(['CRN','CRSE','SECT','TITLE','DAYS','START','END','BLDG','ROOM','INSTRUCTOR'])

        hours = 0
        for rowT in result:
            row = getCourseByCRN(rowT["courseCRN"])[0]
            start = convertFrom24Time(row['startTime'])
            end = convertFrom24Time(row['endTime'])
            hours += row['hours']
            cWriter.writerow([row['crn'],row['crse'],row['sect'],row['title'],row['days'],start,end,row['bldg'],row['room'],row['primaryInstructor']])
        cWriter.writerow(['','','','','','','','','',''])
        cWriter.writerow(['','','','','','','','','Total Hours',hours])
        cWriter.writerow(['Advising Signature','','','','','','','','',''])
        cWriter.writerow(['Student Signature','','','','','','','','',''])

    CSV = pd.read_csv(filename)  
    CSV.to_html(htmlFileName)
    CSV.fillna('')
    pdfkit.from_file(htmlFileName,pdfFileName)  
    
    returnFileName = item.studentMNumber + '-' + item.semester + '-' + str(item.year) + '.pdf'
    fileResponse = FileResponse(pdfFileName,filename=returnFileName)
    # os.unlink(filename)
    # os.unlink(htmlFileName)
    # os.unlink(pdfFileName)

    return fileResponse

@app.post("/advising_form/upload/")
async def uploadAdvisingForm(file: UploadFile = File(...)):
    csvPD = pd.read_csv(file.file)
    buffer = StringIO()
    csvPD.to_csv(buffer)
    buffer.seek(0)

    mNumber = ''
    semester = ''
    year = 0
    courseCRNs = []

    index = -1
    for row in csv.reader(buffer):
        index += 1
        if index == 1:
            mNumber = row[3]
            semester = row[5]
            year = int(row[6])
        elif index >= 4:
            courseCRNs.append(int(row[1])) 
    if mNumber[-1]=='m' or mNumber[-1]=='M':
        dropPreviousAdvising(mNumber,semester,year)

        for crn in courseCRNs:
            enrollInCourse(mNumber,semester,year,crn)
        result = jsonable_encoder({'Result':'Upload Successful.'})
        return JSONResponse(content = result)
    else:
        result = jsonable_encoder({'Result':'There was an error or no M number was provided.'})
        return JSONResponse(content = result)

@app.post("/advising_form/")
async def addAdvisingForm(item: AdvisingForm):
    dropPreviousAdvising(item.studentMNumber,item.semester,item.year)
    for crn in item.courseCRNs:
        addResult = enrollInCourse(item.studentMNumber,item.semester,item.year,crn)
    result = jsonable_encoder({'Result':'Upload Successful.'})
    return JSONResponse(content = result)

@app.delete("/advising_form/course")
async def deleteAdvisingLink(item: AdvisingLink):
    dropPreviousAdvising(item.studentMNumber,item.semester,item.year,item.courseCRN)
    result = jsonable_encoder({'Result':'Upload Successful.'})
    return JSONResponse(content = result)