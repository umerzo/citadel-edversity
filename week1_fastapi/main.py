from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


app = FastAPI(
    title ="Student Management API",
    description ="fully typed REST API for student management",
    version="1.0.0"
)

#creating a pydantic schema / data model

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Full Name")
    age: int = Field(..., ge=5, le=100, description="age must be between 5 and 100")
    course: str = Field(..., description="The course the student is enrolled in")
    email: str = Field(..., description="Student email ID")
    grade: Optional[float] = Field(None, ge=0.0, le=100.0, description="Grade out of 100")
 

class StudentUpdate(BaseModel):
    name : Optional[str] = Field(None, min_length=2, max_length=50)
    age : Optional[int] = Field(None, ge=5, le=50)
    course : Optional[str] = None
    email : Optional[str] = None
    grade : Optional[float] = Field(None, ge=0.0, le=100.0)

class Student(BaseModel):
    
    id:int
    name:str
    age:int
    course:str
    email: str
    grade: Optional[float] = None


#3 0here we will store data in python dictionary!

students_db: Dict[int, Student]={}
student_id_counter: int=1


#4get/read all students 

@app.get("/students", response_model=List[Student],tags=["Students"])
def get_all_students():
    return list(students_db.values())

#5 read one student by id
@app.get("/students/{student_id}", response_model=Student, tags=["Students"])
def get_students(student_id: int):
    if student_id not in students_db:
        

        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found!")
    return students_db[student_id]



#6 creating a new student
@app.post("/students", response_model=Student, status_code=201, tags=["Students"])

def create_student(student: StudentCreate):
    global student_id_counter
    new_student = Student(id= student_id_counter, **student.model_dump())

    students_db[student_id_counter]=new_student
    student_id_counter +=1
    return new_student

#update existing student PUT

@app.put("/students/{student_id}", response_model=Student, tags=["Students"])
def update_students(student_id:int, student_update: StudentUpdate):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail=f"Student{student_id} not found!")
    
    existing_student = students_db[student_id]

    update_data= student_update.model_dump(exclude_unset=True)
    updated_students = existing_student.model_copy(update=update_data)
    students_db[student_id]= updated_students

    return updated_students

#delete student
@app.delete("/students/{student_id}", tags=["Students"])
def delete_student(student_id: int):

    if student_id not in students_db:
        raise HTTPException(status_code=404, detail=f"Student {student_id} Not found in the record!")

    deleted_student= students_db.pop(student_id)

    return{
        "message" : f"Student '{deleted_student}' deleted successfully",
        "success" : True

    }
#adding root and health check endpoints

@app.get("/", tags=["General"])
def root():
    return{
        "message" : "this management api is running",
        "docs"   : "visit /docs for Swagger UI",
        "total_students": len(students_db)

    }

@app.get("/health", tags=["General"])
def health_check():
    return {
        "status" : "healthy",
        "total_students" : len(students_db)
    }
    



