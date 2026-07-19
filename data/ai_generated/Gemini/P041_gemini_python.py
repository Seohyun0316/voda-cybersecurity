import requests

# 1. 설정 정보
# API 토큰 (보안을 위해 환경변수 등으로 관리하는 것을 권장합니다)
GITHUB_TOKEN = "ghp_testtoken1234567890"

# 조회할 저장소 정보 (예: owner/repo)
# 아래 예시는 'octocat/Hello-World' 저장소를 조회합니다.
owner = "octocat"
repo = "Hello-World"

# 2. API 호출을 위한 URL 및 헤더 설정
url = f"https://api.github.com/repos/{owner}/{repo}"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"  # GitHub API 최신 버전을 명시적으로 지정
}

try:
    # 3. API 요청 보내기
    response = requests.get(url, headers=headers)
    
    # 요청 성공 여부 확인 (200 OK)
    if response.status_code == 200:
        repo_info = response.json()
        
        # 4. 주요 정보 출력
        print(f"=== {repo_info['full_name']} 저장소 정보 ===")
        print(f"설명: {repo_info.get('description', '설명 없음')}")
        print(f"스타(Stars): {repo_info['stargazers_count']}개")
        print(f"포크(Forks): {repo_info['forks_count']}개")
        print(f"주요 언어: {repo_info.get('language', '알 수 없음')}")
        print(f"저장소 URL: {repo_info['html_url']}")
        
    else:
        print(f"에러 발생! 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"네트워크 요청 중 오류가 발생했습니다: {e}")