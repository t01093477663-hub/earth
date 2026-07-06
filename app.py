import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="SkyWatcher Pro: 천체 시뮬레이터", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #0E1117;
    }
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #8bc34a 0%, #00a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .info-card {
        background: rgba(255, 255, 255, 0.04);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# 2. 제어 패널 (사이드바)
st.sidebar.title("🔭 천체 관측 제어 패널")
st.sidebar.markdown("---")

target = st.sidebar.selectbox("1. 관측 대상 선택", ["달 (The Moon)", "금성 (Venus, 내행성)", "화성 (Mars, 외행성)"])
selected_hour = st.sidebar.slider("2. 관측 시간 설정 (00시 ~ 24시)", min_value=0, max_value=24, value=22, step=1, format="%d:00")
direction = st.sidebar.radio("3. 바라보는 방위", ["동 (East)", "남 (South)", "서 (West)", "북 (North)"], index=1)

# 3. 천문 기하학 각도 계산 (시간 연동)
# 지구 자전에 의한 시간당 각도 변화량 (라디안)
time_angle = ((selected_hour - 12) / 12) * np.pi 

if target.startswith("달"):
    orbit_angle = np.pi / 2 + (time_angle * 0.1)
    target_name = "달"
elif target.startswith("금성"):
    orbit_angle = np.sin(time_angle) * (np.pi / 4)
    target_name = "금성"
else:
    orbit_angle = time_angle + np.pi
    target_name = "화성"

# 4. 하늘 배경색 및 관측 상태 정의
if 6 <= selected_hour < 11:
    sky_bg = "linear-gradient(180deg, #74ebd5 0%, #ACB6E5 100%)"
    sky_msg = "☀️ 아침 하늘: 태양빛 유입 시작"
    is_dark = False
elif 11 <= selected_hour < 17:
    sky_bg = "linear-gradient(180deg, #4facfe 0%, #00f2fe 100%)"
    sky_msg = "☀️ 낮 하늘: 강한 태양빛으로 관측 차단"
    is_dark = False
elif 17 <= selected_hour < 20:
    sky_bg = "linear-gradient(180deg, #ff9a9e 0%, #feada6 100%)"
    sky_msg = "🌅 저녁 노을: 서쪽 하늘 천체 관측 유리"
    is_dark = True
else:
    sky_bg = "linear-gradient(180deg, #050505 0%, #111122 100%)"
    sky_msg = "🌌 밤하늘: 최적의 관측 환경 제공"
    is_dark = True

# 5. UI 레이아웃 구성
st.markdown('<p class="main-header">SkyWatcher 천체 관측 웹앱</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# [왼쪽 화면] 지구 시점: 사용자가 선택한 방위에서 보이는 실제 천체 위상 그래픽
with col1:
    st.subheader("👀 지구 시점 (Sky View)")
    st.caption("선택한 시간과 방위의 지평선 위 천체 모습")
    
    ratio = np.cos(orbit_angle)
    rx_val = abs(ratio) * 45
    main_color = "#F4D03F" if target_name == "달" else ("#F5B041" if target_name == "금성" else "#E74C3C")
    ell_color = '#2C3E50' if ratio < 0 else main_color
    opacity_val = "0.2" if (not is_dark and target_name == "화성") else "1.0"

    if target_name == "금성" and (21 <= selected_hour or selected_hour <= 3):
        celestial_body_svg = f'<circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.2)" stroke-dasharray="3"/><text x="50" y="55" fill="white" font-size="10" text-anchor="middle">지평선 아래</text>'
    else:
        celestial_body_svg = f"""
        <circle cx="50" cy="50" r="45" fill="#2C3E50" opacity="{opacity_val}"/>
        <path d="M 50 5 A 45 45 0 0 1 50 95" fill="{main_color}" opacity="{opacity_val}"/>
        <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ell_color}" opacity="{opacity_val}"/>
        """

    sky_component_html = f"""
    <div style="background: {sky_bg}; border-radius: 20px; padding: 30px; text-align: center; font-family: 'Pretendard', sans-serif; border: 1px solid rgba(255,255,255,0.1);">
        <div style="font-size: 1.2rem; color: white; font-weight: bold; margin-bottom: 15px;">{selected_hour:02d}:00 | {direction}쪽 지평선 시야</div>
        <svg width="120" height="120" viewBox="0 0 100 100" style="margin: 20px 0;">
            {celestial_body_svg}
        </svg>
        <div style="color: white; font-size: 0.95rem; background: rgba(0,0,0,0.5); display: inline-block; padding: 6px 14px; border-radius: 8px; margin-top: 10px;">{sky_msg}</div>
    </div>
    """
    components.html(sky_component_html, height=350)

# [오른쪽 화면] 우주 시점: 도형과 선으로 실시간 연동되는 공간 기하 관계도 (이모티콘 제거 버전)
with col2:
    st.subheader("🌌 우주 시점 (Orbit Position View)")
    st.caption("시간 설정에 따라 실시간으로 공전 궤도와 자전축 시선이 계산되어 움직이는 기하학적 그래프")

    sun_x, sun_y = 50, 50
    earth_x, earth_y = 50, 78
    
    # 천체별 실시간 공전 궤도상 좌표 매핑
    if target_name == "달":
        obj_x = earth_x + 14 * np.cos(orbit_angle)
        obj_y = earth_y - 14 * np.sin(orbit_angle)
        orbit_radius = 14
        orbit_center_x, orbit_center_y = earth_x, earth_y
        obj_color = "#F4D03F"
        label_text = "MOON"
    elif target_name == "금성":
        obj_x = sun_x + 18 * np.cos(orbit_angle + np.pi/2)
        obj_y = sun_y + 18 * np.sin(orbit_angle + np.pi/2)
        orbit_radius = 18
        orbit_center_x, orbit_center_y = sun_x, sun_y
        obj_color = "#F5B041"
        label_text = "VENUS"
    else:
        obj_x = sun_x + 38 * np.cos(orbit_angle - np.pi/2)
        obj_y = sun_y + 38 * np.sin(orbit_angle - np.pi/2)
        orbit_radius = 38
        orbit_center_x, orbit_center_y = sun_x, sun_y
        obj_color = "#E74C3C"
        label_text = "MARS"

    # 관측자의 시선 화살표 연동 계산
    pointer_x = earth_x + 10 * np.sin(time_angle)
    pointer_y = earth_y - 10 * np.cos(time_angle)

    orbit_component_html = f"""
    <div style="background: #111622; border-radius: 20px; padding: 25px; text-align: center; font-family: 'Pretendard', sans-serif; border: 1px solid rgba(255,255,255,0.1);">
        <svg width="260" height="260" viewBox="0 0 100 100" style="margin: 0 auto; display: block;">
            
            <line x1="0" y1="50" x2="100" y2="50" stroke="rgba(255,255,255,0.03)" stroke-width="100"/>
            
            <circle cx="{sun_x}" cy="{sun_y}" r="6" fill="#FF5722"/>
            <circle cx="{sun_x}" cy="{sun_y}" r="10" fill="#FF9800" opacity="0.2"/>
            <text x="{sun_x}" y="{sun_y-8}" fill="#FF9800" font-size="3.5" font-weight="bold" text-anchor="middle">SUN</text>
            
            <circle cx="{orbit_center_x}" cy="{orbit_center_y}" r="{orbit_radius}" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="0.4" stroke-dasharray="1.5"/>
            
            <circle cx="{earth_x}" cy="{earth_y}" r="5" fill="#2196F3"/>
            <path d="M {earth_x} {earth_y-5} A 5 5 0 0 1 {earth_x} {earth_y+5} Z" fill="#09101E" opacity="0.85"/>
            <text x="{earth_x}" y="{earth_y+9}" fill="#2196F3" font-size="3.5" font-weight="bold" text-anchor="middle">EARTH</text>
            
            <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#8BC34A" stroke-width="0.8" marker-end="url(#arrow)"/>
            <circle cx="{pointer_x}" cy="{pointer_y}" r="0.8" fill="#8BC34A"/>
            
            <circle cx="{obj_x}" cy="{obj_y}" r="3.5" fill="{obj_color}"/>
            <path d="M {obj_x} {obj_y-3.5} A 3.5 3.5 0 0 1 {obj_x} {obj_y+3.5} Z" fill="#1C2833" opacity="0.75"/>
            <text x="{obj_x}" y="{obj_y-5}" fill="{obj_color}" font-size="3" font-weight="bold" text-anchor="middle">{label_text}</text>
            
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#8BC34A"/>
                </marker>
            </defs>
        </svg>
        <div style="color: #8BC34A; font-size: 0.85rem; font-weight: 600; margin-top: 12px;">초록색 화살표(▲) = 관측 시간대에 따른 지구 자전 시선 방향</div>
    </div>
    """
    components.html(orbit_component_html, height=350)

# 6. 하단 지구과학 핵심 교과 가이드 리포트
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.subheader("💡 천체 기하학 관측 핵심 원리 해설")

if target_name == "달":
    st.info(f"**🌖 달의 위치 관계:** 우주 시점의 궤도 원형 다이어그램을 보면 태양-지구-달의 사잇각이 실시간으로 표현됩니다. 상현달 시기에는 두 천체가 직각(90도)을 이루며, 지구 자전축 화살표가 남쪽(18:00 무렵 정면)을 가리킬 때 달과 일직선상에 놓이게 됨을 기하학적으로 확인할 수 있습니다.")
elif target_name == "금성":
    st.success(f"**✨ 내행성의 이각과 관측 한계:** 금성 궤도를 선택하고 시간 슬라이더를 한밤중(22시~02시)으로 움직이면, 지구의 밤 지역을 나타내는 초록색 화살표 시선 방향이 금성 공전 궤도를 완전히 비껴가게 됩니다. 이를 통해 내행성이 한밤중에 관측될 수 없는 이유가 명확히 증명됩니다.")
else:
    st.warning(f"**🔴 외행성의 충 위치와 남중:** 화성이 지구와 태양 일직선상에 정렬되는 '충' 조건의 공전 궤도 기하학입니다. 태양이 안 보이는 자정(24:00) 시간대에 관측자의 초록색 시선 바늘이 외행성(화성)의 중심점 좌표를 정면으로 관측하게 됩니다.")
st.markdown('</div>', unsafe_allow_html=True)
