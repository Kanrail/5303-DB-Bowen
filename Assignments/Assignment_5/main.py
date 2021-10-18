import mysqlCnx
import json
import uvicorn
from models import *

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse

app = FastAPI()

#query(database,sql,returnType):

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

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

@app.get("/",response_class=HTMLResponse)
async def root():
    html = """
    <html>
        <body>
            <h1>Assignment 5 API</h1>
            <h3>Daniel Bowen</h3>
            </br>
            <div>
                <p>
                    <a href="http://143.198.60.31:8002/docs">API Swagger</a>
                </p>
            </div>
        </body>
    </html>
    """
    return html

@app.get("/movies/all")
async def getAllMovies(item:Limit):
    try:
        rowcount = item.rowcount if item.rowcount < 10000 else 10000
    except:
        rowcount = 25
    try:
        offset = item.offset if item.offset != None else 0
    except:
        offset = 0

    sql = f"""
    SELECT id,primaryTitle,releaseDate,runtimeMinutes,isAdult,
            a.avgRating, a.numVotes,
            GROUP_CONCAT(DISTINCT g.genre SEPARATOR ', ') as 'genres'
    FROM `movies`
        LEFT OUTER JOIN ratings AS a ON id = a.movieId
        LEFT OUTER JOIN moviegenres AS g ON id = g.movieId
    GROUP BY id,primaryTitle,releaseDate,runtimeMinutes,isAdult,
            a.avgRating, a.numVotes
    LIMIT {rowcount} OFFSET {offset}
    """

    result = mysqlCnx.query('imdb',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/movies")
async def getMovies(item:Movie):
    try:
        rowcount = item.limit.rowcount if item.limit.rowcount < 10000 else 10000
    except:
        rowcount = 25
    try:
        offset = item.limit.offset if item.limit.offset != None else 0
    except:
        offset = 0

    orderby = item.orderby
    orderbysql = ""
    if orderby != None:
        orderbysql += "ORDER BY "
        for o in orderby:
            orderbysql += o.col.name + " " + o.order.name + " , " 
        orderbysql = orderbysql[:-2]
    sql = """
    SELECT DISTINCT id,primaryTitle,releaseDate,runtimeMinutes,isAdult,
            a.avgRating, a.numVotes,
            GROUP_CONCAT(DISTINCT genres.genre SEPARATOR ', ') as 'genres'
    FROM `movies`
        LEFT OUTER JOIN ratings AS a ON id = a.movieId
        LEFT OUTER JOIN role AS actor ON id = actor.movieId
        LEFT OUTER JOIN directors AS director ON id = director.movieId
        LEFT OUTER JOIN moviegenres AS genres ON id = genres.movieId
    """
    groupby = """
        GROUP BY id,primaryTitle,releaseDate,runtimeMinutes,isAdult,
            a.avgRating, a.numVotes
    """
    limit = f"LIMIT {rowcount} OFFSET {offset}"
    whereQuery = "WHERE "
    numWhereQueries = 0
    numAnds = 0
    ids = item.ids
    if ids != None:
        numWhereQueries += 1
        idQuery = "("
        for movieId in ids:
            idQuery += f"id = '{movieId}'"
            idQuery += " OR "
        idQuery = idQuery[:-4]
        whereQuery += idquery + ") "
        
    titles = item.titles
    if titles != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        titleQuery = "("
        for title in titles:
            titleQuery += f"primaryTitle = '{title}'"
            titleQuery += " OR "
        titleQuery = titleQuery[:-4]
        whereQuery += titleQuery + ") "
    
    releaseDates = item.releasedates
    if releaseDates != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        releaseDateQuery = "("
        for date in releaseDates:
            releaseDateQuery += f"releaseDate = {date}"
            releaseDateQuery += " OR "
        releaseDateQuery = releaseDateQuery[:-4]
        whereQuery += releaseDateQuery + ") "
    try:
        releaseDateComp = item.releasedate
        if releaseDateComp != None:
            val1 = releaseDateComp.valuea
            operator = releaseDateComp.operator
            numWhereQueries += 1
            if(numWhereQueries - 1 != numAnds):
                whereQuery += " AND "
                numAnds += 1

            releaseDateQuery = "("
            try:#if two release date values have been passed in
                val2 = releaseDateComp.valueb
                if val2 != None:
                    ops = comp2Vals(operator)
                    releaseDateQuery += f"releaseDate {ops[0]} {val1} AND releaseDate {ops[1]} {val2}"
                else:
                    raise ValueError("Second value not present")
            except:#if doing a single release date comparison
                op = compVal(operator)
                releaseDateQuery += f"releaseDate {op} {val1}"
            whereQuery += releaseDateQuery + ") "
    except:
        pass
    try:
        runtime = item.runtime
        if runtime != None:
            val1 = runtime.valuea
            operator = runtime.operator
            numWhereQueries += 1
            if(numWhereQueries - 1 != numAnds):
                whereQuery += " AND "
                numAnds += 1

            runtimeQuery = "("
            try:#if two release date values have been passed in
                val2 = runtime.valueb
                if val2 != None:
                    ops = comp2Vals(operator)
                    runtimeQuery += f"runtimeMinutes {ops[0]} {val1} AND runtimeMinutes {ops[1]} {val2}"
                else:
                    raise ValueError("Second value not present")
            except:#if doing a single release date comparison
                op = compVal(operator)
                runtimeQuery += f"runtimeMinutes {op} {val1}"
            whereQuery += runtimeQuery + ") "
    except:
        pass
    try:
        rating = item.rating
        if rating != None:
            val1 = rating.valuea
            operator = rating.operator
            numWhereQueries += 1
            if(numWhereQueries - 1 != numAnds):
                whereQuery += " AND "
                numAnds += 1

            ratingQuery = "("
            try:#if two release date values have been passed in
                val2 = rating.valueb
                if val2 != None:
                    ops = comp2Vals(operator)
                    ratingQuery += f"a.avgRating {ops[0]} {val1} AND a.avgRating {ops[1]} {val2}"
                else:
                    raise ValueError("Second value not present")
            except:#if doing a single release date comparison
                op = compVal(operator)
                ratingQuery += f"a.avgRating {op} {val1}"
            whereQuery += ratingQuery + ") "
    except:
        pass
    isadult = item.isadult
    if isadult != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        
        isadultVal = 0 if isadult == False else 1
        whereQuery += f"(isAdult = {isadultVal}) "
    actors = item.actors
    if actors != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        actorsQuery = "("
        for actor in actors:
            actorsQuery += f"actor.actorId = '{actor}'"
            actorsQuery += " OR "
        actorsQuery = actorsQuery[:-4]
        whereQuery += actorsQuery + ") "
    directors = item.directors
    if directors != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        directorsQuery = "("
        for director in directors:
            directorsQuery += f"director.directorId = '{director}'"
            directorsQuery += " OR "
        directorsQuery = directorsQuery[:-4]
        whereQuery += directorsQuery + ") "
    genres = item.genres
    if genres != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        genresQuery = "("
        for genre in genres:
            genresQuery += f"genres.genre = '{genre}'"
            genresQuery += " OR "
        genresQuery = genresQuery[:-4]
        whereQuery += genresQuery + ") "

    if whereQuery == "WHERE ":
        whereQuery = ""
    sql += whereQuery + groupby + orderbysql + limit
    result = mysqlCnx.query('imdb',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/genres")
def getGenres():
    sql = f"""
    SELECT *
    FROM `genres`
    """

    result = mysqlCnx.query('imdb',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/professions")
def getProfessions():
    sql = f"""
    SELECT *
    FROM `professions`
    """

    result = mysqlCnx.query('imdb',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/people/all")
def getAllPeople(item:Limit):
    try:
        rowcount = item.rowcount if item.rowcount < 10000 else 10000
    except:
        rowcount = 25
    try:
        offset = item.offset if item.offset != None else 0
    except:
        offset = 0

    sql = f"""
    SELECT id, firstname, lastname, birthyear, deathyear,
            GROUP_CONCAT(DISTINCT a.profession SEPARATOR ', ') as 'professions'
    FROM `person`
        LEFT OUTER JOIN personprofessions AS a ON id = a.personId
    GROUP BY id,firstname,lastname,birthyear,deathyear
    LIMIT {rowcount} OFFSET {offset}
    """

    result = mysqlCnx.query('imdb',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

@app.get("/people")
def getPeople(item:Person):
    try:
        rowcount = item.limit.rowcount if item.limit.rowcount < 10000 else 10000
    except:
        rowcount = 25
    try:
        offset = item.limit.offset if item.limit.offset != None else 0
    except:
        offset = 0

    sql = f"""
    SELECT id, firstname, lastname, birthyear, deathyear,
            GROUP_CONCAT(DISTINCT a.profession SEPARATOR ', ') as 'professions'
    FROM `person`
        LEFT OUTER JOIN personprofessions AS a ON id = a.personId
        LEFT OUTER JOIN role AS r ON id = r.actorId
        LEFT OUTER JOIN directors AS d ON id = d.directorId
    """
    orderby = item.orderby
    orderbysql = ""
    if orderby != None:
        orderbysql += "ORDER BY "
        for o in orderby:
            orderbysql += o.col.name + " " + o.order.name + " , " 
        orderbysql = orderbysql[:-2]
    groupby = " GROUP BY id,firstname,lastname,birthyear,deathyear "
    limit = f" LIMIT {rowcount} OFFSET {offset} "

    whereQuery = "WHERE "
    numWhereQueries = 0
    numAnds = 0

    ids = item.ids
    if ids != None:
        numWhereQueries += 1
        idQuery = "("
        for personId in ids:
            idQuery += f"id = '{personId}'"
            idQuery += " OR "
        idQuery = idQuery[:-4]
        whereQuery += idquery + ") "

    firstnames = item.firstnames
    if firstnames != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        fnameQuery = "("
        for fname in firstnames:
            fnameQuery += f"firstname = '{fname}'"
            fnameQuery += " OR "
        fnameQuery = fnameQuery[:-4]
        whereQuery += fnameQuery + ") "

    lastnames = item.lastnames
    if lastnames != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        lnameQuery = "("
        for lname in lastnames:
            lnameQuery += f"lastname = '{lname}'"
            lnameQuery += " OR "
        lnameQuery = lnameQuery[:-4]
        whereQuery += lnameQuery + ") "
        
    birthyears = item.birthyears
    if birthyears != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        birthyearQuery = "("
        for date in birthyears:
            birthyearQuery += f"birthyear = {date}"
            birthyearQuery += " OR "
        birthyearQuery = birthyearQuery[:-4]
        whereQuery += birthyearQuery + ") "

    try:
        birthyearComp = item.birthyear
        if birthyearComp != None:
            val1 = birthyearComp.valuea
            operator = birthyearComp.operator
            numWhereQueries += 1
            if(numWhereQueries - 1 != numAnds):
                whereQuery += " AND "
                numAnds += 1

            birthyearQuery = "("
            try:#if two release date values have been passed in
                val2 = birthyearComp.valueb
                if val2 != None:
                    ops = comp2Vals(operator)
                    birthyearQuery += f"birthyear {ops[0]} {val1} AND birthyear {ops[1]} {val2}"
                else:
                    raise ValueError("Second value not present")
            except:#if doing a single release date comparison
                op = compVal(operator)
                birthyearQuery += f"birthyear {op} {val1}"
            whereQuery += birthyearQuery + ") "
    except:
        pass

    deathyears = item.deathyears
    if deathyears != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        deathyearQuery = "("
        for date in deathyears:
            deathyearQuery += f"deathyear = {date}"
            deathyearQuery += " OR "
        deathyearQuery = deathyearQuery[:-4]
        whereQuery += deathyearQuery + ") "

    try:
        deathyearComp = item.birthyear
        if deathyearComp != None:
            val1 = deathyearComp.valuea
            operator = deathyearComp.operator
            numWhereQueries += 1
            if(numWhereQueries - 1 != numAnds):
                whereQuery += " AND "
                numAnds += 1

            deathyearQuery = "("
            try:#if two release date values have been passed in
                val2 = deathyearComp.valueb
                if val2 != None:
                    ops = comp2Vals(operator)
                    deathyearQuery += f"deathyear {ops[0]} {val1} AND deathyear {ops[1]} {val2}"
                else:
                    raise ValueError("Second value not present")
            except:#if doing a single release date comparison
                op = compVal(operator)
                deathyearQuery += f"deathyear {op} {val1}"
            whereQuery += deathyearQuery + ") "
    except:
        pass

    #NEEDS WORK
    genres = item.genres
    if genres != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        genresQuery = "("
        for genre in genres:
            genresQuery += f"g.genre = '{genre}'"
            genresQuery += " OR "
        genresQuery = genresQuery[:-4]
        whereQuery += genresQuery + ") "

    #NEEDS WORK
    workedwith = item.workedwithids
    if workedwith != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        wwQuery = "("
        for ww in workedwith:
            wwQuery += f"r.movieId = ('{ww}')"
            wwQuery += " OR "
        wwQuery = wwQuery[:-4]
        whereQuery += wwQuery + ") "

    professions = item.professions
    if professions != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        professionsQuery = "("
        for profession in professions:
            professionsQuery += f"a.profession = '{profession}'"
            professionsQuery += " OR "
        professionsQuery = professionsQuery[:-4]
        whereQuery += professionsQuery + ") "

    movie = item.movie
    if movie != None:
        numWhereQueries += 1
        if(numWhereQueries - 1 != numAnds):
            whereQuery += " AND "
            numAnds += 1
        movieQuery = f"(r.movieId = '{movie}' OR d.movieId = '{movie}') "
        whereQuery += movieQuery


    if whereQuery == "WHERE ":
        whereQuery = ""
    sql += whereQuery + groupby + orderbysql + limit

    result = mysqlCnx.query('imdb',sql,'select')
    jsonResult = jsonable_encoder(result)
    return JSONResponse(content = jsonResult)

#if __name__ == "__main__":
    #uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")