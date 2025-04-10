from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager

from typing import List, Final

import models
from schemas import UserCreate, UserResponse, UserUpdate, UserPatch
from pydantic import parse_obj_as

DEFAULT_MAX_RECORD_RETURN: Final = 1000
DATABASE_URL: Final = "sqlite:///dev_database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

app = FastAPI()
# @asynccontextmanager
# async def lifespan(app):
#     global db_session
#     db_session = models.Base.metadata.create_all(bind=engine)
#
# app = FastAPI(lifespan=lifespan)

# This is deprecated
@app.on_event("startup")
async def startup():
    models.Base.metadata.create_all(bind=engine)

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse(**db_user.__dict__)

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    db_record = db.query(models.User).filter(models.User.id == user_id).first()

    if db_record is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**db_record.__dict__)

# extra getter
@app.get("/users/email/{user_email}")
def get_user_by_email(user_email: str, db: Session = Depends(get_db)) -> UserResponse:
    db_record = db.query(models.User).filter(models.User.email == user_email).first()

    if db_record is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**db_record.__dict__)

# parameters example
@app.get("/users")
def get_users(limit: int = None, db: Session = Depends(get_db)) -> List[UserResponse]:
    # TODO: refactor to class
    if limit:
        db_records = db.query(models.User).limit(limit).all()
    else:
        db_records = db.query(models.User).limit(DEFAULT_MAX_RECORD_RETURN).all()

    # TODO: Figure out how to return extra data if limited
    return parse_obj_as(List[UserResponse], db_records)

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
    db_record = db.query(models.User).filter(models.User.id == user_id).first()

    if db_record is None:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump().items():
        setattr(db_record, key, value)

    db.commit()
    db.refresh(db_record)

    return UserResponse(**db_record.__dict__)

@app.patch("/users/{user_id}")
def patch_user(user_id: int, user: UserPatch, db: Session = Depends(get_db)) -> UserResponse:
    db_record = db.query(models.User).filter(models.User.id == user_id).first()

    if db_record is None:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump().items():
        if value:
            setattr(db_record, key, value)

    db.commit()
    db.refresh(db_record)

    return UserResponse(**db_record.__dict__)


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    db_record = db.query(models.User).filter(models.User.id == user_id).first()

    if db_record is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_record)
    db.commit()

    return db_record