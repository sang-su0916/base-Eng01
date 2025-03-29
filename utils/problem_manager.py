import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
import uuid

class ProblemManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.problems_file = self.data_dir / "problems.json"
        self.pending_problems = []  # 검토 대기 중인 문제들
        self._load_problems()
        self._load_pending_problems()

    def _load_problems(self):
        """문제 데이터를 로드합니다."""
        if self.problems_file.exists():
            with open(self.problems_file, 'r', encoding='utf-8') as f:
                self.problems = json.load(f)
        else:
            self.problems = []

    def _save_problems(self):
        """문제 데이터를 저장합니다."""
        with open(self.problems_file, 'w', encoding='utf-8') as f:
            json.dump(self.problems, f, ensure_ascii=False, indent=2)

    def _load_pending_problems(self):
        """검토 대기 중인 문제들을 불러옵니다."""
        try:
            with open(self.data_dir / "pending_problems.json", 'r', encoding='utf-8') as f:
                self.pending_problems = json.load(f)
        except FileNotFoundError:
            self.pending_problems = []

    def _save_pending_problems(self):
        """검토 대기 중인 문제들을 파일에 저장합니다."""
        with open(self.data_dir / "pending_problems.json", 'w', encoding='utf-8') as f:
            json.dump(self.pending_problems, f, ensure_ascii=False, indent=2)

    def add_problem(self, title, type, content, difficulty, correct_answer, keywords=None, explanation=None, time_limit=None, points=None):
        """새로운 문제를 추가합니다."""
        problem = {
            'id': str(uuid.uuid4()),
            'title': title,
            'type': type,
            'content': content,
            'difficulty': difficulty,
            'correct_answer': correct_answer,
            'keywords': keywords or [],
            'explanation': explanation or '',
            'time_limit': time_limit or 30,
            'points': points or 100,
            'created_at': datetime.now().isoformat()
        }
        self.problems.append(problem)
        self._save_problems()
        return problem

    def get_problem(self, problem_id: int) -> Optional[Dict]:
        """특정 ID의 문제를 가져옵니다."""
        for problem in self.problems:
            if problem['id'] == problem_id:
                return problem
        return None

    def get_all_problems(self) -> List[Dict]:
        """모든 문제를 가져옵니다."""
        return self.problems

    def update_problem(self, problem_id: int, **kwargs) -> bool:
        """문제를 업데이트합니다."""
        for i, problem in enumerate(self.problems):
            if problem['id'] == problem_id:
                problem.update(kwargs)
                self.problems[i] = problem
                self._save_problems()
                return True
        return False

    def delete_problem(self, problem_id: int) -> bool:
        """문제를 삭제합니다."""
        for i, problem in enumerate(self.problems):
            if problem['id'] == problem_id:
                del self.problems[i]
                self._save_problems()
                return True
        return False

    def add_pending_problem(self, problem):
        """검토가 필요한 새로운 문제를 추가합니다."""
        if 'id' not in problem:
            problem['id'] = len(self.pending_problems) + 1
        problem['created_at'] = datetime.now().isoformat()
        problem['status'] = 'pending'
        self.pending_problems.append(problem)
        self._save_pending_problems()
        return True

    def get_pending_problems(self):
        """검토 대기 중인 문제들을 반환합니다."""
        return self.pending_problems

    def approve_problem(self, problem_id):
        """문제를 승인하고 정식 문제 목록에 추가합니다."""
        for i, problem in enumerate(self.pending_problems):
            if problem['id'] == problem_id:
                problem['status'] = 'approved'
                problem['approved_at'] = datetime.now().isoformat()
                # 승인된 문제를 정식 문제 목록에 추가
                self.add_problem(**problem)
                # 대기 목록에서 제거
                self.pending_problems.pop(i)
                self._save_pending_problems()
                return True
        return False

    def reject_problem(self, problem_id):
        """문제를 거절하고 대기 목록에서 제거합니다."""
        for i, problem in enumerate(self.pending_problems):
            if problem['id'] == problem_id:
                problem['status'] = 'rejected'
                problem['rejected_at'] = datetime.now().isoformat()
                self.pending_problems.pop(i)
                self._save_pending_problems()
                return True
        return False

    def get_problems_by_type(self, problem_type):
        """특정 유형의 문제 목록을 반환합니다."""
        return [p for p in self.problems if p['type'] == problem_type]

    def get_problems_by_difficulty(self, difficulty):
        """특정 난이도의 문제 목록을 반환합니다."""
        return [p for p in self.problems if p['difficulty'] == difficulty]

    def get_problems_by_keyword(self, keyword):
        """특정 키워드가 포함된 문제 목록을 반환합니다."""
        return [p for p in self.problems if keyword in p['keywords']]

    def get_problems_by_level(self, level):
        """특정 레벨에 맞는 문제 목록을 반환합니다."""
        difficulty_mapping = {
            '초급': 1,
            '중급': 2,
            '고급': 3
        }
        target_difficulty = difficulty_mapping.get(level, 2)  # 기본값: 중급
        return [p for p in self.problems if difficulty_mapping.get(p['difficulty'], 2) <= target_difficulty] 