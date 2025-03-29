import streamlit as st
from utils.student_manager import StudentManager
from utils.problem_manager import ProblemManager
from utils.feedback_generator import FeedbackGenerator
import pandas as pd
from datetime import datetime
import time

# 관리자 초기화
student_manager = StudentManager()
problem_manager = ProblemManager()
feedback_generator = FeedbackGenerator()

def display_student_dashboard(student):
    """학생 대시보드를 표시합니다."""
    st.markdown("""
    <style>
    .dashboard-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

    # 학생 정보 카드
    st.markdown(f"""
    <div class="dashboard-card">
        <h3>👋 안녕하세요, {student['name']}님!</h3>
        <p>학년: {student['grade']} | 레벨: {student['level']}{' | 반: ' + student['class'] if 'class' in student else ''}</p>
    </div>
    """, unsafe_allow_html=True)

    # 통계 정보
    assignments = student_manager.get_student_assignments(student['id'])
    total_problems = len(assignments)
    completed_problems = len([a for a in assignments if a['completed']])
    if completed_problems > 0:
        average_score = sum(a['score'] for a in assignments if a['completed'] and a['score'] is not None) / completed_problems
    else:
        average_score = 0

    st.markdown("""
    <div class="stat-grid">
        <div class="stat-card">
            <p>할당된 문제</p>
            <div class="stat-value">{}</div>
        </div>
        <div class="stat-card">
            <p>완료한 문제</p>
            <div class="stat-value">{}</div>
        </div>
        <div class="stat-card">
            <p>평균 점수</p>
            <div class="stat-value">{:.1f}</div>
        </div>
    </div>
    """.format(total_problems, completed_problems, average_score), unsafe_allow_html=True)

    # 최근 제출한 문제
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("### 📝 최근 제출한 문제")
    recent_assignments = [a for a in assignments if a['completed']][-3:]  # 최근 3개
    if recent_assignments:
        for assignment in reversed(recent_assignments):
            problem = problem_manager.get_problem(assignment['problem_id'])
            if problem:
                status = "✅" if assignment['score'] and assignment['score'] >= 70 else "⚠️"
                st.write(f"{status} {problem['title']} - 점수: {assignment['score'] if assignment['score'] else 'N/A'}")
    else:
        st.info("아직 제출한 문제가 없습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

def request_new_problem(student):
    """새로운 문제를 요청합니다."""
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("### 📨 문제 요청하기")
    
    # 자동 할당 설정 가져오기
    auto_assign_settings = student_manager.get_auto_assign_settings()
    
    if auto_assign_settings.get('enabled', False):
        st.markdown("#### 🤖 자동 문제 할당")
        st.info("선택한 개수만큼 레벨에 맞는 문제가 자동으로 할당됩니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            problem_count = st.number_input(
                "문제 개수",
                min_value=5,
                max_value=100,
                value=10,
                step=5,
                key="auto_assign_count"
            )
        with col2:
            problem_type = st.selectbox(
                "문제 유형",
                ["전체", "문법", "독해", "작문", "회화", "단어"],
                key="auto_assign_type"
            )
        
        if st.button("자동 할당받기", use_container_width=True, key="auto_assign_button"):
            if student_manager.auto_assign_problems(student['id'], problem_count, problem_type):
                st.success(f"✅ {problem_count}개의 문제가 자동으로 할당되었습니다!")
                st.balloons()
                
                # 즉시 문제 풀이로 전환할지 물어보기
                if st.button("👉 바로 문제 풀기", use_container_width=True):
                    st.session_state.current_tab = "문제 풀기"
                    st.rerun()
            else:
                st.error("문제 할당 중 오류가 발생했습니다. 하루 최대 문제 수를 초과했을 수 있습니다.")
        
        st.markdown("---")
    
    # 수동 문제 요청 폼
    st.markdown("#### ✏️ 수동 문제 요청")
    col1, col2 = st.columns(2)
    with col1:
        problem_type = st.selectbox(
            "원하는 문제 유형",
            ["문법", "독해", "작문", "회화", "단어"],
            key="request_type"
        )
    with col2:
        difficulty = st.selectbox(
            "원하는 난이도",
            list(range(1, 6)),
            key="request_difficulty"
        )
    
    request_note = st.text_area(
        "추가 요청사항 (선택사항)",
        placeholder="예: 과거시제 문법 문제를 풀고 싶어요.",
        max_chars=200
    )
        
    if st.button("문제 요청하기", use_container_width=True, key="request_button"):
        request_data = {
            'type': problem_type,
            'difficulty': difficulty,
            'note': request_note
        }
        
        if student_manager.request_problem(student['id'], request_data):
            st.success("✅ 문제 요청이 완료되었습니다! 선생님이 확인 후 문제를 할당해 드릴 예정입니다.")
            st.balloons()
            time.sleep(1)
            st.rerun()
        else:
            st.error("문제 요청 중 오류가 발생했습니다.")
            
    st.markdown("</div>", unsafe_allow_html=True)

def display_problem_solving_interface():
    """문제 풀이 인터페이스를 표시합니다."""
    # 로그아웃 버튼을 우측 상단에 배치
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🚪 로그아웃"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.rerun()
    
    # 학생 이름 입력
    if "student_name" not in st.session_state:
        st.markdown('<div class="problem-card">', unsafe_allow_html=True)
        st.subheader("👋 환영합니다!")
        student_name = st.text_input("이름을 입력해주세요:")
        if student_name:
            st.session_state.student_name = student_name
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # 학생 정보 가져오기
    student = student_manager.get_student_by_name(st.session_state.student_name)
    if not student:
        st.error("등록되지 않은 학생입니다. 선생님께 문의해주세요.")
        return

    # 탭 생성
    tab1, tab2 = st.tabs(["📊 대시보드", "📝 문제 풀기"])
    
    with tab1:
        display_student_dashboard(student)
        request_new_problem(student)
        
    with tab2:
        # 할당된 문제 확인
        assignments = student_manager.get_student_assignments(student['id'])
        incomplete_assignments = [a for a in assignments if not a['completed']]
        
        if not incomplete_assignments:
            st.info("📢 현재 풀 수 있는 문제가 없습니다. 문제 요청하기 기능을 이용해보세요!")
            return
        
        # 문제 목록 표시
        st.subheader("📚 풀 수 있는 문제")
        problem_list = []
        for assignment in incomplete_assignments:
            problem = problem_manager.get_problem(assignment['problem_id'])
            if problem:
                problem_list.append({
                    'assignment_id': assignment['id'],
                    'title': problem['title'],
                    'problem': problem
                })
        
        if not problem_list:
            st.error("문제 정보를 불러올 수 없습니다.")
            return
            
        # 문제 선택
        if "current_problem" not in st.session_state:
            st.markdown('<div class="problem-card">', unsafe_allow_html=True)
            problem_titles = [p["title"] for p in problem_list]
            selected_title = st.selectbox("문제 선택:", problem_titles)
            
            if st.button("시작하기", use_container_width=True):
                selected_problem = next(p for p in problem_list if p["title"] == selected_title)
                st.session_state.current_problem = selected_problem['problem']
                st.session_state.current_assignment_id = selected_problem['assignment_id']
                st.session_state.start_time = datetime.now()
                st.rerun()
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
                # 답안 저장
                if student_manager.submit_answer(st.session_state.current_assignment_id, answer):
                    st.session_state.submitted_answer = answer
                    st.session_state.submission_time = datetime.now()
                    st.rerun()
                else:
                    st.error("답안 제출 중 오류가 발생했습니다.")
        
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
                del st.session_state.current_assignment_id
                del st.session_state.submitted_answer
                if "feedback" in st.session_state:
                    del st.session_state.feedback
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align: center;'>📚 문제 풀이</h1>", unsafe_allow_html=True)
    display_problem_solving_interface()

if __name__ == "__main__":
    main() 