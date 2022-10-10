import asyncio
import os
from pprint import pprint
from time import time

from loguru import logger

from ._conflict_resolver import get_conflicts, resolve_conflicts
from ._dependency_mapping import get_dependency_map


async def run_inspection() -> None:
    t0 = time()
    wiki_articles = await get_dependency_map()
    pprint(wiki_articles)
    conflicts = get_conflicts(wiki_articles)
    pprint(conflicts)
    await resolve_conflicts(conflicts)
    logger.debug(f"Run time: {time() - t0}s")


async def start_daemon() -> None:
    while True:
        await run_inspection()
        sleep_delay = float(os.getenv("SLEEP_DELAY", 60 * 60))
        await asyncio.sleep(sleep_delay)
