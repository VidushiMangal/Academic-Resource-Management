from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, ValidationError
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import json

SECRET_KEY = "1234" 
ALGORITHM = "HS256" 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") #Extract bearer & pass to token
users = []

class Hashed_Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
  username: str
  hashed_password: str

#Reading all users and converting password to hashing password
def prepare_user_list(file_path: str = "./Database/users.json"):
    try:
        with open(file_path, "r") as f:
            user_data = json.load(f)
            #return user_data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return []
    for user_info in user_data:
        hashed_password=pwd_context.hash(user_info["password"])
        users.append(UserInDB(username=user_info["username"], hashed_password=hashed_password))

# Method to Verify Password
def verify_password(plain_password: str, hashed_password: str):
   return pwd_context.verify(plain_password, hashed_password)

# Method to create bearer token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=120)
    to_encode["exp"] = expire  # exp is jwt standard to specify token expiration time
    encoded_jwt = jwt.encode( to_encode, SECRET_KEY, algorithm=ALGORITHM )  # Making the actual token
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Permitted time slot completed/Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")# sub is jwt standard to get user name
        user = next((u for u in users if u.username == username), None)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
    except ValidationError:
        raise credentials_exception
 
router = APIRouter(prefix="/login")

@router.post("/token",response_model=Hashed_Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((user for user in users if user.username == form_data.username), None) # using generator 
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"} 
            )
    access_token_data = {"sub": user.username}  
    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}

app = FastAPI()
prepare_user_list()
app.include_router(router)