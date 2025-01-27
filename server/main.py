from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://postgres:password@localhost:5432/mydatabase"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app
app = FastAPI()

# SQLAlchemy User model
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    email = Column(String, unique=True, index=True)

# Pydantic model for API
class User(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str

    class Config:
        orm_mode = True

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def index():
    return {"message": "Hello world"}

@app.get("/user", response_model=List[User])
async def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@app.get("/user/{id}", response_model=User)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
    return user

@app.post("/user", response_model=User)
async def create_user(user: User, db: Session = Depends(get_db)):
    db_user = UserDB(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
