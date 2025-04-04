from sqlalchemy import Column, Integer, String
from db import Base


class Books(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    description = Column(String, index=True)
    rating = Column(Integer, index=True)
    # Add any additional fields or relationships here
