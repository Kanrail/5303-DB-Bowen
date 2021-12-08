import pymongo
from pymongo import GEO2D,MongoClient
from bson.json_util import dumps
from bson.son import SON

# connect to mongodb
cnx = pymongo.MongoClient("mongodb://localhost:27017/")
# use businessData
mongoDB = cnx["businessData"]
# choose collection
mongoColl = mongoDB['experiment']

def EmptyCollection():
    mongoColl.delete_many({})
