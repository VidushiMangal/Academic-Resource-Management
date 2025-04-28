from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
import datetime
from passlib.context import CryptContext


SECRET_KEY = "your_secret_key" 
ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 30 
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
def verify_password(plain_password: str, hashed_password: str):
   return pwd_context.verify(plain_password, hashed_password)
 
def get_password_hash(password: str):
  return pwd_context.hash(password)

users = []

class UserInDB(BaseModel):
  username: str
  hashed_password: str
 
 # --- Making the Special Token ---
def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
  else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Default time
  to_encode["exp"] = expire  # This is when the token stops working
  encoded_jwt = jwt.encode( to_encode, SECRET_KEY, algorithm=ALGORITHM )  # Making the actual token
  return encoded_jwt
 
app = FastAPI()
 
hashed_password = pwd_context.hash("testpassword")  # Jumbling the test password
users.append( UserInDB(username="testuser", hashed_password=hashed_password))  # Saving the test user
print(users)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm ):  # FastAPI helps me get the username/password
    user = next((u for u in users if u.username == form_data.username), None  )  # Finding the user in my list
    if (user is None or not verify_password(form_data.password, user.hashed_password)): 
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED,detail="Wrong username or password")
                            ''',headers={
                                        "WWW-Authenticate": "Bearer"
                                    }, ''' # Something about needing this for how tokens work
    else:                        
        access_token = create_access_token(data={"sub": form_data.username})  # Making the token for them
        return {   "access_token": access_token,   "token_type": "bearer",   }  # Sending the token back
 