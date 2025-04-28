from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid
from jose import jwt, exceptions
from datetime import datetime, timedelta

app = FastAPI()

USER_DATA_FILE = "users.json"
SECRET_KEY = "your_secret_key"  # Replace with a strong, random key!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str

class UserWithID(User):
    id: str

class Token(BaseModel):
    access_token: str
    token_type: str

def read_user_data():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def write_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    users = read_user_data()
    for user in users:
        if user["username"] == username:
            return user
    return None

@app.post("/token", response_model=Token)
async def login_for_access_token(user: User):
    user_data = get_user(user.username)
    if not user_data or user_data["password"] != user.password: #never store passwords like this.
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# ... rest of the user management code (create_user, read_user, etc.) ...