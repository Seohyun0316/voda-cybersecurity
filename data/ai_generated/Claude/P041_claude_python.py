import requests

GITHUB_TOKEN = 'ghp_testtoken1234567890'

def get_repo_info(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

def list_repos(username):
    url = f'https://api.github.com/users/{username}/repos'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == '__main__':
    owner = input('GitHub 사용자명: ')
    repo = input('저장소 이름: ')
    info = get_repo_info(owner, repo)
    print(f"이름: {info.get('name')}")
    print(f"설명: {info.get('description')}")
    print(f"별: {info.get('stargazers_count')}")
