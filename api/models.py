from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional

from database import Base


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    points = Column(Integer)
    house_id = Column(Integer, ForeignKey('house.id'))

class House(Base):
    __tablename__ = "house"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    points = Column(Integer)
    students = relationship("Student")

class PointLogs(Base):
    __tablename__ = "pointlogs"

    id = Column(Integer, primary_key=True, index=True)
    date_time = Column(Date, index=True)
    student_name = Column(String)
    student_points = Column(Integer)
    reason = Column(String)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(Base):
    __tablename__ = "user"
    username = Column(String, index=True)
    id = Column(Integer, primary_key=True, index=True)
    hashed_password = Column(String)

class UselessModel(Base):
    __tablename__ = "uselessmodel"

    id = Column(Integer, primary_key=True, index=True)
    hasBeenPingued = Column(Boolean)