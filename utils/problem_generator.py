import pandas as pd
from typing import List, Dict
import random
from datetime import datetime

class ProblemGenerator:
    def __init__(self):
        # 문제 유형별 템플릿
        self.templates = {
            "문법": [
                "다음 문장의 괄호 안에 들어갈 알맞은 표현을 고르시오.",
                "다음 문장을 주어진 시제로 바꾸어 쓰시오.",
                "다음 문장의 틀린 부분을 찾아 고치시오."
            ],
            "어휘": [
                "다음 단어의 알맞은 의미를 고르시오.",
                "다음 문장의 빈칸에 들어갈 가장 적절한 단어를 고르시오.",
                "다음 단어와 반대되는 의미의 단어를 쓰시오."
            ],
            "독해": [
                "다음 글을 읽고 물음에 답하시오.",
                "다음 글의 주제로 가장 적절한 것을 고르시오.",
                "다음 글의 빈칸에 들어갈 가장 적절한 내용을 고르시오."
            ],
            "작문": [
                "다음 주제에 대해 영어로 작문하시오.",
                "다음 상황을 영어로 표현하시오.",
                "다음 문장을 영작하시오."
            ],
            "회화": [
                "다음 대화의 빈칸에 들어갈 가장 적절한 표현을 고르시오.",
                "다음 상황에서 사용할 수 있는 적절한 표현을 쓰시오.",
                "다음 대화를 완성하시오."
            ]
        }
        
        # 난이도별 키워드
        self.difficulty_keywords = {
            "초급": ["be동사", "현재시제", "일상생활", "기본 단어", "간단한 문장"],
            "중급": ["과거시제", "미래시제", "조동사", "관계대명사", "중급 어휘"],
            "고급": ["가정법", "분사구문", "이디엄", "전문용어", "복잡한 구문"]
        }
    
    def generate_problems(self, problem_type: str, difficulty: str, count: int = 3) -> list:
        """지정된 유형과 난이도의 문제를 생성합니다."""
        problems = []
        templates = self.templates.get(problem_type, [])
        keywords = self.difficulty_keywords.get(difficulty, [])
        
        for i in range(count):
            template = random.choice(templates)
            keyword = random.choice(keywords)
            
            problem = {
                'id': f"{datetime.now().strftime('%Y%m%d%H%M%S')}{i}",
                'title': f"{problem_type} - {keyword}",
                'type': problem_type,
                'difficulty': difficulty,
                'content': self._generate_content(template, keyword, difficulty),
                'model_answer': self._generate_model_answer(problem_type, difficulty),
                'time_limit': self._get_time_limit(difficulty),
                'keywords': [keyword],
                'created_at': datetime.now().isoformat()
            }
            problems.append(problem)
        
        return problems
    
    def _generate_content(self, template: str, keyword: str, difficulty: str) -> str:
        """문제 내용을 생성합니다."""
        # 실제 구현에서는 더 복잡한 로직이 필요할 수 있습니다
        return f"{template}\n\n[{difficulty} - {keyword}에 관한 문제 내용]"
    
    def _generate_model_answer(self, problem_type: str, difficulty: str) -> str:
        """모범 답안을 생성합니다."""
        # 실제 구현에서는 더 복잡한 로직이 필요할 수 있습니다
        return f"[{problem_type} - {difficulty} 수준의 모범 답안]"
    
    def _get_time_limit(self, difficulty: str) -> int:
        """난이도에 따른 제한시간을 반환합니다."""
        return {
            "초급": 15,
            "중급": 20,
            "고급": 30
        }.get(difficulty, 20)

    @staticmethod
    def save_to_csv(problems: List[Dict], filepath: str) -> None:
        """문제를 CSV 파일로 저장합니다."""
        df = pd.DataFrame(problems)
        df.to_csv(filepath, index=False)

    @staticmethod
    def save_to_json(problems: List[Dict], filepath: str) -> None:
        """문제를 JSON 파일로 저장합니다."""
        df = pd.DataFrame(problems)
        df.to_json(filepath, orient='records') 