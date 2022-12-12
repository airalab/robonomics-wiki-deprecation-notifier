import asyncio
import os
from time import time

import httpx
import httpx_cache
from loguru import logger

from .gihub_api_wrapper.api_wrappers import get_files_in_dir, get_latest_release_name_url_and_datetime
from .gihub_api_wrapper.client_settings import httpx_client_settings
from .gihub_api_wrapper.FileDescriptor import FileDescriptor
from .gihub_api_wrapper.utils import get_repo_name, get_repo_owner
from .wiki_parser.Article import Article
from .wiki_parser.front_matter_parser import extract_contributors_usernames, extract_dependencies
from .wiki_parser.GithubAccount import GithubAccount
from .wiki_parser.Release import Release
from .wiki_parser.Repo import Repo


async def get_dependency_map() -> list[Article]:
    t0 = time()
    logger.debug("Started gathering dependency map")
    async with httpx_cache.AsyncClient(**httpx_client_settings) as client:
        article_files = await get_files_in_dir(
            client=client,
            repo_owner=os.environ["WIKI_REPO_OWNER"],
            repo_name=os.environ["WIKI_REPO_NAME"],
            dir_path="/docs",
        )
        logger.debug(f"Fetched {len(article_files)} articles in {round(time() - t0, 4)}s")
        tasks = (_parse_article(client=client, article_file=article_file) for article_file in article_files)
        articles: list[Article] = await asyncio.gather(*tasks)
        return articles


async def _parse_article(client: httpx.AsyncClient, article_file: FileDescriptor) -> Article:
    t0 = time()
    article_dependencies = extract_dependencies(article_file.content)
    contributors = [
        GithubAccount(username=contributor) for contributor in extract_contributors_usernames(article_file.content)
    ]
    dependencies_tasks = (
        _get_repo_w_latest_release(client=client, project_name=project_name, repo_url=repo_url)
        for project_name, repo_url in article_dependencies
    )
    dependencies: list[Repo] = await asyncio.gather(*dependencies_tasks)
    article = Article(
        filename=article_file.name,
        url=article_file.download_url,
        dependencies=dependencies,
        contributors=contributors,
        last_modified_date=article_file.last_modified_date,
    )
    logger.debug(f"Dependency map gathering for article {article.name} complete in {round(time() - t0, 4)}s")
    return article


async def _get_repo_w_latest_release(client: httpx.AsyncClient, project_name: str, repo_url: str) -> Repo:
    repo_owner = get_repo_owner(repo_url)
    repo_name = get_repo_name(repo_url)
    release_name, release_url, release_date = await get_latest_release_name_url_and_datetime(
        client=client, repo_owner=repo_owner, repo_name=repo_name
    )
    release = Release(
        name=release_name,
        url=release_url,
        date=release_date,
    )
    base_repo_url = "/".join(repo_url.split("/")[:5])
    return Repo(name=project_name, url=base_repo_url, latest_release=release)
