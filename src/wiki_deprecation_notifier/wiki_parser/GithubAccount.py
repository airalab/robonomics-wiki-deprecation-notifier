from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GithubAccount:
    username: str

    @property
    def url(self) -> str:
        return f"https://github.com/{self.username}"

    @property
    def handle(self) -> str:
        return f"@{self.username}"
