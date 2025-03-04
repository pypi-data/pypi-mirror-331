from datetime import date, timedelta
import datetime
from dataclasses import dataclass
from loguru import logger

RELEASE_DAY_OF_WEEK = 2  # Wednesday, datetime starts from 0
NUM_DAYS_OF_WEEK = 7


def _get_wednesday_for_week_num(week_num, **kwargs):
    """Get all Wednesdays i.e. release days for a given year.
    Defaults to this year, if no year is specified """
    year = kwargs.pop('year', date.today().year)
    # Initialize the list to store all Wednesdays
    wednesdays = []

    # Start from the first day of the year
    current_date = datetime.date(year, 1, 1)

    # Adjust to the first Wednesday
    while current_date.weekday() != 2:  # 0=Monday, 1=Tuesday, 2=Wednesday, etc.
        current_date += datetime.timedelta(days=1)

    # Loop through the year
    while current_date.year == year:
        wednesdays.append(current_date)
        current_date += datetime.timedelta(weeks=1)

    return wednesdays[week_num]


@dataclass(init=False)
class ReleaseDay:
    release_date: date
    year: int
    week: int

    @staticmethod
    def today():
        return ReleaseDay(_date=date.today())

    def __init__(self, **kwargs):
        year = kwargs.pop('year', date.today().year)
        week = kwargs.pop('week', None)
        _date = kwargs.pop('_date', None)
        if _date:
            start_date = _date
        elif week:
            if week <= 0:
                raise ValueError(f"Week number must be greater than zero, got {week}")
            # arrays do start at 0
            start_date = _get_wednesday_for_week_num(week - 1, year=year)
        else:
            start_date = date.today()
        logger.trace(str.format("Using start date {0}", start_date))
        self.year = year
        self.week = week
        self.release_date = start_date + timedelta((RELEASE_DAY_OF_WEEK -
                                                    start_date.weekday()) %
                                                   NUM_DAYS_OF_WEEK)
