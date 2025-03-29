import streamlit as st
from utils.student_manager import StudentManager
from utils.problem_manager import ProblemManager
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# 관리자 초기화
student_manager = StudentManager()
problem_manager = ProblemManager()

def display_student_results():
    """학생별 결과를 표시합니다."""
    st.subheader("학생별 결과 확인")
    
    students = student_manager.get_all_students()
    if not students:
        st.info("등록된 학생이 없습니다.")
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
            assignment['answer'] = problem['answer']
    
    # 데이터프레임 생성
    df = pd.DataFrame(assignments)
    df['assigned_at'] = pd.to_datetime(df['assigned_at']).dt.strftime('%Y-%m-%d %H:%M')
    df['submitted_at'] = pd.to_datetime(df['submitted_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # 제출된 문제만 필터링
    submitted_df = df[df['completed'] == True].copy()
    
    if submitted_df.empty:
        st.info(f"{selected_student}님이 아직 제출한 문제가 없습니다.")
        return
    
    # 결과 요약
    st.write("### 결과 요약")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_problems = len(submitted_df)
        st.metric("총 문제 수", total_problems)
    
    with col2:
        avg_score = submitted_df['score'].mean() if 'score' in submitted_df.columns else 0
        st.metric("평균 점수", f"{avg_score:.1f}")
    
    with col3:
        completion_rate = len(submitted_df) / len(df) * 100
        st.metric("제출률", f"{completion_rate:.1f}%")
    
    # 문제 유형별 성적
    if 'score' in submitted_df.columns:
        st.write("### 문제 유형별 성적")
        type_scores = submitted_df.groupby('problem_type')['score'].mean().reset_index()
        fig = px.bar(type_scores, x='problem_type', y='score',
                    title='문제 유형별 평균 점수')
        st.plotly_chart(fig)
    
    # 문제 목록
    st.write("### 상세 결과")
    
    # 정렬 옵션
    sort_by = st.selectbox(
        "정렬 기준",
        ["제출일시", "문제 유형", "난이도", "점수"]
    )
    
    if sort_by == "제출일시":
        submitted_df = submitted_df.sort_values('submitted_at', ascending=False)
    elif sort_by == "문제 유형":
        submitted_df = submitted_df.sort_values('problem_type')
    elif sort_by == "난이도":
        submitted_df = submitted_df.sort_values('difficulty')
    elif sort_by == "점수":
        submitted_df = submitted_df.sort_values('score', ascending=False)
    
    # 결과 표시
    for _, row in submitted_df.iterrows():
        with st.expander(f"{row['problem_title']} ({row['problem_type']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**문제 내용**")
                st.write(row['problem_title'])
                st.write(row['content'])
                st.write("**학생 답안**")
                st.write(row['student_answer'])
            
            with col2:
                st.write("**정답**")
                st.write(row['answer'])
                if 'score' in row and row['score'] is not None:
                    st.write(f"**점수**: {row['score']}")
                else:
                    st.write("**점수**: 미채점")
                
                # 채점 폼
                if 'score' not in row or row['score'] is None:
                    with st.form(f"grade_form_{row['id']}"):
                        score = st.slider("점수", 0, 100, 50)
                        if st.form_submit_button("채점하기"):
                            if student_manager.grade_assignment(row['id'], score):
                                st.success("채점이 완료되었습니다!")
                                st.experimental_rerun()
                            else:
                                st.error("채점 중 오류가 발생했습니다.")

def display_statistics():
    """전체 통계를 표시합니다."""
    st.subheader("전체 통계")
    
    students = student_manager.get_all_students()
    if not students:
        st.info("등록된 학생이 없습니다.")
        return
    
    # 전체 할당 데이터 수집
    all_assignments = []
    for student in students:
        assignments = student_manager.get_student_assignments(student['id'])
        for assignment in assignments:
            problem = problem_manager.get_problem(assignment['problem_id'])
            if problem:
                assignment['student_name'] = student['name']
                assignment['student_grade'] = student['grade']
                assignment['problem_title'] = problem['title']
                assignment['problem_type'] = problem['type']
                assignment['difficulty'] = problem['difficulty']
                all_assignments.append(assignment)
    
    if not all_assignments:
        st.info("할당된 문제가 없습니다.")
        return
    
    # 데이터프레임 생성
    df = pd.DataFrame(all_assignments)
    
    # 통계 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_students = len(students)
        st.metric("전체 학생 수", total_students)
    
    with col2:
        total_assignments = len(df)
        st.metric("전체 할당 문제 수", total_assignments)
    
    with col3:
        completed_assignments = len(df[df['completed'] == True])
        completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
        st.metric("전체 제출률", f"{completion_rate:.1f}%")
    
    # 학년별 통계
    st.write("### 학년별 통계")
    grade_stats = df.groupby('student_grade').agg({
        'completed': ['count', 'sum']
    }).reset_index()
    
    grade_stats.columns = ['학년', '전체 문제 수', '제출된 문제 수']
    grade_stats['제출률'] = (grade_stats['제출된 문제 수'] / grade_stats['전체 문제 수'] * 100)
    
    fig = px.bar(grade_stats, x='학년', y=['전체 문제 수', '제출된 문제 수'],
                 title='학년별 문제 할당 및 제출 현황',
                 barmode='group')
    st.plotly_chart(fig)
    
    # 문제 유형별 통계
    st.write("### 문제 유형별 통계")
    type_stats = df.groupby('problem_type').agg({
        'completed': ['count', 'sum']
    }).reset_index()
    
    type_stats.columns = ['문제 유형', '전체 문제 수', '제출된 문제 수']
    type_stats['제출률'] = (type_stats['제출된 문제 수'] / type_stats['전체 문제 수'] * 100)
    
    fig = px.bar(type_stats, x='문제 유형', y=['전체 문제 수', '제출된 문제 수'],
                 title='문제 유형별 할당 및 제출 현황',
                 barmode='group')
    st.plotly_chart(fig)

def main():
    st.title("결과 확인")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["학생별 결과", "전체 통계"])
    
    with tab1:
        display_student_results()
    
    with tab2:
        display_statistics()

if __name__ == "__main__":
    main() 