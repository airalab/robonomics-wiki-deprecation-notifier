from dataclasses import dataclass
from datetime import datetime

from .Repo import Repo


@dataclass(frozen=True, slots=True)
class Article:
    filename: str
    url: str
    dependencies: list[Repo]
    last_modified_date: datetime

    @property
    def name(self) -> str:
        raise NotImplementedError  # TODO
