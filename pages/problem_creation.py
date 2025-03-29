import streamlit as st
from utils.problem_manager import ProblemManager
from utils.github_sync import GitHubSync
import pandas as pd
from datetime import datetime
import io
import json
from utils.problem_generator import ProblemGenerator

# 문제 관리자 초기화
problem_manager = ProblemManager()
problem_generator = ProblemGenerator()

def github_sync_form():
    """GitHub 연동 폼을 표시합니다."""
    st.write("### GitHub 연동")
    
    # GitHub 설정
    with st.expander("GitHub 설정"):
        github_token = st.text_input("GitHub 토큰", type="password")
        github_owner = st.text_input("저장소 소유자")
        github_repo = st.text_input("저장소 이름")
        github_path = st.text_input("파일 경로", value="problems.json")
        
        if all([github_token, github_owner, github_repo]):
            github_sync = GitHubSync(github_token)
            
            col1, col2 = st.columns(2)
            
            # GitHub에서 가져오기
            with col1:
                if st.button("GitHub에서 가져오기"):
                    content = github_sync.get_file_content(github_owner, github_repo, github_path)
                    if content:
                        try:
                            problems = json.loads(content)
                            for problem in problems:
                                problem_manager.add_problem(problem)
                            st.success("GitHub에서 문제를 성공적으로 가져왔습니다!")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"문제 데이터 처리 중 오류가 발생했습니다: {str(e)}")
                    else:
                        st.error("GitHub에서 파일을 가져오는데 실패했습니다.")
            
            # GitHub에 업로드
            with col2:
                if st.button("GitHub에 업로드"):
                    problems = problem_manager.get_all_problems()
                    content = json.dumps(problems, ensure_ascii=False, indent=2)
                    
                    success = github_sync.update_file(
                        github_owner,
                        github_repo,
                        github_path,
                        content,
                        "Update problems.json"
                    )
                    
                    if success:
                        st.success("문제가 GitHub에 성공적으로 업로드되었습니다!")
                    else:
                        # 파일이 없는 경우 새로 생성
                        success = github_sync.create_file(
                            github_owner,
                            github_repo,
                            github_path,
                            content,
                            "Create problems.json"
                        )
                        if success:
                            st.success("문제가 GitHub에 성공적으로 업로드되었습니다!")
                        else:
                            st.error("GitHub 업로드에 실패했습니다.")

def create_problem_form():
    """문제 생성 폼을 표시합니다."""
    st.subheader("새로운 문제 출제")
    
    # AI 문제 생성 섹션
    st.subheader("🤖 AI 문제 생성")
    if st.button("기본 문제 생성"):
        with st.spinner("문제를 생성하는 중..."):
            problems = problem_generator.generate_basic_problems()
            for problem in problems:
                problem_manager.add_problem(problem)
            st.success(f"{len(problems)}개의 기본 문제가 생성되었습니다!")
    
    st.write("---")
    
    # 문제 입력 방식 선택
    input_method = st.radio(
        "문제 입력 방식을 선택하세요:",
        ["직접 입력", "CSV 파일 업로드", "GitHub JSON 연동"]
    )
    
    if input_method == "직접 입력":
        with st.form("problem_form"):
            st.subheader("문제 직접 입력")
            
            title = st.text_input("제목")
            problem_type = st.selectbox("유형", ["문법", "어휘", "독해", "영작문"])
            difficulty = st.selectbox("난이도", ["초급", "중급", "고급"])
            time_limit = st.number_input("제한시간(분)", min_value=1, value=15)
            content = st.text_area("문제 내용")
            keywords = st.text_input("키워드 (쉼표로 구분)")
            model_answer = st.text_area("모범 답안")
            
            submitted = st.form_submit_button("문제 추가")
            
            if submitted:
                problem = {
                    "title": title,
                    "type": problem_type,
                    "difficulty": difficulty,
                    "time_limit": time_limit,
                    "content": content,
                    "keywords": keywords,
                    "model_answer": model_answer
                }
                
                if problem_manager.add_problem(problem):
                    st.success("문제가 추가되었습니다!")
                else:
                    st.error("문제 추가 중 오류가 발생했습니다.")
                    
    elif input_method == "CSV 파일 업로드":
        st.subheader("CSV 파일 업로드")
        uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                problems = df.to_dict('records')
                
                for problem in problems:
                    problem_manager.add_problem(problem)
                    
                st.success(f"{len(problems)}개의 문제가 추가되었습니다!")
            except Exception as e:
                st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
                
    else:  # GitHub JSON 연동
        st.subheader("GitHub JSON 연동")
        repo_url = st.text_input("GitHub 저장소 URL")
        json_path = st.text_input("JSON 파일 경로")
        
        if st.button("문제 가져오기"):
            try:
                # GitHub에서 JSON 파일 가져오기 로직
                st.info("GitHub 연동 기능은 준비 중입니다...")
            except Exception as e:
                st.error(f"GitHub 연동 중 오류가 발생했습니다: {str(e)}")
    
    # 현재 등록된 문제 목록 표시
    st.write("---")
    st.subheader("📝 등록된 문제 목록")
    problems = problem_manager.get_all_problems()
    
    if problems:
        df = pd.DataFrame(problems)
        st.dataframe(df[["title", "type", "difficulty", "time_limit"]])
    else:
        st.info("등록된 문제가 없습니다.")

def display_problems():
    """등록된 문제 목록을 표시합니다."""
    st.subheader("등록된 문제 목록")
    
    problems = problem_manager.get_all_problems()
    if not problems:
        st.info("등록된 문제가 없습니다.")
        return
    
    # 문제 목록을 데이터프레임으로 변환
    df = pd.DataFrame(problems)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # 표시할 컬럼 선택
    display_columns = ['id', 'type', 'title', 'difficulty', 'created_at']
    
    # 문제 목록 표시
    st.dataframe(df[display_columns])
    
    # CSV 다운로드 버튼
    if st.button("문제 목록 CSV 다운로드"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name="problems.csv",
            mime="text/csv"
        )
    
    # 문제 삭제 기능
    problem_id = st.number_input("삭제할 문제 ID", min_value=1, max_value=len(problems), value=1)
    if st.button("문제 삭제"):
        if problem_manager.delete_problem(problem_id):
            st.success(f"문제 ID {problem_id}가 삭제되었습니다.")
            st.experimental_rerun()
        else:
            st.error("문제 삭제 중 오류가 발생했습니다.")

def main():
    st.title("문제 출제")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["새 문제 출제", "문제 관리"])
    
    with tab1:
        create_problem_form()
    
    with tab2:
        display_problems()

if __name__ == "__main__":
    main() 