import asyncio
import sqlite3

import httpx

from .db_wrapper.db import connection as db_connection
from .gihub_api_wrapper.api_wrappers import create_new_issue
from .gihub_api_wrapper.client_settings import httpx_client_settings
from .wiki_parser.Article import Article
from .wiki_parser.DeprecationConflict import DeprecationConflict
from .wiki_parser.issue_generation import create_issue


def get_conflicts(articles: list[Article]) -> list[DeprecationConflict]:
    conflicts = []
    for article in articles:
        article_conflicts = article.get_conflicts()
        conflicts.extend(article_conflicts)
    return conflicts


def conflict_saved(conflict: DeprecationConflict, connection: sqlite3.Connection) -> bool:
    cursor = connection.cursor()
    statement = "SELECT * FROM conflicts WHERE hash=?;"
    cursor.execute(statement, (conflict.conflict_hash,))
    return bool(cursor.fetchone())


def save_conflict(conflict: DeprecationConflict, connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    statement = "INSERT INTO conflicts VALUES (?, ?, ?, ?);"
    cursor.execute(statement, (conflict.conflict_hash, conflict.conflict_signature, True, False))


async def resolve_conflicts(conflicts: list[DeprecationConflict]) -> None:
    for conflict in conflicts:
        if conflict_saved(conflict, db_connection):
            continue
        save_conflict(conflict, db_connection)
        db_connection.commit()


async def post_issue(client: httpx.AsyncClient, conflict: DeprecationConflict, connection: sqlite3.Connection) -> str:
    issue = create_issue(conflict)
    issue_url: str = await create_new_issue(
        client=client,
        repo_owner=issue.repo_owner,
        repo_name=issue.repo_name,
        title=issue.title,
        body=issue.body,
    )
    cursor = connection.cursor()
    statement = "UPDATE conflicts SET action_done=? WHERE hash=?;"
    cursor.execute(statement, (True, conflict.conflict_hash))
    return issue_url


def get_pending_conflicts_hashes(connection: sqlite3.Connection) -> set[str]:
    cursor = connection.cursor()
    statement = "SELECT hash FROM conflicts WHERE action_required=1 AND action_done=0;"
    cursor.execute(statement)
    return {result[0] for result in cursor.fetchall()}


async def create_issues(conflicts: list[DeprecationConflict]) -> list[str]:
    pending_conflicts_hashes = get_pending_conflicts_hashes(db_connection)

    async with httpx.AsyncClient(**httpx_client_settings) as client:
        conflict_tasks = (
            post_issue(client=client, conflict=conflict, connection=db_connection)
            for conflict in conflicts
            if conflict.conflict_hash in pending_conflicts_hashes
        )
        issue_urls: list[str] = await asyncio.gather(*conflict_tasks)

    db_connection.commit()
    return issue_urls
