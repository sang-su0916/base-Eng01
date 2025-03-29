import google.generativeai as genai
import json
from typing import List, Dict
import streamlit as st
import os
from datetime import datetime, timedelta

class AIProblemGenerator:
    def __init__(self):
        """AI 문제 생성기를 초기화합니다."""
        self._initialize_daily_count()
        self._load_api_key()
        
    def _initialize_daily_count(self):
        """일일 생성 카운트를 초기화합니다."""
        # 날짜가 바뀌었는지 확인
        current_date = datetime.now().date()
        last_reset = st.session_state.get('last_count_reset')
        
        if not last_reset or last_reset != current_date:
            st.session_state.daily_generation_count = 0
            st.session_state.last_count_reset = current_date
            
    def _load_api_key(self):
        """API 키를 로드하고 설정합니다."""
        api_key = st.session_state.get('gemini_api_key')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            
    def set_api_key(self, api_key: str) -> bool:
        """API 키를 설정합니다."""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            st.session_state.gemini_api_key = api_key
            return True
        except Exception:
            return False
            
    def remove_api_key(self):
        """API 키를 제거합니다."""
        if 'gemini_api_key' in st.session_state:
            del st.session_state.gemini_api_key
        self.model = None
        
    def can_generate_more(self) -> bool:
        """추가 생성이 가능한지 확인합니다."""
        return st.session_state.get('daily_generation_count', 0) < 100
        
    def get_remaining_generations(self) -> int:
        """남은 생성 가능 횟수를 반환합니다."""
        return 100 - st.session_state.get('daily_generation_count', 0)
        
    def generate_problems(self, 
                         problem_type: str,
                         difficulty: int,
                         count: int = 1,
                         topic: str = None) -> List[Dict]:
        """AI를 사용하여 문제를 생성합니다."""
        
        # API 키 확인
        if not self.model:
            raise ValueError("API 키가 설정되지 않았습니다.")
            
        # 일일 생성 한도 확인
        current_count = st.session_state.get('daily_generation_count', 0)
        if current_count + count > 100:
            raise ValueError(f"일일 생성 한도(100개)를 초과했습니다. 남은 생성 가능 횟수: {100 - current_count}개")
            
        # 프롬프트 생성
        prompt = f"""
        영어 교육 전문가로서 다음 조건에 맞는 영어 문제를 생성해주세요:
        
        조건:
        - 문제 유형: {problem_type}
        - 난이도: {difficulty}점 (1-5점 척도)
        {f'- 주제: {topic}' if topic else ''}
        - 생성할 문제 수: {count}개
        
        각 문제는 다음 JSON 형식으로 생성해주세요:
        {{
            "type": "문제 유형",
            "title": "문제 제목",
            "content": "문제 내용",
            "difficulty": 난이도,
            "correct_answer": "정답",
            "keywords": ["채점", "키워드", "목록"],
            "explanation": "문제 해설"
        }}
        
        응답은 반드시 유효한 JSON 형식이어야 하며, 여러 문제의 경우 JSON 배열로 반환해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # JSON 응답 파싱
            response_text = response.text
            # JSON 부분만 추출 (텍스트에서 {...} 또는 [...] 찾기)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start == -1:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
            if json_start == -1 or json_end == 0:
                raise ValueError("유효한 JSON 응답을 찾을 수 없습니다.")
                
            json_str = response_text[json_start:json_end]
            problems = json.loads(json_str)
            
            # 단일 문제인 경우 리스트로 변환
            if not isinstance(problems, list):
                problems = [problems]
                
            # 문제 검증
            validated_problems = []
            for problem in problems:
                if self.validate_problem(problem):
                    validated_problems.append(problem)
                    
            if not validated_problems:
                raise ValueError("유효한 문제가 생성되지 않았습니다.")
                
            # 생성 카운트 증가
            st.session_state.daily_generation_count = current_count + len(validated_problems)
                
            return validated_problems
            
        except Exception as e:
            raise Exception(f"문제 생성 중 오류가 발생했습니다: {str(e)}")
            
    def validate_problem(self, problem: Dict) -> bool:
        """생성된 문제가 올바른 형식인지 검증합니다."""
        required_fields = ['type', 'title', 'content', 'difficulty', 
                         'correct_answer', 'keywords', 'explanation']
        
        # 모든 필수 필드가 있는지 확인
        if not all(field in problem for field in required_fields):
            return False
            
        # 타입 검증
        try:
            assert isinstance(problem['type'], str)
            assert isinstance(problem['title'], str)
            assert isinstance(problem['content'], str)
            assert isinstance(problem['difficulty'], (int, float))
            assert isinstance(problem['correct_answer'], str)
            assert isinstance(problem['keywords'], list)
            assert isinstance(problem['explanation'], str)
            assert all(isinstance(k, str) for k in problem['keywords'])
            return True
        except:
            return False 