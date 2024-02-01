import asyncio
import functools


def celery_sync(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))

    return wrapper
