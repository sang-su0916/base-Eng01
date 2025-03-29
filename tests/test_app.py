import unittest
import streamlit as st
from utils.student_manager import StudentManager
from utils.problem_manager import ProblemManager

class TestApp(unittest.TestCase):
    def setUp(self):
        """테스트 전 초기화"""
        self.student_manager = StudentManager()
        self.problem_manager = ProblemManager()
        
    def test_student_registration(self):
        """학생 등록 테스트"""
        # 테스트용 학생 데이터
        test_student = {
            "name": "테스트학생",
            "grade": "중1",
            "contact": "010-1234-5678"
        }
        
        # 학생 등록
        student_id = self.student_manager.add_student(test_student)
        self.assertIsNotNone(student_id)
        
        # 등록된 학생 확인
        student = self.student_manager.get_student_by_name(test_student["name"])
        self.assertIsNotNone(student)
        self.assertEqual(student["name"], test_student["name"])
        
    def test_problem_creation(self):
        """문제 생성 테스트"""
        # 테스트용 문제 데이터
        test_problem = {
            "title": "테스트 문제",
            "type": "영작문",
            "difficulty": "중급",
            "time_limit": 30,
            "content": "This is a test problem.",
            "keywords": ["test", "problem"],
            "model_answer": "This is a test answer."
        }
        
        # 문제 생성
        problem_id = self.problem_manager.add_problem(test_problem)
        self.assertIsNotNone(problem_id)
        
        # 생성된 문제 확인
        problem = self.problem_manager.get_problem(problem_id)
        self.assertIsNotNone(problem)
        self.assertEqual(problem["title"], test_problem["title"])

if __name__ == '__main__':
    unittest.main() 