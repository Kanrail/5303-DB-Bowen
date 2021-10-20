# Assignment 6 - Restaurants Database (http://143.198.60.31:8003/)

##Description
#### API covers a large swathe of restaurants in the greater New York area and some beyond.

### Project Files
|   #   | File            | Description                                          |
| :---: | --------------- | --------------------------------------------------   |
|   1   | main.py         | Fastapi py file that holds the movie database routes |

### API Routes

|   #   | Route                   | Model | Description                                                                   |
| :---: | ----------------------- | --------- | ----------------------------------------------------------------- |
|   1   | /restaurants            | Limit     | Returns all restaurants in the database within the limit provided |
|   2   | /restaurants/categories | Movie     | Returns all restaurant cuisine types                              |
|   3   | /restaurants/category   | Category  | Returns all restaurants that match a specified cuisine.           |
|   4   | /restaurants/zipcodes   | Zipcode   | Returns all restaurants within the passed zipcode                 |
|   5   | /restaurants/minrating  | MinRating | Returns all restaurants with a rating higher than specified       |
|   6   | /restaurants/near       | Point     | Returns all restaurants within 500 meters of a specified lat/long |


