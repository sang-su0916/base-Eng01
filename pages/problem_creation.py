import streamlit as st
from utils.problem_manager import ProblemManager
from utils.github_sync import GitHubSync
import pandas as pd
from datetime import datetime
import io
import json

# 문제 관리자 초기화
problem_manager = ProblemManager()

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
    
    # GitHub 연동
    github_sync_form()
    
    st.write("---")
    
    # CSV 파일 업로드
    st.write("### CSV 파일로 문제 업로드")
    st.write("CSV 파일 형식: type,title,content,answer,keywords,difficulty")
    uploaded_file = st.file_uploader("CSV 파일 선택", type="csv")
    
    if uploaded_file is not None:
        try:
            # CSV 파일 읽기
            df = pd.read_csv(uploaded_file)
            required_columns = ['type', 'title', 'content', 'answer', 'keywords', 'difficulty']
            
            # 필수 컬럼 확인
            if not all(col in df.columns for col in required_columns):
                st.error("CSV 파일에 필요한 모든 컬럼이 없습니다.")
                return
            
            # 데이터 미리보기
            st.write("### 업로드된 문제 미리보기")
            st.dataframe(df)
            
            if st.button("문제 일괄 등록"):
                success_count = 0
                for _, row in df.iterrows():
                    problem_data = {
                        "type": row['type'],
                        "title": row['title'],
                        "content": row['content'],
                        "answer": row['answer'],
                        "keywords": [k.strip() for k in str(row['keywords']).split(",") if k.strip()],
                        "difficulty": int(row['difficulty']),
                        "created_at": datetime.now().isoformat()
                    }
                    if problem_manager.add_problem(problem_data):
                        success_count += 1
                
                st.success(f"{success_count}개의 문제가 성공적으로 등록되었습니다!")
                st.experimental_rerun()
                
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
    
    st.write("---")
    st.write("### 직접 입력으로 문제 출제")
    
    with st.form("problem_form"):
        # 문제 유형 선택
        problem_type = st.selectbox(
            "문제 유형",
            ["단어", "문법", "독해", "회화"]
        )
        
        # 문제 제목
        title = st.text_input("문제 제목")
        
        # 문제 내용
        content = st.text_area("문제 내용")
        
        # 정답
        answer = st.text_area("정답")
        
        # 키워드 (쉼표로 구분)
        keywords = st.text_input("키워드 (쉼표로 구분)")
        
        # 난이도
        difficulty = st.slider("난이도", 1, 5, 3)
        
        # 제출 버튼
        submitted = st.form_submit_button("문제 등록")
        
        if submitted:
            if not title or not content or not answer:
                st.error("필수 항목을 모두 입력해주세요.")
                return
            
            # 문제 데이터 구성
            problem_data = {
                "type": problem_type,
                "title": title,
                "content": content,
                "answer": answer,
                "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                "difficulty": difficulty,
                "created_at": datetime.now().isoformat()
            }
            
            # 문제 저장
            if problem_manager.add_problem(problem_data):
                st.success("문제가 성공적으로 등록되었습니다!")
                st.experimental_rerun()
            else:
                st.error("문제 등록 중 오류가 발생했습니다.")

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