from dataclasses import dataclass
from comicbot_api.utils.comic import Comic
from typing import Any
from bs4 import BeautifulSoup, Tag
import stealth_requests as srequests
from typing import List
from comicbot_api.utils.comic_release_builder import ComicReleaseURLBuilder
from comicbot_api.utils.release_day import ReleaseDay


def comic_title_finder(tag: Tag) -> bool:
    return tag.has_attr('class') and 'title' in tag.get('class')


@dataclass
class WebScraper:
    base_url: str
    api_endpoint: str = '/comic/get_comics'
    parser: str = 'html.parser'

    def find_comic_elements_from_html(self, html: str) -> List[Any]:
        soup = BeautifulSoup(html, self.parser)
        return soup.findAll(comic_title_finder)

    def link_contents_to_string(self, link_contents) -> str:
        return link_contents[0].strip()

    def scrape_comics(self, url: str, release_day: ReleaseDay) -> List[Comic]:
        response = srequests.get(url)
        # TODO throw error if status code is not 2xx
        if response.status_code == 200:
            comic_releases_html = response.json().pop('list')
            all_comic_elements = self.find_comic_elements_from_html(comic_releases_html)
            return list(map(lambda link:
                            Comic(url=self.base_url + link.attrs.pop('href'),
                                  week=release_day.week,
                                  year=release_day.year,
                                  title=self.link_contents_to_string(link.contents)),
                            all_comic_elements))
        return []

    def scrape_comics_with_filters(self, week: int, year: int, _format: str, publisher: str) -> List[Comic]:
        release_day = ReleaseDay(week=week, year=year)
        url = ComicReleaseURLBuilder().with_formats(_format) \
            .with_date(release_day) \
            .with_publishers(publisher) \
            .with_url(self.base_url + self.api_endpoint).build()
        comics = self.scrape_comics(url, release_day)
        # TODO metric bump here
        # list evaluates the map since map is lazy
        return list(map(lambda comic: comic.to_dao(), comics))
