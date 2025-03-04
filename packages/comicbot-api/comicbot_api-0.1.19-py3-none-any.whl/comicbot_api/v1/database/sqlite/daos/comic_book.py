from sqlmodel import Field, SQLModel
from dataclasses import dataclass
import uuid

@dataclass
class PublicationType:
    SINGLE_ISSUE = "single_issue"
    HARDCOVER = "hardcover"
    TRADEPAPERBACK = "trade_paperback"

class ComicBook(SQLModel, table=True):
    __tablename__ = "comic_books"
    id: str
    title: str = Field(primary_key=True, index=True)
    week: int = Field(primary_key=True, index=True)
    year: int = Field(primary_key=True, index=True)
    publication_type: str
    publisher: str
    url: str
    cover_image_url: str

    def __init__(self,
                 title: str,
                 year: int,
                 week: int,
                 publication_type: PublicationType,
                 publisher: str,
                 url: str,
                 cover_image_url: str):
        self.title = title
        self.week = week
        self.id = str(uuid.uuid4())
        self.publisher = publisher
        self.year = year
        self.publication_type = publication_type
        self.url = url
        self.cover_image_url = cover_image_url