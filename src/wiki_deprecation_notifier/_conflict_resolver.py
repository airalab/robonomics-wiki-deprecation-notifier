from .wiki_parser.Article import Article
from .wiki_parser.DeprecationConflict import DeprecationConflict


def get_conflicts(articles: list[Article]) -> list[DeprecationConflict]:
    conflicts = []
    for article in articles:
        article_conflicts = article.get_conflicts()
        conflicts.extend(article_conflicts)
    return conflicts


async def resolve_conflicts(conflicts: list[DeprecationConflict]) -> None:
    raise NotImplementedError  # TODO
