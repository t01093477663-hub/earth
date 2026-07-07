import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# 1. 프리미엄 천문 대시보드 UI 스타일 (Cyber Black & Minimal)
st.set_page_config(page_title="지구과학I 천체 운동 시뮬레이터", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=500;700&family=Pretendard:wght=400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #05070A;
        color: #F8FAFC;
    }
    
    .dashboard-card {
        background: #0D1117;
        border: 1px solid #21262D;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .main-header {
        font-family: 'Space Grotesk', 'Pretendard', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366F1 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-header {
        color: #484F58;
        font-size: 0.95rem;
        margin-bottom: 1.8rem;
    }
    
    .status-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(56, 189, 248, 0.1);
        color: #58A6FF;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    
    .control-label {
        font-size: 0.9rem;
        color: #8B949E;
        font-weight: 600;
        margin-bottom: 8px;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 2. 세션 상태 데이터 초기화
if "current_hour" not in st.session_state:
    st.session_state.current_hour = 18  # 내행성 관측의 핵심인 초저녁(18시)을 기본값으로 설정
if "current_phase" not in st.session_state:
    st.session_state.current_phase = 47 # 초기 위치를 동방최대이각(47°)으로 설정

# 3. 사이드바 제어 패널 (간결하게 핵심 옵션 유지)
st.sidebar.title("🔭 Astro Control")
st.sidebar.markdown("---")

target_mode = st.sidebar.selectbox(
    "1. 관측 핵심 주제 선택", 
    ["내행성의 운동 (금성)", "일식과 월식 (달의 운동)", "외행성의 운동 (화성)"]
)

direction = st.sidebar.radio("2. 바라보는 방위 선택",
