from fastapi import FastAPI, HTTPException,APIRouter,Query
from pydantic import BaseModel
from typing import Optional,List
import json
#import uuid
import os

router = APIRouter(prefix="/userlogin")
app = FastAPI()

USER_DATA_FILE = "./Database/users.json"
#USER_DATA_FILE ="C:/Users/Vidushi.Dev/Documents/work/Academic-Resource-Management/My_project/Database/users.json"
#My_project\Database\users.json
class User(BaseModel):
    id:str
    username: str
    email: str
    full_name: str
    password: str  

# class UserWithID(User):
#     id: str

def read_user_data():
    try:
       if not os.path.exists(USER_DATA_FILE): #check if file exists
            print("File Doen not Exist ")
            # choice=input("--------Do you want to create new file(y/n)-------")
            #if choice=="y" or choice=="Y":
            with open(USER_DATA_FILE, "w") as f: #create if it does not
                json.dump([], f) #dump empty list to it.
                print("-----------New File Created-------------")
            # else:
            #   print("Nothing to read")
       with open(USER_DATA_FILE, "r") as f:
           return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def write_user_data(data):
    try:
      with open(USER_DATA_FILE, "w") as file:  # ✅ Open in write mode to overwrite file
            json.dump(data, file, indent=2)
    except json.JSONDecodeError:
        return []
    except Exception as e: # Handle any other potential exceptions
        print(f"An error occurred: {e}")
        return []
    
@router.post("/", response_model=User)
async def create_user(user: User):
    Total_user = read_user_data()
    new_user = user.model_dump()
    #new_user["id"] = str(uuid.uuid4())
    Total_user.append(new_user)
    write_user_data(Total_user)
    print("---------New uers added to USERS file ------------")
    return User(**new_user)

# Get Details With UserName using PATH parameter
@router.get("/{username}", response_model=User)
async def read_user(username: str):
    data = read_user_data() # Method call to read all records
    for item in data:
        if item["username"] == username:
            return User(**item)
    raise HTTPException(status_code=404, detail="------------User not found-------------")

#Get Details with UserId/Username using QUERY Parameter
@router.get("/", response_model=User)
async def read_user(userid:Optional[str]= Query(default=None),
                    username:Optional[str]=Query(default=None)):
    data = read_user_data()
    if userid:
        for item in data:
            if item["id"] == userid:
                return User(**item)
    else:
        for item in data:
            if item["username"]==username:
                return User(**item)
    raise HTTPException(status_code=404, detail="User not found")


#Updating the record with user id 
@router.put("/update/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    data = read_user_data()
    for index, item in enumerate(data):
        if item["id"] == user_id:
            updated_user = user.model_dump()
            updated_user["id"] = user_id
            data[index] = updated_user
            write_user_data(data)
            print(f"Record with user id --{user_id}-- is updated")
            return User(**updated_user)
    raise HTTPException(status_code=404, detail="User not found")

#Deleting Records usind UserID
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str):
    data = read_user_data()
    for index,user in enumerate(data):
        if user["id"] == user_id:
            del data[index]
            print(f"------------Record with {user_id} is deleted-----------------")
        else:
            print("Record with {user_id} does not exist")
        
        write_user_data(data)
        return
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/list_users/", response_model=List[User])
async def list_users():
    data = read_user_data()
    return [User(**item) for item in data] # **item unpack dictionary to class User model

