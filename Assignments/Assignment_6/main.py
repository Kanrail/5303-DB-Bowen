import json
from typing import Optional,List,Tuple
from decimal import Decimal
import uvicorn
import pymongo
from pymongo import GEO2D,MongoClient
import pprint
import random
from bson.json_util import dumps
from bson.son import SON

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

# connect to mongodb
cnx = pymongo.MongoClient("mongodb://localhost:27017/")
cnx2 = MongoClient("mongodb://localhost:27017/")
# use businessData
db = cnx["businessData"]
# choose collection
coll = db['restaurants']

app = FastAPI()

class Limit(BaseModel):
    rowcount : Optional[int]
    offset : Optional[int]

class Category(BaseModel):
    limit : Limit
    category : str

class Zipcode(BaseModel):
    limit : Limit
    zipcodes : List[str]

class MinRating(BaseModel):
    limit : Limit
    minrating : int

class Point(BaseModel):
    limit : Limit
    pointx : float
    pointy : float

#query(database,sql,returnType):

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

@app.get("/",response_class=HTMLResponse)
async def root():
    html = """
    <html>
        <body>
            <h1>Assignment 6 API</h1>
            <h3>Daniel Bowen</h3>
            </br>
            <div>
                <p>
                    <a href="http://143.198.60.31:8003/docs">API Swagger</a>
                </p>
            </div>
        </body>
    </html>
    """
    return html

@app.get("/restaurants")
async def getAllRestaurants(item:Limit):
    try:
        rowcount = item.rowcount if item.rowcount < 1000 else 1000
    except:
        rowcount = 25
    try:
        offset = item.offset if item.offset != None else 0
    except:
        offset = 0

    res = list(coll.find({},{'_id':0}).skip(offset).limit(rowcount))
    
    result = {"result":res,"count":len(res)}
    jsonResult = jsonable_encoder(result)
    return JSONResponse(jsonResult)

@app.get("/restaurants/categories")
async def getRestaurantCategories():
    res = list(coll.distinct('cuisine'))
    result = {"result":res,"count":len(res)}
    jsonResult = jsonable_encoder(result)
    return JSONResponse(jsonResult)

@app.get("/restaurants/category")
async def getRestaurantsByCategory(item:Category):
    try:
        rowcount = item.limit.rowcount if item.limit.rowcount < 1000 else 1000
    except:
        rowcount = 25
    try:
        offset = item.limit.offset if item.limit.offset != None else 0
    except:
        offset = 0

    res = list(coll.find({'cuisine':{"$regex":item.category,"$options":'i'}},{'_id':0}).skip(offset).limit(rowcount))

    result = {"result":res,"count":len(res)}
    jsonResult = jsonable_encoder(result)
    return JSONResponse(jsonResult)

@app.get("/restaurants/zipcodes")
async def getRestaurantsByZipcode(item:Zipcode):
    try:
        rowcount = item.limit.rowcount if item.limit.rowcount < 1000 else 1000
    except:
        rowcount = 25
    try:
        offset = item.limit.offset if item.limit.offset != None else 0
    except:
        offset = 0

    zipcodes = item.zipcodes
    print(zipcodes)
    result = {}
    if len(zipcodes) == 0:
        result = {"error":"No zipcodes passed in"}
    else:
        res = list(coll.find({'address.zipcode':{"$in":zipcodes}},{'_id':0}).skip(offset).limit(rowcount))
        result = {"result":res,"count":len(res)}

    jsonResult = jsonable_encoder(result)
    return JSONResponse(jsonResult)

@app.get("/restaurants/minrating")
async def getRestaurantsByMinRaiting(item:MinRating):
    try:
        rowcount = item.limit.rowcount if item.limit.rowcount < 1000 else 1000
    except:
        rowcount = 25
    try:
        offset = item.limit.offset if item.limit.offset != None else 0
    except:
        offset = 0

    minrating = item.minrating

    res = list(coll.find({'grades.score':{"$gt":minrating}},{'_id':0}).skip(offset).limit(rowcount))

    result = {"result":res,"count":len(res)}
    jsonResult = jsonable_encoder(result)
    return JSONResponse(jsonResult)

@app.get("/restaurants/near")
async def getRestaurantsNearPoint(item:Point):
    try:
        rowcount = item.limit.rowcount if item.limit.rowcount < 1000 else 1000
    except:
        rowcount = 25
    try:
        offset = item.limit.offset if item.limit.offset != None else 0
    except:
        offset = 0

    pointx = item.pointx
    pointy = item.pointy

    res = list(coll.find({'location':{ '$near':{'$geometry': { 'type': "Point",  'coordinates': [ pointx, pointy ] },'$minDistance': 0,'$maxDistance': 500}}},{'_id': 0}).skip(offset).limit(rowcount))

    result = {"result":res,"count":len(res)}
    jsonResult = jsonable_encoder(result)
    return JSONResponse(jsonResult)

 if __name__ == "__main__":
     uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")