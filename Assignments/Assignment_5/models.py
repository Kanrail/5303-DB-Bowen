from typing import Optional,List
from decimal import Decimal
from enum import Enum

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

class Operator(Enum):
    equals = 0
    greater_than = 1
    greater_than_or_equal_to = 2
    less_than = 3
    less_than_or_equal_to = 4
    not_equals = 5

class MovieCol(Enum):
    id = 0
    primaryTitle = 1
    releaseDate = 2
    runtimeMinutes = 3
    isAdult = 4
    avgRating = 5
    numVotes = 6

class PersonCol(Enum):
    id = 0
    firstname = 1
    lastname = 2
    birthyear = 3
    deathyear = 4

class AscDsc(Enum):
    ASC = 0
    DESC = 1

class Limit(BaseModel):
    rowcount : Optional[int]
    offset : Optional[int]

class CompareInt(BaseModel):
    valuea : int
    operator : Operator
    valueb : Optional[int]

class MovieOrderby(BaseModel):
    col : MovieCol
    order : AscDsc

class PersonOrderby(BaseModel):
    col : PersonCol
    order : AscDsc

class Movie(BaseModel):
    limit : Limit
    orderby : Optional[List[MovieOrderby]]
    ids : Optional[List[constr(max_length=20)]]
    titles : Optional[List[constr(max_length=200)]]
    releasedates : Optional[List[int]]
    releasedate : Optional[CompareInt]
    runtime : Optional[CompareInt]
    rating : Optional[CompareInt]
    isadult : Optional[bool] 
    actors : Optional[List[constr(max_length=20)]]
    directors : Optional[List[constr(max_length=20)]]
    genres : Optional[List[constr(max_length=20)]]

class Person(BaseModel):
    limit : Limit
    orderby : Optional[List[PersonOrderby]]
    firstnames : Optional[List[constr(max_length=100)]]
    lastnames : Optional[List[constr(max_length=100)]]
    ids : Optional[List[constr(max_length=20)]]
    birthyears : Optional[List[int]]
    birthyear : Optional[CompareInt]
    deathyears : Optional[List[int]]
    deathyear : Optional[CompareInt]
    genres : Optional[List[constr(max_length=20)]]
    workedwithids : Optional[List[constr(max_length=20)]]
    professions : Optional[List[constr(max_length=40)]]
    movie : Optional[constr(max_length=20)]