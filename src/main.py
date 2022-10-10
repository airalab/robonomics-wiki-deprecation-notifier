import asyncio
import os
import sys
from pathlib import Path

import dotenv
from loguru import logger

from wiki_deprecation_notifier import run_inspection, start_daemon

dotenv_file = Path(".env")
if dotenv_file.exists():
    dotenv.load_dotenv(dotenv_file.absolute())


async def main() -> None:
    runner_mode = os.getenv("RUNNER_MODE", "single")

    match runner_mode:
        case "single":
            await run_inspection()
        case "daemon":
            await start_daemon()
        case _:
            logger.critical(f"Unrecognized runner mode: '{runner_mode}'")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

# TODO: Add logging
# TODO: Add Sqlite DB
# TODO: Implement issue creation
