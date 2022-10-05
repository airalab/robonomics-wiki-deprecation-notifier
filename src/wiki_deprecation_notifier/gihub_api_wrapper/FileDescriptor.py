from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FileDescriptor:
    name: str
    path: str
    download_url: str
    content: str = ""
    last_modified_date: datetime = field(default_factory=datetime.now)
