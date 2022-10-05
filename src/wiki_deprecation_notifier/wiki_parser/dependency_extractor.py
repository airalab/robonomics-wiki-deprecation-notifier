import yaml
from yarl import URL

TARGET_ORGANISATIONS = {"Multi-Agent-io", "airalab"}  # TODO: Make configurable


def extract_dependencies(article: str) -> list[tuple[str, str]]:  # noqa: CAC001
    front_matter: dict[str, str | list[str]] = next(yaml.load_all(article, Loader=yaml.FullLoader))
    dependencies: list[str] = front_matter.get("tools", [])  # type: ignore
    result = []

    for dependency in dependencies:
        try:
            name, source = dependency.rsplit(" ", 1)
        except ValueError:
            continue

        source_url = URL(source)

        if source_url.host != "github.com":
            continue

        organisation, _ = source_url.path.lstrip("/").split("/", 1)

        if organisation not in TARGET_ORGANISATIONS:
            continue

        result.append((name, source))

    return result
