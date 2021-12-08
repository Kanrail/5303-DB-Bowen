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
### Brief
The goal of the experiment is to compare the relative computation time in direct comparison under similar circumstances for three database solutions; MongoDB, Redis and MySQL. 
### Methods
Each database was compared on four operations (inserts, searches, updates, and deletes) as well as with three different data types (strings, integers, and complex data structures). Within each search comparison, they were compared on single searches, multiple value searches, and entire database queries.
### Setup
The program was written in python and interfaced with each database using an acquired python library. The program was ran on a Apple M1 Macbook Air.
### Results
The results were surprising with MySQL and Redis far out performing MongoDB in every category. At 5000 items, in nearly every category, Redis and MySQL were sub five seconds for completion whereas MongoDB was over 45 seconds. While MySQL came out the clear winner, there were discrepancies with the results from the string search results for MySQL that were inconsistent with other results.
### Errors
In comparing the string search method to the other methods, a discrepancy was noticed. A change had been made early on in the process to give each language the best possible scenario for making individual calls. The MySQL calls were all concatenated to one string and passed as a single query. In hindsight, this likely gave MySQL an unfair advantage in computation time as reflected in the string search results.

Also had significant difficulties translating the resulting CSV file to usable charts.
### Conclusion
On a subsequent run of this experiment, the methods should definitely be modified to remove the unfair bias that MySQL received in these results. If the string search results are anything to go by, MongoDB still likely is the slowest of the three databases, but Redis would enjoy a comfortable lead over MySQL. Also, given the difficulties in translating the resulting data to usable charts, an inclusion of a graphing library into the program would definitely have been an improvement.
