import json
import os
import re
from functools import lru_cache
from typing import Any

import typed_getenv
import yaml
from loguru import logger
from yarl import URL

from ..gihub_api_wrapper.utils import get_repo_name

TARGET_REPO_OWNERS = set(json.loads(os.getenv("TARGET_REPO_OWNERS", '["Multi-Agent-io", "airalab"]')))
FILTER_REPOS_BY_OWNERS: bool = typed_getenv.getenv("FILTER_REPOS_BY_OWNERS", True, var_type=bool, optional=True)


@lru_cache
def extract_front_matter(source_text: str) -> dict[str, Any]:
    return next(yaml.load_all(source_text, Loader=yaml.FullLoader), {})


def extract_contributors_usernames(article: str) -> list[str]:
    front_matter: dict[str, str | list[str]] = extract_front_matter(article)
    return front_matter.get("contributors", [])  # type: ignore


def extract_dependencies(article: str) -> list[tuple[str, str]]:  # noqa: CAC001,CCR001
    front_matter: dict[str, str | list[str]] = extract_front_matter(article)
    dependencies: list[str] = front_matter.get("tools", [])  # type: ignore
    result = []

    for dependency in dependencies:
        try:
            _, source = dependency.rsplit(" ", 1)
            repo_name = get_repo_name(source)
        except ValueError:
            continue

        source_url = URL(source)

        if source_url.host != "github.com":
            continue

        organisation, _ = source_url.path.lstrip("/").split("/", 1)

        if FILTER_REPOS_BY_OWNERS and organisation not in TARGET_REPO_OWNERS:
            continue

        pattern = r"https?://github.com/[^/]+/[^/]+"
        repo_url = re.match(pattern, source)

        if repo_url is None:
            logger.error(f"Failed to extract repo url from URL '{source}'")
            continue

        result.append((repo_name, repo_url[0]))

    return result
