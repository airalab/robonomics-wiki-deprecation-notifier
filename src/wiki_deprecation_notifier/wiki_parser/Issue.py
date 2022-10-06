from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Issue:
    repo_owner: str
    repo_name: str
    title: str
    body: str
