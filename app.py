import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from pages.problem_creation import main as problem_creation_main
from pages.student_management import main as student_management_main
from pages.result_check import main as result_check_main
from pages.problem_solving import main as problem_solving_main
from utils.student_manager import StudentManager
import base64

# 학생 관리자 초기화
student_manager = StudentManager()

# 페이지 설정
st.set_page_config(
    page_title="영어학원 문제풀이 시스템",
    page_icon="📚",
    layout="wide"
)

# 세션 상태 초기화
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# CSV 파일 다운로드 함수
def get_csv_download_link():
    csv_path = Path("data/sample_problems.csv")
    if csv_path.exists():
        with open(csv_path, 'rb') as f:
            csv_data = f.read()
        b64 = base64.b64encode(csv_data).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="sample_problems.csv">📥 문제 양식 다운로드</a>'
        return href
    return None

# 메인 페이지 스타일
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .role-button {
        text-align: center;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem;
        transition: transform 0.2s;
    }
    .role-button:hover {
        transform: translateY(-5px);
    }
    .role-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 메인 페이지 제목
st.markdown('<div class="main-header"><h1>📚 영어학원 문제풀이 시스템</h1></div>', unsafe_allow_html=True)

# 로그인하지 않은 경우 역할 선택
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>👋 환영합니다!</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>아래에서 사용자 유형을 선택해주세요</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="role-button">
                <div class="role-icon">👩‍🏫</div>
                <h3>선생님</h3>
                <p>문제 출제 및 학생 관리</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("선생님으로 시작하기", key="teacher_btn", use_container_width=True):
            st.session_state.user_role = "teacher"
            st.session_state.logged_in = True
            st.experimental_rerun()
            
    with col2:
        st.markdown("""
            <div class="role-button">
                <div class="role-icon">👨‍🎓</div>
                <h3>학생</h3>
                <p>문제 풀이 및 결과 확인</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("학생으로 시작하기", key="student_btn", use_container_width=True):
            st.session_state.user_role = "student"
            st.session_state.logged_in = True
            st.experimental_rerun()
            
    with col3:
        st.markdown("""
            <div class="role-button">
                <div class="role-icon">👨‍💼</div>
                <h3>관리자</h3>
                <p>시스템 관리 및 통계</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("관리자로 시작하기", key="admin_btn", use_container_width=True):
            st.session_state.user_role = "admin"
            st.session_state.logged_in = True
            st.experimental_rerun()

# 로그인한 경우 해당 역할의 인터페이스 표시
else:
    # 로그아웃 버튼
    if st.sidebar.button("🚪 로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.experimental_rerun()
    
    if st.session_state.user_role == "teacher":
        st.markdown("<h2>👩‍🏫 선생님 메뉴</h2>", unsafe_allow_html=True)
        
        # 탭 생성
        tab1, tab2, tab3 = st.tabs(["📝 문제 출제", "👥 학생 관리", "📊 결과 확인"])
        
        with tab1:
            st.subheader("📝 문제 출제")
            # CSV 샘플 파일 다운로드 링크
            csv_link = get_csv_download_link()
            if csv_link:
                st.markdown(csv_link, unsafe_allow_html=True)
                st.info("💡 위 양식을 다운로드하여 문제를 작성할 수 있습니다.")
            problem_creation_main()
            
        with tab2:
            student_management_main()
            
        with tab3:
            result_check_main()
            
    elif st.session_state.user_role == "student":
        st.markdown("<h2>👨‍🎓 학생 메뉴</h2>", unsafe_allow_html=True)
        problem_solving_main()
        
    else:  # admin
        st.markdown("<h2>👨‍💼 관리자 메뉴</h2>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["⚙️ 시스템 관리", "📈 통계", "🔧 설정"])
        
        with tab1:
            st.subheader("⚙️ 시스템 관리")
            st.info("시스템 관리 기능 준비 중입니다...")
            
        with tab2:
            st.subheader("📈 통계")
            st.info("통계 기능 준비 중입니다...")
            
        with tab3:
            st.subheader("🔧 설정")
            st.info("설정 기능 준비 중입니다...") 