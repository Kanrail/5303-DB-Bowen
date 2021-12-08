# Assignment 8 - Database Performance Comparison Experiment

## Description
#### This program compares Mongo, Redis, and MySQL on performance for insertions, searches, updates, and deletions for 3 object types: strings, integers, and complex json objects.

## Instructions
#### In main.py, at the top of the main function, the variable N denotes the number of values to be used, NOffset denotes the step period between. The when run, it'll start at the lowest offset, then work its way up to one offset below N. (e.g. if you want it to go from 500-5000, N = 5500 and NOffset = 500)

### Project Files
|   #   | File            | Description                                                              |
| :---: | --------------- | -------------------------------------------------------------------------|
|   1   | main.py         | Main file that holds the all of the search calls and file printing       |
|   1   | myPyMongo.py    | Holds the Mongo database connection strings and includes.                |
|   1   | myRedis.py      | Holds the Redis database connection strings and includes.                |
|   1   | mysqlCnx.py     | Holds the MySQL database connection strings, includes, and methods.      |
|   1   | output.csv      | A CSV output of the run of main.py that can then be used to create graphs|



## Experiment Results
### Inserts
