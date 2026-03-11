from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)         
    species = Column(String)                  
    age = Column(Float)                       
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Привязка к конкретному пользователю
    owner_id = Column(Integer, ForeignKey("users.id"))