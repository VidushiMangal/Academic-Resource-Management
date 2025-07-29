from fastapi import FastAPI, APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import List,Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base,Session
from sqlalchemy import create_engine
from authentication import get_current_user,UserInDB
import uuid

router = APIRouter(prefix="/publisher")
app = FastAPI()

#DATABASE_URL = "postgresql://user:password@localhost/dbname"--- server connection
DATABASE_URL = "postgresql://postgres:postgres@localhost/postgres"
if DATABASE_URL:
    print("server/Databse connected")
else:
    print("server/database not connected")
engine = create_engine(DATABASE_URL)# Creating connection with database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class PublicationDB(Base):
    __tablename__ = "publications"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    authors = Column(String)
    journal = Column(String)
    year = Column(Integer)
    doi = Column(String)

Base.metadata.create_all(bind=engine) # bind existing tables and create new one if not there

class Publication(BaseModel):
    title: str
    authors: str
    journal: str
    year: int
    doi: str
class PublicationWithID(Publication):
    id: str

#Method to create fresh connection (open /close) for each request 
def get_db(): 
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

#METHOD TO CREATE A DATABASE RECORD
@router.post("/create_publications/", response_model=PublicationWithID)
async def create_publication(publication: Publication, current_user: UserInDB=Depends(get_current_user),
                             db:Session = Depends(get_db)):
    db_publication = PublicationDB(id=str(uuid.uuid4()), **publication.model_dump())
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    print(f"{current_user.username} has append another record to publisher database")
    return db_publication

#METHOD TO LIST ALL RECORDS OR RECORD WITH A FIELD INFORMATION USING QUERY PARAMATER
@router.get("/list_publications_by_query/",response_model=List[PublicationWithID])
async def read_publications(
    publication_id: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    authors: Optional[str] = Query(None),
    journal: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    doi: Optional[str] = Query(None),
    db: Session = Depends(get_db) ):

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

# @router.get("/publications/{publication_id}", response_model=PublicationWithID)
# async def read_publication(publication_id: str, current_user: UserInDB=Depends(get_current_user), db: SessionLocal = Depends(get_db)):
#     db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
#     if db_publication is None:
#         raise HTTPException(status_code=404, detail="Publication not found")
#     return {"detail": f"Publication with id '{current_user.publication_id}' reterived successfully"}

#METHOD TO UPDATE A RECORD BY PROVIDING ID
@router.put("/update_publications/{publication_id}", response_model=PublicationWithID)
async def update_publication(publication_id: str, publication: Publication, 
                             current_user:UserInDB=Depends(get_current_user),db: Session = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    print(f"{PublicationDB.id},{publication_id}")
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    for key, value in publication.model_dump().items():
        setattr(db_publication, key, value)
    db.commit()
    print(f"{current_user.username} has updated the record")
    db.refresh(db_publication)
    return db_publication

#METHOD TO DELETE A RECORD BY ID
@router.delete("/delete_publications/{publication_id}", response_model=dict)
async def delete_publication_by_id(publication_id: str, current_user:UserInDB=Depends(get_current_user),db: Session = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    db.delete(db_publication)
    db.commit()
    print(f"Record with {publication_id} is deleted")
    return {"detail": f"Publication with id '{publication_id}' deleted successfully"}

#METHOD TO LIST ALL RECORD USING CURRENT USER
@router.get("/list_publications/", response_model=List[PublicationWithID]) 
async def list_publications(current_user: UserInDB = Depends(get_current_user), 
                            db: Session = Depends(get_db)):
    print(f"Authenticated user: {current_user.username}")
    publications = db.query(PublicationDB).all()
    return publications


