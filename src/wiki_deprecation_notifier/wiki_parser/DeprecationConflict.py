from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .Issue import Issue
from .issue_generation import create_issue

if TYPE_CHECKING:
    from .Article import Article
    from .Repo import Repo


@dataclass(frozen=True, slots=True)
class DeprecationConflict:
    article: Article
    dependency: Repo

    @property
    def conflict_signature(self) -> str:
        signature_parts = (
            self.article.url,
            str(self.article.last_modified_date),
            self.dependency.name,
            self.dependency.latest_release.name,
            str(self.dependency.latest_release.date),
        )
        return "; ".join(signature_parts)

    @property
    def conflict_hash(self) -> str:
        return hashlib.md5(self.conflict_signature.encode()).hexdigest()

    @property
    def issue(self) -> Issue:
        return create_issue(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeprecationConflict):
            raise NotImplementedError(
                "An instance of DeprecationConflict can only be compared with another instance of type DeprecationConflict"
            )
        return self.conflict_hash == other.conflict_hash
