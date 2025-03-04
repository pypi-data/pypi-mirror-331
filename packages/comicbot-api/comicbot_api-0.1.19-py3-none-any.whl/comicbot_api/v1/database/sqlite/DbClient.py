from sqlalchemy.exc import IntegrityError
from sqlmodel import create_engine, SQLModel, select, Session
from loguru import logger
from comicbot_api.v1.database.sqlite.daos.comic_book import ComicBook, PublicationType


class DbClient:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)
        logger.trace(f"Using DB with path: {db_path}")

    def add_comic_book(self, comic_book: ComicBook):
        try:
            with Session(self.engine, expire_on_commit=False) as session:
                session.add(comic_book)
                session.commit()
        except IntegrityError:
            logger.warning(f"Integrity Error on comic book {comic_book.title}. May have been previously inserted to DB "
                           f"by another query")


    def insert_comics(self, comics: list[ComicBook]):
        for comic in comics:
            self.add_comic_book(comic)
        return comics

    def get_comics_for_release_week(
            self, week: int, year: int, _format: PublicationType, publisher: str) -> list[ComicBook]:
        with Session(self.engine, expire_on_commit=False) as session:
            statement = select(ComicBook).where(
                ComicBook.week == week).where(
                ComicBook.year == year).where(
                ComicBook.publication_type == _format).where(
                ComicBook.publisher == publisher
            )
            # TODO metric bump here
            return session.exec(statement).all()

    def has_release_week_given_filters(self, week: int, _format: str, year: int, publisher: str) -> bool:
        with Session(self.engine, expire_on_commit=False) as session:
            statement = select(ComicBook).where(
                ComicBook.publication_type == _format).where(
                ComicBook.week == week).where(
                ComicBook.year == year).where(
                ComicBook.publisher == publisher).limit(1)
            return session.exec(statement).first() is not None
