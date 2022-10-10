import json
import os
from functools import lru_cache
from typing import Any

import yaml
from yarl import URL

TARGET_REPO_OWNERS = set(json.loads(os.getenv("TARGET_REPO_OWNERS", '["Multi-Agent-io", "airalab"]')))


@lru_cache
def extract_front_matter(source_text: str) -> dict[str, Any]:
    return next(yaml.load_all(source_text, Loader=yaml.FullLoader), {})


def extract_contributors_usernames(article: str) -> list[str]:
    front_matter: dict[str, str | list[str]] = extract_front_matter(article)
    return front_matter.get("contributors", [])  # type: ignore


def extract_dependencies(article: str) -> list[tuple[str, str]]:  # noqa: CAC001
    front_matter: dict[str, str | list[str]] = extract_front_matter(article)
    dependencies: list[str] = front_matter.get("tools", [])  # type: ignore
    result = []

    for dependency in dependencies:
        try:
            name, source = dependency.rsplit(" ", 1)
        except ValueError:
            continue

        source_url = URL(source)

        if source_url.host != "github.com":
            continue

        organisation, _ = source_url.path.lstrip("/").split("/", 1)

        if organisation not in TARGET_REPO_OWNERS:
            continue

        result.append((name, source))

    return result
