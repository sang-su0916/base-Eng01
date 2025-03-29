import streamlit as st
from utils.problem_manager import ProblemManager
from utils.github_sync import GitHubSync
import pandas as pd
from datetime import datetime
import io
import json
from utils.problem_generator import ProblemGenerator
from pathlib import Path
from utils.ai_problem_generator import AIProblemGenerator
import os

# 문제 관리자 초기화
problem_manager = ProblemManager()
problem_generator = ProblemGenerator()

# AI 문제 생성기 초기화
ai_generator = AIProblemGenerator()

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
    .review-pending {
        color: #ffc107;
        font-weight: bold;
    }
    .review-approved {
        color: #28a745;
        font-weight: bold;
    }
    .review-rejected {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # AI 문제 생성 섹션
    st.markdown('<div class="problem-section">', unsafe_allow_html=True)
    st.subheader("🤖 AI 문제 추천")
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.write("AI가 기본적인 영어 문제를 생성하면, 선생님/관리자의 검토 후 등록됩니다.")
    st.write("- 문법, 어휘, 독해 등 다양한 유형")
    st.write("- 초급, 중급, 고급 수준별 문제")
    st.write("- 모범 답안과 채점 기준 포함")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        ai_problem_type = st.selectbox(
            "문제 유형",
            ["문법", "어휘", "독해", "작문", "회화"],
            key="ai_problem_type"
        )
    with col2:
        ai_difficulty = st.selectbox(
            "난이도",
            ["초급", "중급", "고급"],
            key="ai_difficulty"
        )
    
    if st.button("🎲 AI 문제 생성", use_container_width=True):
        with st.spinner("문제를 생성하는 중..."):
            problems = problem_generator.generate_problems(ai_problem_type, ai_difficulty)
            for problem in problems:
                problem['status'] = 'pending'  # 검토 대기 상태로 설정
                problem_manager.add_pending_problem(problem)
            st.success(f"✅ {len(problems)}개의 문제가 생성되어 검토 대기열에 추가되었습니다!")
    
    # 검토 대기 중인 문제 표시 (선생님/관리자용)
    if st.session_state.get('user_role') in ['teacher', 'admin']:
        st.markdown("### 📋 검토 대기 중인 문제")
        pending_problems = problem_manager.get_pending_problems()
        
        if pending_problems:
            for problem in pending_problems:
                with st.expander(f"📝 {problem['title']} ({problem['type']} - {problem['difficulty']})"):
                    st.write("**문제 내용:**")
                    st.write(problem['content'])
                    st.write("**모범 답안:**")
                    st.write(problem['model_answer'])
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        if st.button("✅ 승인", key=f"approve_{problem['id']}", use_container_width=True):
                            problem_manager.approve_problem(problem['id'])
                            st.success("문제가 승인되었습니다!")
                            st.rerun()
                    with col4:
                        if st.button("❌ 거절", key=f"reject_{problem['id']}", use_container_width=True):
                            problem_manager.reject_problem(problem['id'])
                            st.error("문제가 거절되었습니다.")
                            st.rerun()
        else:
            st.info("검토 대기 중인 문제가 없습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 문제 입력 방식 선택
    st.markdown('<div class="problem-section">', unsafe_allow_html=True)
    st.subheader("📝 문제 직접 입력")
    
    input_method = st.radio(
        "문제 입력 방식을 선택하세요:",
        ["✏️ 직접 입력", "📎 CSV 파일 업로드", "🔄 GitHub 연동"]
    )
    
    if input_method == "✏️ 직접 입력":
        show_manual_input_form()
    elif input_method == "📎 CSV 파일 업로드":
        show_file_upload_section()
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

def show_file_upload_section():
    """파일 업로드 섹션을 표시합니다."""
    st.markdown("""
    <style>
    .upload-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .guide-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .sample-table {
        font-size: 0.9rem;
        margin: 1rem 0;
        border-collapse: collapse;
        width: 100%;
    }
    .sample-table th {
        background-color: #e9ecef;
        padding: 0.5rem;
        text-align: left;
    }
    .sample-table td {
        padding: 0.5rem;
        border-bottom: 1px solid #dee2e6;
    }
    .required {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    # 가이드 섹션
    st.markdown('<div class="guide-section">', unsafe_allow_html=True)
    st.markdown("""
    ### 📋 CSV 파일 형식 안내
    
    #### 필수 컬럼
    - `title`: 문제 제목 <span class="required">*</span>
    - `type`: 문제 유형 (문법/어휘/독해/영작문/듣기/말하기) <span class="required">*</span>
    - `content`: 문제 내용 <span class="required">*</span>
    - `difficulty`: 난이도 (초급/중급/고급) <span class="required">*</span>
    - `correct_answer`: 정답 <span class="required">*</span>
    
    #### 선택 컬럼
    - `keywords`: 채점 키워드 (쉼표로 구분)
    - `explanation`: 문제 해설
    - `time_limit`: 제한시간(분)
    - `points`: 배점
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 샘플 파일 다운로드
    sample_csv = """title,type,content,difficulty,correct_answer,keywords,explanation,time_limit,points
Unit 1 - Present Simple,문법,Complete the sentence: I ___ to school every day.,초급,go,"go,present simple,daily routine",Present simple is used for daily habits,15,10
Vocabulary - Food,어휘,What is the meaning of 'apple' in Korean?,초급,사과,"fruit,food,vocabulary",Basic food vocabulary,5,5
Reading Comprehension 1,독해,Read the passage and answer the questions...,중급,B,"reading,comprehension",Detailed explanation of the passage,20,15
Speaking Practice,말하기,Describe your daily routine using present simple.,중급,Sample answer provided,"speaking,daily routine",Focus on using time expressions,10,10"""
    
    st.download_button(
        label="📥 샘플 파일 다운로드",
        data=sample_csv,
        file_name="problem_template.csv",
        mime="text/csv",
        help="문제 업로드를 위한 샘플 CSV 파일을 다운로드합니다."
    )
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "CSV 파일 선택",
        type=['csv'],
        help="UTF-8 인코딩으로 저장된 CSV 파일을 업로드하세요."
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['title', 'type', 'content', 'difficulty', 'correct_answer']
            
            # 필수 컬럼 확인
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                st.error(f"⚠️ 다음 필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
                return
                
            # 데이터 미리보기
            st.success("✅ 파일이 성공적으로 업로드되었습니다!")
            st.markdown("### 📊 데이터 미리보기")
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "title": "제목",
                    "type": "유형",
                    "content": "내용",
                    "difficulty": "난이도",
                    "correct_answer": "정답",
                    "keywords": "키워드",
                    "explanation": "해설",
                    "time_limit": "제한시간(분)",
                    "points": "배점"
                }
            )
            
            # 문제 등록
            if st.button("📥 문제 일괄 등록", type="primary", use_container_width=True):
                success_count = 0
                error_count = 0
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, row in df.iterrows():
                    try:
                        problem_data = {
                            'title': row['title'],
                            'type': row['type'],
                            'content': row['content'],
                            'difficulty': row['difficulty'],
                            'correct_answer': row['correct_answer'],
                            'keywords': [k.strip() for k in str(row.get('keywords', '')).split(',') if k.strip()],
                            'explanation': row.get('explanation', ''),
                            'time_limit': int(row.get('time_limit', 15)),
                            'points': int(row.get('points', 10)),
                            'created_at': datetime.now().isoformat()
                        }
                        
                        if problem_manager.add_problem(problem_data):
                            success_count += 1
                        else:
                            error_count += 1
                            
                        # 진행률 업데이트
                        progress = (i + 1) / len(df)
                        progress_bar.progress(progress)
                        status_text.text(f"처리 중... ({i + 1}/{len(df)})")
                        
                    except Exception as e:
                        error_count += 1
                        st.error(f"행 {i+1} 처리 중 오류 발생: {str(e)}")
                
                if success_count > 0:
                    st.success(f"✅ {success_count}개의 문제가 성공적으로 등록되었습니다!")
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count}개의 문제는 등록에 실패했습니다.")
                    st.balloons()
                else:
                    st.error("❌ 문제 등록에 실패했습니다.")
                    
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
            
    st.markdown('</div>', unsafe_allow_html=True)

def show_ai_generation_section():
    """AI 문제 생성 섹션을 표시합니다."""
    st.markdown("""
    <style>
    .ai-section {
        padding: 1.5rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        background-color: #e9ecef;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stat-box {
        padding: 0.5rem 1rem;
        background-color: white;
        border-radius: 5px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="ai-section">', unsafe_allow_html=True)
    st.subheader("🤖 AI 문제 생성")
    
    ai_generator = AIProblemGenerator()
    
    # API 키 상태 확인
    if not st.session_state.get('gemini_api_key'):
        st.warning("⚠️ AI 문제 생성을 위해서는 관리자가 API 키를 설정해야 합니다.")
        if st.session_state.get('user_role') == 'admin':
            st.info("관리자 설정 페이지에서 API 키를 설정할 수 있습니다.")
        return
        
    # 남은 생성 횟수 표시
    remaining = ai_generator.get_remaining_generations()
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("오늘 남은 생성 횟수", f"{remaining}개")
    with col2:
        st.metric("일일 최대 생성 한도", "100개")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not ai_generator.can_generate_more():
        st.error("❌ 오늘의 문제 생성 한도를 모두 사용했습니다. 내일 다시 시도해주세요.")
        return
        
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 📝 AI 문제 생성 가이드
    1. 문제 유형과 난이도를 선택하세요
    2. 주제를 지정하면 더 구체적인 문제가 생성됩니다
    3. 한 번에 최대 5개까지 문제를 생성할 수 있습니다
    4. 생성된 문제는 검토 후 저장할 수 있습니다
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 문제 생성 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        problem_type = st.selectbox(
            "문제 유형",
            ["단어", "문법", "독해", "회화"],
            help="생성할 문제의 유형을 선택하세요."
        )
        
        count = st.number_input(
            "생성할 문제 수",
            min_value=1,
            max_value=min(5, remaining),
            value=1,
            help=f"한 번에 최대 {min(5, remaining)}개까지 생성할 수 있습니다."
        )
        
    with col2:
        difficulty = st.slider(
            "난이도",
            min_value=1,
            max_value=5,
            value=3,
            help="1: 매우 쉬움, 5: 매우 어려움"
        )
        
        topic = st.text_input(
            "주제 (선택사항)",
            placeholder="예: 일상생활, 비즈니스, 여행 등",
            help="특정 주제에 대한 문제를 생성하려면 입력해주세요."
        )
    
    if st.button("🤖 AI 문제 생성", type="primary", use_container_width=True):
        try:
            with st.spinner("AI가 문제를 생성하고 있습니다..."):
                problems = ai_generator.generate_problems(
                    problem_type=problem_type,
                    difficulty=difficulty,
                    count=count,
                    topic=topic if topic else None
                )
                
            st.success(f"✨ {len(problems)}개의 문제가 생성되었습니다!")
            
            # 생성된 문제 표시
            for i, problem in enumerate(problems, 1):
                with st.expander(f"📝 문제 {i}: {problem['title']}", expanded=True):
                    st.markdown(f"""
                    **유형:** {problem['type']}  
                    **난이도:** {'⭐' * int(problem['difficulty'])}
                    
                    **문제 내용:**  
                    {problem['content']}
                    
                    <details>
                    <summary>정답 보기</summary>
                    
                    **정답:** {problem['correct_answer']}
                    
                    **채점 키워드:** {', '.join(problem['keywords'])}
                    
                    **해설:** {problem['explanation']}
                    </details>
                    """, unsafe_allow_html=True)
            
            # 문제 저장 버튼
            if st.button("💾 생성된 문제 저장", type="primary", use_container_width=True):
                success_count = 0
                with st.spinner("문제를 저장하고 있습니다..."):
                    for problem in problems:
                        if problem_manager.add_problem(problem):
                            success_count += 1
                
                if success_count > 0:
                    st.success(f"✅ {success_count}개의 문제가 성공적으로 저장되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 문제 저장 중 오류가 발생했습니다.")
                    
        except Exception as e:
            st.error(f"문제 생성 중 오류가 발생했습니다: {str(e)}")
            if "rate limit" in str(e).lower():
                st.warning("⚠️ API 호출 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
                
    st.markdown('</div>', unsafe_allow_html=True)

def show_manual_input_form():
    """직접 입력 폼을 표시합니다."""
    st.markdown("""
    <style>
    .form-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .preview-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .keyword-tag {
        display: inline-block;
        background-color: #e9ecef;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    
    with st.form("problem_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "제목",
                placeholder="예: Unit 1 - Present Simple",
                help="문제의 제목을 입력하세요."
            )
            
            problem_type = st.selectbox(
                "문제 유형",
                ["문법", "어휘", "독해", "영작문", "듣기", "말하기"],
                help="문제의 유형을 선택하세요."
            )
            
            difficulty = st.select_slider(
                "난이도",
                options=["초급", "중급", "고급"],
                value="중급",
                help="문제의 난이도를 선택하세요."
            )
            
        with col2:
            time_limit = st.number_input(
                "제한시간(분)",
                min_value=1,
                max_value=60,
                value=15,
                help="문제 풀이에 주어지는 시간을 설정하세요."
            )
            
            keywords = st.text_input(
                "키워드",
                placeholder="예: present simple, daily routine, habits",
                help="채점에 사용될 키워드를 쉼표로 구분하여 입력하세요."
            )
            
            points = st.number_input(
                "배점",
                min_value=1,
                max_value=100,
                value=10,
                help="이 문제의 배점을 설정하세요."
            )
        
        content = st.text_area(
            "문제 내용",
            height=200,
            placeholder="여기에 문제 내용을 작성하세요...",
            help="문제의 지문, 보기, 질문 등을 포함한 전체 내용을 작성하세요."
        )
        
        col3, col4 = st.columns(2)
        with col3:
            correct_answer = st.text_area(
                "정답",
                height=100,
                placeholder="정답을 입력하세요...",
                help="문제의 정답을 입력하세요."
            )
        with col4:
            explanation = st.text_area(
                "해설",
                height=100,
                placeholder="문제 해설을 작성하세요...",
                help="학생들의 이해를 돕기 위한 해설을 작성하세요."
            )
        
        # 미리보기 섹션
        if content:
            st.markdown("### 📝 미리보기")
            st.markdown('<div class="preview-section">', unsafe_allow_html=True)
            st.markdown(f"""
            **{title or '제목 없음'}** ({difficulty} 난이도, {time_limit}분)
            
            **문제 내용:**
            {content}
            
            <details>
            <summary>정답 및 해설 보기</summary>
            
            **정답:** {correct_answer or '미입력'}
            
            **해설:** {explanation or '미입력'}
            
            **키워드:** {' '.join([f'<span class="keyword-tag">{k.strip()}</span>' for k in keywords.split(',') if k.strip()])}
            </details>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        col5, col6, col7 = st.columns([1,2,1])
        with col6:
            submitted = st.form_submit_button(
                "💾 문제 저장",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            if not title or not content or not correct_answer:
                st.error("⚠️ 제목, 문제 내용, 정답은 필수 입력 항목입니다.")
            else:
                problem = {
                    "title": title,
                    "type": problem_type,
                    "difficulty": difficulty,
                    "time_limit": time_limit,
                    "content": content,
                    "correct_answer": correct_answer,
                    "explanation": explanation,
                    "keywords": [k.strip() for k in keywords.split(',') if k.strip()],
                    "points": points,
                    "created_at": datetime.now().isoformat()
                }
                
                if problem_manager.add_problem(problem):
                    st.success("✅ 문제가 성공적으로 저장되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 문제 저장 중 오류가 발생했습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 최근 등록된 문제 목록
    st.markdown("### 📚 최근 등록된 문제")
    problems = problem_manager.get_all_problems()
    if problems:
        recent_problems = sorted(
            problems,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )[:5]
        
        for problem in recent_problems:
            with st.expander(f"📝 {problem['title']} ({problem['type']} - {problem['difficulty']})"):
                st.markdown(f"""
                **문제 내용:**
                {problem['content']}
                
                <details>
                <summary>정답 및 해설 보기</summary>
                
                **정답:** {problem['correct_answer']}
                
                **해설:** {problem.get('explanation', '해설 없음')}
                
                **키워드:** {' '.join([f'<span class="keyword-tag">{k}</span>' for k in problem['keywords']])}
                
                **배점:** {problem.get('points', 10)}점
                </details>
                """, unsafe_allow_html=True)
    else:
        st.info("아직 등록된 문제가 없습니다.")

def show_github_integration():
    """GitHub 연동 섹션을 표시합니다."""
    st.markdown("""
    <style>
    .github-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .guide-section {
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
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="github-section">', unsafe_allow_html=True)
    st.subheader("🔄 GitHub 연동")
    
    # 가이드 섹션
    st.markdown('<div class="guide-section">', unsafe_allow_html=True)
    st.markdown("""
    ### 📋 GitHub 연동 가이드
    
    1. GitHub 저장소 설정
       - 문제 데이터가 저장된 GitHub 저장소 URL을 입력하세요
       - JSON 파일 경로를 지정하세요 (예: data/problems.json)
    
    2. 액세스 토큰 설정 (선택사항)
       - 비공개 저장소를 사용하는 경우 필요합니다
       - GitHub Settings > Developer settings > Personal access tokens에서 생성
    
    3. 동기화 설정
       - 자동 동기화: 저장소 변경 시 자동으로 문제를 가져옵니다
       - 수동 동기화: 버튼을 클릭하여 문제를 가져옵니다
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # GitHub 설정
    col1, col2 = st.columns(2)
    with col1:
        repo_url = st.text_input(
            "GitHub 저장소 URL",
            placeholder="예: https://github.com/username/repo",
            help="문제 데이터가 저장된 GitHub 저장소의 URL을 입력하세요."
        )
    with col2:
        json_path = st.text_input(
            "JSON 파일 경로",
            placeholder="예: data/problems.json",
            help="저장소 내 문제 데이터가 저장된 JSON 파일의 경로를 입력하세요."
        )
    
    # 액세스 토큰 설정
    access_token = st.text_input(
        "GitHub 액세스 토큰 (선택사항)",
        type="password",
        help="비공개 저장소를 사용하는 경우 액세스 토큰을 입력하세요."
    )
    
    # 동기화 설정
    auto_sync = st.checkbox(
        "자동 동기화 활성화",
        help="저장소 변경 시 자동으로 문제를 가져옵니다."
    )
    
    # 연동 상태 표시
    if 'github_sync_status' not in st.session_state:
        st.session_state.github_sync_status = {
            'connected': False,
            'last_sync': None,
            'error': None
        }
    
    status = st.session_state.github_sync_status
    status_class = 'status-success' if status['connected'] else 'status-error'
    if status['error']:
        status_class = 'status-error'
    elif not status['connected']:
        status_class = 'status-warning'
    
    st.markdown(f'<div class="status-box {status_class}">', unsafe_allow_html=True)
    if status['connected']:
        st.markdown("""
        ### ✅ GitHub 연동 상태
        - 상태: 연결됨
        - 마지막 동기화: {last_sync}
        """.format(last_sync=status['last_sync'] if status['last_sync'] else '없음'))
    elif status['error']:
        st.markdown(f"""
        ### ❌ GitHub 연동 오류
        - 오류: {status['error']}
        """)
    else:
        st.markdown("""
        ### ⚠️ GitHub 연동 상태
        - 상태: 미연결
        - 저장소 정보를 입력하고 연동을 시작하세요
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 연동 버튼
    col3, col4 = st.columns(2)
    with col3:
        if st.button("🔄 GitHub 연동", type="primary", use_container_width=True):
            try:
                with st.spinner("GitHub 저장소와 연동 중..."):
                    github_sync = GitHubSync(repo_url, json_path, access_token)
                    if github_sync.connect():
                        st.session_state.github_sync_status = {
                            'connected': True,
                            'last_sync': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'error': None
                        }
                        st.success("✅ GitHub 저장소와 성공적으로 연동되었습니다!")
                        st.balloons()
                    else:
                        st.error("❌ GitHub 저장소 연동에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 연동 중 오류가 발생했습니다: {str(e)}")
                st.session_state.github_sync_status['error'] = str(e)
    
    with col4:
        if st.button("📥 문제 가져오기", use_container_width=True):
            if not status['connected']:
                st.warning("⚠️ 먼저 GitHub 저장소와 연동해주세요.")
            else:
                try:
                    with st.spinner("GitHub에서 문제를 가져오는 중..."):
                        problems = github_sync.get_problems()
                        if problems:
                            success_count = 0
                            for problem in problems:
                                if problem_manager.add_problem(problem):
                                    success_count += 1
                            
                            if success_count > 0:
                                st.success(f"✅ {success_count}개의 문제를 성공적으로 가져왔습니다!")
                                st.balloons()
                            else:
                                st.warning("⚠️ 가져온 문제 중 저장된 문제가 없습니다.")
                        else:
                            st.warning("⚠️ 가져올 문제가 없습니다.")
                except Exception as e:
                    st.error(f"❌ 문제 가져오기 중 오류가 발생했습니다: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align: center;'>📝 문제 출제</h1>", unsafe_allow_html=True)
    
    # 사용 설명서
    with st.expander("📖 사용 설명서", expanded=False):
        st.markdown("""
        ### 🎯 문제 출제 시스템 사용 방법
        
        #### 1. 직접 입력으로 문제 출제
        1. '직접 입력' 탭을 선택합니다.
        2. 다음 정보를 입력합니다:
           - 제목: 문제의 제목
           - 유형: 문법, 독해, 작문 중 선택
           - 난이도: 1~5 레벨 중 선택
           - 제한시간: 문제 풀이 제한 시간(분)
           - 내용: 실제 문제 내용
           - 모범답안: 정답 또는 예시 답안
           - 키워드: 채점에 사용될 핵심 단어(쉼표로 구분)
        3. '문제 등록' 버튼을 클릭하여 저장합니다.
        
        #### 2. CSV 파일로 문제 업로드
        1. 'CSV 업로드' 탭을 선택합니다.
        2. CSV 파일 형식:
           - 필수 열: title, type, difficulty, time_limit, content, model_answer, keywords
           - 각 행이 하나의 문제를 나타냅니다.
        3. '파일 선택' 버튼으로 CSV 파일을 선택합니다.
        4. '업로드' 버튼을 클릭하여 문제를 일괄 등록합니다.
        
        #### 3. GitHub에서 문제 가져오기
        1. 'GitHub 연동' 탭을 선택합니다.
        2. GitHub 저장소 정보를 입력합니다:
           - 저장소 URL
           - 파일 경로
           - 액세스 토큰(필요한 경우)
        3. '문제 가져오기' 버튼을 클릭하여 동기화합니다.
        
        ### ⚠️ 주의사항
        - 문제 내용은 명확하고 이해하기 쉽게 작성해주세요.
        - 모범답안은 상세하게 작성하여 학생들의 이해를 돕습니다.
        - 키워드는 채점의 기준이 되므로 신중하게 선택해주세요.
        - CSV 파일 업로드 시 형식을 정확히 지켜주세요.
        """)
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs([
        "✍️ 직접 입력",
        "📎 CSV 파일 업로드",
        "🤖 AI 문제 생성",
        "🔄 GitHub 연동"
    ])
    
    with tab1:
        show_manual_input_form()
        
    with tab2:
        show_file_upload_section()
        
    with tab3:
        show_ai_generation_section()
        
    with tab4:
        show_github_integration()

if __name__ == "__main__":
    main() 