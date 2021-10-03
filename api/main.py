from datetime import datetime, timedelta, date
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import csv
import json
from database import SessionLocal, engine
from models import Student, House, User, Token, TokenData, PointLogs, UselessModel
import asyncio
from websockets.protocol import State
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from secret import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, origins, hiddenFlag

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

houses_name = {
    "Slytherin",
    "Hufflepuff",
    "Ravenclaw"
    "Gryffindor",
}

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str, user: User):
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ) 
    user = db.query(User).filter_by(username=token_data.username)
    if user is None:
        raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_db = db.query(User).filter_by(username=form_data.username).first()
    user = authenticate_user(form_data.username, form_data.password, user_db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

@app.post('/api/students/import')
async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="User not allowed")
    nb_added = 0
    csv_entry = file.file.read().decode().split('\r\n')
    csv_list = [tuple(n.split(',')) for n in csv_entry]
    for entry in csv_list:
        if not db.query(Student).filter_by(name=entry[0]).first():
            student = Student(name=entry[0], house_id=int(entry[1]), points=0)
            db.add(student)
            nb_added += 1
    db.commit()
    if nb_added == 0:
        return JSONResponse(content={'data': f'Added {nb_added} listed students (all of them are already in db)'})
    return JSONResponse(content={'data': f'Added {nb_added} listed students'})
    
@app.get('/api/houses')
@limiter.limit("5/minute")
async def house_point(request: Request,db: Session = Depends(get_db)):
    houses = db.query(House).all()
    if not houses:
        raise HTTPException(
            status_code=404,
            detail="Houses not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = {
        "Slytherin": houses[0].points,
        "Hufflepuff": houses[1].points,
        "Ravenclaw": houses[2].points,
        "Gryffindor": houses[3].points,
    }
    return JSONResponse(content=result)

@app.get('/api/students')
async def all_students(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="User not allowed")
    student = db.query(Student).all()
    if not student:
        raise HTTPException(status_code=404, detail='No students')
    student_list = [{"name": elem.name, "id": elem.id, "points": elem.points, "house": elem.house_id} for elem in student]
    return JSONResponse(content=student_list)

@app.get('/api/student/{student_id}')
async def student_points(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="User not allowed")
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        house = db.query(House).filter_by(id=student.house_id).first()
    except:
        raise HTTPException(status_code=404, detail='cannot find specified student')
    return JSONResponse(content={"student_id": student_id, "points": student.points, "house": house.name})

@app.get('/api/house/{house_id}')
async def house_points(house_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="User not allowed")
    try:
        house = db.query(House).filter_by(id=house_id).first()
    except:
        raise HTTPException(status_code=404, detail='cannot find specified house')
    return JSONResponse(content={"house": house.name, "points": house.points})

@app.put('/api/student/{student_id}/{points}')
async def add_student_points(student_id: int, points, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), reason: Optional[str] = ""):
    if not current_user:
        raise HTTPException(status_code=401, detail="User not allowed")
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not points.lstrip('-').isdigit():
        raise HTTPException(status_code=400, detail='Points must have a numerical value') 
    student.points += int(points)
    try:
        house = db.query(House).filter(House.id==student.house_id).first()
        students = db.query(Student).filter_by(house_id=house.id).all()
    except:
        raise HTTPException(status_code=404, detail="Student House not found")
    house_points = 0
    for stud in students:
        house_points += stud.points 
    house.points = house_points
    pts_log = PointLogs(student_name=student.name, student_points=points, date_time=datetime.now(), reason=reason)
    db.add(pts_log)
    db.commit()
    return JSONResponse(content={"student": student.name, "house": {"id": house.id ,"name": house.name, "points": house.points}})

@app.get('/api/students/logs')
async def get_student_log(db: Session = Depends(get_db)):
    student_log = db.query(PointLogs).filter(
        func.date(PointLogs.date_time) == date.today()
    ).all()
    json_student_log = [{'id': elem.id, 'house': db.query(Student).filter_by(name=elem.student_name).first().house_id, 'name': elem.student_name, 'points': elem.student_points, 'reason': elem.reason} for elem in student_log]
    if not json_student_log:
        raise HTTPException(status_code=404, detail="no student log for today")
    return JSONResponse(content=json_student_log)

class UselessBody(BaseModel):
    canWork: bool

@app.get('/api/hidden/secret/route')
@limiter.limit("5/minute")
async def hidden_secret_route(request: Request, body: UselessBody, db:Session = Depends(get_db)):
    useless = db.query(UselessModel).first()
    if body.canWork == True and useless.hasBeenPingued == False:
        useless.hasBeenPingued = True
        db.commit()
        return JSONResponse(content={'data': 'Come see an APE with the flag and open the chamber of secrets !', 'flag': hiddenFlag})
    return JSONResponse(content={'data': 'Nothing to do here :)'})
    