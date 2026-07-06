import streamlit as st
import numpy as np

# 1. 페이지 기본 설정 및 디자인 (Custom CSS)
st.set_page_config(page_title="SkyWatcher: 천체 관측 시뮬레이터", layout="wide")

st.markdown("""
<style>
    /* 전체 배경 및 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #0E1117;
    }
    
    /* 관측창(Sky View) 스타일 */
    .sky-container {
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        min-height: 400px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.5s ease;
    }
    
    /* 대시보드 카드 스타일 */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 10px;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 컨트롤러 (사용자 설정)
st.sidebar.title("🔭 Observation Settings")
st.sidebar.markdown("---")

target = st.sidebar.selectbox("관측 대상 선택", ["달 (The Moon)", "금성 (Venus)"])
direction = st.sidebar.radio("바라보는 방위", ["동 (East)", "남 (South)", "서 (West)", "북 (North)"], index=1)
time_of_day = st.sidebar.select_slider(
    "시간대 선택",
    options=["새벽 (03:00)", "아침 (08:00)", "낮 (12:00)", "저녁 (18:00)", "밤 (22:00)"],
    value="밤 (22:00)"
)

# 데이터 계산을 위한 내부 로직
phase_day = st.sidebar.slider("달의 음력 날짜 (위상 조절)", 0, 28, 7) if target == "달 (The Moon)" else 15

# 3. 메인 레이아웃
st.markdown(f'<p class="main-header">SkyWatcher Simulator</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# 시간대에 따른 하늘 배경색 결정
sky_colors = {
    "새벽 (03:00)": "linear-gradient(180deg, #020111 10%, #191938 100%)",
    "아침 (08:00)": "linear-gradient(180deg, #74ebd5 0%, #ACB6E5 100%)",
    "낮 (12:00)": "linear-gradient(180deg, #4facfe 0%, #00f2fe 100%)",
    "저녁 (18:00)": "linear-gradient(180deg, #ff9a9e 0%, #fecfef 99%, #feada6 100%)",
    "밤 (22:00)": "linear-gradient(180deg, #050505 0%, #1a1a2e 100%)"
}
current_sky = sky_colors[time_of_day]

# 4. 시각화 로직 (지평선 및 천체 위치)
with col1:
    # 천체가 보이는지 여부 판단 (매우 간소화된 교육용 로직)
    # 남중 기준: 상현달(음력7일)은 저녁에 남쪽, 보름달(15일)은 밤에 남쪽 등
    visible = True
    msg = ""
    
    # 달의 위상 모양 (SVG 생성)
    def get_moon_svg(day):
        ratio = np.cos((day/28)*2*np.pi)
        # 상현/하현 방향 결정
        is_waxing = day < 14
        color = "#F4D03F" if "밤" in time_of_day or "새벽" in time_of_day or "저녁" in time_of_day else "#FFFFFFCC"
        
        # 간단한 위상 시각화 (좌우 차오름)
        if day == 0: return "" # 삭
        return f"""
        <svg width="100" height="100" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="#2c3e50" />
            <path d="M 50 5 A 45 45 0 0 {'1' if is_waxing else '0'} 50 95" fill="{color}" />
            <ellipse cx="50" cy="50" rx="{abs(ratio)*45}" ry="45" fill="{'#2c3e50' if abs(ratio)<0.1 else color if ratio*(-1 if is_waxing else 1)>0 else '#2c3e50'}" />
        </svg>
        """

    moon_svg = get_moon_svg(phase_day) if target == "달 (The Moon)" else "🪐"

    # 하늘창 렌더링
    st.markdown(f"""
    <div class="sky-container" style="background: {current_sky};">
        <div style="position: absolute; bottom: 20px; width: 100%; color: white; font-weight: bold; font-size: 1.5rem;">
            {direction}쪽 하늘 지평선
        </div>
        <div style="margin-top: 80px; font-size: 5rem;">
            {moon_svg if visible else "이 시간/방향에는 보이지 않습니다"}
        </div>
        <div style="color: white; opacity: 0.8; margin-top: 20px;">
            {target} 관측 중
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. 정보 카드 (우측 컬럼)
with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("📊 관측 데이터")
    st.write(f"**현재 위치:** 서울 (위도 37.5°N)")
    st.write(f"**방위각:** {direction} (관측자 기준)")
    st.write(f"**고도:** 시간대에 따라 보정됨")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("💡 과학적 원리")
    if target == "달 (The Moon)":
        if direction == "남 (South)":
            st.info("남쪽 하늘에서는 달이 가장 높게 뜨는 '남중'을 관측할 수 있습니다.")
        elif direction == "동 (East)":
            st.info("모든 천체는 지구의 자전으로 인해 동쪽에서 떠오릅니다.")
        st.write(f"음력 {phase_day}일경 달은 {target.split()[0]} 상태입니다.")
    else:
        st.warning("금성은 내행성이므로 한밤중(자정)에는 절대로 보이지 않습니다! 오직 새벽이나 초저녁에만 볼 수 있습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 하단 가이드
st.markdown("---")
st.markdown("### 🎓 학습 가이드")
tabs = st.tabs(["달의 이동", "행성의 위상", "방위별 특징"])
with tabs[0]:
    st.write("달은 매일 약 50분씩 늦게 뜹니다. 이는 달이 지구 주위를 공전하기 때문입니다.")
with tabs[1]:
    st.write("금성은 태양 근처에서만 보이며, 망원경으로 보면 보름달 모양부터 초승달 모양까지 변하는 것을 알 수 있습니다.")
with tabs[2]:
    st.write("북쪽 하늘에서는 별들이 북극성을 중심으로 시계 반대 방향으로 회전하는 것처럼 보입니다.")
