from typing import Callable

global service_version_provider
service_version_provider: Callable[[], str] = lambda: "development"


def set_service_version_provider(provider: Callable[[], str]) -> None:
    if not callable(provider):
        raise ValueError("Service version provider must be a callable.")
    global service_version_provider
    service_version_provider = provider


def get_current_service_version() -> str:
    result = service_version_provider()
    if type(result) is not str:
        raise ValueError("Service version provider must return a string.")

    return result
