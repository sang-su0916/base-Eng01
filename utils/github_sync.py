import requests
import json
import base64
from typing import Dict, List, Optional

class GitHubSync:
    def __init__(self, token: Optional[str] = None):
        """GitHub API 연동을 위한 클래스를 초기화합니다."""
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'

    def get_file_content(self, owner: str, repo: str, path: str, ref: str = 'main') -> Optional[str]:
        """GitHub 저장소에서 파일 내용을 가져옵니다."""
        try:
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            content = response.json()
            if 'content' in content:
                decoded_content = base64.b64decode(content['content']).decode('utf-8')
                return decoded_content
            return None
            
        except Exception as e:
            print(f"GitHub 파일 읽기 오류: {str(e)}")
            return None

    def update_file(self, owner: str, repo: str, path: str, content: str, 
                   message: str, branch: str = 'main') -> bool:
        """GitHub 저장소의 파일을 업데이트합니다."""
        if not self.token:
            print("GitHub 토큰이 필요합니다.")
            return False

        try:
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            
            # 현재 파일 정보 가져오기
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            current_file = response.json()
            
            # 파일 업데이트
            data = {
                'message': message,
                'content': base64.b64encode(content.encode()).decode(),
                'sha': current_file['sha'],
                'branch': branch
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"GitHub 파일 업데이트 오류: {str(e)}")
            return False

    def create_file(self, owner: str, repo: str, path: str, content: str,
                   message: str, branch: str = 'main') -> bool:
        """GitHub 저장소에 새 파일을 생성합니다."""
        if not self.token:
            print("GitHub 토큰이 필요합니다.")
            return False

        try:
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            
            data = {
                'message': message,
                'content': base64.b64encode(content.encode()).decode(),
                'branch': branch
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"GitHub 파일 생성 오류: {str(e)}")
            return False 