import datetime
from typing import List
from comicbot_api.v1.router.RequestRouter import RequestRouter
from .database.sqlite.DbClient import DbClient
from .web_scraper import WebScraper
from comicbot_api.utils.release_day import ReleaseDay
import loguru
from loguru import logger
from comicbot_api.v1.validation import VALIDATION_RULES
import sys


class ComicBotAPIClientV1:
    """
    Client for the Comic Bot API v1
    """
    request_router: RequestRouter
    _web_scraper: WebScraper = None
    _logger: loguru.logger = None
    base_url: str = None
    _logger_id: int = None
    _log_level: str = "INFO"
    _api_endpoint: str = '/comic/get_comics'

    def __init__(self):
        self.reconfigure_logger(level=self._log_level)
        self._web_scraper = WebScraper(base_url=self.base_url)

    def validate(self, week: int, publishers: List[str], formats: List[str]):
        for rule in VALIDATION_RULES:
            rule.validate(self, week=week, publishers=publishers, formats=formats)

    def get_releases_for_week(self, week: int, **kwargs):
        formats = kwargs['formats']
        publishers = kwargs['publishers']
        self.validate(week=week, publishers=publishers, formats=formats)

        if formats is None:
            formats = []
        if publishers is None:
            publishers = []

        year = kwargs.get('year', datetime.date.today().year)
        if len(formats) > 0:
            formats = list(map(lambda f: f.lower(), formats))
        release_day = ReleaseDay(week=week, year=year)
        comics = self.request_router.route_request(
            release_day=release_day,
            formats=formats,
            publishers=publishers)
        return comics

    def get_latest_releases(self, **kwargs):
        return self.get_releases_for_week(week=datetime.date.today().isocalendar().week,
                                          **kwargs)

    def reconfigure_logger(self, sink=sys.stdout,
                           message="<green>{time}</green> - {level} - {message}", level="INFO"):
        if self.__getattribute__("_logger_id") is not None:
            logger.remove(self._logger_id)
        else:
            logger.remove()
        level = self._log_level.upper() or level
        self._logger_id = logger.add(sink, format=message, level=level)

    def set_web_scraper(self, web_scraper: WebScraper):
        self._web_scraper = web_scraper

    def set_log_level(self, log_level: str):
        self._log_level = log_level
        self.reconfigure_logger()

    def set_base_url(self, base_url: str):
        self.base_url = base_url
        # Also set the webscraper since it depends on the base_url
        self._web_scraper = WebScraper(base_url=base_url)

    def set_api_endpoint(self, api_endpoint: str):
        self._api_endpoint = api_endpoint


class ComicBotAPIClientV1Builder:
    """
    Client Builder for Comic Bot API Client
    """
    comic_bot_client: ComicBotAPIClientV1

    def __init__(self):
        self.comic_bot_client = ComicBotAPIClientV1()

    def with_sqlite(self, db_path: str):
        self.comic_bot_client.request_router = RequestRouter(DbClient(db_path), self.comic_bot_client._web_scraper)
        return self

    def with_base_url(self, base_url: str):
        self.comic_bot_client.set_base_url(base_url)
        self.with_web_scraper(WebScraper(base_url=base_url))
        return self

    def with_api_endpoint(self, api_endpoint: str):
        self.comic_bot_client.set_api_endpoint(api_endpoint)
        return self

    def with_web_scraper(self, web_scraper):
        self.comic_bot_client.set_web_scraper(web_scraper)
        return self

    def with_log_level(self, log_level: str):
        self.comic_bot_client.set_log_level(log_level)
        return self

    def build(self) -> ComicBotAPIClientV1:
        return self.comic_bot_client
