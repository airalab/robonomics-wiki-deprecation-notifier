import asyncio
from datetime import datetime
from typing import Any

import httpx

from .FileDescriptor import FileDescriptor


async def get_file_text_contents(client: httpx.AsyncClient, file_link: str) -> str:
    response = await client.get(file_link)
    return str(response.text)


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


async def get_files_in_dir(  # noqa: CAC001
    client: httpx.AsyncClient, repo_owner: str, repo_name: str, dir_path: str
) -> list[FileDescriptor]:
    dir_path = dir_path.lstrip("/")
    url = f"/repos/{repo_owner}/{repo_name}/contents/{dir_path}"
    response = await client.get(url=url)
    files = [
        FileDescriptor(
            name=file_data["name"],
            path=file_data["path"],
            download_url=file_data["download_url"],
        )
        for file_data in response.json()
    ]
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


async def get_latest_release_name_and_datetime(
    client: httpx.AsyncClient, repo_owner: str, repo_name: str
) -> tuple[str, datetime]:
    url = f"/repos/{repo_owner}/{repo_name}/releases"
    params = {"per_page": 1, "page": 1}
    response = await client.get(url=url, params=params)
    latest_releases: list[Any] = response.json()
    if not latest_releases:
        return "Unknown", datetime.fromtimestamp(0)
    latest_release = latest_releases[0]
    release_name = latest_release["name"]
    release_datetime = datetime.fromisoformat(latest_release["created_at"].rstrip("Z"))
    return release_name, release_datetime


async def create_new_issue(client: httpx.AsyncClient, repo_owner: str, repo_name: str, title: str, body: str) -> str:
    url = f"/{repo_owner}/{repo_name}/issues"
    json = {
        "title": title,
        "body": body,
    }
    response = await client.post(url=url, json=json)
    return str(response.json()["html_url"])
