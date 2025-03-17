from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils.request_payload import UserCreate
from utils.user_curd import create_user, get_user, get_users, update_user, delete_user
from utils.logging_utils import setup_logging

logger = setup_logging()

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create_user")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/list_users")
def list_users(db: Session = Depends(get_db)):
    return get_users(db)

@router.get("/get_user_by_name/{user_name}")
def read_user(user_name: str, db: Session = Depends(get_db)):
    user = get_user(db, user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/modify_user/{user_name}")
def modify_user(user_name: str, user: UserCreate, db: Session = Depends(get_db)):
    return update_user(db, user_name, user)

@router.delete("/remove_user/{user_name}")
def remove_user(user_name: str, db: Session = Depends(get_db)):
    delete_user(db, user_name)
    return {"message": "User deleted successfully"}