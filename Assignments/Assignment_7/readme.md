# Assignment 7 - School Advising (http://143.198.60.31:8004/)

## Description
#### API covers a large swathe of restaurants in the greater New York area and some beyond.

### Project Files
|   #   | File                     | Description                                                |
| :---: | ------------------------ | --------------------------------------------------------   |
|   1   | 2022_spring_schedule.json| Holds class data                                           |
|   2   | advising_form.csv        | CSV template for an end user to fill out then upload       |
|   3   | api_seed.py              | For use with a json file to seed the database with courses |
|   4   | main.py                  | Fastapi py file that holds the movie database routes       |
|   5   | models.py                | File that holds all of the models for main.py.             |
|   6   | mysqlCnx.py              | File that holds the database query information and methods |

### API Routes

|   #   | Route                    | Type | Model              | Description                                                         |
| :---: | -----------------------  | ---- | ------------------ | -----------------------------------------------------------------   |
|   1   | /course/{crn}            | GET  | N/A                | Returns all the information on a course by the CRN provided         |
|   2   | /course/                 | GET  | CourseGet          | Returns all courses that match the provided paremeters              |
|   3   | /course/                 | PUT  | Course             | Updates a course with the provided parameters                       |
|   4   | /course/                 | POST | Course             | Creates a new course entry in the database with provided parameters |
|   5   | /courses/all             | GET  | N/A                | Returns all courses in the database                                 |
|   6   | /courses/closed          | GET  | N/A                | Returns all courese in the database that are closed.                |
|   7   | /student/                | GET  | StudentGet         | Returns all students that match the given parameters                |
|   8   | /student/                | PUT  | Student            | Updates a student with the provided parameters                      |
|   9   | /student/                | POST | Student            | Creates a new student entry in the database with provided parameters|
|  10   | /student/all             | GET  | N/A                | Returns all students in the database                                |
|  11   | /advising_form/template  | GET  | N/A                | Returns the CSV template to the end user                            |
|  12   | /advising_form           | GET  | AdvisingFormGet    | Gets a specific advising form based on given parameters             |
|  13   | /advising_form           | POST | AdvisingForm       | Creates an advising form within the database based on parameters    |
|  14   | /advising_form/all       | GET  | N/A                | Returns all advising forms in the database                          |
|  15   | /advising_form/export/csv| GET  | AdvisingIdentifier | Ouputs a student's advising form as a csv                           |
|  16   | /advising_form/export/pdf| GET  | AdvisingIdentifier | Outputs a student's advising form as a pdf                          |
|  17   | /advising_form/upload    | POST | None: CSV File     | Processes a provided, filled out template same as the adv form post |
|  18   | /advising_form/course    | DEL  | AdvisingLink       | Deletes a course from a advising form, implicit adv form delete if no links|



