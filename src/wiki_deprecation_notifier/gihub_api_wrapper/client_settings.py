import os

import httpx

API_TOKEN = os.environ["GITHUB_API_TOKEN"]


async def raise_on_4xx_5xx(response: httpx.Response) -> None:
    response.raise_for_status()


headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {API_TOKEN}",
}
httpx_client_settings = {
    "base_url": "https://api.github.com",
    "headers": headers,
    "event_hooks": {"response": [raise_on_4xx_5xx]},
    "timeout": 30.0,  # FIXME: Reduce timeout for production deployment
}
