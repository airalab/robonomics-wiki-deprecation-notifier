from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .Issue import Issue

if TYPE_CHECKING:
    from .DeprecationConflict import DeprecationConflict


def create_issue(conflict: DeprecationConflict) -> Issue:
    issue_title = "".join(  # noqa: ECE001
        (
            "[Deprecation]: ",
            f'Article "{conflict.article.name}" is deprecated due to ',
            f'a release "{conflict.dependency.latest_release.name}" ',
            f'in "{conflict.dependency.name}".',
        )
    )
    if contributors := conflict.article.contributors:
        contributors_block = "".join(
            (
                "An action has been requested from the article contributors:\n",
                "\n".join(f"- {c.handle}" for c in contributors),
                "\n\n",
            )
        )
    else:
        contributors_block = ""

    issue_body = "".join(  # noqa: ECE001
        (
            "### Issue description\n\n",
            f'Article ["{conflict.article.name}"]({conflict.article.url}) ',
            "has been automatically marked as deprecated due to ",
            f'a recent release ["{conflict.dependency.latest_release.name}"]({conflict.dependency.latest_release.url}) ',
            f'in ["{conflict.dependency.name}"]({conflict.dependency.url}).',
            "\n\n",
            contributors_block,
            f"Deprecation reference id: {conflict.conflict_hash}",
            "\n\n### Doc Page\n\n",
            f"[{conflict.article.name}]({conflict.article.url})",
            "\n\n### Note\n\n",
            "This issue has been automatically created by the ",
            "[Wiki deprecation bot](https://github.com/airalab/robonomics-wiki-deprecation-notifier). ",
            "If this is a false alarm and the article is not actually deprecated - ",
            "feel free to close this issue. It will not be created again "
            f"unless a new release comes out in [{conflict.dependency.name}]({conflict.dependency.url}).",
        )
    )
    return Issue(
        repo_owner=os.environ["WIKI_REPO_OWNER"],
        repo_name=os.environ["WIKI_REPO_NAME"],
        title=issue_title,
        body=issue_body,
    )
