# Robonomics Wiki Deprecation Notifier

This tool is designed to prevent
wiki articles from getting deprecated and irrelevant by notifying the article's contributors of the potential
deprecation.

## How It Works

This daemon runs on set schedule to identify potential deprecations and notify contributors.
The workflow and the algorithm used is described below.

## 1. Gathering the Dependency Map of the Wiki

Every article in the `/docs/en` directory of the repository is listed to gather the list of all wiki articles.
Then, every article's text is parsed to extract the front matter block, containing the links to the contributors'
accounts and all the technologies, which are mentioned in the article. Date of last change made to the article is
also extracted.

The technologies, mentioned in the article, are referred to as its dependencies. The dependencies are filtered, so
that only GitHub repositories are used. Then, repositories are filtered by owner to ensure that only the
repositories, that are created and directly controlled by Robonomics team and its associates are marked as tracked
dependencies.

The result of this step is the "dependency map" is a collection of all wiki articles mapped to their tracked
dependencies and contributors. At this stage, the date of last change is also known for every wiki article.

## 2. Identifying Potential Deprecations Based on Releases

Having the dependency map on hand, we can identify potential deprecations. For that, we fetch the latest release
date for every tracked dependency the article has. If the release date of the dependency exceeds the last modified
date of the article it is identified as a deprecation conflict.

The result of this process is a map of deprecation conflicts, pointing to the concrete articles and their dependencies,
that match the deprecation criteria.

Every deprecation conflict is hashed using its unique attributes (the deprecation conflict signature). This hash is
referred to as "deprecation reference" or "deprecation hash". The hash is needed to avoid duplicates of
notifications on the next step.

Every new deprecation conflict is saved to the database for later reference.

## 3. Creating Issues

For each of the newly identified deprecation conflicts an issue shall be created in the Robonomics Wiki repository
to address the deprecation.

The database containing the information about the known deprecations is parsed identify the new ones and avoid duplicate
issues. For every new deprecation an issue is created in the wiki repository tagging all the article's contributors.
The info about the created issue is saved to the DB.

## Deployment

This app runs on the set schedule using the GitHub actions platform. The schedule of the runs can be altered by
modifying the Cron syntax in the `/.github/dcheduled_run.yml` file.

Settings can be applied using the environment variables. Environment variables can either be set using the `.env`
file or the repository secrets.

The environment variables and their meanings are listed below.

- `RUNNER_MODE` (string) - Set to "single" for a single run or "daemon" for a daemon mode: a single process running
  multiple times every set amount of seconds (delay). Defaults to "single".
- `SLEEP_DELAY` (integer) - Sleep delay in seconds between runs (daemon mode). Defaults to 3600.
- `WIKI_REPO_NAME` (string) - Robonomics wiki repository name.
- `WIKI_REPO_OWNER` (string) - Robonomics wiki repository owner account (organisation) name.
- `TARGET_REPO_OWNERS` (JSON array of strings) - Only repositories owned by these accounts (organisations) will be
  marked as tracked dependencies.
- `SKIP_PATCH_RELEASES` (boolean) - Whether to skip patch releases in dependencies or not (defaults to `false`)
- `FILTER_REPOS_BY_OWNERS` (boolean) - Whether to filter repositories by their owner or not (defaults to `true`)
- `GITHUB_API_TOKEN` (string) - Since this app makes heavy use of the GitHub API, you need to generate and provide an
  API token for the bot.

If you want to deploy the application as a standalone daemon inside a Docker container you can use the Dockerfile
provided. Supply the provided environment variables to your container using a `docker-compose.yml`, `docker run`
syntax or by mounting the `.env` file inside the container using Docker volumes.

## Contributing

Create issues in this repository if there are any problems with this app or if you want to communicate a feature
request. Fork this repository and file a pull request to contribute to the app development.

This project complies with the code formatting guidelines defined in the provided `.pre-commit-config.yaml` file.

This repository uses semantic versioning and conventional commits to describe its updates.
