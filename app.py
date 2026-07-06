import streamlit as st
import numpy as np

# 1. 페이지 기본 설정 및 디자인 (Custom CSS)
st.set_page_config(page_title="SkyWatcher: 천체 관측 시뮬레이터", layout="wide")

st.markdown("""
<style>
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
        border: 1px solid rgba(255, 255, 255, 0.1);
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

# 내행성과 외행성을 모두 포함한 관측 대상 선택
target = st.sidebar.selectbox("관측 대상 선택", ["달 (The Moon)", "금성 (Venus, 내행성)", "화성 (Mars, 외행성)"])
direction = st.sidebar.radio("바라보는 방위", ["동 (East)", "남 (South)", "서 (West)", "북 (North)"], index=1)
time_of_day = st.sidebar.select_slider(
    "시간대 선택",
    options=["새벽 (03:00)", "아침 (08:00)", "낮 (12:00)", "저녁 (18:00)", "밤 (22:00)"],
    value="밤 (22:00)"
)

# 천체 종류별 세부 위치 및 위상 설정
if target == "달 (The Moon)":
    phase_day = st.sidebar.slider("달의 음력 날짜 (위상 조절)", 0, 28, 7)
elif target == "금성 (Venus, 내행성)":
    venus_position = st.sidebar.select_slider(
        "금성의 위치 상태 변경",
        options=["내합 (Inferior Conjunction)", "최대이각 (Greatest Elongation)", "외합 (Superior Conjunction)"],
        value="최대이각 (Greatest Elongation)"
    )
else:
    mars_position = st.sidebar.select_slider(
        "화성의 위치 상태 변경",
        options=["충 (Opposition)", "구 (Quadrature)", "합 (Conjunction)"],
        value="충 (Opposition)"
    )

# 3. 메인 레이아웃 타이틀
st.markdown('<p class="main-header">SkyWatcher Simulator</p>', unsafe_allow_html=True)

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

# 낮/아침일 때는 천체 색상을 흐리게, 밤/새벽/저녁일 때는 밝게 설정
is_dark = "밤" in time_of_day or "새벽" in time_of_day or "저녁" in time_of_day
main_color = "#F4D03F" if is_dark else "#FFFFFFCC"
mars_color = "#E74C3C" if is_dark else "#E74C3CCC"

# 4. 시각화 로직 (지평선 및 천체 위치)
with col1:
    
    # [1] 달의 위상 SVG 생성 함수
    def get_moon_svg(day):
        ratio = np.cos((day/28)*2*np.pi)
        is_waxing = day < 14
        if day == 0: 
            return '<circle cx="50" cy="50" r="45" fill="#2c3e50" />'
        flag = '1' if is_waxing else '0'
        rx_val = abs(ratio) * 45
        ell_color = '#2c3e50' if abs(ratio) < 0.1 else main_color if ratio * (-1 if is_waxing else 1) > 0 else '#2c3e50'
        return f'<circle cx="50" cy="50" r="45" fill="#2c3e50" /><path d="M 50 5 A 45 45 0 0 {flag} 50 95" fill="{main_color}" /><ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ell_color}" />'

    # [2] 금성(내행성)의 위상 SVG 생성 함수
    def get_venus_svg(pos):
        if "내합" in pos:
            # 지구와 가장 가까우나 삭(망치) 형태라 안 보임 (가장 큰 크기의 어두운 원)
            return '<circle cx="50" cy="50" r="45" fill="#2c3e50" />'
        elif "최대이각" in pos:
            # 딱 절반만 빛나는 반달 모양 (내행성이므로 크기가 중간 정도)
            return f'<circle cx="50" cy="50" r="35" fill="#2c3e50" /><path d="M 50 15 A 35 35 0 0 1 50 85" fill="{main_color}" />'
        else:
            # 외합: 지구와 가장 멀지만 태양빛을 다 받아 보름달 모양 (크기가 매우 작은 원)
            return f'<circle cx="50" cy="50" r="15" fill="{main_color}" />'

    # [3] 화성(외행성)의 위상 SVG 생성 함수
    def get_mars_svg(pos):
        if "충" in pos:
            return f'<circle cx="50" cy="50" r="45" fill="{mars_color}" />'
        elif "구" in pos:
            return f'<circle cx="50" cy="50" r="45" fill="#2c3e50" /><path d="M 50 5 A 45 45 0 0 1 50 95" fill="{mars_color}" /><ellipse cx="50" cy="50" rx="25" ry="45" fill="{mars_color}" />'
        else:
            return f'<circle cx="50" cy="50" r="45" fill="{mars_color}" opacity="0.3" />'

    # 각 조건에 맞춰 알맹이 태그들만 선택
    if target.startswith("달"):
        svg_core = get_moon_svg(phase_day)
    elif target.startswith("금성"):
        svg_core = get_venus_svg(venus_position)
    else:
        svg_core = get_mars_svg(mars_position)

    # 🚨 오류 완벽 차단 구조: 문자열 포맷팅을 쪼개지 않고, 완벽하게 닫힌 하나의 HTML block으로 렌더링합니다.
    sky_html = f"""
    <div class="sky-container" style="background: {current_sky};">
        <div style="font-size: 1.5rem; color: white; font-weight: bold; margin-bottom: 25px;">
            {direction}쪽 하늘 지평선
        </div>
        <div style="margin: 30px auto; width: 100px; height: 100px;">
            <svg width="100" height="100" viewBox="0 0 100 100">
                {svg_core}
            </svg>
        </div>
        <div style="color: white; opacity: 0.9; font-size: 1.2rem; font-weight: bold; margin-top: 20px;">
            {target} 관측 시뮬레이션 중
        </div>
    </div>
    """
    st.markdown(sky_html, unsafe_allow_html=True)

# 5. 정보 카드 (우측 컬럼)
with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("📊 관측 데이터 정보")
    st.write(f"**대상 천체:** {target}")
    st.write(f"**바라보는 방향:** {direction}쪽 하늘")
    st.write(f"**선택된 시간 대:** {time_of_day}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("💡 지구과학 핵심 원리")
    
    if target.startswith("달"):
        st.info(f"**음력 {phase_day}일의 달:**\n달의 공전 위치에 따라 지구-태양과의 사이 각도가 달라져 눈에 보이는 위상이 지속적으로 변합니다.")
    elif target.startswith("금성"):
        if "내합" in venus_position:
            st.error("⚠️ **내합 특징:** 금성이 태양과 지구 사이에 일직선으로 놓입니다. 거리는 가장 가깝지만 어두운 면만 향하므로 보이지 않으며, 낮에 태양과 함께 뜨고 집니다.")
        elif "최대이각" in venus_position:
            st.success("✨ **최대이각 특징:** 태양과 가장 멀리 떨어져 보이는 시기여서 관측 시간이 가장 길고, 망원경으로 보면 반달 모양으로 보입니다.")
        else:
            st.warning("🔍 **외합 특징:** 금성이 태양 반대편 쪽에 위치합니다. 형태는 보름달처럼 둥글지만 거리가 가장 멀어 크기가 작고 태양빛에 가려져 관측하기 어렵습니다.")
    else:
        if "충" in mars_position:
            st.success("✨ **충 위치 특징:** 외행성이 지구와 가장 가까워지는 타이밍입니다. 크고 밝게 빛나며 한밤중(자정)에 남쪽 하늘에서 아주 뚜렷하게 관측됩니다.")
        elif "구" in mars_position:
            st.warning("🌗 **구 위치 특징:** 태양-지구-화성이 90도를 이룹니다. 이때 화성은 완전히 둥글지 못하고 지구에서 보기에 가장 많이 이지러진 형태(약간 찌그러진 보름달)가 됩니다.")
        else:
            st.error("☀️ **합 위치 특징:** 화성이 태양 뒤로 숨어버리는 시기입니다. 태양빛이 너무 강해 지구에서는 관측이 불가능합니다.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 하단 교과 학습 가이드
st.markdown("---")
st.markdown("### 🎓 내행성과 외행성의 결정적 차이 요약")
tabs = st.tabs(["내행성 (금성)", "외행성 (화성)", "천체의 겉보기 운동"])
with tabs[0]:
    st.write("- **위상 변화 범위:** 초승달, 반달, 보름달 모양을 모두 가질 수 있습니다.\n- **관측 시간:** 지구 안쪽 궤도에 묶여 있으므로 한밤중(자정)에는 절대 볼 수 없고, 오직 새벽(동쪽 하늘)이나 초저녁(서쪽 하늘)에만 잠깐 보입니다.")
with tabs[1]:
    st.write("- **위상 변화 범위:** 지구 바깥을 돌기 때문에 결코 초승달이나 그믐달 모양이 될 수 없으며, 항상 반달 이상으로 가득 찬 보름달 형태 근처만 유지합니다.\n- **관측 시간:** '충' 위치에 올 때 한밤중(자정) 남쪽 하늘에서 가장 높고 밝게 빛납니다.")
with tabs[2]:
    st.write("- **일주 운동:** 모든 천체는 지구의 자전(서->동) 때문에 하루에 한 번 동쪽에서 떠서 서쪽으로 지는 겉보기 운동을 합니다.\n- **행성의 공전(순행/역행):** 배경 별자리 사이를 이동할 때 외행성은 지구에게 추월당하는 '충' 근처에서 서쪽으로 역행하는 흐름을 보여줍니다.")
