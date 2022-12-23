from dataclasses import dataclass

from .Release import Release


@dataclass(frozen=True, slots=True)
class Repo:
    name: str
    url: str
    repo_owner: str
    repo_name: str
    latest_release: Release
