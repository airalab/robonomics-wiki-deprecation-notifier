import re
from contextlib import suppress

from semantic_version import Version


def extract_version_from_string(source_string: str) -> Version:
    versions = re.findall(r"\d*\.\d*\.*\d*", source_string)
    for version_string in filter(bool, versions):
        with suppress(ValueError):
            return Version.coerce(version_string)
    raise ValueError(f"String '{source_string}' does not contain any semantic version")


def notification_required(current_release_title: str, previous_release_title: str) -> bool:
    current = extract_version_from_string(current_release_title)
    previous = extract_version_from_string(previous_release_title)
    is_notification_required: bool = current.major > previous.major or current.minor > previous.minor
    return is_notification_required
