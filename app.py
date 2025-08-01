import streamlit as st
import google.generativeai as genai
import json
from collections import OrderedDict

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="선수 맞춤 상담사 추천 AI",
    page_icon="🥇",
    layout="centered"
)

# --- 상담사 데이터베이스 (파이썬 리스트) ---
# booking_link에 각 상담사의 실제 예약 페이지 URL을 입력하세요.
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
    "introduction": "'스포츠 심리학의 대가' 인하대학교 김병준 교수, 20년 이상의 상담 경력 및 유명 스포츠 팀, 선수, 메달리스트 대상 포트폴리오 보유",
    "booking_link": "https://app.tufly.co.kr/counselors/%EA%B9%80%ED%98%95%EC%98%A5?resource=0a166abf-9185-4246-b328-836d8fa6001c"
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
    "introduction": "프로 선수 및 유소년 선수들의 심리 기술 훈련을 통해 꾸준한 경기력을 유지하고 목표를 달성할 수 있도록 지원합니다.",
    "booking_link": "https://app.tufly.co.kr/counselors/full-name-06?resource=8dc8e72e-74c4-4f7b-bb39-186197bd553f"
  },
  {
    "counselor_name": "우영임",
    "gender": "여성",
    "experience_years": 4,
    "specialized_sports": ["골프", "일반"],
    "specialized_areas": ["멘탈 퍼포먼스 향상", "루틴 개발", "집중력 향상", "실질적 문제 해결"],
    "qualification_level": "석사급/2급",
    "certifications": ["스포츠심리상담사 2급", "중등 정교사 2급 (체육)", "스포츠윤리지도사", "우수논문상 수상 (한국스포츠심리학회)"],
    "counseling_locations": ["인천", "경기도", "비대면(온라인)"],
    "introduction": "오랜 기간 동안 현장 중심의 스포츠심리상담 경험과 학문적 연구 성과를 모두 쌓아온 전문가입니다. 스포츠 현장의 실질적인 문제 해결부터, 프로그램 개발과 평가까지 폭넓게 다뤄온 이력을 갖추고 있습니다.",
    "booking_link": "https://app.tufly.co.kr/counselors/full-name-04?resource=c5b8ad96-7b32-440e-a308-2274f9b87d0f"
  },
  {
    "counselor_name": "송재경",
    "gender": "여성",
    "experience_years": 5,
    "specialized_sports": ["수영", "국가대표 일반"],
    "specialized_areas": ["선수 경험 기반 상담", "심리적 고충 이해", "멘탈 퍼포먼스 향상", "집중력 향상"],
    "qualification_level": "석사급/2급",
    "certifications": ["스포츠심리상담사 2급"],
    "counseling_locations": ["인천", "서울", "비대면(온라인)"],
    "introduction": "대한민국 국가대표 수영선수 출신이라는 특별한 이력을 바탕으로, 선수들의 심리적 고충을 실질적으로 이해하고 소통할 수 있는 강점을 지닌 전문가입니다. 현재는 박사과정 중에도 다양한 강의와 프로그램을 진행하며 스포츠심리 현장에 적극적으로 참여하고 있습니다.",
    "booking_link": "https://app.tufly.co.kr/counselors/full-name-02?resource=0a166abf-9185-4246-b328-836d8fa6001c"
  }
]

# --- 선택지 목록 정의 ---
SPORTS_LIST = [
    "축구", "야구", "농구", "배구", "핸드볼", "럭비", "미식축구", "아이스하키",
    "골프", "테니스", "배드민턴", "탁구", "스쿼시", "수영", "다이빙", "육상",
    "체조", "리듬체조", "유도", "태권도", "가라테", "레슬링", "복싱", "펜싱",
    "양궁", "사격", "역도", "사이클", "승마", "스키", "스노보드", "스케이트",
    "컬링", "e스포츠", "기타"
]
LOCATION_LIST = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시",
    "울산광역시", "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도",
    "전북특별자치도", "전라남도", "경상북도", "경상남도", "제주특별자치도",
    "비대면(온라인)", "비대면(전화)"
]
all_areas = list(OrderedDict.fromkeys([area for c in counselor_db for area in c['specialized_areas']]))
AREAS_OF_CONCERN = all_areas


# --- Gemini API 설정 및 추천 함수 ---
def get_gemini_recommendation(user_data, db):
    """Gemini API를 호출하여 상담사 추천을 받는 함수"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        st.error("Gemini API 키를 설정하는 중 오류가 발생했습니다.")
        return None

    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    당신은 선수의 고민을 분석하여 최적의 스포츠 심리 상담사를 추천하는 AI 전문가입니다.

    ### 상담사 데이터베이스 (JSON):
    {json.dumps(db, indent=2, ensure_ascii=False)}

    ### 상담을 요청한 선수 정보:
    - **소속 운동 종목:** {user_data['sport']}
    - **주요 고민 분야:** {', '.join(user_data['areas_of_concern'])}
    - **선호 상담 지역/방식:** {', '.join(user_data['preferred_location'])}
    - **선호 상담사 성별:** {user_data['preferred_gender']}
    - **선호 상담사 전문성 수준:** {user_data['preferred_experience_level']}

    ### 지시사항:
    1. 선수의 '주요 고민 분야'를 깊이 분석하여 데이터베이스에서 **가장 적합한 상담사 한 명**을 선택하세요.
    2. 아래의 JSON 형식에 맞춰 결과를 반환해주세요.
       - "recommendation_text": Markdown 형식의 추천사 텍스트. 추천 이유와 기대효과를 포함해야 합니다.
       - "booking_link": 추천된 상담사의 `booking_link` 값.

    ```json
    {{
      "recommendation_text": "...",
      "booking_link": "..."
    }}
    ```
    """
    try:
        response = model.generate_content(prompt)
        # 응답 텍스트에서 JSON 부분만 추출하여 파싱
        response_json_str = response.text.strip().lstrip("```json").rstrip("```")
        response_json = json.loads(response_json_str)
        return response_json
    except (json.JSONDecodeError, AttributeError, ValueError) as e:
        st.error(f"AI 응답을 처리하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. (오류: {e})")
        return None
    except Exception as e:
        st.error(f"추천을 생성하는 중 오류가 발생했습니다: {e}")
        return None

# --- Streamlit UI 구성 ---
st.title("🥇 선수를 위한 맞춤 상담사 추천 AI")
st.write("당신의 마음을 가장 잘 이해하는 전문가를 찾아드릴게요.")

if counselor_db:
    with st.form("counseling_request_form"):
        st.header("1. 선수 정보를 알려주세요.")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름", placeholder="이고잉")
        with col2:
            sport = st.selectbox("소속 운동 종목", SPORTS_LIST)

        areas_of_concern = st.multiselect(
            "어떤 도움이 필요하신가요? (주요 고민 분야, 복수 선택 가능)",
            AREAS_OF_CONCERN
        )

        st.header("2. 원하시는 상담 조건이 있나요?")
        preferred_location = st.multiselect("선호 상담 지역/방식", LOCATION_LIST)

        col3, col4 = st.columns(2)
        with col3:
            preferred_gender = st.radio("선호 상담사 성별", ["남성", "여성", "상관없음"], index=2, horizontal=True)
        with col4:
            preferred_experience_level = st.selectbox("선호 상담사 전문성 수준", ["상관없음", "석사급 이상", "박사급 이상"])

        st.header("3. 마지막으로 동의해주세요.")
        privacy_consent = st.checkbox("개인정보 수집 및 이용에 동의합니다. (필수)")
        terms_consent = st.checkbox("상담 유의사항을 확인했으며, 이에 동의합니다. (필수)")

        submitted = st.form_submit_button("AI에게 추천 요청하기 🚀")

    if submitted:
        # 새로운 요청이 제출되면 이전 추천 결과는 초기화
        if 'recommendation_result' in st.session_state:
            del st.session_state['recommendation_result']

        if not all([name, areas_of_concern, privacy_consent, terms_consent]):
            st.error("필수 항목(이름, 도움이 필요한 분야, 필수 동의)을 모두 채워주세요!")
        else:
            with st.spinner('AI가 내 마음을 알아주는 상담사님을 찾고 있어요... 잠시만 기다려주세요!'):
                user_data = {
                    "sport": sport,
                    "areas_of_concern": areas_of_concern,
                    "preferred_location": preferred_location,
                    "preferred_gender": preferred_gender,
                    "preferred_experience_level": preferred_experience_level,
                }

                recommendation_result = get_gemini_recommendation(user_data, counselor_db)

                if recommendation_result:
                    st.success(f"{name}님을 위한 맞춤 상담사를 찾았어요!")
                    st.session_state.recommendation_result = recommendation_result

    # 추천 결과가 세션 상태에 저장되어 있으면 출력
    if 'recommendation_result' in st.session_state:
        result = st.session_state.recommendation_result
        st.markdown("---")
        st.markdown(result.get("recommendation_text", "추천 내용을 불러오는 데 실패했습니다."))

        booking_link = result.get("booking_link")
        if booking_link:
            st.link_button("상담 예약하기", booking_link, type="primary")

else:
    st.warning("상담사 데이터가 비어있습니다. `app.py` 파일의 `counselor_db` 리스트를 확인해주세요.")