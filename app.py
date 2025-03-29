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
        href = f'<a href="data:file/csv;base64,{b64}" download="sample_problems.csv">샘플 CSV 파일 다운로드</a>'
        return href
    return None

# 메인 페이지 제목
st.title("📚 영어학원 문제풀이 시스템")

# 로그인하지 않은 경우 역할 선택
if not st.session_state.logged_in:
    st.header("👋 환영합니다!")
    st.write("시스템을 사용하기 위해 역할을 선택해주세요.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👩‍🏫 선생님", use_container_width=True):
            st.session_state.user_role = "teacher"
            st.session_state.logged_in = True
            st.experimental_rerun()
            
    with col2:
        if st.button("👨‍🎓 학생", use_container_width=True):
            st.session_state.user_role = "student"
            st.session_state.logged_in = True
            st.experimental_rerun()
            
    with col3:
        if st.button("👨‍💼 관리자", use_container_width=True):
            st.session_state.user_role = "admin"
            st.session_state.logged_in = True
            st.experimental_rerun()

# 로그인한 경우 해당 역할의 인터페이스 표시
else:
    # 로그아웃 버튼
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.experimental_rerun()
    
    if st.session_state.user_role == "teacher":
        st.header("👩‍🏫 선생님 메뉴")
        
        # 탭 생성
        tab1, tab2, tab3 = st.tabs(["문제 출제", "학생 관리", "결과 확인"])
        
        with tab1:
            st.subheader("문제 출제")
            # CSV 샘플 파일 다운로드 링크
            csv_link = get_csv_download_link()
            if csv_link:
                st.markdown(csv_link, unsafe_allow_html=True)
                st.write("CSV 파일 형식에 맞춰 문제를 작성해주세요.")
            problem_creation_main()
            
        with tab2:
            student_management_main()
            
        with tab3:
            result_check_main()
            
    elif st.session_state.user_role == "student":
        st.header("👨‍🎓 학생 메뉴")
        problem_solving_main()
        
    else:  # admin
        st.header("👨‍💼 관리자 메뉴")
        
        tab1, tab2, tab3 = st.tabs(["시스템 관리", "통계", "설정"])
        
        with tab1:
            st.subheader("시스템 관리")
            st.write("시스템 관리 기능 준비 중...")
            
        with tab2:
            st.subheader("통계")
            st.write("통계 기능 준비 중...")
            
        with tab3:
            st.subheader("설정")
            st.write("설정 기능 준비 중...") 