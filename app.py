import streamlit as st
import google.generativeai as genai
import json

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="선수 맞춤 상담사 추천 AI",
    page_icon="🥇",
    layout="centered"
)

# --- 상담사 데이터베이스 (파이썬 리스트) ---
# 상담사 정보를 수정, 추가, 삭제하려면 이 부분을 직접 편집하세요.
counselor_db = [
  {
    "counselor_name": "김병준",
    "gender": "남성",
    "experience_years": 20,
    "specialized_sports": ["골프", "축구", "국가대표 일반","야구"],
    "specialized_areas": ["슬럼프 극복", "성과 압박 관리", "경쟁 스트레스 해소", "자신감 회복", "회복 탄력성 강화", "커리어 전환 지원", "부상 후 심리 회복"],
    "qualification_level": "교수급/1급",
    "certifications": ["스포츠심리상담사 1급", "인하대학교  석사", "스포츠심리학 박사"],
    "counseling_locations": ["인천", "서울", "비대면(온라인)", "비대면(전화)"],
    "introduction": "'스포츠 심리학의 대가' 인하대학교 김병준 교수, 20년 이상의 상담 경력 및 유명 스포츠 팀, 선수, 메달리스트 대상 포트폴리오 보유"
  },
  {
    "counselor_name": "최유정",
    "gender": "여성",
    "experience_years": 2,
    "specialized_sports": ["스키", "수영", "골프"],
    "specialized_areas": ["루틴 개발", "집중력 향상", "팀워크 갈등 해결", "은퇴 후 진로 상담"],
    "qualification_level": "석사급/3급",
    "certifications": ["스포츠심리상담사 3급", "스포츠심리학 석사"],
    "counseling_locations": ["인천", "비대면(온라인)"],
    "introduction": "프로 선수 및 유소년 선수들의 심리 기술 훈련을 통해 꾸준한 경기력을 유지하고 목표를 달성할 수 있도록 지원합니다."
  }
]

# --- Gemini API 설정 및 추천 함수 ---
def get_gemini_recommendation(user_data, db):
    """Gemini API를 호출하여 상담사 추천을 받는 함수"""
    try:
        # Streamlit Cloud의 Secrets에서 API 키를 가져옵니다.
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        st.error("Gemini API 키를 설정하는 중 오류가 발생했습니다. Streamlit Cloud의 'Secrets'에 API 키가 올바르게 설정되었는지 확인해주세요.")
        return None

    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    당신은 선수의 고민과 상황을 분석하여 최적의 스포츠 심리 상담사를 추천하는 AI 전문가입니다.

    ### 상담사 데이터베이스 (JSON):
    {json.dumps(db, indent=2, ensure_ascii=False)}

    ### 상담을 요청한 선수 정보:
    - **소속 운동 종목:** {user_data['sport']}
    - **주요 고민:** {user_data['primary_concern']}
    - **상담 목표:** {', '.join(user_data['counseling_goal'])}
    - **선호 상담 지역/방식:** {', '.join(user_data['preferred_location'])}
    - **선호 상담사 성별:** {user_data['preferred_gender']}
    - **선호 상담사 전문성 수준:** {user_data['preferred_experience_level']}

    ### 지시사항:
    1. 선수의 '주요 고민'과 '상담 목표'를 깊이 분석하세요.
    2. 분석 내용을 바탕으로 상담사 데이터베이스에서 **가장 적합한 상담사 한 명**을 선택하세요.
    3. 아래 형식에 맞춰, 추천 이유를 상세하고 친절하게 설명하는 추천사를 작성해주세요. 추천사에는 반드시 구체적인 매칭 포인트를 명시해야 합니다.
    4. Markdown 형식을 사용하여 깔끔하게 출력해주세요.

    ---
    ### **AI 추천 결과**

    **[추천 상담사 이름]** 상담사님을 추천해 드립니다.

    **✅ 추천 이유:**
    * (여기에 선수의 고민과 상담사의 전문 분야가 어떻게 일치하는지 구체적으로 서술)
    * (여기에 선수가 선호하는 조건(지역, 성별 등)과 상담사가 어떻게 부합하는지 서술)

    **💡 이런 도움을 받을 수 있어요:**
    * (상담사의 전문성을 바탕으로 선수가 얻을 수 있는 기대효과 서술)
    ---
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"추천을 생성하는 중 오류가 발생했습니다: {e}")
        return None

# --- Streamlit UI 구성 ---
st.title("🥇 선수를 위한 맞춤 상담사 추천 AI")
st.write("당신의 마음을 가장 잘 이해하는 전문가를 찾아드릴게요.")

if counselor_db:
    with st.form("counseling_request_form"):
        st.header("1. 기본 정보를 알려주세요.")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름", placeholder="이고잉")
        with col2:
            contact = st.text_input("연락처", placeholder="010-1234-5678")
        
        sport = st.selectbox("소속 운동 종목", ["축구", "야구", "농구", "배구", "양궁", "기타"])

        st.header("2. 어떤 어려움을 겪고 있나요?")
        primary_concern = st.text_area(
            "현재 겪는 어려움이나 고민을 편하게 이야기해주세요.",
            height=150,
            placeholder="예시) 중요한 경기를 앞두고 너무 불안하고, 자신감이 떨어져 훈련에 집중하기 어렵습니다."
        )
        counseling_goal = st.multiselect(
            "상담을 통해 무엇을 얻고 싶으신가요? (복수 선택 가능)",
            ["자신감 회복", "스트레스 관리", "경기 중 집중력 향상", "슬럼프 극복", "부상 후 심리 회복", "은퇴 후 진로 설계"]
        )

        st.header("3. 원하시는 상담 조건이 있나요?")
        col3, col4 = st.columns(2)
        with col3:
            preferred_location = st.multiselect("선호 상담 지역/방식", ["서울 강남", "부산 해운대", "비대면(온라인)", "비대면(전화)"])
            preferred_gender = st.radio("선호 상담사 성별", ["남성", "여성", "상관없음"], index=2, horizontal=True)
        with col4:
            preferred_experience_level = st.selectbox("선호 상담사 전문성 수준", ["상관없음", "석사급 이상", "박사급 이상"])
        
        st.header("4. 마지막으로 동의해주세요.")
        privacy_consent = st.checkbox("개인정보 수집 및 이용에 동의합니다. (필수)")
        terms_consent = st.checkbox("상담 유의사항을 확인했으며, 이에 동의합니다. (필수)")

        submitted = st.form_submit_button("AI에게 추천 요청하기 🚀")

    if submitted:
        if not all([name, contact, primary_concern, privacy_consent, terms_consent]):
            st.error("필수 항목(이름, 연락처, 현재 겪는 어려움, 필수 동의)을 모두 채워주세요!")
        else:
            with st.spinner('AI가 내 마음을 알아주는 상담사님을 찾고 있어요... 잠시만 기다려주세요!'):
                user_data = {
                    "sport": sport,
                    "primary_concern": primary_concern,
                    "counseling_goal": counseling_goal,
                    "preferred_location": preferred_location,
                    "preferred_gender": preferred_gender,
                    "preferred_experience_level": preferred_experience_level,
                }
                
                recommendation = get_gemini_recommendation(user_data, counselor_db)
                
                if recommendation:
                    st.success(f"{name}님을 위한 맞춤 상담사를 찾았어요!")
                    st.markdown(recommendation)
else:
    st.warning("상담사 데이터가 비어있습니다. `app.py` 파일의 `counselor_db` 리스트를 확인해주세요.")
    