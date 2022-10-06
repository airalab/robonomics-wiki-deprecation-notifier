from dataclasses import dataclass, field
from datetime import datetime

from .DeprecationConflict import DeprecationConflict
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

    def get_conflicts(self) -> list[DeprecationConflict]:
        conflicts = []
        for dependency in self.dependencies:
            if dependency.latest_release.date > self.last_modified_date:
                conflict = DeprecationConflict(
                    article=self,
                    dependency=dependency,
                )
                conflicts.append(conflict)

        return conflicts
