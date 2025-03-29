import streamlit as st
from utils.student_manager import StudentManager
from utils.problem_manager import ProblemManager
import pandas as pd
from datetime import datetime

# 관리자 초기화
student_manager = StudentManager()
problem_manager = ProblemManager()

def create_student_form():
    """학생 등록 폼을 표시합니다."""
    st.subheader("새로운 학생 등록")
    
    with st.form("student_form"):
        # 학생 이름
        name = st.text_input("학생 이름")
        
        # 학년
        grade = st.selectbox(
            "학년",
            ["초등학교 1학년", "초등학교 2학년", "초등학교 3학년", 
             "초등학교 4학년", "초등학교 5학년", "초등학교 6학년",
             "중학교 1학년", "중학교 2학년", "중학교 3학년",
             "고등학교 1학년", "고등학교 2학년", "고등학교 3학년"]
        )
        
        # 레벨
        level = st.selectbox(
            "레벨",
            ["초급", "중급", "고급"]
        )
        
        # 메모
        memo = st.text_area("메모")
        
        # 제출 버튼
        submitted = st.form_submit_button("학생 등록")
        
        if submitted:
            if not name:
                st.error("학생 이름을 입력해주세요.")
                return
            
            # 학생 데이터 구성
            student_data = {
                "name": name,
                "grade": grade,
                "level": level,
                "memo": memo
            }
            
            # 학생 저장
            if student_manager.add_student(student_data):
                st.success("학생이 성공적으로 등록되었습니다!")
                st.experimental_rerun()
            else:
                st.error("학생 등록 중 오류가 발생했습니다.")

def display_students():
    """등록된 학생 목록을 표시합니다."""
    st.subheader("등록된 학생 목록")
    
    students = student_manager.get_all_students()
    if not students:
        st.info("등록된 학생이 없습니다.")
        return
    
    # 학생 목록을 데이터프레임으로 변환
    df = pd.DataFrame(students)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # 표시할 컬럼 선택
    display_columns = ['id', 'name', 'grade', 'level', 'created_at']
    
    # 학생 목록 표시
    st.dataframe(df[display_columns])
    
    # 학생 삭제 기능
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.number_input("삭제할 학생 ID", min_value=1, max_value=len(students), value=1)
        if st.button("학생 삭제"):
            if student_manager.delete_student(student_id):
                st.success(f"학생 ID {student_id}가 삭제되었습니다.")
                st.experimental_rerun()
            else:
                st.error("학생 삭제 중 오류가 발생했습니다.")

def assign_problems_form():
    """문제 할당 폼을 표시합니다."""
    st.subheader("문제 할당")
    
    students = student_manager.get_all_students()
    problems = problem_manager.get_all_problems()
    
    if not students:
        st.warning("등록된 학생이 없습니다. 먼저 학생을 등록해주세요.")
        return
        
    if not problems:
        st.warning("등록된 문제가 없습니다. 먼저 문제를 등록해주세요.")
        return
    
    # 학생 선택
    student_df = pd.DataFrame(students)[['id', 'name', 'grade', 'level']]
    selected_student = st.selectbox(
        "학생 선택",
        student_df['name'].tolist(),
        format_func=lambda x: f"{x} ({student_df[student_df['name'] == x]['grade'].iloc[0]})"
    )
    
    # 선택된 학생의 ID 가져오기
    student_id = student_df[student_df['name'] == selected_student]['id'].iloc[0]
    
    # 문제 선택
    st.write("### 할당할 문제 선택")
    
    # 문제 필터링 옵션
    col1, col2 = st.columns(2)
    with col1:
        problem_type = st.multiselect(
            "문제 유형",
            ["단어", "문법", "독해", "회화"],
            default=["단어", "문법", "독해", "회화"]
        )
    with col2:
        difficulty = st.multiselect(
            "난이도",
            [1, 2, 3, 4, 5],
            default=[1, 2, 3, 4, 5]
        )
    
    # 필터링된 문제 목록
    filtered_problems = [p for p in problems 
                        if p['type'] in problem_type 
                        and p['difficulty'] in difficulty]
    
    if not filtered_problems:
        st.warning("선택한 조건에 맞는 문제가 없습니다.")
        return
    
    problem_df = pd.DataFrame(filtered_problems)
    st.dataframe(problem_df[['id', 'type', 'title', 'difficulty']])
    
    # 문제 선택
    selected_problems = st.multiselect(
        "할당할 문제 선택",
        problem_df['id'].tolist(),
        format_func=lambda x: f"ID {x}: {problem_df[problem_df['id'] == x]['title'].iloc[0]}"
    )
    
    if st.button("문제 할당"):
        if not selected_problems:
            st.error("할당할 문제를 선택해주세요.")
            return
            
        if student_manager.assign_problems(student_id, selected_problems):
            st.success(f"{selected_student}님에게 {len(selected_problems)}개의 문제가 할당되었습니다!")
            st.experimental_rerun()
        else:
            st.error("문제 할당 중 오류가 발생했습니다.")

def display_assignments():
    """할당된 문제 목록을 표시합니다."""
    st.subheader("할당된 문제 목록")
    
    students = student_manager.get_all_students()
    if not students:
        st.info("등록된 학생이 없습니다.")
        return
    
    # 학생 선택
    student_df = pd.DataFrame(students)[['id', 'name', 'grade', 'level']]
    selected_student = st.selectbox(
        "학생 선택",
        student_df['name'].tolist(),
        format_func=lambda x: f"{x} ({student_df[student_df['name'] == x]['grade'].iloc[0]})",
        key="assignment_student_select"
    )
    
    # 선택된 학생의 ID 가져오기
    student_id = student_df[student_df['name'] == selected_student]['id'].iloc[0]
    
    # 할당된 문제 가져오기
    assignments = student_manager.get_student_assignments(student_id)
    if not assignments:
        st.info(f"{selected_student}님에게 할당된 문제가 없습니다.")
        return
    
    # 문제 정보 추가
    for assignment in assignments:
        problem = problem_manager.get_problem(assignment['problem_id'])
        if problem:
            assignment['problem_title'] = problem['title']
            assignment['problem_type'] = problem['type']
            assignment['difficulty'] = problem['difficulty']
    
    # 할당된 문제 목록을 데이터프레임으로 변환
    df = pd.DataFrame(assignments)
    df['assigned_at'] = pd.to_datetime(df['assigned_at']).dt.strftime('%Y-%m-%d %H:%M')
    df['submitted_at'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # 표시할 컬럼 선택
    display_columns = ['id', 'problem_title', 'problem_type', 'difficulty', 
                      'assigned_at', 'completed', 'submitted_at', 'score']
    
    # 할당된 문제 목록 표시
    st.dataframe(df[display_columns])

def main():
    st.title("학생 관리")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs([
        "학생 등록",
        "학생 목록",
        "문제 할당",
        "할당된 문제 확인"
    ])
    
    with tab1:
        create_student_form()
    
    with tab2:
        display_students()
    
    with tab3:
        assign_problems_form()
    
    with tab4:
        display_assignments()

if __name__ == "__main__":
    main() 