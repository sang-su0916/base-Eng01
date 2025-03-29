import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import random

class StudentManager:
    def __init__(self):
        """학생 관리자를 초기화합니다."""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.students_file = self.data_dir / "students.json"
        self.assignments_file = self.data_dir / "assignments.json"
        self.settings_file = self.data_dir / "settings.json"
        self.problem_requests_file = self.data_dir / "problem_requests.json"
        
        # 초기화
        self.students = []
        self.assignments = []
        self.settings = {}
        self.problem_requests = []
        
        self._load_data()
    
    def _load_data(self):
        """데이터를 로드합니다."""
        # 학생 데이터 로드
        if self.students_file.exists():
            with open(self.students_file, 'r', encoding='utf-8') as f:
                self.students = json.load(f)
            
        # 과제 데이터 로드
        if self.assignments_file.exists():
            with open(self.assignments_file, 'r', encoding='utf-8') as f:
                self.assignments = json.load(f)
            
        # 설정 데이터 로드
        if self.settings_file.exists():
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                'auto_assign': {
                    'enabled': True,
                    'options': [10, 20],
                    'time_limit': 30,
                    'max_daily_problems': 50
                }
            }
            
        # 문제 요청 데이터 로드
        if self.problem_requests_file.exists():
            with open(self.problem_requests_file, 'r', encoding='utf-8') as f:
                self.problem_requests = json.load(f)
        else:
            self.problem_requests = []
    
    def _save_data(self):
        """데이터를 저장합니다."""
        # 학생 데이터 저장
        with open(self.students_file, 'w', encoding='utf-8') as f:
            json.dump(self.students, f, ensure_ascii=False, indent=2)
            
        # 과제 데이터 저장
        with open(self.assignments_file, 'w', encoding='utf-8') as f:
            json.dump(self.assignments, f, ensure_ascii=False, indent=2)
            
        # 설정 데이터 저장
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
            
        # 문제 요청 데이터 저장
        with open(self.problem_requests_file, 'w', encoding='utf-8') as f:
            json.dump(self.problem_requests, f, ensure_ascii=False, indent=2)
    
    def add_student(self, name, grade, level, contact=None, notes=None):
        """새로운 학생을 추가합니다."""
        student = {
            'id': str(uuid.uuid4()),
            'name': name,
            'grade': grade,
            'level': level,
            'contact': contact or '',
            'notes': notes or '',
            'status': '활성',
            'created_at': datetime.now().isoformat()
        }
        self.students.append(student)
        self._save_data()
        return student
    
    def get_all_students(self):
        """모든 학생 목록을 반환합니다."""
        return self.students
    
    def get_student(self, student_id):
        """특정 학생의 정보를 반환합니다."""
        for student in self.students:
            if student['id'] == student_id:
                return student
        return None
    
    def update_student(self, student_id, **kwargs):
        """학생 정보를 업데이트합니다."""
        for student in self.students:
            if student['id'] == student_id:
                student.update(kwargs)
                self._save_data()
                return True
        return False
    
    def delete_student(self, student_id):
        """학생을 삭제합니다."""
        for i, student in enumerate(self.students):
            if student['id'] == student_id:
                del self.students[i]
                self._save_data()
                return True
        return False
    
    def get_auto_assign_settings(self):
        """자동 할당 설정을 반환합니다."""
        return self.settings.get('auto_assign', {
            'enabled': True,
            'options': [10, 20],
            'time_limit': 30,
            'max_daily_problems': 50
        })
    
    def update_auto_assign_settings(self, new_settings):
        """자동 할당 설정을 업데이트합니다."""
        try:
            self.settings['auto_assign'] = new_settings
            self._save_data()
            return True
        except Exception as e:
            print(f"설정 업데이트 중 오류 발생: {str(e)}")
            return False

    def get_student_assignments(self, student_id):
        """학생에게 할당된 문제 목록을 반환합니다."""
        return [a for a in self.assignments if a['student_id'] == student_id]
    
    def assign_problems(self, student_id, problem_ids):
        """학생에게 문제를 할당합니다."""
        for problem_id in problem_ids:
            assignment = {
                'id': str(uuid.uuid4()),
                'student_id': student_id,
                'problem_id': problem_id,
                'assigned_at': datetime.now().isoformat(),
                'completed': False,
                'submitted_at': None,
                'score': None
            }
            self.assignments.append(assignment)
        self._save_data()
        return True
    
    def submit_assignment(self, assignment_id, answer, score=None):
        """학생의 답안을 제출하고 점수를 기록합니다."""
        for assignment in self.assignments:
            if assignment['id'] == assignment_id:
                assignment['completed'] = True
                assignment['submitted_at'] = datetime.now().isoformat()
                assignment['score'] = score
                self._save_data()
                return True
        return False
    
    def request_problem(self, student_id, problem_type, difficulty, description):
        """학생이 문제를 요청합니다."""
        request = {
            'id': str(uuid.uuid4()),
            'student_id': student_id,
            'problem_type': problem_type,
            'difficulty': difficulty,
            'description': description,
            'status': '대기',
            'created_at': datetime.now().isoformat(),
            'processed_at': None
        }
        self.problem_requests.append(request)
        self._save_data()
        return request
    
    def get_problem_requests(self, status=None):
        """문제 요청 목록을 반환합니다."""
        if status:
            return [r for r in self.problem_requests if r['status'] == status]
        return self.problem_requests
    
    def process_problem_request(self, request_id, action, feedback=None):
        """문제 요청을 처리합니다."""
        for request in self.problem_requests:
            if request['id'] == request_id:
                request['status'] = action
                request['processed_at'] = datetime.now().isoformat()
                request['feedback'] = feedback
                self._save_data()
                return True
        return False
    
    def get_auto_assigned_problems(self, student_id, count=3):
        """학생의 레벨에 맞는 문제를 자동으로 할당합니다."""
        student = self.get_student(student_id)
        if not student:
            return []
        
        # 난이도 매핑
        difficulty_mapping = {
            '초급': 1,
            '중급': 2,
            '고급': 3
        }
        
        student_level = difficulty_mapping.get(student['level'], 2)  # 기본값: 중급
        
        # 문제 목록 가져오기
        from utils.problem_manager import ProblemManager
        problem_manager = ProblemManager()
        problems = problem_manager.get_all_problems()
        if not problems:
            return []
        
        # 학생 레벨에 맞는 문제 필터링
        suitable_problems = [
            p for p in problems 
            if difficulty_mapping.get(p['difficulty'], 2) <= student_level
        ]
        
        # 랜덤으로 문제 선택
        selected_problems = random.sample(
            suitable_problems, 
            min(count, len(suitable_problems))
        )
        
        # 문제 할당
        problem_ids = [p['id'] for p in selected_problems]
        self.assign_problems(student_id, problem_ids)
        
        return selected_problems 
            return False 
