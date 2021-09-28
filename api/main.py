from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import csv
import json
from database import SessionLocal, engine
from models import Student, House, User, Token, TokenData
import asyncio
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from secret import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, origins
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

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
        raise credentials_exception
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

@app.post("/token", response_model=Token)
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
    return {"access_token": access_token, "token_type": "bearer"}

@app.post('/students/import')
async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db)):
    csv_entry = file.file.read().decode().split('\r\n')
    csv_list = [tuple(n.split(',')) for n in csv_entry]
    for entry in csv_list:
        student = Student(name=entry[0], house_id=int(entry[1]), points=0)
        db.add(student)
    db.commit()
    return {'data': 'Added all listed students'}

@app.websocket('/ws/houses')
async def websocket_house_points(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            houses = db.query(House).all()
            db.refresh(houses[0])
            db.refresh(houses[1])
            db.refresh(houses[2])
            db.refresh(houses[3])
            result = {
                "Slytherin": houses[0].points,
                "Hufflepuff": houses[1].points,
                "Ravenclaw": houses[2].points,
                "Gryffindor": houses[3].points,
            }
            print(result)
            await manager.broadcast(json.dumps(result))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get('/student/{student_id}')
async def student_points(student_id: int, db: Session = Depends(get_db)):
    # get total points and house of student_id 
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        house = db.query(House).filter_by(id=student.house_id).first()
    except:
        raise HTTPException(status_code=404, detail='cannot find specified student')
    return {"student_id": student_id, "points": student.points, "house": house.name}

@app.get('/house/{house_id}')
async def house_points(house_id: int, db: Session = Depends(get_db)):
    try:
        house = db.query(House).filter_by(id=house_id).first()
    except:
        raise HTTPException(status_code=404, detail='cannot find specified house')
    return {"house": house.name, "points": house.points}

@app.put('/student/{student_id}/{points}')
async def add_student_points(student_id: int, points, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
    db.commit()
    return {"student": student.name, "house": {"id": house.id ,"name": house.name, "points": house.points}}