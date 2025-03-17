from sqlalchemy.orm import Session
from user_model import User
from utils.request_payload import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.username,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_name: str):
    return db.query(User).filter(User.full_name == user_name).first()

def get_users(db: Session):
    return db.query(User).all()

def update_user(db: Session, user_name: str, user: UserCreate):
    db_user = db.query(User).filter(User.full_name == user_name).first()
    if db_user:
        db_user.full_name = user.username
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_name: str):
    db_user = db.query(User).filter(User.full_name == user_name).first()
    if db_user:
        db.delete(db_user)
        db.commit()
