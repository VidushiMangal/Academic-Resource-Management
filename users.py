from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid
import os

app = FastAPI()

USER_DATA_FILE = "users.json"

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str  # In a real app, hash this!

class UserWithID(User):
    id: str

def read_user_data():
    try:
        if not os.path.exists(USER_DATA_FILE): #check if file exists
          with open(USER_DATA_FILE, "w") as f: #create if it does not
            json.dump([], f) #dump empty list to it.
            print("New File Create")
        with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def write_user_data(data):
    try:
        if not os.path.exists(USER_DATA_FILE): #check if file exists
          with open(USER_DATA_FILE, "w") as f: #create if it does not
            json.dump([], f) #dump empty list to it.
          with open(USER_DATA_FILE, "w") as file:
                json.dump(data, file, indent=4)    
    except json.JSONDecodeError:
        return []
    except Exception as e: # Handle any other potential exceptions
        print(f"An error occurred: {e}")
        return []
    

@app.post("/users/", response_model=UserWithID)
async def create_user(user: User):
    data = read_user_data()
    new_user = user.dict()
    new_user["id"] = str(uuid.uuid4())
    data.append(new_user)
    write_user_data(data)
    return UserWithID(**new_user)

'''@app.get("/users/{name}", response_model=UserWithID)
async def read_user(name: str):
    data = read_user_data()
    for item in data:
        if item["username"] == name:
            return UserWithID(**item)
    raise HTTPException(status_code=404, detail="User not found")'''

@app.get("/users/{user_id}", response_model=UserWithID)
async def read_user(user_id: str):
    data = read_user_data()
    for item in data:
        if item["id"] == user_id:
            return UserWithID(**item)
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=UserWithID)
async def update_user(user_id: str, user: User):
    data = read_user_data()
    for index, item in enumerate(data):
        if item["id"] == user_id:
            updated_user = user.dict()
            updated_user["id"] = user_id
            data[index] = updated_user
            write_user_data(data)
            return UserWithID(**updated_user)
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str):
    data = read_user_data()
    print("In delete method")
    for index, item in enumerate(data):
        if item["id"] == user_id:
            del data[index]
            print(f"record with {index} deleted")
            write_user_data(data)
            return
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/", response_model=List[UserWithID])
async def list_users():
    data = read_user_data()
    return [UserWithID(**item) for item in data]