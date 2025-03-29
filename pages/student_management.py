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
        
        # 반 추가
        class_name = st.text_input("반")
        
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
                "class_name": class_name,
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
    """학생 목록을 표시합니다."""
    st.markdown("### 👥 학생 목록")
    
    # 필터링 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        grade_filter = st.multiselect(
            "학년 필터",
            ["1", "2", "3", "4", "5", "6"],
            default=["1", "2", "3", "4", "5", "6"],
            help="표시할 학년을 선택하세요."
        )
    
    with col2:
        level_filter = st.multiselect(
            "레벨 필터",
            ["초급", "중급", "고급"],
            default=["초급", "중급", "고급"],
            help="표시할 레벨을 선택하세요."
        )
    
    with col3:
        status_filter = st.multiselect(
            "상태 필터",
            ["활성", "비활성"],
            default=["활성", "비활성"],
            help="표시할 상태를 선택하세요."
        )
    
    # 학생 목록 가져오기
    students = student_manager.get_all_students()
    if not students:
        st.info("등록된 학생이 없습니다.")
        return
    
    # DataFrame 생성
    df = pd.DataFrame(students)
    
    # 필터링 적용
    if grade_filter:
        df = df[df['grade'].isin(grade_filter)]
    if level_filter:
        df = df[df['level'].isin(level_filter)]
    if status_filter:
        df = df[df['status'].isin(status_filter)]
    
    if df.empty:
        st.info("선택한 조건에 맞는 학생이 없습니다.")
        return
    
    # 표시할 컬럼 선택
    display_columns = ['id', 'name', 'grade', 'level', 'status', 'contact', 'notes']
    column_names = {
        'id': 'ID',
        'name': '이름',
        'grade': '학년',
        'level': '레벨',
        'status': '상태',
        'contact': '연락처',
        'notes': '메모'
    }
    
    # 학생 목록 표시
    st.dataframe(
        df[display_columns].rename(columns=column_names),
        use_container_width=True,
        hide_index=True
    )
    
    # 학생 상세 정보 표시
    st.markdown("### 📋 학생 상세 정보")
    selected_student = st.selectbox(
        "학생을 선택하세요",
        df['name'].tolist(),
        format_func=lambda x: f"{x} ({df[df['name'] == x]['grade'].iloc[0]}학년 {df[df['name'] == x]['level'].iloc[0]})",
        help="상세 정보를 볼 학생을 선택하세요."
    )
    
    if selected_student:
        student = df[df['name'] == selected_student].iloc[0]
        with st.expander("학생 정보", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **기본 정보**
                - 이름: {student['name']}
                - 학년: {student['grade']}학년
                - 레벨: {student['level']}
                - 상태: {student['status']}
                """)
            
            with col2:
                st.markdown(f"""
                **연락처 정보**
                - 연락처: {student['contact']}
                - 메모: {student['notes']}
                """)
            
            # 할당된 문제 목록
            assignments = student_manager.get_student_assignments(student['id'])
            if assignments:
                st.markdown("**할당된 문제**")
                for assignment in assignments:
                    problem = problem_manager.get_problem(assignment['problem_id'])
                    if problem:
                        st.markdown(f"- {problem['title']} ({problem['type']} - {problem['difficulty']})")
            else:
                st.info("아직 할당된 문제가 없습니다.")
            
            # 편집/삭제 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ 정보 수정", key=f"edit_{student['id']}"):
                    st.session_state.edit_student = student
                    st.rerun()
            with col2:
                if st.button("🗑️ 학생 삭제", key=f"delete_{student['id']}"):
                    if student_manager.delete_student(student['id']):
                        st.success(f"✅ {student['name']} 학생이 삭제되었습니다.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ 학생 삭제 중 오류가 발생했습니다.")

def show_problem_assignment_section():
    """문제 할당 섹션을 표시합니다."""
    st.markdown("""
    <style>
    .assignment-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .problem-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    .metric-box {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="assignment-section">', unsafe_allow_html=True)
    st.subheader("📚 문제 할당")
    
    # 학생 목록 가져오기
    students = student_manager.get_all_students()
    if not students:
        st.warning("⚠️ 등록된 학생이 없습니다. 먼저 학생을 등록해주세요.")
        return
    
    # 문제 목록 가져오기
    problems = problem_manager.get_all_problems()
    if not problems:
        st.warning("⚠️ 등록된 문제가 없습니다. 먼저 문제를 등록해주세요.")
        return
    
    # 학생 선택
    st.markdown("### 👤 학생 선택")
    student_df = pd.DataFrame(students)
    selected_student = st.selectbox(
        "학생을 선택하세요",
        student_df['name'].tolist(),
        format_func=lambda x: f"{x} ({student_df[student_df['name'] == x]['grade'].iloc[0]}학년 {student_df[student_df['name'] == x].get('class_name', '미지정').iloc[0]}반)",
        help="문제를 할당할 학생을 선택하세요."
    )
    
    # 선택된 학생의 ID 가져오기
    student_id = student_df[student_df['name'] == selected_student]['id'].iloc[0]
    
    # 문제 필터링 옵션
    st.markdown("### 🔍 문제 필터")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        problem_type = st.multiselect(
            "문제 유형",
            ["문법", "어휘", "독해", "영작문", "듣기", "말하기"],
            default=["문법", "어휘", "독해"],
            help="할당할 문제의 유형을 선택하세요."
        )
    
    with col2:
        difficulty = st.multiselect(
            "난이도",
            ["초급", "중급", "고급"],
            default=["중급"],
            help="할당할 문제의 난이도를 선택하세요."
        )
    
    with col3:
        problem_count = st.number_input(
            "할당할 문제 수",
            min_value=1,
            max_value=10,
            value=3,
            help="한 번에 할당할 문제의 수를 선택하세요."
        )
    
    # 필터링된 문제 목록
    filtered_problems = [p for p in problems 
                        if p['type'] in problem_type 
                        and p['difficulty'] in difficulty]
    
    if not filtered_problems:
        st.warning("⚠️ 선택한 조건에 맞는 문제가 없습니다.")
        return
    
    # 문제 목록 표시
    st.markdown("### 📝 문제 목록")
    problem_df = pd.DataFrame(filtered_problems)
    
    # 문제 선택
    selected_problems = st.multiselect(
        "할당할 문제를 선택하세요",
        problem_df['id'].tolist(),
        format_func=lambda x: f"{problem_df[problem_df['id'] == x]['title'].iloc[0]} ({problem_df[problem_df['id'] == x]['type'].iloc[0]} - {problem_df[problem_df['id'] == x]['difficulty'].iloc[0]})",
        help="할당할 문제를 선택하세요. 선택한 문제 수가 지정한 문제 수와 일치해야 합니다."
    )
    
    # 선택된 문제 수 확인
    if len(selected_problems) != problem_count:
        st.warning(f"⚠️ {problem_count}개의 문제를 선택해주세요. (현재 {len(selected_problems)}개 선택됨)")
        return
    
    # 문제 할당 버튼
    if st.button("📥 문제 할당", type="primary", use_container_width=True):
        try:
            if student_manager.assign_problems(student_id, selected_problems):
                st.success(f"✅ {selected_student}님에게 {len(selected_problems)}개의 문제가 성공적으로 할당되었습니다!")
                st.balloons()
            else:
                st.error("❌ 문제 할당 중 오류가 발생했습니다.")
        except Exception as e:
            st.error(f"❌ 문제 할당 중 오류가 발생했습니다: {str(e)}")
    
    # 할당된 문제 목록 표시
    st.markdown("### 📋 현재 할당된 문제")
    assignments = student_manager.get_student_assignments(student_id)
    
    if assignments:
        for assignment in assignments:
            problem = problem_manager.get_problem(assignment['problem_id'])
            if problem:
                with st.expander(f"📝 {problem['title']} ({problem['type']} - {problem['difficulty']})"):
                    st.markdown('<div class="problem-card">', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **문제 정보**
                        - 유형: {problem['type']}
                        - 난이도: {problem['difficulty']}
                        - 할당일: {assignment['assigned_at'].split('T')[0]}
                        """)
                    
                    with col2:
                        status = "✅ 완료" if assignment.get('completed') else "⏳ 미완료"
                        st.markdown(f"""
                        **진행 상태**
                        - 상태: {status}
                        - 제출일: {assignment.get('submitted_at', '미제출').split('T')[0] if assignment.get('submitted_at') else '미제출'}
                        - 점수: {assignment.get('score', '미채점')}
                        """)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("아직 할당된 문제가 없습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_problem_requests():
    """문제 요청 목록을 표시합니다."""
    st.subheader("📨 문제 요청 목록")
    
    # 모든 문제 요청 가져오기
    requests = student_manager.get_all_problem_requests()
    if not requests:
        st.info("아직 문제 요청이 없습니다.")
        return
    
    # 상태별 필터링
    status_filter = st.multiselect(
        "상태 필터",
        ["pending", "approved", "rejected"],
        default=["pending"]
    )
    
    # 필터링된 요청 목록
    filtered_requests = [r for r in requests if r['status'] in status_filter]
    
    for req in filtered_requests:
        # 학생 정보 가져오기
        student = student_manager.get_student(req['student_id'])
        if not student:
            continue
            
        with st.expander(
            f"{student['name']} - {req['type']} (난이도: {req['difficulty']}) "
            f"- {datetime.fromisoformat(req['requested_at']).strftime('%Y-%m-%d %H:%M')}"
        ):
            st.write(f"**학생:** {student['name']} ({student['grade']})")
            st.write(f"**요청 유형:** {req['type']}")
            st.write(f"**난이도:** {req['difficulty']}")
            st.write(f"**요청 일시:** {datetime.fromisoformat(req['requested_at']).strftime('%Y-%m-%d %H:%M')}")
            if 'note' in req and req['note']:
                st.write(f"**추가 요청사항:** {req['note']}")
            st.write(f"**현재 상태:** {req['status']}")
            
            if req['status'] == 'pending':
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 승인", key=f"approve_{req['id']}"):
                        student_manager.update_problem_request_status(req['id'], 'approved')
                        st.success("요청이 승인되었습니다.")
                        st.rerun()
                with col2:
                    if st.button("❌ 거절", key=f"reject_{req['id']}"):
                        student_manager.update_problem_request_status(req['id'], 'rejected')
                        st.success("요청이 거절되었습니다.")
                        st.rerun()

def add_student_form():
    """학생 추가 폼을 표시합니다."""
    with st.form("add_student_form"):
        st.subheader("📝 학생 정보 입력")
        
        name = st.text_input("이름")
        
        # 학교급 선택
        school_type = st.selectbox(
            "학교",
            ["초등학교", "중학교", "고등학교"]
        )
        
        # 학년 선택 (학교급에 따라 다르게)
        if school_type == "초등학교":
            grade_options = [f"{i}학년" for i in range(1, 7)]
        else:
            grade_options = [f"{i}학년" for i in range(1, 4)]
            
        grade = st.selectbox("학년", options=grade_options)
        
        # 최종 학년 형식 생성
        full_grade = f"{school_type} {grade}"
        
        class_name = st.text_input("반")
        level = st.selectbox("레벨", options=["초급", "중급", "고급"])
        
        submitted = st.form_submit_button("학생 추가", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("이름을 입력해주세요.")
                return
                
            student_data = {
                "name": name,
                "grade": full_grade,
                "class_name": class_name,
                "level": level
            }
            
            if student_manager.add_student(student_data):
                st.success(f"✅ {name} 학생이 추가되었습니다.")
                st.rerun()
            else:
                st.error("학생 추가 중 오류가 발생했습니다.")

def show_student_management_section():
    """학생 관리 섹션을 표시합니다."""
    st.markdown("""
    <style>
    .student-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    .student-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    .metric-box {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="student-section">', unsafe_allow_html=True)
    st.subheader("👥 학생 관리")
    
    # 통계 섹션
    st.markdown("### 📊 학생 통계")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_students = len(student_manager.get_all_students())
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("전체 학생 수", f"{total_students}명")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        active_students = len([s for s in student_manager.get_all_students() if s.get('status') == 'active'])
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("활성 학생 수", f"{active_students}명")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        assigned_problems = len(student_manager.get_all_assignments())
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("할당된 문제 수", f"{assigned_problems}개")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 학생 등록 폼
    st.markdown("### 📝 학생 등록")
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "이름",
                placeholder="학생 이름을 입력하세요",
                help="학생의 이름을 입력하세요."
            )
            
            grade = st.number_input(
                "학년",
                min_value=1,
                max_value=6,
                value=1,
                help="학생의 학년을 선택하세요."
            )
            
            level = st.select_slider(
                "영어 레벨",
                options=["초급", "중급", "고급"],
                value="중급",
                help="학생의 영어 수준을 선택하세요."
            )
            
        with col2:
            class_name = st.text_input(
                "반",
                placeholder="예: A반, B반",
                help="학생이 속한 반을 입력하세요."
            )
            
            contact = st.text_input(
                "연락처",
                placeholder="학부모 연락처",
                help="학부모 연락처를 입력하세요."
            )
            
            notes = st.text_area(
                "메모",
                placeholder="특이사항이나 참고사항을 입력하세요",
                help="학생에 대한 특이사항이나 참고사항을 입력하세요."
            )
        
        submitted = st.form_submit_button(
            "💾 학생 등록",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not name:
                st.error("⚠️ 이름은 필수 입력 항목입니다.")
            else:
                student_data = {
                    "name": name,
                    "grade": grade,
                    "class_name": class_name,
                    "level": level,
                    "contact": contact,
                    "notes": notes,
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                
                if student_manager.add_student(student_data):
                    st.success("✅ 학생이 성공적으로 등록되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 학생 등록 중 오류가 발생했습니다.")
    
    # 학생 목록
    st.markdown("### 📚 학생 목록")
    students = student_manager.get_all_students()
    
    if students:
        # 필터 옵션
        col1, col2, col3 = st.columns(3)
        with col1:
            grade_filter = st.multiselect(
                "학년 필터",
                sorted(set(s['grade'] for s in students)),
                placeholder="모든 학년"
            )
        with col2:
            class_filter = st.multiselect(
                "반 필터",
                sorted(set(s['class_name'] for s in students if s.get('class_name'))),
                placeholder="모든 반"
            )
        with col3:
            level_filter = st.multiselect(
                "레벨 필터",
                sorted(set(s['level'] for s in students)),
                placeholder="모든 레벨"
            )
        
        # 필터 적용
        filtered_students = students
        if grade_filter:
            filtered_students = [s for s in filtered_students if s['grade'] in grade_filter]
        if class_filter:
            filtered_students = [s for s in filtered_students if s.get('class_name') in class_filter]
        if level_filter:
            filtered_students = [s for s in filtered_students if s['level'] in level_filter]
        
        # 학생 카드 표시
        for student in filtered_students:
            with st.expander(f"👤 {student['name']} ({student['grade']}학년 {student.get('class_name', '미지정')}반)"):
                st.markdown('<div class="student-card">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **기본 정보**
                    - 학년: {student['grade']}학년
                    - 반: {student.get('class_name', '미지정')}
                    - 레벨: {student['level']}
                    - 상태: {'🟢 활성' if student.get('status') == 'active' else '🔴 비활성'}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **연락처**
                    - 연락처: {student.get('contact', '미등록')}
                    - 등록일: {student['created_at'].split('T')[0]}
                    """)
                
                if student.get('notes'):
                    st.markdown(f"""
                    **메모**
                    {student['notes']}
                    """)
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.button("✏️ 정보 수정", key=f"edit_{student['id']}", use_container_width=True):
                        # 수정 폼 표시
                        with st.form(f"edit_form_{student['id']}"):
                            edited_name = st.text_input("이름", value=student['name'])
                            edited_grade = st.number_input("학년", min_value=1, max_value=6, value=student['grade'])
                            edited_class = st.text_input("반", value=student.get('class_name', ''))
                            edited_level = st.select_slider("레벨", options=["초급", "중급", "고급"], value=student['level'])
                            edited_contact = st.text_input("연락처", value=student.get('contact', ''))
                            edited_notes = st.text_area("메모", value=student.get('notes', ''))
                            
                            if st.form_submit_button("💾 저장"):
                                student_manager.update_student(student['id'], {
                                    "name": edited_name,
                                    "grade": edited_grade,
                                    "class_name": edited_class,
                                    "level": edited_level,
                                    "contact": edited_contact,
                                    "notes": edited_notes
                                })
                                st.success("✅ 학생 정보가 업데이트되었습니다!")
                                st.rerun()
                
                with col4:
                    if st.button("🗑️ 삭제", key=f"delete_{student['id']}", use_container_width=True):
                        if student_manager.delete_student(student['id']):
                            st.success("✅ 학생이 삭제되었습니다!")
                            st.rerun()
                        else:
                            st.error("❌ 학생 삭제 중 오류가 발생했습니다.")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("등록된 학생이 없습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """학생 관리 페이지의 메인 함수입니다."""
    st.markdown("## 👨‍👩‍👧‍👦 학생 관리")
    
    # 사용 설명서
    with st.expander("📖 사용 설명서", expanded=False):
        st.markdown("""
        ### 🎯 학생 관리 시스템 사용 방법
        
        #### 1. 학생 등록하기
        1. '학생 등록' 섹션에서 학생 정보를 입력합니다.
           - 이름: 학생의 실명을 입력
           - 학년: 학생의 현재 학년 선택
           - 반: 소속 반 입력 (예: A반, 1반 등)
           - 레벨: 학생의 영어 실력 수준 선택
        2. '등록하기' 버튼을 클릭하여 학생을 시스템에 추가합니다.
        
        #### 2. 문제 할당하기
        1. '문제 할당' 섹션에서 학생을 선택합니다.
        2. 할당할 문제 유형과 난이도를 선택합니다.
           - 문제 유형: 문법, 독해, 작문 등
           - 난이도: 1~5 레벨 중 선택
        3. '문제 검색' 버튼을 클릭하여 조건에 맞는 문제를 찾습니다.
        4. 할당할 문제를 선택하고 '할당하기' 버튼을 클릭합니다.
        
        #### 3. 학생 목록 관리
        - 전체 학생 목록을 확인할 수 있습니다.
        - 각 학생별로 할당된 문제와 진행 상황을 볼 수 있습니다.
        - 필요한 경우 학생 정보를 수정하거나 삭제할 수 있습니다.
        
        #### 4. 문제 할당 현황
        - 학생별로 할당된 문제 목록을 확인할 수 있습니다.
        - 제출 여부와 점수를 확인할 수 있습니다.
        - 필요한 경우 할당을 취소하거나 새로운 문제를 추가할 수 있습니다.
        
        #### 5. 문제 요청 확인
        - 문제 요청 목록을 확인할 수 있습니다.
        - 요청 상태를 확인하고 승인 또는 거절할 수 있습니다.
        
        ### ⚠️ 주의사항
        - 학생 등록 시 이름은 중복될 수 없습니다.
        - 한 번에 너무 많은 문제를 할당하지 않도록 주의하세요.
        - 학생의 레벨에 맞는 난이도의 문제를 할당하는 것이 좋습니다.
        """)
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 학생 목록",
        "➕ 학생 추가",
        "문제 할당",
        "할당된 문제 확인",
        "문제 요청 확인"
    ])
    
    with tab1:
        show_student_management_section()
    
    with tab2:
        add_student_form()
    
    with tab3:
        show_problem_assignment_section()
    
    with tab4:
        display_assignments()
        
    with tab5:
        display_problem_requests()

if __name__ == "__main__":
    main() 