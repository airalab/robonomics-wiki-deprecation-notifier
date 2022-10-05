from dataclasses import dataclass

from .Release import Release


@dataclass(frozen=True, slots=True)
class Repo:
    name: str
    url: str
    latest_release: Release
