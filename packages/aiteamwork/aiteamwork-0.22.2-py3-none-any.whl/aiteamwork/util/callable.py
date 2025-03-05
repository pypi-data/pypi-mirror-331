import asyncio
import inspect
from time import sleep
from typing import Callable, Coroutine, cast

type SyncOrAsyncReturn[T] = T | Coroutine[None, None, T]
type SyncOrAsyncCallback[**Args, ReturnType] = Callable[Args, SyncOrAsyncReturn[ReturnType]]  # noqa F821


def with_retrying[Fn: Callable](retries: list[int]) -> Callable[[Fn], Fn]:
    def decorator(fn: Fn) -> Fn:
        if not callable(fn):
            raise ValueError("tool must be a callable")

        if inspect.iscoroutinefunction(fn):

            async def wrapped_async(*args, **kwargs):
                attempt = 0
                while True:
                    try:
                        return await fn(*args, **kwargs)
                    except Exception:
                        if attempt >= len(retries):
                            raise
                        await asyncio.sleep(retries[attempt] / 1000)
                        attempt += 1

            wrapped_async.__name__ = fn.__name__

            return cast(Fn, wrapped_async)

        def wrapped(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt >= len(retries):
                        raise
                    sleep(retries[attempt] / 1000)
                    attempt += 1

        wrapped.__name__ = fn.__name__

        return cast(Fn, wrapped)

    return decorator
