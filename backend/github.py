import httpx
import re
from typing import Optional


def parse_pr_url(url: str) -> Optional[tuple[str, str, int]]:
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url)
    if not match:
        return None
    return match.group(1), match.group(2), int(match.group(3))


async def fetch_pr_files(
    owner: str, repo: str, pr_number: int, token: Optional[str] = None
) -> list[dict]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=headers,
        )
        if response.status_code >= 400:
            return []
        files = response.json()

    result = []
    for f in files:
        if f.get("patch") and f.get("filename", "").endswith(
            (".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cpp", ".c", ".sol")
        ):
            result.append(
                {
                    "filename": f["filename"],
                    "patch": f["patch"],
                    "raw_url": f.get("raw_url", ""),
                }
            )
    return result
