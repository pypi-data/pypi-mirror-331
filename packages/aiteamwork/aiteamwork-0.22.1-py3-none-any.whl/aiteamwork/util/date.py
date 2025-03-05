import datetime
from typing import Callable

global date_provider
date_provider: Callable[[], datetime.datetime] = datetime.datetime.now


def set_date_provider(provider: Callable[[], datetime.datetime]) -> None:
    global date_provider
    date_provider = provider


def get_current_time() -> datetime.datetime:
    return date_provider()
