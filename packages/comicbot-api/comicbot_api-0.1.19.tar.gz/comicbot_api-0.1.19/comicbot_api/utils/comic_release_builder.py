from typing import List
from functools import reduce
from comicbot_api.utils.release_day import ReleaseDay
from comicbot_api.v1.static.types import PUBLISHERS, FORMATS

def resolve_url_param_type(translation_dict, param_type, selected_params) -> str:
    if len(selected_params) > 0:
        return reduce(lambda param_string, param:
                      param_string + f'&{param_type}[]={translation_dict[param]}',
                      selected_params, '')
    return ''


def publisher_options():
    return PUBLISHERS.keys()


def format_options():
    return FORMATS.keys()

class ComicReleaseURLBuilder:
    date: ReleaseDay
    publishers: List = []
    formats: List = []
    base_url: str = None
    base_url_params: List = ['view=text', 'list=releases', 'date_type=week']

    def resolve_base_params(self):
        return '?' + '&'.join(self.base_url_params)

    def build(self) -> str:
        return self.base_url + self.resolve_base_params() + f'&date={self.date.release_date}' + \
            resolve_url_param_type(FORMATS, 'format', self.formats) + \
            resolve_url_param_type(PUBLISHERS, 'publisher', self.publishers)

    def with_url(self, url: str):
        self.base_url = url
        return self

    def with_publishers(self, *args):
        if len(args) == 0:
            return self
        for publisher in args:
            self.publishers.append(publisher)
        return self

    def with_date(self, date: ReleaseDay):
        self.date = date
        return self

    def with_formats(self, *args):
        if len(args) == 0:
            return self
        for issue_format in args:
            self.formats.append(issue_format)
        return self
