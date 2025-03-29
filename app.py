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

# CSS로 사이드바 숨기기
def hide_sidebar():
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            section[data-testid="stSidebarContent"] {display: none;}
            button[data-testid="baseButton-headerNoPadding"] {display: none;}
            div[data-testid="stToolbar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

# 페이지 설정
st.set_page_config(
    page_title="영어학원 문제풀이 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "문제 출제"

# 사용자 역할별 접근 가능한 메뉴 정의
ROLE_MENUS = {
    "teacher": ["문제 출제", "학생 관리", "결과 확인"],
    "student": ["문제 풀기"],
    "admin": ["문제 출제", "학생 관리", "결과 확인", "시스템 관리"]
}

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
    .stRadio > label {
        font-size: 1.2rem;
        padding: 1rem;
    }
    .stButton > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 메인 페이지 제목
st.markdown('<div class="main-header"><h1>📚 영어학원 문제풀이 시스템</h1></div>', unsafe_allow_html=True)

def show_login_screen():
    """로그인 화면을 표시합니다."""
    # 사이드바 숨기기
    hide_sidebar()
    
    # 헤더
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>📚 영어학원 문제풀이 시스템</h1>", unsafe_allow_html=True)
    
    # 역할 선택 컨테이너
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>👨‍🎓</div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>학생</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>문제 풀기 및 결과 확인</p>", unsafe_allow_html=True)
        if st.button("학생으로 로그인", key="student_login", use_container_width=True):
            st.session_state.user_role = "student"
            st.rerun()
    
    with col2:
        st.markdown("<div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>👩‍🏫</div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>선생님</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>문제 출제 및 학생 관리</p>", unsafe_allow_html=True)
        if st.button("선생님으로 로그인", key="teacher_login", use_container_width=True):
            st.session_state.user_role = "teacher"
            st.rerun()
    
    with col3:
        st.markdown("<div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>👨‍💼</div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>관리자</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>시스템 설정 및 관리</p>", unsafe_allow_html=True)
        if st.button("관리자로 로그인", key="admin_login", use_container_width=True):
            st.session_state.user_role = "admin"
            st.rerun()

def show_sidebar():
    """사이드바를 표시합니다."""
    # 학생인 경우 사이드바를 완전히 숨김
    if st.session_state.user_role == 'student':
        hide_sidebar()
        return "문제 풀기"

    with st.sidebar:
        if 'user_role' not in st.session_state:
            st.info("로그인이 필요합니다.")
            return
        
        # 선생님/관리자인 경우 전체 메뉴 표시
        st.markdown("### 🎓 관리자 메뉴")
        selected_menu = st.radio(
            "메뉴 선택",
            ["문제 출제", "학생 관리", "결과 확인", "시스템 설정"] if st.session_state.user_role == 'admin'
            else ["문제 출제", "학생 관리", "결과 확인"],
            label_visibility="collapsed"
        )
        
        if st.button("로그아웃", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        return selected_menu

def main():
    """메인 애플리케이션을 실행합니다."""
    if 'user_role' not in st.session_state or st.session_state.user_role is None:
        show_login_screen()
        return

    # 사이드바 메뉴 표시
    selected_menu = show_sidebar()
    
    # 학생인 경우 문제 풀기 화면으로 바로 이동
    if st.session_state.user_role == 'student':
        # 상단에 로그아웃 버튼 추가
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("로그아웃", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        problem_solving_main()
        return

    # 선생님/관리자 메뉴 처리
    if selected_menu == "문제 출제":
        problem_creation_main()
    elif selected_menu == "학생 관리":
        student_management_main()
    elif selected_menu == "결과 확인":
        result_check_main()
    elif selected_menu == "시스템 설정" and st.session_state.user_role == 'admin':
        display_admin_settings()

def display_admin_settings():
    """관리자 설정을 표시합니다."""
    st.subheader("⚙️ 시스템 설정")
    
    # 자동 할당 설정
    st.markdown("### 🤖 자동 문제 할당 설정")
    
    settings = student_manager.get_auto_assign_settings()
    
    # 활성화 여부
    enabled = st.toggle("자동 할당 기능 활성화", value=settings.get('enabled', True))
    
    # 문제 개수 옵션
    st.markdown("#### 문제 개수 옵션")
    st.info("학생들이 선택할 수 있는 문제 개수를 설정합니다.")
    options = st.multiselect(
        "문제 개수 옵션",
        options=[5, 10, 15, 20, 25, 30],
        default=settings.get('options', [10, 20])
    )
    
    # 제한 시간
    time_limit = st.number_input(
        "기본 제한 시간 (분)",
        min_value=5,
        max_value=120,
        value=settings.get('time_limit', 30)
    )
    
    # 하루 최대 문제 수
    max_daily = st.number_input(
        "하루 최대 문제 수",
        min_value=10,
        max_value=100,
        value=settings.get('max_daily_problems', 50)
    )
    
    if st.button("설정 저장", use_container_width=True):
        new_settings = {
            'enabled': enabled,
            'options': sorted(options),
            'time_limit': time_limit,
            'max_daily_problems': max_daily
        }
        
        if student_manager.update_auto_assign_settings(new_settings):
            st.success("✅ 설정이 저장되었습니다.")
            st.rerun()
        else:
            st.error("설정 저장 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main() 