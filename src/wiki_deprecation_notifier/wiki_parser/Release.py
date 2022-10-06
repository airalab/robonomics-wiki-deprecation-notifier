from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Release:
    name: str
    url: str
    date: datetime
