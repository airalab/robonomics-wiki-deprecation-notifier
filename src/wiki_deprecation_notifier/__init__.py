import asyncio
import os
from time import time

from loguru import logger

from ._conflict_resolver import get_conflicts, resolve_conflicts
from ._dependency_mapping import get_dependency_map


async def run_inspection() -> None:
    logger.info("Inspection run started")
    t0 = time()
    wiki_articles = await get_dependency_map()
    if conflicts := get_conflicts(wiki_articles):
        logger.info(f"{len(conflicts)} deprecations found. Starting conflict resolution")
        await resolve_conflicts(conflicts)
    else:
        logger.info("No deprecations found. Skipping conflict resolution")
    logger.debug(f"Inspection run complete. Run time: {round(time() - t0, 4)}s")


async def start_daemon() -> None:
    logger.info("Daemon started")
    while True:
        await run_inspection()
        sleep_delay = float(os.getenv("SLEEP_DELAY", 60 * 60))
        logger.debug(f"Daemon sleep delay set to {sleep_delay}s")
        await asyncio.sleep(sleep_delay)
