from fastapi import FastAPI, HTTPException, Query, Depends, Header, status
from pydantic import BaseModel
import uuid
import json
from typing import List, Optional
from jose import jwt, exceptions

# Assuming you have SECRET_KEY, ALGORITHM, get_user, read_user_data from your auth file
# Replace with actual values and functions from your auth file.
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
ALGORITHM = "HS256"

app = FastAPI()

# File path for data storage
DATA_FILE = "publications.json"

# Function to read data from the JSON file
def read_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to write data to the JSON file
def write_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

class Publication(BaseModel):
    title: str
    authors: str
    journal: str
    year: int
    doi: str

class PublicationWithID(Publication):
    id: str

# Dependency to get the current user from the token
async def get_current_user(authorization: str = Header(...)):
    try:
        token_type, token = authorization.split(" ")
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = get_user(username)  # Assuming get_user is defined in your authentication file
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except exceptions.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.post("/publications/", response_model=PublicationWithID, dependencies=[Depends(get_current_user)])
async def create_publication(publication: Publication, current_user: dict = Depends(get_current_user)):
    print(f"User {current_user['username']} is creating a publication")
    data = read_data()
    new_publication = publication.dict()
    new_publication["id"] = str(uuid.uuid4())
    data.append(new_publication)
    write_data(data)
    return PublicationWithID(**new_publication)

@app.get("/publications/", response_model=List[PublicationWithID], dependencies=[Depends(get_current_user)])
async def read_publications(
    current_user: dict = Depends(get_current_user),
    publication_id: str = None,
    title: str = None,
    authors: str = None,
    journal: str = None,
    year: int = None,
    doi: str = None,
):
    print(f"User {current_user['username']} is accessing publications with query parameters")
    data = read_data()
    filtered_data = data
    if publication_id:
        filtered_data = [item for item in filtered_data if item.get("id") == publication_id]
    if title:
        filtered_data = [item for item in filtered_data if title in item.get("title", "")]
    if authors:
        filtered_data = [item for item in filtered_data if authors in item.get("authors", "")]
    if journal:
        filtered_data = [item for item in filtered_data if journal in item.get("journal", "")]
    if year:
        filtered_data = [item for item in filtered_data if year == item.get("year", 0)]
    if doi:
        filtered_data = [item for item in filtered_data if doi in item.get("doi", "")]
    if not filtered_data:
        raise HTTPException(status_code=404, detail="Details not found")
    return [PublicationWithID(**item) for item in filtered_data]

@app.get("/publications/{author_title}", dependencies=[Depends(get_current_user)])
async def read_publication(author_title: str, current_user: dict = Depends(get_current_user)):
    print(f"User {current_user['username']} is accessing publication with author title {author_title}")
    data = read_data()
    for item in data:
        if item.get("title") == author_title:
            return PublicationWithID(**item)
    raise HTTPException(status_code=404, detail="Author not found")

@app.get("/publications/", response_model=List[PublicationWithID], dependencies=[Depends(get_current_user)])
async def list_publications(current_user: dict = Depends(get_current_user)):
    print(f"User {current_user['username']} is listing all publications")
    data = read_data()
    return [PublicationWithID(**item) for item in data]

@app.put("/publications/{publication_id}", response_model=PublicationWithID, dependencies=[Depends(get_current_user)])
async def update_publication(publication_id: str, publication: Publication, current_user: dict = Depends(get_current_user)):
    print(f"User {current_user['username']} is updating publication {publication_id}")
    data = read_data()
    for index, item in enumerate(data):
        if item["id"] == publication_id:
            updated_publication = publication.dict()
            updated_publication["id"] = publication_id
            data[index] = updated_publication
            write_data(data)
            return PublicationWithID(**updated_publication)
    raise HTTPException(status_code=404, detail="Publication not found")

@app.delete("/publications/{author_title}", dependencies=[Depends(get_current_user)])
async def delete_publication(author_title: str, current_user: dict = Depends(get_current_user)):
    print(f"User {current_user['username']} is deleting publication with author title {author_title}")
    data = read_data()
    for index, item in enumerate(data):
        if author_title in item["authors"]:
            print("I am in delete method")
            del data[index]
            write_data(data)
            return
    raise HTTPException(status_code=404, detail="Author not found")