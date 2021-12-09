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

class Operator(str,Enum):
    equals = "equals"
    greater_than = "greater_than"
    greater_than_or_equal_to = "greater_than_or_equal_to"
    less_than = "less_than"
    less_than_or_equal_to = "less_than_or_equal_to"
    not_equals = "not_equals"

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

class CompareDec(BaseModel):
    valuea : Decimal
    operator : Operator
    valueb : Optional[Decimal]

class BetweenValues(BaseModel):
    startTime : constr(max_length=10)
    endTime : constr(max_length=10)

class Course(BaseModel):
    crn : int
    college : constr(max_length=6)
    subject : constr(max_length=6)
    courseNumber : int
    section : constr(max_length=6)
    title : constr(max_length=80)
    primaryInstructor : constr(max_length=80)
    maxNumber : int
    currentlyEnrolled : int
    days : constr(max_length=10)
    startTime : constr(max_length=10)
    endTime : constr(max_length=10)
    building : constr(max_length=6)
    room : constr(max_length=6)

class Courses(BaseModel):
    courses : List[Course]

class CourseGet(BaseModel):
    crn : Optional[int]
    subject : Optional[constr(max_length=6)] 
    courseNumber : Optional[int]  
    title : Optional[constr(max_length=80)]  
    primaryInstructor : Optional[constr(max_length=80)]  
    building : Optional[constr(max_length=6)]  
    room : Optional[constr(max_length=6)] 
    betweenTimes : Optional[BetweenValues] 

class Student(BaseModel):
    firstName : constr(max_length=40)
    lastName : constr(max_length=40)
    mNumber : constr(max_length=15)
    classification : constr(max_length=20)
    email : constr(max_length=40)
    gpa : Optional[Decimal]
    githubUserName : Optional[constr(max_length=20)]

class Students(BaseModel):
    students : List[Student]

class StudentGet(BaseModel):
    firstName : Optional[constr(max_length=40)]
    lastName : Optional[constr(max_length=40)]
    mNumber : Optional[constr(max_length=15)]
    gpa : Optional[CompareDec]

class AdvisingIdentifier(BaseModel):
    studentMNumber : constr(max_length=15)
    semester : constr(max_length=10)
    year : int

class AdvisingForm(AdvisingIdentifier):
    courseCRNs : List[int]

class AdvisingFormGet(BaseModel):
    firstName : Optional[constr(max_length=40)]
    lastName : Optional[constr(max_length=40)]
    studentMNumber : Optional[constr(max_length=15)]
    semester : Optional[constr(max_length=10)]
    year : Optional[int]

class AdvisingLink(AdvisingIdentifier):
    courseCRN : int