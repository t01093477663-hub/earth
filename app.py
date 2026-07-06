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

target = st.sidebar.selectbox("관측 대상 선택", ["달 (The Moon)", "화성 (Mars, 외행성)"])
direction = st.sidebar.radio("바라보는 방위", ["동 (East)", "남 (South)", "서 (West)", "북 (North)"], index=1)
time_of_day = st.sidebar.select_slider(
    "시간대 선택",
    options=["새벽 (03:00)", "아침 (08:00)", "낮 (12:00)", "저녁 (18:00)", "밤 (22:00)"],
    value="밤 (22:00)"
)

# 데이터 계산을 위한 내부 로직 (위상 조절 슬라이더)
if target == "달 (The Moon)":
    phase_day = st.sidebar.slider("달의 음력 날짜 (위상 조절)", 0, 28, 7)
else:
    # 화성의 이각/위상 조건 설정 (충, 구, 합 등)
    mars_position = st.sidebar.select_slider(
        "화성의 위치 상태 변경",
        options=["충 (Opposition, 지구와 가장 가깝고 밝음)", "구 (Quadrature, 반달 모양에 가까움)", "합 (Conjunction, 태양 반대편)"],
        value="충 (Opposition, 지구와 가장 가깝고 밝음)"
    )

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
    
    # 달의 위상 모양 (SVG 알맹이 생성)
    def get_moon_svg(day):
        ratio = np.cos((day/28)*2*np.pi)
        is_waxing = day < 14
        color = "#F4D03F" if "밤" in time_of_day or "새벽" in time_of_day or "저녁" in time_of_day else "#FFFFFFCC"
        
        if day == 0: 
            return '<circle cx="50" cy="50" r="45" fill="#2c3e50" />'
        
        flag = '1' if is_waxing else '0'
        rx_val = abs(ratio) * 45
        ell_color = '#2c3e50' if abs(ratio) < 0.1 else color if ratio * (-1 if is_waxing else 1) > 0 else '#2c3e50'
        
        return f"""
        <circle cx="50" cy="50" r="45" fill="#2c3e50" />
        <path d="M 50 5 A 45 45 0 0 {flag} 50 95" fill="{color}" />
        <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ell_color}" />
        """

    # 화성의 위상 모양 (SVG 알맹이 생성)
    def get_mars_svg(pos):
        # 외행성은 항상 보름달에 가깝거나 약간 이지러진 형태만 가짐 (초승달/그믐달 불가)
        color = "#E74C3C" if "밤" in time_of_day or "새벽" in time_of_day or "저녁" in time_of_day else "#E74C3CCC"
        if pos.startswith("충"):
            # 완전히 둥근 보름달 모양의 화성
            return f'<circle cx="50" cy="50" r="45" fill="{color}" />'
        elif pos.startswith("구"):
            # 가장 많이 이지러졌을 때 (약 85% 정도만 차오른 반달 형태)
            return f"""
            <circle cx="50" cy="50" r="45" fill="#2c3e50" />
            <path d="M 50 5 A 45 45 0 0 1 50 95" fill="{color}" />
            <ellipse cx="50" cy="50" rx="30" ry="45" fill="{color}" />
            """
        else:
            # 합 위치일 때는 거의 둥글지만 태양 뒤에 숨어 실제론 안 보임
            return f'<circle cx="50" cy="50" r="45" fill="{color}" opacity="0.3" />'

    # 천체 그래픽 생성 및 HTML 조립
    if target == "달 (The Moon)":
        content_html = f"""
        <svg width="100" height="100" viewBox="0 0 100 100" style="display: block; margin: 0 auto;">
            {get_moon_svg(phase_day)}
        </svg>
        """
    else:
        content_html = f"""
        <svg width="100" height="100" viewBox="0 0 100 100" style="display: block; margin: 0 auto;">
            {get_mars_svg(mars_position)}
        </svg>
        """

    # 안전하게 결합된 마크다운 렌더링 (코드 깨짐 현상 방지 완료)
    st.markdown(f"""
    <div class="sky-container" style="background: {current_sky};">
        <div style="font-size: 1.5rem; color: white; font-weight: bold; margin-bottom: 20px;">
            {direction}쪽 하늘 지평선
        </div>
        <div style="margin: 30px 0;">
            {content_html}
        </div>
        <div style="color: white; opacity: 0.8; font-size: 1.1rem;">
            {target} 관측 중
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. 정보 카드 (우측 컬럼)
with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("📊 관측 데이터")
    st.write(f"**현재 관측 대상:** {target}")
    st.write(f"**바라보는 방향:** {direction}쪽 하늘")
    st.write(f"**선택한 시간:** {time_of_day}")
    if target == "화성 (Mars, 외행성)":
        st.write(f"**화성의 겉보기 크기:** {'가장 크고 밝음(시직경 최대)' if mars_position.startswith('충') else '매우 작고 어두움'}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("💡 과학적 원리 탐구")
    
    if target == "달 (The Moon)":
        st.info(f"음력 {phase_day}일의 달을 관측하고 있습니다. 달의 위상은 태양-지구-달이 이루는 각도에 따라 결정됩니다.")
    else:
        if mars_position.startswith("충"):
            st.success("✨ **'충' 위치의 외행성 특징:**\n지구-화성 거리가 가장 가까워 역대급으로 밝게 보이며, 한밤중(자정 무렵)에 남쪽 하늘에서 가장 높게 뜹니다. 태양의 정반대에 있으므로 보름달처럼 둥글게 보입니다.")
        elif mars_position.startswith("구"):
            st.warning("🌗 **'구' 위치의 외행성 특징:**\n외행성이 태양과 90도 각도를 이룰 때입니다. 이때 외행성은 완벽한 보름달 형태가 되지 못하고, 지구에서 볼 때 가장 많이 이지러진 형태(약간 찌그러진 보름달 모양)로 관측됩니다.")
        else:
            st.error("☀️ **'합' 위치의 외행성 특징:**\n화성이 태양의 바로 뒤편에 위치합니다. 낮 시간대에 태양과 함께 뜨고 지기 때문에 강한 태양빛에 가려져 지구에서는 관측할 수 없습니다.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 하단 학습 탭 가이드
st.markdown("---")
st.markdown("### 🎓 지구과학 핵심 개념 학습")
tabs = st.tabs(["외행성의 겉보기 운동", "외행성의 위상 변화 특징", "내행성과의 결정적 차이"])
with tabs[0]:
    st.write("**순행과 역행:** 외행성은 보통 별자리 사이를 서쪽에서 동쪽으로 이동(순행)하지만, 지구의 공전 속도가 더 빠르기 때문에 화성을 추월하는 **'충' 근처 시점에서는 동쪽에서 서쪽으로 역행**하는 것처럼 보입니다.")
with tabs[1]:
    st.write("**위상 범위 제한:** 내행성(금성)은 초승달, 반달, 보름달 모양이 모두 나타나지만, **외행성은 지구 공전 궤도 바깥에 있으므로 결코 초승달이나 반달 모양으로 보일 수 없으며**, 항상 보름달에 가까운 찬 모양만 보입니다.")
with tabs[2]:
    st.write("**관측 시간대:** 금성은 한밤중(자정)에 절대 볼 수 없지만, 화성 같은 외행성은 '충'의 위치에 있을 때 **한밤중인 자정에 남쪽 하늘에서 가장 잘 보입니다.**")
