import asyncio
from pprint import pprint

from wiki_deprecation_notifier._dependency_mapping import get_dependency_map

if __name__ == "__main__":
    res = asyncio.run(get_dependency_map())
    pprint(res)  # noqa: T203

# TODO: Add docker-compose
# TODO: Add logging
# TODO: Add conflict detection
# TODO: Add Sqlite DB
# TODO: Implement Telegram bot functions
# TODO: Implement issue creation
