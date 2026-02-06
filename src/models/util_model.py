from enum import Enum
from pydantic import BaseModel

class Emp_Type(str, Enum):
    part_time: "part_time"
    full_time: "full_time"

class Loc_Type(str, Enum):
    remote: "remote"
    onsite: "onsite"

class Salary(BaseModel):
    min_salary: float
    max_salary: float
    