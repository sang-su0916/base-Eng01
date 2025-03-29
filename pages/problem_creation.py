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

def create_problem_form():
    """문제 생성 폼을 표시합니다."""
    st.markdown("""
    <style>
    .problem-section {
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # AI 문제 생성 섹션
    st.markdown('<div class="problem-section">', unsafe_allow_html=True)
    st.subheader("🤖 AI 문제 자동 생성")
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.write("AI가 기본적인 영어 문제를 자동으로 생성합니다.")
    st.write("- 문법, 어휘, 독해 등 다양한 유형")
    st.write("- 초급, 중급, 고급 수준별 문제")
    st.write("- 모범 답안과 채점 기준 포함")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🎲 기본 문제 자동 생성", use_container_width=True):
        with st.spinner("문제를 생성하는 중..."):
            problems = problem_generator.generate_basic_problems()
            for problem in problems:
                problem_manager.add_problem(problem)
            st.success(f"✅ {len(problems)}개의 기본 문제가 생성되었습니다!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 문제 입력 방식 선택
    st.markdown('<div class="problem-section">', unsafe_allow_html=True)
    st.subheader("📝 문제 직접 입력")
    
    input_method = st.radio(
        "문제 입력 방식을 선택하세요:",
        ["✏️ 직접 입력", "📎 CSV 파일 업로드", "🔄 GitHub 연동"]
    )
    
    if input_method == "✏️ 직접 입력":
        with st.form("problem_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("제목 (예: Unit 1 - Present Simple)")
                problem_type = st.selectbox(
                    "문제 유형",
                    ["문법", "어휘", "독해", "영작문", "듣기", "말하기"]
                )
                difficulty = st.select_slider(
                    "난이도",
                    ["초급", "중급", "고급"],
                    value="중급"
                )
                
            with col2:
                time_limit = st.number_input(
                    "제한시간(분)",
                    min_value=1,
                    max_value=60,
                    value=15
                )
                keywords = st.text_input(
                    "키워드 (쉼표로 구분)",
                    placeholder="예: present simple, daily routine, habits"
                )
            
            content = st.text_area(
                "문제 내용",
                height=200,
                placeholder="여기에 문제 내용을 작성하세요..."
            )
            
            model_answer = st.text_area(
                "모범 답안",
                height=100,
                placeholder="정답과 해설을 작성하세요..."
            )
            
            col3, col4, col5 = st.columns([1,1,1])
            with col4:
                submitted = st.form_submit_button(
                    "💾 문제 저장",
                    use_container_width=True
                )
            
            if submitted:
                if not title or not content or not model_answer:
                    st.error("⚠️ 제목, 문제 내용, 모범 답안은 필수 입력 항목입니다.")
                else:
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
                        st.success("✅ 문제가 성공적으로 저장되었습니다!")
                        st.balloons()
                    else:
                        st.error("❌ 문제 저장 중 오류가 발생했습니다.")
                    
    elif input_method == "📎 CSV 파일 업로드":
        st.info("💡 CSV 파일을 업로드하여 여러 문제를 한 번에 등록할 수 있습니다.")
        uploaded_file = st.file_uploader(
            "CSV 파일을 선택하세요",
            type="csv",
            help="샘플 양식을 다운로드하여 작성 후 업로드해주세요."
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                problems = df.to_dict('records')
                
                with st.spinner("문제를 등록하는 중..."):
                    for problem in problems:
                        problem_manager.add_problem(problem)
                    
                st.success(f"✅ {len(problems)}개의 문제가 성공적으로 등록되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ 파일 처리 중 오류가 발생했습니다: {str(e)}")
                
    else:  # GitHub 연동
        st.info("💡 GitHub 저장소와 연동하여 문제를 관리할 수 있습니다.")
        repo_url = st.text_input(
            "GitHub 저장소 URL",
            placeholder="예: https://github.com/username/repo"
        )
        json_path = st.text_input(
            "JSON 파일 경로",
            placeholder="예: data/problems.json"
        )
        
        if st.button("🔄 GitHub에서 가져오기"):
            with st.spinner("GitHub에서 문제를 가져오는 중..."):
                try:
                    # GitHub 연동 로직 구현 예정
                    st.info("GitHub 연동 기능은 현재 개발 중입니다.")
                except Exception as e:
                    st.error(f"❌ GitHub 연동 중 오류가 발생했습니다: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 현재 등록된 문제 목록 표시
    st.markdown('<div class="problem-section">', unsafe_allow_html=True)
    st.subheader("📚 등록된 문제 목록")
    
    problems = problem_manager.get_all_problems()
    if problems:
        df = pd.DataFrame(problems)
        
        # 필터 옵션
        col6, col7 = st.columns(2)
        with col6:
            type_filter = st.multiselect(
                "유형 필터",
                df["type"].unique().tolist(),
                placeholder="모든 유형"
            )
        with col7:
            difficulty_filter = st.multiselect(
                "난이도 필터",
                df["difficulty"].unique().tolist(),
                placeholder="모든 난이도"
            )
        
        # 필터 적용
        if type_filter:
            df = df[df["type"].isin(type_filter)]
        if difficulty_filter:
            df = df[df["difficulty"].isin(difficulty_filter)]
        
        # 데이터프레임 표시
        st.dataframe(
            df[["title", "type", "difficulty", "time_limit"]],
            use_container_width=True,
            column_config={
                "title": "제목",
                "type": "유형",
                "difficulty": "난이도",
                "time_limit": "제한시간(분)"
            }
        )
    else:
        st.info("아직 등록된 문제가 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    create_problem_form()

if __name__ == "__main__":
    main() 