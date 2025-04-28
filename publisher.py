from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
import uuid
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session

app = FastAPI()

# Step 1: Define the PostgreSQL Database URL
DATABASE_URL = "postgresql://postgres:postgres@localhost/postgres"

# Step 2: Create the SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Step 3: Create a SessionLocal class to access the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Step 4: Define the Base for our SQLAlchemy models
Base = declarative_base()

# Step 5: Define the Publication database model (maps to the 'publications' table)
class PublicationDB(Base):
    __tablename__ = "publications"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    authors = Column(String)
    journal = Column(String)
    year = Column(Integer)
    doi = Column(String)

# Step 6: Create the database table if it doesn't exist (on application startup)
Base.metadata.create_all(bind=engine)

# Step 7: Pydantic models for request and response (same as before)
class Publication(BaseModel):
    title: str
    authors: str
    journal: str
    year: int
    doi: str

class PublicationWithID(Publication):
    id: str

# Step 8: Dependency to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Step 9: Update the API endpoints to use the database (these remain largely the same)

@app.post("/publications/", response_model=PublicationWithID)
async def create_publication(publication: Publication, db: SessionLocal = Depends(get_db)): # type: ignore
    db_publication = PublicationDB(id=str(uuid.uuid4()), **publication.dict())
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return db_publication

@app.get("/publications/", response_model=List[PublicationWithID])
async def read_publications(
    publication_id: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    authors: Optional[str] = Query(None),
    journal: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    doi: Optional[str] = Query(None),
    db: SessionLocal = Depends(get_db),
):
    query = db.query(PublicationDB)
    if publication_id:
        query = query.filter(PublicationDB.id == publication_id)
    if title:
        query = query.filter(PublicationDB.title.contains(title))
    if authors:
        query = query.filter(PublicationDB.authors.contains(authors))
    if journal:
        query = query.filter(PublicationDB.journal.contains(journal))
    if year:
        query = query.filter(PublicationDB.year == year)
    if doi:
        query = query.filter(PublicationDB.doi.contains(doi))

    publications = query.all()
    if not publications and (publication_id or title or authors or journal or year or doi):
        raise HTTPException(status_code=404, detail="Details not found")
    return publications

@app.get("/publications/{publication_id}", response_model=PublicationWithID)
async def read_publication(publication_id: str, db: SessionLocal = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return db_publication

@app.put("/publications/{publication_id}", response_model=PublicationWithID)
async def update_publication(publication_id: str, publication: Publication, db: SessionLocal = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    for key, value in publication.dict().items():
        setattr(db_publication, key, value)
    db.commit()
    db.refresh(db_publication)
    return db_publication

@app.delete("/publications/delete/{publication_id}", response_model=dict)
async def delete_publication_by_id(publication_id: str, db: SessionLocal = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    db.delete(db_publication)
    db.commit()
    return {"detail": f"Publication with id '{publication_id}' deleted successfully"}

@app.get("/list_publications/", response_model=List[PublicationWithID])
async def list_publications(db: SessionLocal = Depends(get_db)):
    publications = db.query(PublicationDB).all()
    return publications