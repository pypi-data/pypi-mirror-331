from typing import List
from comicbot_api.utils.release_day import ReleaseDay
from comicbot_api.v1.database.sqlite.DbClient import DbClient
from comicbot_api.v1.web_scraper import WebScraper
from comicbot_api.v1.database.sqlite.daos.comic_book import ComicBook


# Request Router routes an incoming request to the appropriate component,
# either sqlite cache or web scraper.
# TODO request router needs to default to scrape if db client is None
class RequestRouter:
    db_client: DbClient
    web_scraper: WebScraper

    def __init__(self, db_client: DbClient, web_scraper: WebScraper):
        self.db_client = db_client
        self.web_scraper = web_scraper

    def route_request(self,
                      release_day: ReleaseDay,
                      formats: List[str],
                      publishers: List[str]) -> List[ComicBook]:
        comics = []
        week = release_day.week
        year = release_day.year
        for publisher in publishers:
            for _format in formats:
                if self.db_client.has_release_week_given_filters(
                        week=week,
                        year=year,
                        _format=_format,
                        publisher=publisher):
                    comics.extend(self.db_client.get_comics_for_release_week(
                        week=week,
                        year=year,
                        _format=_format,
                        publisher=publisher))
                else:
                    scraped_comics = self.web_scraper.scrape_comics_with_filters(week=week,
                                                                                 year=year,
                                                                                 _format=_format,
                                                                                 publisher=publisher)
                    inserted_comics = self.db_client.insert_comics(scraped_comics)
                    comics.extend(inserted_comics)
        return comics
