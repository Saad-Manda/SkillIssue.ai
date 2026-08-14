from enum import Enum
from pydantic import BaseModel

class Emp_Type(str, Enum):
    part_time: str = "part_time"
    full_time: str =  "full_time"

class Loc_Type(str, Enum):
    remote: str = "remote"
    onsite: str =  "onsite"

class Salary(BaseModel):
    min_salary: float
    max_salary: float
    