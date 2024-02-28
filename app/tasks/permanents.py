import asyncio

from app.tasks.permanents.app import start_app

loop = asyncio.get_event_loop()
loop.run_until_complete(start_app())
