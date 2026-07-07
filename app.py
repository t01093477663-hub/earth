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
    st.session_state.current_hour = 18  # 초저녁(18시) 기본값
if "current_phase" not in st.session_state:
    st.session_state.current_phase = 47 # 초기 위치: 동방최대이각(47°)

# 3. 사이드바 제어 패널
st.sidebar.title("🔭 Astro Control")
st.sidebar.markdown("---")

target_mode = st.sidebar.selectbox(
    "1. 관측 핵심 주제 선택", 
    ["내행성의 운동 (금성)", "일식과 월식 (달의 운동)", "외행성의 운동 (화성)"]
)

direction = st.sidebar.radio("2. 바라보는 방위 선택", ["동 (East)", "서 (West)", "남 (South)", "북 (North)"], index=1)

# 4. 정밀 기하 천문 수식 연산 (반시계 공전 구조 반영)
rotation_angle = ((st.session_state.current_hour - 12) / 12) * np.pi 
alpha = (st.session_state.current_phase / 180) * np.pi

sun_x, sun_y = 50, 50      
earth_x, earth_y = 50, 80  

pointer_x = earth_x + 12 * np.sin(rotation_angle)
pointer_y = earth_y - 12 * np.cos(rotation_angle)

if st.session_state.current_hour < 6 or st.session_state.current_hour > 18:
    sky_gradient = "linear-gradient(180deg, #090D16 0%, #0F1420 100%)"
else:
    sky_gradient = "linear-gradient(180deg, #1D4ED8 0%, #3B82F6 100%)"

# 5. 메인 대시보드 렌더링
st.markdown('<p class="main-header">Cosmic Orbital Diagnostics</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">지구과학I 천체 기하학·위상 변화 메커니즘 시뮬레이터 (교과서 기준 교정본)</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# --- [좌측 카드] 지구 관측 시점 위상 그래픽 (Sky View) ---
with col1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:15px;'>👀 지구 관측 시점 (Sky View)</h3>", unsafe_allow_html=True)
    
    pos_status = "정상 위상 관계"
    target_color = "#F59E0B"
    celestial_graphics = ""
    
    if "내행성" in target_mode:
        target_color = "#FB923C"
        phase_angle = st.session_state.current_phase
        
        # 동방구역(0~180)은 상현달(우반달), 서방구역(180~360)은 하현달(좌반달) 위상 매핑
        phase_ratio = (1 + np.cos(np.radians(phase_angle))) / 2
        is_lit_right = (phase_angle < 180) 
        rx_val = abs(45 * (2 * phase_ratio - 1))
        
        celestial_graphics = f"""
        <circle cx="50" cy="50" r="45" fill="#1A1F2C" />
        <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
        <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{"#1A1F2C" if phase_ratio > 0.5 else target_color}" />
        """
        if phase_angle == 0:
            pos_status = "내합 (시직경 최대, 관찰 불가/삭)"
            celestial_graphics = '<circle cx="50" cy="50" r="45" fill="#1A1F2C" stroke="rgba(255,255,255,0.1)"/>'
        elif phase_angle == 180:
            pos_status = "외합 (시직경 최소, 관찰 불가/망)"
            celestial_graphics = f'<circle cx="50" cy="50" r="45" fill="{target_color}"/>'
        elif 40 <= phase_angle <= 50:
            pos_status = "동방최대이각 (초저녁 서쪽하늘 관측, 오른쪽 반달)"
        elif 310 <= phase_angle <= 320:
            pos_status = "서방최대이각 (새벽 동쪽하늘 관측, 왼쪽 반달)"
            
    elif "일식과 월식" in target_mode:
        target_color = "#FBBF24"
        p_ang = st.session_state.current_phase
        p_ratio = (1 - np.cos(np.radians(p_ang))) / 2
        is_lit_right = (p_ang < 180)
        rx_val = abs(45 * (2 * p_ratio - 1))
        
        celestial_graphics = f"""
        <circle cx="50" cy="50" r="45" fill="#1A1F2C" />
        <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
        <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{"#1A1F2C" if p_ratio < 0.5 else target_color}" />
        """
        if p_ang == 0:
            celestial_graphics = '<circle cx="50" cy="50" r="45" fill="none" stroke="#FBBF24" stroke-width="2.5"/><circle cx="50" cy="50" r="44.5" fill="#05070A" />'
            pos_status = "개기일식 (삭)"
        elif p_ang == 180:
            celestial_graphics = '<circle cx="50" cy="50" r="45" fill="#991B1B"/>'
            pos_status = "개기월식 (망)"
        elif p_ang == 90: pos_status = "상현달 (우반달)"
        elif p_ang == 270: pos_status = "하현달 (좌반달)"
    else:
        target_color = "#EF4444"
        celestial_graphics = f'<circle cx="50" cy="50" r="45" fill="{target_color}"/>'
        if st.session_state.current_phase == 0: pos_status = "충 (자정 남중, 시직경 최대, 역행)"
        elif st.session_state.current_phase == 180: pos_status = "합 (관측 불가)"

    sky_html = f"""
    <div style="background:{sky_gradient}; border-radius:12px; padding:35px; text-align:center;">
        <div style="color:#C9D1D9; font-weight:600; margin-bottom:20px; font-size:1rem;">{st.session_state.current_hour:02d}:00 | {direction}쪽 하늘 시야</div>
        <svg width="140" height="140" viewBox="0 0 100 100">{celestial_graphics}</svg>
        <div style="margin-top:20px;"><span class="status-pill">{pos_status}</span></div>
    </div>
    """
    components.html(sky_html, height=310)
    
    st.markdown('<p class="control-label">⏰ 관측 시각 제어 (지구 자전 제어)</p>', unsafe_allow_html=True)
    t_col1, t_col2, t_col3 = st.columns([1, 1, 2])
    with t_col1:
        if st.button("⏰ -1시간", key="time_dec"):
            st.session_state.current_hour = (st.session_state.current_hour - 1) % 24
            st.rerun()
    with t_col2:
        if st.button("⏰ +1시간", key="time_inc"):
            st.session_state.current_hour = (st.session_state.current_hour + 1) % 24
            st.rerun()
    with t_col3:
        st.markdown(f"<div style='padding-top:6px; font-size:0.95rem;'>설정 시각: <b>{st.session_state.current_hour:02d}:00</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- [우측 카드] 우주 공간 위치 관계 (Orbit View) ---
with col2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:15px;'>🌌 우주 공간 위치 관계 (Orbit View)</h3>", unsafe_allow_html=True)
    
    shadow_overlay = ""
    if "내행성" in target_mode:
        orbit_radius = 16
        rad = np.radians(-90 + st.session_state.current_phase)
        obj_x = sun_x + orbit_radius * np.cos(rad)
        obj_y = sun_y + orbit_radius * np.sin(rad)
        obj_color = "#FB923C"
    elif "일식과 월식" in target_mode:
        orbit_radius = 10
        rad = np.radians(-90 + st.session_state.current_phase)
        obj_x = earth_x + orbit_radius * np.cos(rad)
        obj_y = earth_y + orbit_radius * np.sin(rad)
        obj_color = "#FBBF24"
        shadow_overlay = f'<polygon points="{earth_x-3},{earth_y} {earth_x+3},{earth_y} {earth_x+8},100 {earth_x-8},100" fill="rgba(239, 68, 68, 0.05)" />'
    else:
        orbit_radius = 34
        rad = np.radians(-90 + st.session_state.current_phase)
        obj_x = sun_x + orbit_radius * np.cos(rad)
        obj_y = sun_y + orbit_radius * np.sin(rad)
        obj_color = "#EF4444"

    orbit_html = f"""
    <div style="background-color:#090D16; border-radius:12px; padding:20px; text-align:center;">
        <svg width="100%" height="250" viewBox="0 0 100 100" style="max-width:270px; margin:0 auto; display:block;">
            {shadow_overlay}
            <circle cx="{sun_x}" cy="{sun_y}" r="5" fill="#EA580C" />
            <circle cx="{earth_x if "일식" in target_mode else sun_x}" cy="{earth_y if "일식" in target_mode else sun_y}" r="{orbit_radius}" fill="none" stroke="#21262D" stroke-width="0.4" stroke-dasharray="1.5" />
            <circle cx="{earth_x}" cy="{earth_y}" r="4" fill="#2563EB" />
            <path d="M 50 80 A 4 4 0 0 0 54 80 Z" fill="#05070A" />
            <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#10B981" stroke-width="0.8" marker-end="url(#arrow)" />
            <circle cx="{obj_x}" cy="{obj_y}" r="2.5" fill="{obj_color}" />
            <defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#10B981"/></marker></defs>
        </svg>
    </div>
    """
    components.html(orbit_html, height=310)
    
    st.markdown('<p class="control-label">🌌 천체 공전 위치 퀵 매핑 (PPT 완벽 동기화)</p>', unsafe_allow_html=True)
    if "내행성" in target_mode:
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        with p_col1:
            if st.button("💥 내합 (0°)", key="p_naehap"): st.session_state.current_phase = 0; st.rerun()
        with p_col2:
            if st.button("📈 동방최대", key="p_east_max"): st.session_state.current_phase = 47; st.rerun()
        with p_col3:
            if st.button("☀️ 외합 (180°)", key="p_oehap"): st.session_state.current_phase = 180; st.rerun()
        with p_col4:
            if st.button("📉 서방최대", key="p_west_max"): st.session_state.current_phase = 313; st.rerun()
    elif "일식과 월식" in target_mode:
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        with p_col1:
            if st.button("🌑 삭 (일식/0°)", key="p_sax"): st.session_state.current_phase = 0; st.rerun()
        with p_col2:
            if st.button("🌓 상현달 (90°)", key="p_sang"): st.session_state.current_phase = 90; st.rerun()
        with p_col3:
            if st.button("🌕 망 (월식/180°)", key="p_mang"): st.session_state.current_phase = 180; st.rerun()
        with p_col4:
            if st.button("🌗 하현달 (270°)", key="p_ha"): st.session_state.current_phase = 270; st.rerun()
    else:
        p_col1, p_col2, p_col3 = st.columns([1, 1, 2])
        with p_col1:
            if st.button("🔴 충 (0°)", key="p_choong"): st.session_state.current_phase = 0; st.rerun()
        with p_col2:
            if st.button("☀️ 합 (180°)", key="p_hap"): st.session_state.current_phase = 180; st.rerun()
        with p_col3:
            st.markdown(f"<div style='padding-top:6px; font-size:0.95rem; text-align:right;'>공전 연산 각도: <b>{st.session_state.current_phase}°</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 하단 교과 원리 가이드 리포트
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:12px;'>📘 지구과학I 천체 파트 교과 기하 원리 가이드</h3>", unsafe_allow_html=True)

if "내행성" in target_mode:
    st.markdown("""
    * **동방최대이각 (47° 부근):** 북극 상공 시점에서 지구-태양 연결선 기준 **오른쪽**에 위치합니다. 지구가 반시계로 자전하며 저녁이 될 때, 태양이 서쪽으로 지고 난 후 여전히 왼쪽(동쪽 방향) 천구에 남아있어 **초저녁 서쪽 하늘**에서 **오른쪽 반달(상현 모양)**로 관측됩니다.
    * **내합 (0°):** 행성이 지구와 태양 사이에 정렬하는 위치입니다. 시직경은 가장 크지만 햇빛을 받지 못하는 등면을 보게 되므로 **삭(그믐)** 위상이 되어 관측이 불가능합니다.
    * **서방최대이각 (313° 부근):** 북극 상공 시점에서 지구-태양 연결선 기준 **왼쪽**에 위치합니다. 새벽에 태양이 동쪽에서 뜨기 전 오른쪽(서쪽 방향) 천구에 미리 떠올라 있으므로 **새벽 동쪽 하늘**에서 **왼쪽 반달(하현 모양)**로 관측됩니다.
    * **외합 (180°):** 행성이 태양 너머 반대편에 위치하는 시점입니다. 위상은 망(보름)에 가깝고 시직경은 최소가 되며, 태양와 같은 방향에 있어 관측되지 않습니다.
    """)
elif "일식과 월식" in target_mode:
    st.markdown("""
    * **일식(Solar Eclipse):** 달이 태양과 지구 사이인 **삭(0°)** 정렬에 위치할 때 성립하며, 달의 본그림자가 닿는 지구 표면 구역에서 태양이 완전히 가려지는 개기일식이 일어납니다.
    * **월식(Lunar Eclipse):** 달이 지구 반대편의 본그림자 속에 완벽하게 들어가는 **망(180°)** 정렬일 때 성립하며, 굴절된 태양빛의 영향으로 어두운 붉은색의 블러드문이 연출됩니다.
    """)
else:
    st.markdown("""
    * **외행성의 운동:** 화성 등의 외행성이 지구-태양 일직선 바깥쪽인 **충(0°)** 위치에 올 때 지구와 가장 가까워 시직경이 최대가 되며, 자정(24시)에 정남쪽 하늘에 남중하므로 한밤중에 가장 관측하기 이상적인 조건이 됩니다.
    """)
st.markdown('</div>', unsafe_allow_html=True)
