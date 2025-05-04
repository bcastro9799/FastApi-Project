from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    bookmarks = relationship("Bookmark", back_populates="owner", lazy="selectin")