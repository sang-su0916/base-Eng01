import streamlit as st
from utils.student_manager import StudentManager
from utils.problem_manager import ProblemManager
from utils.feedback_generator import FeedbackGenerator
import pandas as pd
from datetime import datetime

# 관리자 초기화
student_manager = StudentManager()
problem_manager = ProblemManager()
feedback_generator = FeedbackGenerator()

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

def display_problem_solving_interface():
    """문제 풀이 인터페이스를 표시합니다."""
    st.markdown("""
    <style>
    .problem-card {
        padding: 1.5rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .feedback-section {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin-top: 1rem;
    }
    .timer {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 학생 이름 입력
    if "student_name" not in st.session_state:
        st.markdown('<div class="problem-card">', unsafe_allow_html=True)
        st.subheader("👋 환영합니다!")
        student_name = st.text_input("이름을 입력해주세요:")
        if student_name:
            st.session_state.student_name = student_name
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # 할당된 문제 확인
    assigned_problems = student_manager.get_assigned_problems(st.session_state.student_name)
    if not assigned_problems:
        st.info("📢 아직 할당된 문제가 없습니다. 선생님께 문의해주세요.")
        return
    
    # 현재 풀고 있는 문제 선택
    if "current_problem" not in st.session_state:
        st.markdown('<div class="problem-card">', unsafe_allow_html=True)
        st.subheader("📚 풀 문제를 선택해주세요")
        problem_titles = [p["title"] for p in assigned_problems]
        selected_title = st.selectbox("문제 선택:", problem_titles)
        if st.button("시작하기", use_container_width=True):
            st.session_state.current_problem = next(
                p for p in assigned_problems if p["title"] == selected_title
            )
            st.session_state.start_time = datetime.now()
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # 문제 풀이 인터페이스
    problem = st.session_state.current_problem
    st.markdown('<div class="problem-card">', unsafe_allow_html=True)
    
    # 제목과 정보
    st.subheader(f"📝 {problem['title']}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"유형: {problem['type']}")
    with col2:
        st.write(f"난이도: {problem['difficulty']}")
    with col3:
        st.write(f"제한시간: {problem['time_limit']}분")
    
    # 남은 시간 표시
    elapsed_time = datetime.now() - st.session_state.start_time
    remaining_seconds = max(0, problem['time_limit'] * 60 - elapsed_time.total_seconds())
    remaining_minutes = int(remaining_seconds // 60)
    remaining_secs = int(remaining_seconds % 60)
    
    st.markdown(
        f'<div class="timer">⏱️ 남은 시간: {remaining_minutes:02d}:{remaining_secs:02d}</div>',
        unsafe_allow_html=True
    )
    
    # 문제 내용
    st.markdown("### 문제")
    st.write(problem["content"])
    
    # 답안 입력
    st.markdown("### 답안 작성")
    if "submitted_answer" not in st.session_state:
        answer = st.text_area(
            "답안을 작성해주세요:",
            height=200,
            key="answer_input"
        )
        
        # 제출 버튼
        if st.button("제출하기", use_container_width=True):
            st.session_state.submitted_answer = answer
            st.session_state.submission_time = datetime.now()
            st.experimental_rerun()
    
    # 제출된 답안 평가 및 피드백
    if "submitted_answer" in st.session_state:
        st.markdown("### 제출된 답안")
        st.write(st.session_state.submitted_answer)
        
        # 첨삭 피드백 생성
        if "feedback" not in st.session_state:
            with st.spinner("첨삭을 생성하는 중..."):
                st.session_state.feedback = feedback_generator.generate_detailed_feedback(
                    st.session_state.submitted_answer,
                    problem["model_answer"],
                    problem["type"]
                )
        
        # 피드백 표시
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown("### 📝 첨삭 결과")
        st.markdown(st.session_state.feedback["korean_summary"])
        
        # 모범 답안 표시
        st.markdown("### ✨ 모범 답안")
        st.write(problem["model_answer"])
        
        # 다른 문제 풀기 버튼
        if st.button("다른 문제 풀기", use_container_width=True):
            del st.session_state.current_problem
            del st.session_state.submitted_answer
            del st.session_state.feedback
            st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align: center;'>📚 문제 풀이</h1>", unsafe_allow_html=True)
    display_problem_solving_interface()

if __name__ == "__main__":
    main() 