import os
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]


def get_repo_info(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    data = response.json()

    return {
        "name": data["name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "language": data["language"]
    }


# Å×½ºÆ®
repo = get_repo_info(
    "octocat",
    "Hello-World"
)

print(repo)