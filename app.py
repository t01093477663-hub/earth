import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# 1. 최고급 천문 대시보드 UI 스타일 (Premium Cyber Space CSS)
st.set_page_config(page_title="지구과학I 천체 운동 시뮬레이터", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Pretendard:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #080A0F;
        color: #F1F5F9;
    }
    
    /* 네온 테두리와 부드러운 그라데이션이 적용된 프리미엄 카드 */
    .dashboard-card {
        background: rgba(15, 22, 36, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 28px;
        backdrop-filter: blur(12px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        margin-bottom: 24px;
    }
    
    .main-header {
        font-family: 'Space Grotesk', 'Pretendard', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818CF8 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    
    .sub-header {
        color: #475569;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    
    .status-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 제어 패널 (세련된 다크 테마 트랙 요소 배치)
st.sidebar.title("🔭 Astro Control Center")
st.sidebar.markdown("---")

target_mode = st.sidebar.selectbox(
    "1. 관측 핵심 주제 선택", 
    ["일식과 월식 (달의 운동)", "내행성의 운동 (금성)", "외행성의 운동 (화성)"]
)

st.sidebar.markdown("### 2. 관측 시각 제어 (지구 자전)")
if "current_hour" not in st.session_state:
    st.session_state.current_hour = 22

t_col1, t_col2 = st.sidebar.columns(2)
with t_col1:
    if st.button("⏰ -1시간"):
        st.session_state.current_hour = (st.session_state.current_hour - 1) % 24
with t_col2:
    if st.button("⏰ +1시간"):
        st.session_state.current_hour = (st.session_state.current_hour + 1) % 24

st.sidebar.markdown(f"**현재 설정 시각:** `{st.session_state.current_hour:02d}:00`")

st.sidebar.markdown("### 3. 천문 기하 퀵 포지셔닝")
if "current_phase" not in st.session_state:
    st.session_state.current_phase = 180

if "일식과 월식" in target_mode:
    p_col1, p_col2 = st.sidebar.columns(2)
    with p_col1:
        if st.button("🌑 삭 (일식 위치)"): st.session_state.current_phase = 180
    with p_col2:
        if st.button("🌕 망 (월식 위치)"): st.session_state.current_phase = 0
    p_col3, p_col4 = st.sidebar.columns(2)
    with p_col3:
        if st.button("🌓 상현달 위치"): st.session_state.current_phase = 90
    with p_col4:
        if st.button("🌗 하현달 위치"): st.session_state.current_phase = 270
elif "내행성" in target_mode:
    p_col1, p_col2 = st.sidebar.columns(2)
    with p_col1:
        if st.button("💥 내합 위치"): st.session_state.current_phase = 180
    with p_col2:
        if st.button("☀️ 외합 위치"): st.session_state.current_phase = 0
    p_col3, p_col4 = st.sidebar.columns(2)
    with p_col3:
        if st.button("📈 동방최대이각"): st.session_state.current_phase = 115
    with p_col4:
        if st.button("📉 서방최대이각"): st.session_state.current_phase = 245
else:
    p_col1, p_col2 = st.sidebar.columns(2)
    with p_col1:
        if st.button("🔴 충 (최적 관측)"): st.session_state.current_phase = 0
    with p_col2:
        if st.button("☀️ 합 (관측 불가)"): st.session_state.current_phase = 180

st.sidebar.markdown(f"**현재 공전 각도:** `{st.session_state.current_phase}°`")

direction = st.sidebar.radio("4. 관측 시선 방위", ["동 (East)", "남 (South)", "서 (West)"], index=1)

# 4. 정밀 기하 천문 수식 연산
rotation_angle = ((st.session_state.current_hour - 12) / 12) * np.pi 
alpha = (st.session_state.current_phase / 180) * np.pi

sun_x, sun_y = 50, 50      
earth_x, earth_y = 50, 75  
pointer_x = earth_x + 13 * np.sin(rotation_angle)
pointer_y = earth_y - 13 * np.cos(rotation_angle)

# 다이나믹 스카이 컬러 필터링
if st.session_state.current_hour < 6 or st.session_state.current_hour > 19:
    sky_gradient = "linear-gradient(180deg, #0A0D14 0%, #111827 100%)"
    sky_msg = "🌌 밤하늘 환경 (Night-sky Vision)"
else:
    sky_gradient = "linear-gradient(180deg, #1E40AF 0%, #3B82F6 100%)"
    sky_msg = "☀️ 낮하늘 환경 (Daylight Bleed)"

# 5. 메인 대시보드 구조화
st.markdown('<p class="main-header">Cosmic Orbital Diagnostics</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">지구과학I 천체 기하학·위상 변화 메커니즘 대시보드</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# --- [좌측 카드] 지구 관측 시점 위상 그래픽 ---
with col1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.2rem; font-weight:600; color:#94A3B8; margin-bottom:15px;'>👀 지구 관측 시점 (Sky View)</h3>", unsafe_allow_html=True)
    
    phase_ratio = (1 + np.cos(alpha)) / 2
    is_lit_right = (np.sin(alpha) >= 0)
    rx_val = abs(45 * (2 * phase_ratio - 1))
    
    target_color = "#F59E0B" if "일식" in target_mode else ("#FB923C" if "내행성" in target_mode else "#EF4444")
    # 행성의 보이지 않는 면을 배경색과 확실히 분리하기 위한 미디엄 셰도우 그레이 처리
    shadow_fill = "#242E42" 
    base_fill = target_color if phase_ratio > 0.5 else shadow_fill
    current_shadow = shadow_fill if phase_ratio > 0.5 else target_color

    celestial_graphics = f"""
    <circle cx="50" cy="50" r="45" fill="{shadow_fill}" stroke="rgba(255,255,255,0.05)" />
    <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
    <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{current_shadow}" />
    """
    
    pos_status = "정상 위상 전이 상태"
    if "일식과 월식" in target_mode:
        if 176 <= st.session_state.current_phase <= 184:
            # 완벽한 광학 코로나 골드 링 연출 (텍스트 박기 제거)
            celestial_graphics = """
            <circle cx="50" cy="50" r="45" fill="none" stroke="#FBBF24" stroke-width="2.5" style="filter: drop-shadow(0px 0px 8px #F59E0B);"/>
            <circle cx="50" cy="50" r="44.5" fill="#090D16" />
            """
            pos_status = "개기일식 (Corona Ring)"
        elif 155 <= st.session_state.current_phase <= 205:
            pos_status = "부분일식 (Partial Eclipse)"
        elif st.session_state.current_phase <= 4 or st.session_state.current_phase >= 356:
            # 붉은 대기광 산란에 의한 개기월식 블러드문 그래픽 구현
            celestial_graphics = '<circle cx="50" cy="50" r="45" fill="#991B1B" style="filter: drop-shadow(0px 0px 6px #7F1D1D);" stroke="rgba(255,255,255,0.1)"/>'
            pos_status = "개기월식 (Blood Moon)"
    elif "내행성" in target_mode:
        if 175 <= st.session_state.current_phase <= 185: pos_status = "내합 (최대 크기 그믐달/역행)"
        elif st.session_state.current_phase <= 5 or st.session_state.current_phase >= 355: pos_status = "외합 (최소 크기 보름달)"
    else:
        if st.session_state.current_phase <= 5 or st.session_state.current_phase >= 355: pos_status = "충 (자정 남중, 최적 관측, 역행)"

    sky_html = f"""
    <div style="background:{sky_gradient}; border-radius:18px; padding:35px; text-align:center; box-shadow: inset 0 0 20px rgba(0,0,0,0.6);">
        <div style="color:#E2E8F0; font-weight:600; margin-bottom:20px; font-size:1.05rem; letter-spacing:0.5px;">{st.session_state.current_hour:02d}:00 | {direction}쪽 지평선 시야</div>
        <svg width="150" height="150" viewBox="0 0 100 100">
            {celestial_graphics}
        </svg>
        <div style="margin-top:22px;"><span class="status-pill">{pos_status}</span></div>
    </div>
    """
    components.html(sky_html, height=320)
    st.markdown('</div>', unsafe_allow_html=True)

# --- [우측 카드] 우주 시점 기하 관계도 (동서남북 방위 배치 및 행성 음영 선명화) ---
with col2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.2rem; font-weight:600; color:#94A3B8; margin-bottom:15px;'>🌌 우주 공간 위치 관계 (Orbit View)</h3>", unsafe_allow_html=True)
    
    if "일식과 월식" in target_mode:
        orbit_radius = 12
        obj_x = earth_x + orbit_radius * np.sin(alpha)
        obj_y = earth_y - orbit_radius * np.cos(alpha)
        obj_color = "#F59E0B"
        shadow_overlay = f'<polygon points="{earth_x-4},{earth_y} {earth_x+4},{earth_y} {earth_x+10},0 {earth_x-10},0" fill="rgba(239, 68, 68, 0.05)" />'
    elif "내행성" in target_mode:
        orbit_radius = 18
        obj_x = sun_x + orbit_radius * np.sin(alpha)
        obj_y = sun_y + orbit_radius * np.cos(alpha)
        obj_color = "#FB923C"
        shadow_overlay = ""
    else:
        orbit_radius = 38
        obj_x = sun_x + orbit_radius * np.sin(alpha)
        obj_y = sun_y + orbit_radius * np.cos(alpha)
        obj_color = "#EF4444"
        shadow_overlay = ""

    orbit_html = f"""
    <div style="background-color:#0B0E14; border-radius:18px; padding:20px; border:1px solid rgba(255,255,255,0.04); position:relative;">
        <svg width="100%" height="260" viewBox="0 0 100 100" style="max-width:290px; margin:0 auto; display:block;">
            {shadow_overlay}

            <text x="50" y="6" fill="#475569" font-size="3.5" font-weight="700" text-anchor="middle">N (북)</text>
            <text x="50" y="98" fill="#475569" font-size="3.5" font-weight="700" text-anchor="middle">S (남)</text>
            <text x="2" y="51.5" fill="#475569" font-size="3.5" font-weight="700" text-anchor="left">W (서)</text>
            <text x="98" y="51.5" fill="#475569" font-size="3.5" font-weight="700" text-anchor="end">E (동)</text>
            
            <line x1="50" y1="10" x2="50" y2="90" stroke="rgba(255,255,255,0.03)" stroke-width="0.2" stroke-dasharray="1"/>
            <line x1="10" y1="50" x2="90" y2="50" stroke="rgba(255,255,255,0.03)" stroke-width="0.2" stroke-dasharray="1"/>

            <circle cx="{sun_x}" cy="{sun_y}" r="5" fill="#EA580C" />
            <circle cx="{sun_x}" cy="{sun_y}" r="7" fill="#F59E0B" opacity="0.15" />

            <circle cx="{earth_x if "일식" in target_mode else sun_x}" cy="{earth_y if "일식" in target_mode else sun_y}" r="{orbit_radius}" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.3" stroke-dasharray="1" />

            <circle cx="{earth_x}" cy="{earth_y}" r="4" fill="#2563EB" />
            <path d="M {earth_x-4} {earth_y} A 4 4 0 0 0 {earth_x+4} {earth_y} Z" fill="#070A0F" />
            <circle cx="{earth_x}" cy="{earth_y}" r="4" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="0.3"/>

            <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#10B981" stroke-width="0.8" marker-end="url(#premium-arrow)" />

            <circle cx="{obj_x}" cy="{obj_y}" r="2.5" fill="#334155" />
            <path d="M {obj_x-2.5} {obj_y} A 2.5 2.5 0 0 1 {obj_x+2.5} {obj_y} Z" fill="{obj_color}" transform="rotate(180 {obj_x} {obj_y})" />
            <circle cx="{obj_x}" cy="{obj_y}" r="2.5" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="0.2"/>

            <defs>
                <marker id="premium-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#10B981"/></marker>
            </defs>
        </svg>
    </div>
    """
    components.html(orbit_html, height=320)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 하단 교과 원리 매핑 분석 리포트
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.markdown("<h3 style='font-size:1.2rem; font-weight:600; color:#94A3B8; margin-bottom:12px;'>📘 지구과학I 천체 파트 교과 핵심 분석</h3>", unsafe_allow_html=True)

if "일식과 월식" in target_mode:
    st.markdown("""
    * **일식 원리:** 달이 태양과 지구 사이에 정렬되는 **삭(각도 180°)** 구간에서 달의 본그림자가 지구를 가릴 때 개기일식이 성립합니다. 위 그래픽과 같이 태양이 완전히 가려지면 주위에 개기일식의 상징인 **황금빛 코로나(Corona)**가 관측됩니다.
    * **월식 원리:** 달이 지구 반대편인 **망(각도 0°)** 부근에서 지구의 본그림자 영역 속에 완벽하게 정렬되면 개기월식이 일어나 어둡고 붉은 **블러드문(Blood Moon)**이 관측됩니다.
    """)
elif "내행성" in target_mode:
    st.markdown("""
    * **내행성(금성)의 운동 특징:** 금성은 지구 안쪽 궤도에서 공전하므로 태양과 일정한 사잇각인 **최대이각** 범위 내에서 왕복 운동을 반복하는 겉보기 운동을 보입니다. 내합 부근 퀵 버튼을 누르면 지구와 가까워져 가장 큰 시직경의 그믐달/초승달 위상을 확인할 수 있습니다.
    """)
else:
    st.markdown("""
    * **외행성(화성)의 운동 특징:** 화성이 지구와 태양 일직선 바깥쪽 방향인 **충(각도 0°)** 위치에 올 때 시직경이 가장 크게 관측되며, 관측자의 녹색 시선 바늘이 밤 24시 정면을 향하므로 한밤중에 정남쪽 하늘에서 가장 오랫동안 밝게 관측할 수 있습니다.
    """)
st.markdown('</div>', unsafe_allow_html=True)
