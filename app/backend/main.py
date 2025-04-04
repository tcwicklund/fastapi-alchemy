from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import models
from db import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Book(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    description: Optional[str] = None
    rating: int = Field(ge=1, le=5)


books = []


@app.get("/")
async def root():
    return {"message": "Welcome to the Book API!"}


@app.get("/books")
async def get_books(db: Session = Depends(get_db)):
    return db.query(models.Books).all()


@app.get("/books/{book_id}")
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books")
async def create_book(book: Book, db: Session = Depends(get_db)):

    book_model = models.Books()
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating
    db.add(book_model)
    db.commit()
    db.refresh(book_model)
    return book_model


@app.put("/books/{book_id}")
async def update_book(book_id: int, book: Book, db: Session = Depends(get_db)):
    db_book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted"}


@app.get("/books/search")
async def search_books(query: str, db: Session = Depends(get_db)):
    books = db.query(models.Books).filter(models.Books.title.ilike(f"%{query}%")).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return books
