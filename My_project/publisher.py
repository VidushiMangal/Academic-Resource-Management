from fastapi import FastAPI, APIRouter,HTTPException, Query, Depends
from pydantic import BaseModel
import uuid
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from login import get_current_user,UserInDB

router = APIRouter(prefix="/publisher")
app = FastAPI()
DATABASE_URL = "postgresql://postgres:postgres@localhost/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Step 4: It creates a basic class for sqlalchemt model named as Base whomsoever connect to it will br treated as SQLAlchemy model class.
Base = declarative_base()
# Step 5: As Base class is inheritrd in it so we are instructing this class to be in SQLAlchemy model. here we are copying our pydantic model class to another named publication.
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

class Publication(BaseModel):
    title: str
    authors: str
    journal: str
    year: int
    doi: str
class PublicationWithID(Publication):
    id: str
# Step 8: we create a function get_db() to create dependency to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db # connection will continue till explicitly closed
    finally:
        db.close()

@router.post("/create_publications/", response_model=PublicationWithID)
async def create_publication(publication: Publication, current_user: UserInDB=Depends(get_current_user),
                             db:SessionLocal = Depends(get_db)):
    db_publication = PublicationDB(id=str(uuid.uuid4()), **publication.dict())
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    print(f"{current_user.username} has append another record to publisher database")
    return db_publication

@router.get("/publications/",response_model=List[PublicationWithID])
async def read_publications(
    publication_id: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    authors: Optional[str] = Query(None),
    journal: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    doi: Optional[str] = Query(None),
    current_user:UserInDB=Depends(get_current_user),
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

@router.get("/publications/{publication_id}", response_model=PublicationWithID)
async def read_publication(publication_id: str, current_user: UserInDB=Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return {"detail": f"Publication with id '{current_user.publication_id}' reterived successfully"}

@router.put("/update_publications/{publication_id}", response_model=PublicationWithID)
async def update_publication(publication_id: str, publication: Publication, 
                             current_user:UserInDB=Depends(get_current_user),db: SessionLocal = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    print(f"{PublicationDB.id},{publication_id}")
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    for key, value in publication.dict().items():
        setattr(db_publication, key, value)
    db.commit()
    print(f"{current_user.username} has updated the record")
    db.refresh(db_publication)
    return db_publication

@router.delete("/publications/delete/{publication_id}", response_model=dict)
async def delete_publication_by_id(publication_id: str, current_user:UserInDB=Depends(get_current_user),db: SessionLocal = Depends(get_db)):
    db_publication = db.query(PublicationDB).filter(PublicationDB.id == publication_id).first()
    if db_publication is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    db.delete(db_publication)
    db.commit()
    return {"detail": f"Publication with id '{current_user.publication_id}' deleted successfully"}

@router.get("/list_publications/", response_model=List[PublicationWithID])
async def list_publications(current_user: UserInDB = Depends(get_current_user), 
                            db: SessionLocal = Depends(get_db)):
    print(f"Authenticated user: {current_user.username}")
    publications = db.query(PublicationDB).all()
    return publications


