import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class StudentManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.students_file = self.data_dir / "students.json"
        self.assignments_file = self.data_dir / "assignments.json"
        self._load_data()

    def _load_data(self):
        """학생 데이터와 할당된 문제 데이터를 로드합니다."""
        if self.students_file.exists():
            with open(self.students_file, 'r', encoding='utf-8') as f:
                self.students = json.load(f)
        else:
            self.students = []

        if self.assignments_file.exists():
            with open(self.assignments_file, 'r', encoding='utf-8') as f:
                self.assignments = json.load(f)
        else:
            self.assignments = []

    def _save_students(self):
        """학생 데이터를 저장합니다."""
        with open(self.students_file, 'w', encoding='utf-8') as f:
            json.dump(self.students, f, ensure_ascii=False, indent=2)

    def _save_assignments(self):
        """할당된 문제 데이터를 저장합니다."""
        with open(self.assignments_file, 'w', encoding='utf-8') as f:
            json.dump(self.assignments, f, ensure_ascii=False, indent=2)

    def add_student(self, student_data: Dict) -> bool:
        """새로운 학생을 추가합니다."""
        try:
            # 학생 ID 생성
            student_data['id'] = len(self.students) + 1
            student_data['created_at'] = datetime.now().isoformat()
            self.students.append(student_data)
            self._save_students()
            return True
        except Exception as e:
            print(f"학생 추가 중 오류 발생: {e}")
            return False

    def get_student(self, student_id: int) -> Optional[Dict]:
        """특정 ID의 학생 정보를 가져옵니다."""
        for student in self.students:
            if student['id'] == student_id:
                return student
        return None

    def get_student_by_name(self, name: str) -> Optional[Dict]:
        """이름으로 학생 정보를 가져옵니다."""
        for student in self.students:
            if student['name'] == name:
                return student
        return None

    def get_all_students(self) -> List[Dict]:
        """모든 학생 정보를 가져옵니다."""
        return self.students

    def update_student(self, student_id: int, student_data: Dict) -> bool:
        """학생 정보를 업데이트합니다."""
        for i, student in enumerate(self.students):
            if student['id'] == student_id:
                student_data['id'] = student_id
                student_data['created_at'] = student['created_at']
                self.students[i] = student_data
                self._save_students()
                return True
        return False

    def delete_student(self, student_id: int) -> bool:
        """학생을 삭제합니다."""
        for i, student in enumerate(self.students):
            if student['id'] == student_id:
                del self.students[i]
                self._save_students()
                # 학생에게 할당된 문제도 삭제
                self.assignments = [a for a in self.assignments if a['student_id'] != student_id]
                self._save_assignments()
                return True
        return False

    def assign_problems(self, student_id: int, problem_ids: List[int]) -> bool:
        """학생에게 문제를 할당합니다."""
        try:
            for problem_id in problem_ids:
                assignment = {
                    'id': len(self.assignments) + 1,
                    'student_id': student_id,
                    'problem_id': problem_id,
                    'assigned_at': datetime.now().isoformat(),
                    'completed': False,
                    'student_answer': None,
                    'submitted_at': None,
                    'score': None
                }
                self.assignments.append(assignment)
            self._save_assignments()
            return True
        except Exception as e:
            print(f"문제 할당 중 오류 발생: {e}")
            return False

    def get_student_assignments(self, student_id: int) -> List[Dict]:
        """학생에게 할당된 문제 목록을 가져옵니다."""
        return [a for a in self.assignments if a['student_id'] == student_id]

    def submit_answer(self, assignment_id: int, student_answer: str) -> bool:
        """학생의 답안을 제출합니다."""
        for assignment in self.assignments:
            if assignment['id'] == assignment_id:
                assignment['student_answer'] = student_answer
                assignment['submitted_at'] = datetime.now().isoformat()
                assignment['completed'] = True
                self._save_assignments()
                return True
        return False

    def grade_assignment(self, assignment_id: int, score: int) -> bool:
        """제출된 답안을 채점합니다."""
        for assignment in self.assignments:
            if assignment['id'] == assignment_id:
                assignment['score'] = score
                self._save_assignments()
                return True
        return False 