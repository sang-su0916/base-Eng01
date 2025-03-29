import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import json

class ProblemManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.problems_file = self.data_dir / "problems.json"
        self._load_problems()

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

    def add_problem(self, problem_data: Dict) -> bool:
        """새로운 문제를 추가합니다."""
        try:
            # 문제 ID 생성
            problem_data['id'] = len(self.problems) + 1
            self.problems.append(problem_data)
            self._save_problems()
            return True
        except Exception as e:
            print(f"문제 추가 중 오류 발생: {e}")
            return False

    def get_problem(self, problem_id: int) -> Optional[Dict]:
        """특정 ID의 문제를 가져옵니다."""
        for problem in self.problems:
            if problem['id'] == problem_id:
                return problem
        return None

    def get_all_problems(self) -> List[Dict]:
        """모든 문제를 가져옵니다."""
        return self.problems

    def update_problem(self, problem_id: int, problem_data: Dict) -> bool:
        """문제를 업데이트합니다."""
        for i, problem in enumerate(self.problems):
            if problem['id'] == problem_id:
                problem_data['id'] = problem_id
                self.problems[i] = problem_data
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