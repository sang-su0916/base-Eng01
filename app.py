import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from pages.problem_creation import main as problem_creation_main
from pages.student_management import main as student_management_main
from pages.result_check import main as result_check_main
from pages.problem_solving import main as problem_solving_main
from utils.student_manager import StudentManager

# 학생 관리자 초기화
student_manager = StudentManager()

# 페이지 설정
st.set_page_config(
    page_title="영어학원 문제풀이 시스템",
    page_icon="📚",
    layout="wide"
)

# 메인 페이지 제목
st.title("📚 영어학원 문제풀이 시스템")

# 사이드바 - 사용자 선택
with st.sidebar:
    st.header("사용자 선택")
    user_type = st.radio(
        "사용자 유형을 선택하세요",
        ["선생님", "학생"]
    )

# 메인 컨텐츠
if user_type == "선생님":
    st.header("👩‍🏫 선생님용 메뉴")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["문제 출제", "학생 관리", "결과 확인"])
    
    with tab1:
        problem_creation_main()
        
    with tab2:
        student_management_main()
        
    with tab3:
        result_check_main()
        
else:
    st.header("👧 학생용 메뉴")
    problem_solving_main() 