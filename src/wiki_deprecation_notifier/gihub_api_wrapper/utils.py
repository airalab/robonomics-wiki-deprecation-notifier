from yarl import URL


def get_repo_owner(repo_url: str) -> str:
    source_url = URL(repo_url)
    owner, _ = source_url.path.lstrip("/").split("/", 1)
    return str(owner)


def get_repo_name(repo_url: str) -> str:
    source_url = URL(repo_url)
    owner, name, _ = source_url.path.lstrip("/").split("/", 2)
    return str(name)
