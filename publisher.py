
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uuid
import json
from typing import List, Optional

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

@app.post("/publications/", response_model=PublicationWithID)
async def create_publication(publication: Publication):
    data = read_data()
    new_publication = publication.dict()
    new_publication["id"] = str(uuid.uuid4())
    data.append(new_publication)
    write_data(data)
    return PublicationWithID(**new_publication)

@app.get("/publications/", response_model=List[PublicationWithID]) # Searching data using query parameter
async def read_publications(
    publication_id: str=None,  # without none its a requuired field
    title: str=None,
    authors: str = None,
    journal: str = None,
    year: int = None,
    doi: str = None,
):
    print("I am in query parameter method")
    data = read_data()
    filtered_data = data
    if publication_id:
        filtered_data = [item for item in filtered_data if item.get("id") == publication_id]
            # Filter by other parameters
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


'''app.get("/publications/{publication_id}", response_model=PublicationWithID) # Searching data using path variable
async def read_publication(publication_id: str):
    data = read_data()
    for item in data:
        if item["id"] == publication_id:
            return PublicationWithID(**item)
    print("I am in path variable method")
    raise HTTPException(status_code=404, detail="Publication not found")'''

'''@app.get("/publications/{publication_id}")
async def read_publications(publication_id: str):
    if not publication_id:
        raise HTTPException(status_code=400, detail="publication_id is required")
    data = read_data()
    for item in data:
        if item.get("id") == publication_id:
            return PublicationWithID(**item)
    raise HTTPException(status_code=404, detail="Publication not found")'''

@app.get("/publications/{author_title}")
async def read_publications(author_title: str):
    print("I am in path variable method")
    if not author_title:
        raise HTTPException(status_code=400, detail="author name is required")
    data = read_data()
    for item in data:
        if item.get("title") == author_title:
            return PublicationWithID(**item)
    raise HTTPException(status_code=404, detail="Author not found")

@app.get("/publications/", response_model=List[PublicationWithID])   # Listing all records
async def list_publications():
    data = read_data()
    return [PublicationWithID(**item) for item in data]

@app.put("/publications/{publication_id}", response_model=PublicationWithID)
async def update_publication(publication_id: str, publication: Publication):
    data = read_data()
    for index, item in enumerate(data):
        if item["id"] == publication_id:
            updated_publication = publication.dict()
            updated_publication["id"] = publication_id
            data[index] = updated_publication
            write_data(data)
            return PublicationWithID(**updated_publication)
    raise HTTPException(status_code=404, detail="Publication not found")

@app.delete("/publications/{author_title}")
async def delete_publication(author_title: str):
    print(author_title)
    data = read_data()
    for index, item in enumerate(data):
         print(f"Item: {index}, Item: {item}")
                 # if "authors" in item and isinstance(item["authors"], list): #Check if the authors key exists, and is a list.
         if author_title in item["authors"]:
            print("I am in delete method")
            del data[index]
            write_data(data)
            return
    raise HTTPException(status_code=404, detail="Author not found")