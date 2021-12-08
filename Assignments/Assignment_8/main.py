import myPyMongo,myRedis,mysqlCnx
from myPyMongo import mongoColl
from myRedis import myRedis

from typing import Optional,List,Tuple
from decimal import Decimal
import pprint
import random
import pickle
from bson.json_util import dumps
from bson.son import SON
import json
import time
import csv

def EmptyDBs():
    myPyMongo.EmptyCollection()
    myRedis.flushdb()
    mysqlCnx.query('experiment',"DELETE FROM `person`;",'delete')
    mysqlCnx.query('experiment',"DELETE FROM `numbers`;",'delete')
    mysqlCnx.query('experiment',"DELETE FROM `strings`;",'delete')
    mysqlCnx.query('experiment',"DELETE FROM `person_certifications`;",'delete')

def InsertNStrings(n):
    timeToComplete = []
    #Insert into Mongo
    tic = time.perf_counter()
    for i in range(n):
        mongoColl.insert_one({"testKey":"test"+str(i)})

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)
    #Insert into Redis
    tic = time.perf_counter()
    for i in range(n):
        myRedis.set('testKey'+str(i),'testValue'+str(i))

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)
    #Insert into MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(n):
        sql += f"""
        INSERT INTO `strings` (`id`,`testValue`) VALUES ({i},'test{i}')

        """
    mysqlCnx.query('experiment',sql,'insert')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def InsertNInts(n):
    timeToComplete = []
    #Insert into Mongo
    tic = time.perf_counter()
    for i in range(n):
        mongoColl.insert_one({"testKey":str(i)})

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)
    #Insert into Redis
    tic = time.perf_counter()
    for i in range(n):
        myRedis.set('testKey'+str(i),i)

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)
    #Insert into MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(n):
        sql += f"""
        INSERT INTO `numbers` (`id`,`testValue`) VALUES ({i},{i})

        """
    mysqlCnx.query('experiment',sql,'insert')
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def InsertNComplex(n):
    timeToComplete = []
    #Insert into Mongo
    tic = time.perf_counter()
    for i in range(n):
        personDict = {"person":{
                "testName":"Bob Seger"+str(i),
                "testAge": i ,
                "testCerts":[
                    {
                        "certName":"certification"+str(i),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+1),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+2),
                        "certDate":"1/1/2001"
                    }
                ]} 
            }
        mongoColl.insert_one(personDict)

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)
    #Insert into Redis
    tic = time.perf_counter()
    for i in range(n):
        personObject = {"person":{
                "testName":"Bob Seger"+str(i),
                "testAge": i ,
                "testCerts":[
                    {
                        "certName":"certification"+str(i),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+1),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+2),
                        "certDate":"1/1/2001"
                    }
                ]} }
        jsonPackage = json.dumps(personObject)
        myRedis.set('person'+str(i),jsonPackage)

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)
    #Insert into MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(n):
        sql += f"""
        INSERT INTO `person`(`id`,`testName`,`testAge`)
        VALUES ({i},'Bob Seger{i}',{i})
        
        INSERT INTO `person_certifications` (`certName`,`certDate`,`personId`)
        VALUES 
        ('certification{i}','1/1/2001',{i}),
        ('certification{i+1}','1/1/2001',{i}),
        ('certification{i+2}','1/1/2001',{i})

        """
    mysqlCnx.query('experiment',sql,'insert')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def SearchNStrings(n,numOfSearches):
    timeToComplete = []
    #Search Mongo
    #single-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.find_one({"testKey":"test"+str(i%n)})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.find({"testKey":{"$in":["test"+str(i%n)]}})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()
    mongoColl.find()
        
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Search Redis
    #single-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.get('testKey'+str(i%n))
    
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.get('testKey'+str(i%n))
        myRedis.get('testKey'+str(i%n))
        myRedis.get('testKey'+str(i%n))
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()
    keys = myRedis.keys('*')
    for key in keys:
        myRedis.get(key)
        
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Search MySQL
    #single-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        sql = f"SELECT * FROM `strings` WHERE id = {i%n})"
        mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        sql = f"SELECT * FROM `strings` WHERE id = {i%n} OR id = {(i+1)%n} OR id = {(i+2)%n} )"
        mysqlCnx.query('experiment',sql,'select')
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()

    sql = f"SELECT * FROM `strings`"
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def SearchNInts(n,numOfSearches):
    timeToComplete = []
    #Search Mongo
    #single-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.find_one({"testKey":(i%n)})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.find({"testKey":{"$gt":[i%n]}})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()
    mongoColl.find()
        
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Search Redis
    #single-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.get('testKey'+str(i%n))

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.get('testKey'+str(i%n))
        myRedis.get('testKey'+str(i%n))
        myRedis.get('testKey'+str(i%n))
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()
    keys = myRedis.keys('*')
    for key in keys:
        myRedis.get(key)
        
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Search MySQL
    #single-search
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfSearches):
        sql += f"""
        SELECT * FROM `numbers` WHERE id = {i%n})
        
        """
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfSearches):
        sql += f"""
        SELECT * FROM `numbers` WHERE id = {i%n} OR id = {(i+1)%n} OR id = {(i+2)%n} )
        
        """
    mysqlCnx.query('experiment',sql,'select')
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()
    sql = ""
    sql += f"""SELECT * FROM `numbers`"""
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def SearchNComplex(n,numOfSearches):
    timeToComplete = []
    #Search Mongo
    #single-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.find_one({f"certName":"certification"+str(i%n)})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.find({"certName":{"$in":["certification"+str(i%n)]}})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()
    mongoColl.find()
        
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Search Redis
    #single-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.get('person'+str(i%n))

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.get('person'+str(i%n))
        myRedis.get('person'+str(i%n))
        myRedis.get('person'+str(i%n))
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()
    keys = myRedis.keys('*')
    for key in keys:
        myRedis.get(key)
        
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Search MySQL
    #single-search
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfSearches):
        sql += f"""SELECT * 
        FROM `person` 
        LEFT JOIN `person_certifications` AS c ON c.personId = id 
        WHERE certName = 'certification{i%n})'
        
        """
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #multi-search
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfSearches):
        sql += f"""SELECT * 
        FROM `person` 
        LEFT JOIN `person_certifications` AS c ON c.personId = id 
        WHERE certName = 'certification{i%n}) OR certName = 'certification{i+1%n}) OR certName = 'certification{i+2%n})'
        
        """
    mysqlCnx.query('experiment',sql,'select')
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #find all
    tic = time.perf_counter()

    sql = f"SELECT * FROM `person` LEFT JOIN `person_certifications` AS c ON c.personId = id"
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def UpdateNStrings(n,numOfSearches):
    timeToComplete = []
    #Update Mongo
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.update_one({"testKey":"test"+str(i%n)},{ "$set": { "testKey": "testUpdate"+str(i%n) } })
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update Redis
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.set('testKey'+str(i%n),'testUpdate'+str(i))

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfSearches):
        sql += f"""
        UPDATE `strings` SET testValue = 'UpdatedValue' WHERE id = {i%n})
        
        """
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def UpdateNInts(n,numOfSearches):
    timeToComplete = []
    #Update Mongo
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoColl.update_one({"testKey":(i%n)},{ "$set": { "testKey": i } })
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update Redis
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.set('testKey'+str(i%n),i)

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfSearches):
        sql += f"""
        UPDATE `numbers` SET testValue = {i} WHERE id = {i%n})
        
        """
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def UpdateNComplex(n,numOfSearches):
    timeToComplete = []
    #Update Mongo
    tic = time.perf_counter()
    for i in range(numOfSearches):
        mongoQuery = {"person":{
                "testName":"Bob Seger"+str(i),
                "testAge": i ,
                "testCerts":[
                    {
                        "certName":"certification"+str(i),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+1),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+2),
                        "certDate":"1/1/2001"
                    }
                ]} }
        mongoUpdate = {"$set":{"person":{
                "testName":"Bob Seger"+str(i),
                "testAge": i ,
                "testCerts":[
                    {
                        "certName":"certification"+str(i),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+1),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+2),
                        "certDate":"1/1/2001"
                    }
                ]} } }
        mongoColl.update_one(mongoQuery,mongoUpdate)
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update Redis
    tic = time.perf_counter()
    for i in range(numOfSearches):
        myRedis.set('person'+str(i%n),json.dumps({
                "testName":"Bob Seger"+str(i),
                "testAge": i ,
                "testCerts":[
                    {
                        "certName":"certification"+str(i),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+1),
                        "certDate":"1/1/2001"
                    },
                    {
                        "certName":"certification"+str(i+2),
                        "certDate":"1/1/2001"
                    }
                ]}) )

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfSearches):
        sql += f"""
        UPDATE `person`
        SET testName = 'Eric Claption{i}',testAge = {i} ({i},'Bob Seger{i}',{i})
        WHERE id = {i%n}
        
        UPDATE `person_certifications`
        SET certDate = '2/1/2002'
        WHERE personId = {i%n}

        """
    mysqlCnx.query('experiment',sql,'insert')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def DeleteNStrings(n,numOfDeletes):
    timeToComplete = []
    #Update Mongo
    tic = time.perf_counter()
    for i in range(numOfDeletes):
        mongoColl.delete_one({"testKey":"testUpdate"+str(i%n)})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update Redis
    tic = time.perf_counter()
    for i in range(numOfDeletes):
        myRedis.delete('testKey'+str(i%n))

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfDeletes):
        sql += f"""
        DELETE FROM `strings` WHERE id = {i%n})
        
        """
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def DeleteNInts(n,numOfDeletes):
    timeToComplete = []
    #Update Mongo
    tic = time.perf_counter()
    for i in range(numOfDeletes):
        mongoColl.delete_one({"testKey":(i%n)})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update Redis
    tic = time.perf_counter()
    for i in range(numOfDeletes):
        myRedis.delete('testKey'+str(i%n))

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfDeletes):
        sql += f"""
        DELETE FROM `numbers` WHERE id = {i%n})
        
        """
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def DeleteNComplex(n,numOfDeletes):
    timeToComplete = []
    #Update Mongo
    tic = time.perf_counter()
    for i in range(numOfDeletes):
        mongoColl.delete_one({"person":{"testName":"Bob Seger"+str(i%n)}})
    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update Redis
    tic = time.perf_counter()
    for i in range(numOfDeletes):
        myRedis.delete("person"+str(i%n))

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    #Update MySQL
    tic = time.perf_counter()
    sql = ""
    for i in range(numOfDeletes):
        sql += f"""
        DELETE FROM `person` WHERE id = {i%n})
        
        """
    mysqlCnx.query('experiment',sql,'select')

    toc = time.perf_counter()
    timeToComplete.append(toc-tic)

    return timeToComplete

def ValTypeFromIndex(i):
    valString = "String"
    if valIndex == 1:
        valString = "Int"
    elif valIndex == 2:
        valString = "Complex"
    return valString

def DBTypeFromIndex(i):
    dbString = "Mongo"
    if dbIndex == 1:
        dbString = "Redis"
    elif dbIndex == 2:
        dbString = "MySQL"
    return dbString

if __name__ == "__main__":
    N = 5500
    NOffset = 500

    searchCoefficient = .5
    updateCoefficient = 1.5
    deleteCoefficient = .25

    #[insertTimes,searchTimes,updateTimes,deleteTimes]
    aggregateTimes = []
    outputFile = "output.csv"
    for i in range(NOffset,N,NOffset):
        #Empty databases for new run
        EmptyDBs()
        print(f"Processing {i} items")

        #[mongo time, redis time, sql time]
        insertTimes = []
        #[mongo single-search time,mongo multi-search time, mongo all time,
        #  redis single-search time, redis multi-search time, redis all time,
        #  sql single-search time, sql multi-search time, sql all time]
        searchTimes = []
        #[mongo time, redis time, sql time]
        updateTimes = []
        #[mongo time, redis time, sql time]
        deleteTimes = []
        
        insertTimes.append(InsertNStrings(i))
        searchTimes.append(SearchNStrings(i,int(i*searchCoefficient)))
        updateTimes.append(UpdateNStrings(i,int(i*updateCoefficient)))
        deleteTimes.append(DeleteNStrings(i,int(i*deleteCoefficient)))
        print(f"Finished Processing {i} Strings")
        EmptyDBs()

        insertTimes.append(InsertNInts(i))
        searchTimes.append(SearchNInts(i,int(i*searchCoefficient)))
        updateTimes.append(UpdateNInts(i,int(i*updateCoefficient)))
        deleteTimes.append(DeleteNInts(i,int(i*deleteCoefficient)))
        print(f"Finished Processing  {i} Numbers")
        EmptyDBs()

        insertTimes.append(InsertNComplex(i))
        searchTimes.append(SearchNComplex(i,int(i*searchCoefficient)))
        updateTimes.append(UpdateNComplex(i,int(i*updateCoefficient)))
        deleteTimes.append(DeleteNComplex(i,int(i*deleteCoefficient)))
        print(f"Finished Processing {i} Complex Items")

        aggregateTimes.append([insertTimes,searchTimes,updateTimes,deleteTimes])

        #increase search coefficient
        searchCoefficient += .25

    #write results to csv
    with open(outputFile, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(['# of Entries','DB Type','Action','Sub-Action Type','Value Type','Time to Complete']) 

        nVal = NOffset
        dbIndex = 0
        dbString = "Mongo"
        valIndex = 0
        #print(aggregateTimes)
        for row in aggregateTimes:
            valIndex = 0
            #Parse over Insert data
            for iRow in row[0]:
                dbIndex = 0
                for iVal in iRow:
                    csvwriter.writerow([nVal,DBTypeFromIndex(dbIndex),'Insert','',ValTypeFromIndex(valIndex),iVal])
                    dbIndex += 1
                valIndex += 1
            valIndex = 0
            #Parse over Search Data
            subAction = "single-search"
            subActionIndex = 0
            for iRow in row[1]:
                dbIndex = 0
                for iVal in iRow:
                    if subActionIndex == 0:
                        subAction = "single-search"
                    elif subActionIndex == 1:
                        subAction = "multi-search"
                    else:
                        subAction = "find all"
                        subActionIndex = 3
                    csvwriter.writerow([nVal,DBTypeFromIndex(dbIndex),'Search',subAction,ValTypeFromIndex(valIndex),iVal])
                    
                    if subActionIndex == 3:
                        dbIndex += 1
                        subActionIndex = -1
                    subActionIndex += 1
                valIndex += 1
            valIndex = 0
            #Parse over Update data
            for iRow in row[2]:
                dbIndex = 0
                for iVal in iRow:
                    csvwriter.writerow([nVal,DBTypeFromIndex(dbIndex),'Update','',ValTypeFromIndex(valIndex),iVal])
                    dbIndex += 1
                valIndex += 1
            valIndex = 0
            #Parse over Delete data
            for iRow in row[3]:
                dbIndex = 0
                for iVal in iRow:
                    csvwriter.writerow([nVal,DBTypeFromIndex(dbIndex),'Delete','',ValTypeFromIndex(valIndex),iVal])
                    dbIndex += 1
                valIndex += 1
            nVal += NOffset

