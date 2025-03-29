import streamlit as st
from utils.ai_problem_generator import AIProblemGenerator

def show_api_settings():
    """API 설정을 관리하는 섹션을 표시합니다."""
    st.subheader("🔑 API 키 설정")
    
    ai_generator = AIProblemGenerator()
    
    # 현재 API 키 상태 표시
    current_key = st.session_state.get('gemini_api_key', '')
    if current_key:
        st.success("✅ API 키가 설정되어 있습니다")
        
        # 남은 생성 횟수 표시
        remaining = ai_generator.get_remaining_generations()
        st.info(f"🔄 오늘 남은 문제 생성 횟수: {remaining}개")
        
        # API 키 제거 버튼
        if st.button("🗑 API 키 제거"):
            ai_generator.remove_api_key()
            st.success("API 키가 제거되었습니다.")
            st.rerun()
    else:
        st.warning("⚠️ API 키가 설정되어 있지 않습니다")
        
        # API 키 입력 폼
        with st.form("api_key_form"):
            new_key = st.text_input(
                "Google Gemini API 키",
                type="password",
                help="Google Cloud Console에서 발급받은 API 키를 입력하세요."
            )
            
            submitted = st.form_submit_button("💾 API 키 저장")
            if submitted and new_key:
                if ai_generator.set_api_key(new_key):
                    st.success("✅ API 키가 성공적으로 설정되었습니다!")
                    st.rerun()
                else:
                    st.error("❌ 잘못된 API 키입니다. 다시 확인해주세요.")

def show_admin_settings():
    """관리자 설정 페이지를 표시합니다."""
    st.title("⚙️ 관리자 설정")
    
    # 관리자 권한 확인
    if st.session_state.get('user_role') != 'admin':
        st.error("🚫 관리자 권한이 필요합니다.")
        return
        
    # 탭 생성
    tab1, tab2 = st.tabs(["API 설정", "기타 설정"])
    
    with tab1:
        show_api_settings()
        
    with tab2:
        st.subheader("🛠 기타 설정")
        # 여기에 추가 설정 옵션 구현

def main():
    show_admin_settings()

if __name__ == "__main__":
    main() 