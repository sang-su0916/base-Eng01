import streamlit as st
from utils.student_manager import StudentManager
from utils.problem_manager import ProblemManager
import pandas as pd
from datetime import datetime

# 관리자 초기화
student_manager = StudentManager()
problem_manager = ProblemManager()

def display_problem(problem, student_id, assignment_id):
    """문제를 표시하고 답안을 제출받습니다."""
    st.subheader(problem['title'])
    
    # 문제 정보 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**유형**: {problem['type']}")
    with col2:
        st.write(f"**난이도**: {problem['difficulty']}")
    with col3:
        st.write(f"**제한시간**: {problem['time_limit']}분")
    
    # 문제 내용 표시
    st.write("### 문제")
    st.write(problem['content'])
    
    # 답안 작성 폼
    with st.form(f"answer_form_{assignment_id}"):
        student_answer = st.text_area("답안을 작성하세요", height=200)
        submitted = st.form_submit_button("제출하기")
        
        if submitted and student_answer.strip():
            # 제출 시간 기록
            submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 답안 저장
            if student_manager.submit_assignment(assignment_id, student_answer, submission_time):
                st.success("답안이 제출되었습니다!")
                st.experimental_rerun()
            else:
                st.error("답안 제출 중 오류가 발생했습니다.")
        elif submitted:
            st.warning("답안을 입력해주세요.")

def main():
    st.title("문제 풀이")
    
    # 학생 이름 입력
    student_name = st.text_input("이름을 입력하세요")
    
    if student_name:
        # 학생 정보 확인
        student = student_manager.get_student_by_name(student_name)
        if student:
            st.subheader(f"안녕하세요, {student_name}님!")
            
            # 할당된 문제 가져오기
            assignments = student_manager.get_student_assignments(student['id'])
            if not assignments:
                st.info("아직 할당된 문제가 없습니다.")
                return
            
            # 제출하지 않은 문제만 필터링
            pending_assignments = [a for a in assignments if not a['completed']]
            
            if not pending_assignments:
                st.success("모든 문제를 풀었습니다!")
                return
            
            # 문제 선택
            problem_titles = []
            for assignment in pending_assignments:
                problem = problem_manager.get_problem(assignment['problem_id'])
                if problem:
                    problem_titles.append(problem['title'])
            
            selected_title = st.selectbox(
                "풀어볼 문제를 선택하세요",
                problem_titles
            )
            
            # 선택된 문제 표시
            for assignment in pending_assignments:
                problem = problem_manager.get_problem(assignment['problem_id'])
                if problem and problem['title'] == selected_title:
                    display_problem(problem, student['id'], assignment['id'])
                    break
        else:
            st.error("등록되지 않은 학생입니다. 선생님께 문의해주세요.")
    else:
        st.info("이름을 입력해주세요.")

if __name__ == "__main__":
    main() 