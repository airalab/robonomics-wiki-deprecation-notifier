import asyncio
from pathlib import Path
from time import time

import dotenv
from loguru import logger

from wiki_deprecation_notifier import run_inspection

dotenv_file = Path(".env")
if dotenv_file.exists():
    dotenv.load_dotenv(dotenv_file.absolute(), override=True)


async def main() -> None:
    t0 = time()
    await run_inspection()
    logger.debug(f"Run time: {time() - t0}s")


if __name__ == "__main__":
    asyncio.run(main())

# TODO: Add docker-compose
# TODO: Add logging
# TODO: Add Sqlite DB
# TODO: Implement issue creation
