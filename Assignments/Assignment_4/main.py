import mysqlCnx
import json
from typing import Optional
from decimal import Decimal
import uvicorn

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pydantic import (
    BaseModel,
    NegativeFloat,
    NegativeInt,
    PositiveFloat,
    PositiveInt,
    NonNegativeFloat,
    NonNegativeInt,
    NonPositiveFloat,
    NonPositiveInt,
    conbytes,
    condecimal,
    confloat,
    conint,
    conlist,
    conset,
    constr,
    Field,
)

app = FastAPI()

class Teacher(BaseModel):
    id : int
    dept : int
    name : constr(max_length=50)
    phone : constr(max_length=50)
    mobile : constr(max_length=50)

class Country(BaseModel):
    name : constr(max_length=60)
    continent : Optional[constr(max_length=60)]
    area : Optional[Decimal]
    population : Optional[Decimal]
    gdp : Optional[Decimal]
    capital : Optional[constr(max_length=60)]
    tld : Optional[constr(max_length=5)]
    flag : Optional[constr(max_length=255)]

#query(database,sql,returnType):
basicsDict = {
    1 : "SELECT population FROM world WHERE name = 'Germany';",
    2 : "SELECT name, population FROM world WHERE name IN ('Sweden', 'Norway', 'Denmark');;",
    3 : "SELECT name, area FROM world WHERE area BETWEEN 200000 AND 250000;"
}

worldDict = {
    1 : "SELECT name, continent, population FROM world",
    2 : "SELECT name FROM world WHERE population >= 200000000",
    3 : "SELECT name, gdp/population FROM world WHERE population > 200000000",
    4 : "SELECT name, population/1000000 FROM world WHERE continent = 'South America'",
    5 : "SELECT name, population FROM world WHERE name = 'France' OR name = 'Germany' OR name = 'Italy'",
    6 : "SELECT name FROM world WHERE name LIKE '%United%'",
    7 : "SELECT name, population, area FROM world WHERE area > 3000000 OR population > 250000000",
    8 : "SELECT name, population, area FROM world WHERE area > 3000000 XOR population > 250000000",
    9 : "SELECT name, ROUND(population/1000000,2), ROUND(gdp/1000000000,2) FROM world WHERE continent = 'South America'",
    10 : "SELECT name, ROUND(gdp/population,-3) FROM world WHERE gdp >= 1000000000000 ",
    11 : "SELECT name, LENGTH(name), continent, LENGTH(continent), capital, LENGTH(capital) FROM world WHERE name LIKE 'G%'",
    12 : "SELECT name, capital FROM world WHERE LEFT(name,1) = LEFT(capital,1) AND name <> capital",
    13 : "SELECT name FROM world WHERE name LIKE '%a%' AND name LIKE '%e%' AND name LIKE '%i%' AND name LIKE '%o%' AND name LIKE '%u%' AND name NOT LIKE '% %'"
}

nobelDict = {
    1 : "SELECT yr, subject, winner FROM nobel WHERE yr = 1950",
    2 : "SELECT winner FROM nobel WHERE yr = 1962 AND subject = 'Literature'",
    3 : "SELECT yr, subject FROM nobel WHERE winner = 'Albert Einstein'",
    4 : "SELECT winner FROM nobel WHERE subject = 'Peace' AND yr >= 2000",
    5 : "SELECT yr, subject, winner FROM nobel WHERE subject = 'Literature' AND yr >= 1980 AND yr <= 1989",
    6 : "SELECT * FROM nobel WHERE winner = 'Theodore Roosevelt' OR winner = 'Woodrow Wilson' OR winner = 'Jimmy Carter' OR winner = 'Barack Obama'",
    7 : "SELECT winner FROM nobel WHERE winner LIKE 'John%'",
    8 : "SELECT yr, subject, winner FROM nobel WHERE yr = 1980 AND subject = 'Physics' OR yr = 1984 AND subject = 'Chemistry'",
    9 : "SELECT yr, subject, winner FROM nobel WHERE yr = 1980 AND subject <> 'Chemistry' AND subject <> 'Medicine'",
    10 : "SELECT yr, subject, winner FROM nobel WHERE yr < 1910 AND subject = 'Medicine' OR yr >= 2004 AND subject = 'Literature'",
    11 : "SELECT * FROM nobel WHERE winner = 'PETER GRÜNBERG'",
    12 : "SELECT * FROM nobel WHERE winner = 'EUGENE O''NEILL'",
    13 : "SELECT winner, yr, subject FROM nobel WHERE LEFT(winner,3) = 'Sir' ORDER BY yr desc, winner",
    14 : "SELECT winner, subject FROM nobel WHERE yr=1984 ORDER BY subject IN ('Physics','Chemistry'),subject,winner"
}

withinDict = {
    1 : "SELECT name FROM world WHERE population > (SELECT population FROM world WHERE name='Russia')",
    2 : "SELECT name FROM world WHERE continent = 'Europe' AND gdp/population > (SELECT gdp/population FROM world WHERE name = 'United Kingdom')",
    3 : "SELECT name, continent FROM world WHERE continent = (SELECT continent FROM world WHERE name = 'Argentina') OR continent =  (SELECT continent FROM world WHERE name = 'Australia') ORDER BY name",
    4 : "SELECT name, population FROM world WHERE population > (SELECT population FROM world WHERE name = 'Canada') AND population < (SELECT population FROM world WHERE name = 'Poland')",
    5 : "SELECT name, CONCAT(ROUND(100*population/(SELECT population FROM world WHERE name='Germany')),'%') FROM world WHERE continent = 'Europe'",
    6 : "SELECT name FROM world x WHERE x.gdp > ALL(SELECT gdp FROM world y WHERE y.continent = 'Europe' AND y.gdp IS NOT NULL) AND x.continent <> 'Europe'",
    7 : "SELECT continent, name, area FROM world x WHERE area >= ALL (SELECT area FROM world y WHERE y.continent=x.continent)",
    8 : "SELECT continent, name FROM world x WHERE name =  (SELECT name FROM world WHERE continent = x.continent ORDER BY continent, name LIMIT 1)",
    9 : "SELECT name, continent, population FROM world x WHERE 25000000 >= ALL(SELECT population FROM world WHERE continent = x.continent AND population > 0) ",
    10 : "SELECT name, continent FROM world x WHERE population/3 >= ALL (SELECT MAX(population) FROM world WHERE continent = x.continent AND name <> x.name)"
}

aggregateDict={
    1 : "SELECT SUM(population) FROM world",
    2 : "SELECT DISTINCT continent FROM world",
    3 : "SELECT SUM(gdp) FROM world WHERE continent = 'Africa'",
    4 : "SELECT COUNT(name) FROM world WHERE area > 1000000",
    5 : "SELECT SUM(population) FROM world WHERE name = 'Estonia' OR name = 'Latvia' OR name = 'Lithuania'",
    6 : "SELECT continent, COUNT(name) FROM world GROUP BY continent ",
    7 : "SELECT continent, COUNT(name) FROM world WHERE population >= 10000000 GROUP BY continent",
    8 : "SELECT continent FROM world GROUP BY continent HAVING SUM(population) >= 100000000"
}
joinDict = {
    1 : "SELECT matchid, player FROM goal WHERE teamid = 'GER'",
    2 : "SELECT id,stadium,team1,team2 FROM game WHERE id = 1012",
    3 : "SELECT player,teamid,stadium,mdate FROM game JOIN goal ON (id=matchid) WHERE teamid = 'GER' ",
    4 : "SELECT team1, team2, player FROM game JOIN goal ON (id = matchid) WHERE player LIKE 'Mario%'",
    5 : "SELECT player, teamid, coach, gtime FROM goal JOIN eteam ON (teamid = id) WHERE gtime<=10",
    6 : "SELECT mdate, teamname FROM game JOIN eteam ON (team1 = eteam.id) WHERE coach = 'Fernando Santos'",
    7 : "SELECT player FROM game JOIN goal ON (id = matchid) WHERE stadium = 'National Stadium, Warsaw'",
    8 : "SELECT DISTINCT player FROM game JOIN goal ON matchid = id WHERE (team1='GER' OR team2='GER') AND teamid <> 'GER'",
    9 : "SELECT teamname, COUNT(player) FROM eteam JOIN goal ON id=teamid GROUP BY teamname",
    10 : "SELECT stadium, COUNT(player) FROM game JOIN goal ON (id = matchid) GROUP BY stadium",
    11 : "SELECT matchid,mdate, COUNT(player) FROM game JOIN goal ON id = matchid WHERE (team1 = 'POL' OR team2 = 'POL') GROUP BY matchid,mdate",
    12 : "SELECT matchid,mdate, COUNT(player) FROM game JOIN goal ON id = matchid WHERE (teamid = 'GER') GROUP BY matchid,mdate",
    13 : """SELECT mdate,
team1,
  SUM(CASE WHEN teamid=team1 THEN 1 ELSE 0 END) score1,
team2,
SUM(CASE WHEN teamid=team2 THEN 1 ELSE 0 END) score2
  FROM game LEFT JOIN goal ON matchid = id GROUP BY mdate,id, team1, team2 ORDER BY mdate,id,team1,team2"""
}

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

@app.get("/",response_class=HTMLResponse)
async def root():
    html = """
    <html>
        <body>
            <h1>Assignment 4 API</h1>
            <h3>Daniel Bowen</h3>
            </br>
            <div>
                <p>
                    <a href="http://143.198.60.31:8001/docs">API Swagger</a>
                </p>
            </div>
        </body>
    </html>
    """
    return html

@app.get("/basics")
async def basics():
    result = {}
    for key in basicsDict:
        keyResult = mysqlCnx.query('world',basicsDict[key],'select')
        result[key] = keyResult
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/basics/{id}")
async def basics(id:int):
    jsonResult = jsonable_encoder(mysqlCnx.query('world',basicsDict[id],'select'))
    return JSONResponse(content = jsonResult)

@app.get("/world")
async def world():
    result = {}
    for key in worldDict:
        keyResult = mysqlCnx.query('world',worldDict[key],'select')
        result[key] = keyResult
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/world/{id}")
async def world(id:int):
    jsonResult = jsonable_encoder(mysqlCnx.query('world',worldDict[id],'select'))
    return JSONResponse(content = jsonResult)

@app.get("/nobel")
async def nobel():
    result = {}
    for key in nobelDict:
        keyResult = mysqlCnx.query('nobel',nobelDict[key],'select')
        result[key] = keyResult
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/nobel/{id}")
async def nobel(id:int):
    jsonResult = jsonable_encoder(mysqlCnx.query('nobel',nobelDict[id],'select'))
    return JSONResponse(content = jsonResult)

@app.get("/within")
async def within():
    result = {}
    for key in withinDict:
        keyResult = mysqlCnx.query('world',withinDict[key],'select')
        result[key] = keyResult
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/within/{id}")
async def within(id:int):
    jsonResult = jsonable_encoder(mysqlCnx.query('world',withinDict[id],'select'))
    return JSONResponse(content = jsonResult)

@app.get("/aggregate")
async def aggregate():
    result = {}
    for key in aggregateDict:
        keyResult = mysqlCnx.query('world',aggregateDict[key],'select')
        result[key] = keyResult
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/aggregate/{id}")
async def aggregate(id:int):
    jsonResult = jsonable_encoder(mysqlCnx.query('world',aggregateDict[id],'select'))
    return JSONResponse(content = jsonResult)

@app.get("/join")
async def join():
    result = {}
    for key in joinDict:
        keyResult = mysqlCnx.query('euro2012',joinDict[key],'select')
        result[key] = keyResult
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/join/{id}")
async def join(id:int):
    jsonResult = jsonable_encoder(mysqlCnx.query('euro2012',joinDict[id],'select'))
    return JSONResponse(content = jsonResult)

@app.get("/all")
async def all():
    result = {}
    result["basics"] = {}
    for key in basicsDict:
        keyResult = mysqlCnx.query('world',basicsDict[key],'select')
        result["basics"][key] = keyResult

    result["world"] = {}
    for key in worldDict:
        keyResult = mysqlCnx.query('world',worldDict[key],'select')
        result["world"][key] = keyResult
    
    result["nobel"] = {}
    for key in nobelDict:
        keyResult = mysqlCnx.query('nobel',nobelDict[key],'select')
        result["nobel"][key] = keyResult
    
    result["within"] = {}
    for key in withinDict:
        keyResult = mysqlCnx.query('world',withinDict[key],'select')
        result["within"][key] = keyResult
    
    result["aggregate"] = {}
    for key in aggregateDict:
        keyResult = mysqlCnx.query('world',aggregateDict[key],'select')
        result["aggregate"][key] = keyResult
    
    result["join"] = {}
    for key in joinDict:
        keyResult = mysqlCnx.query('euro2012',joinDict[key],'select')
        result["join"][key] = keyResult

    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.post("/teacher")
async def teacher(item:Teacher):
    print(item.id)
    params = (item.id,item.dept,item.name,item.phone,item.mobile,)

    result = mysqlCnx.sprocQuery('teachers',params,'teacher_insert','insert')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.put("/world")
async def worldPut(item:Country):
    params = ""
    index = 0
    lastIndexed = 0
    for prop, val in vars(item).items():
        if(prop != 'name' and val != None):
            if(lastIndexed < index):
                params+=", "
            if(isinstance(val,str)):
                params+= f"{prop} = '{val}'"
            else:
                params+= f"{prop} = {val}"
            lastIndexed = index
            index+=1

    sql = f"UPDATE world SET {params} WHERE name = '{item.name}'"
    print(sql)
    result = mysqlCnx.query('world',sql,'update')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")