import asyncio
from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from .FileDescriptor import FileDescriptor


@logger.catch(reraise=True)
async def get_file_text_contents(client: httpx.AsyncClient, file_link: str) -> str:
    response = await client.get(file_link)
    return str(response.text)


@logger.catch(reraise=True)
async def get_files_last_modified_date(
    client: httpx.AsyncClient, repo_owner: str, repo_name: str, file_path: str
) -> datetime:
    url = f"/repos/{repo_owner}/{repo_name}/commits"
    params = {
        "path": file_path,
        "page": 1,
        "per_page": 1,
    }
    response = await client.get(url=url, params=params)
    date = response.json()[0]["commit"]["committer"]["date"]
    return datetime.fromisoformat(date.rstrip("Z"))


@logger.catch(reraise=True)
async def get_files_in_dir(  # noqa: CAC001
    client: httpx.AsyncClient, repo_owner: str, repo_name: str, dir_path: str
) -> list[FileDescriptor]:
    dir_path = dir_path.lstrip("/")
    url = f"/repos/{repo_owner}/{repo_name}/contents/{dir_path}"
    response = await client.get(url=url)
    response_data = response.json()
    files = []

    for file_entry in response_data:
        if file_entry.get("type") != "file":
            continue
        if not file_entry.get("name", "").endswith(".md"):
            continue
        entry = FileDescriptor(
            name=file_entry["name"],
            path=file_entry["path"],
            download_url=file_entry["download_url"],
        )
        files.append(entry)

    date_tasks = (
        get_files_last_modified_date(
            client=client,
            repo_owner=repo_owner,
            repo_name=repo_name,
            file_path=file.path,
        )
        for file in files
    )
    dates = await asyncio.gather(*date_tasks)
    content_tasks = (
        get_file_text_contents(
            client=client,
            file_link=file.download_url,
        )
        for file in files
    )
    contents = await asyncio.gather(*content_tasks)

    for file, date, content in zip(files, dates, contents):
        file.last_modified_date = date
        file.content = content

    return files


@logger.catch(reraise=True)
async def get_latest_release_name_url_and_datetime(
    client: httpx.AsyncClient, repo_owner: str, repo_name: str
) -> tuple[str, str, datetime]:
    url = f"/repos/{repo_owner}/{repo_name}/releases"
    params = {"per_page": 1, "page": 1}

    default_return = ("Unknown", "Unknown", datetime.fromtimestamp(0))
    try:
        response = await client.get(url=url, params=params)
        latest_releases: list[Any] = response.json()
        if not latest_releases:
            raise ValueError(f"No releases found in repository '{repo_owner}/{repo_name}'")
    except httpx.HTTPStatusError as e:
        logger.error(f"Could not obtain releases from repo '{repo_owner}/{repo_name}'. Private repository? {e}")
        return default_return
    except ValueError as e:
        logger.warning(str(e))
        return default_return

    latest_release = latest_releases[0]
    release_name = latest_release["name"]
    release_url = latest_release["html_url"]
    release_datetime = datetime.fromisoformat(latest_release["created_at"].rstrip("Z"))
    return release_name, release_url, release_datetime


@logger.catch(reraise=True)
async def get_latest_release_titles(
    client: httpx.AsyncClient, repo_owner: str, repo_name: str, release_count: int
) -> list[str]:
    url = f"/repos/{repo_owner}/{repo_name}/releases"
    params = {"per_page": release_count, "page": 1}

    try:
        response = await client.get(url=url, params=params)
        latest_releases: list[Any] = response.json()
        if len(latest_releases) < release_count:
            raise ValueError(f"No {release_count} releases found in repository '{repo_owner}/{repo_name}'")
        return [release["name"] for release in latest_releases]
    except httpx.HTTPStatusError as e:
        logger.error(f"Could not obtain releases from repo '{repo_owner}/{repo_name}'. Private repository? {e}")
    except ValueError as e:
        logger.warning(str(e))

    return []


@logger.catch(reraise=True)
async def create_new_issue(  # noqa: CFQ002
    client: httpx.AsyncClient,
    repo_owner: str,
    repo_name: str,
    title: str,
    body: str,
    labels: list[str] | None = None,
    assignees: list[str] | None = None,
) -> str:
    url = f"/repos/{repo_owner}/{repo_name}/issues"
    json: dict[str, str | list[str]] = {
        "title": title,
        "body": body,
    }
    if labels:
        json["labels"] = labels
    if assignees:
        json["assignees"] = assignees

    try:
        response = await client.post(url=url, json=json)
    except httpx.HTTPStatusError as e:
        # FIXME: Assignee cannot be a person other than organisation member or repo contributor.
        # If one of the article contributors is not applicable for assignee - the request will return code 422.
        # For now we will just drop assignees all together in this case, as there is no reliable way to know
        # if an account can be an assignee or not
        if "assignees" in json:
            del json["assignees"]
        logger.warning(f"Failed to create an issue. Trying again without specifying the issue assignees. {e}")
        response = await client.post(url=url, json=json)

    return str(response.json()["html_url"])
