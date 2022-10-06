from dataclasses import dataclass, field
from datetime import datetime

from .GithubAccount import GithubAccount
from .Repo import Repo


@dataclass(frozen=True, slots=True)
class Article:
    filename: str
    url: str
    dependencies: list[Repo]
    last_modified_date: datetime
    contributors: list[GithubAccount] = field(default_factory=list)

    @property
    def name(self) -> str:
        raise NotImplementedError  # TODO
