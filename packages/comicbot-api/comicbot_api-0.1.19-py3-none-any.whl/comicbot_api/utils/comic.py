from dataclasses import dataclass
from comicbot_api.v1.database.sqlite.daos.comic_book import PublicationType, ComicBook
import stealth_requests as srequests
from bs4 import Tag
import re

def comic_publisher_finder(tag: Tag) -> bool:
    return tag.has_attr('class') and 'header-intro' in tag.get('class')


@dataclass(init=False)
class Comic:
    title: str
    url: str
    publisher: str
    publication_type: PublicationType
    year: int
    week: int
    thumbnail_url: str = "https://thumbs.dreamstime.com/b/text-error-light-beige-background-comic-book-style-illustration-ai-generated-text-error-solid-background-351249786.jpg"


    def determine_publication_type(self, title: str) -> PublicationType:
        lower_case_title = title.lower()
        if "hardcover" in lower_case_title or "hc" in lower_case_title:
            return PublicationType.HARDCOVER
        elif "trade paperback" in lower_case_title or "tpb" in lower_case_title or "tp" in lower_case_title:
            return PublicationType.TRADEPAPERBACK
        else:
            return PublicationType.SINGLE_ISSUE

    def scrape_image(self, url: str):
        comic_response = srequests.get(url)
        if comic_response.status_code == 200:
            self.thumbnail_url = comic_response.meta.thumbnail

    def get_publisher_from_unformatted_response(self, unformatted_scraped_publisher: str):
        results = re.findall("(\w+\s?\w+)\s\s", unformatted_scraped_publisher.strip())
        if len(results) > 0:
            return results[0].lower()
        return "unknown publisher"

    def scrape_publisher(self, url: str):
        comic_response = srequests.get(url)
        if comic_response.status_code == 200:
            parser = comic_response.soup("html.parser")
            header = parser.findAll(comic_publisher_finder)
            self.publisher = self.get_publisher_from_unformatted_response(header[0].text)


    def __init__(self, **kwargs):
        self.url = kwargs['url']
        self.title = kwargs['title']
        self.publication_type = self.determine_publication_type(self.title)
        self.year = kwargs.get("year", -1)
        self.week = kwargs.get("week", -1)
        self.scrape_image(self.url)
        self.scrape_publisher(self.url)

# TODO scraped comic to db comic book record
    def to_dao(self):
        return ComicBook(title=self.title,
                         week=self.week,
                         year=self.year,
                         publication_type=self.publication_type,
                         publisher=self.publisher,
                         url=self.url,
                         cover_image_url=self.thumbnail_url)