from fastapi import FastAPI, APIRouter,HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ValidationError
from jose import jwt,JWTError
import datetime
import json
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "1234" 
ALGORITHM = "HS256" 
#ACCESS_TOKEN_EXPIRE_MINUTES = 90
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = []
class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
  username: str
  hashed_password: str

def verify_password(plain_password: str, hashed_password: str):
   return pwd_context.verify(plain_password, hashed_password)
'''def get_password_hash(password: str):
  return pwd_context.hash(password)'''
def load_users_from_json(file_path: str = "users.json"):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return []

users_data = load_users_from_json() # Read all users from users.json
users = []
for user_info in users_data:
    hashed_password=pwd_context.hash(user_info["password"])
    #hashed_password = get_password_hash(user_info["password"]) # Hash the password
    users.append(UserInDB(username=user_info["username"], hashed_password=hashed_password))
    
def create_access_token(data: UserInDB, expires_delta: datetime.timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
  else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
  to_encode["exp"] = expire  # This is when the token stops working
  encoded_jwt = jwt.encode( to_encode, SECRET_KEY, algorithm=ALGORITHM )  # Making the actual token
  return encoded_jwt
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Permitted time slot completed/Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = next((u for u in users if u.username == username), None)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
    except ValidationError:
        raise credentials_exception
 
app = FastAPI()
router = APIRouter(prefix="/login")

#@app.post("/token", response_model=Token)
@router.post("/token",response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in users if u.username == form_data.username), None)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_data = {"sub": user.username}  
    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}
