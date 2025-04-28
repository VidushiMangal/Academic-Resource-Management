
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import uuid

app = FastAPI()

# DynamoDB setup (replace with your table name)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Publications')

class Publication(BaseModel):
    title: str
    authors: str
    journal: str
    year: int
    doi: str

@app.post("/publications/", response_model=Publication)
async def create_publication(publication: Publication):
    item = publication.dict()
    item['id'] = str(uuid.uuid4())  # Generate a unique ID
    try:
        table.put_item(Item=item)
        return publication
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/publications/{publication_id}", response_model=Publication)
async def read_publication(publication_id: str):
    response = table.get_item(Key={'id': publication_id})
    item = response.get('Item')
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Publication not found")

@app.get("/publications/", response_model=list[Publication])
async def list_publications():
    response = table.scan()
    items = response.get('Items', [])
    return items

@app.put("/publications/{publication_id}", response_model=Publication)
async def update_publication(publication_id: str, publication: Publication):
    item = publication.dict()
    item['id'] = publication_id
    try:
        table.put_item(Item=item)
        return publication
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/publications/{publication_id}", status_code=204)
async def delete_publication(publication_id: str):
    try:
        table.delete_item(Key={'id': publication_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))