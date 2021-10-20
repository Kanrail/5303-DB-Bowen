# Assignment 5 - Movies Database (http://143.198.60.31:8002/)

## IMDB database subset API
#### API covers all movies in the IMDB provided data from 1950 to present as well as
#### actors, directors, and others from the associated people data available.

### Project Files
|   #   | File            | Description                                          |
| :---: | --------------- | --------------------------------------------------   |
|   1   | main.py         | Fastapi py file that holds the movie database routes |
|   2   | models.py       | Holds all of the class objects in use by main.py     |
|   3   | mysqlCnx.py     | Handles the SQL database connection                  |

### Database Schema
![Screen Shot 2021-10-20 at 1 27 18 AM](https://user-images.githubusercontent.com/3328606/138039601-0eb225a9-4cc2-4d16-9142-cc711313c969.png)

### API Routes

|   #   | Route           | Model | Description                                                  |
| :---: | --------------- | ----- | --------------------------------------------------           |
|   1   | /movies/all     | Limit | Returns all movies in the database within the limit provided |
|   2   | /movies/        | Movie | Returns all movies that match the complex query passed       |
|   3   | /people/all     | Limit | Returns all people in the database within limit provided     |
|   4   | /people/        | Person| Returns all people that match the complex query passed.      |
|   5   | /genres/        | Limit | Returns all movie genres in the database                     |
|   6   | /professions    | Limit | Returns all professions in the database                      |


