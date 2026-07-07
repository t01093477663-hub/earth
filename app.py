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
        font-size: 2.2rem; font-weight: 700;
        background: linear-gradient(135deg, #6366F1 0%, #38BDF8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header { color: #8B949E; font-size: 0.95rem; margin-bottom: 1.8rem; }
    .status-pill {
        display: inline-block; padding: 6px 14px; border-radius: 30px;
        font-size: 0.85rem; font-weight: 600;
        background: rgba(56, 189, 248, 0.1); color: #58A6FF; border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .control-label { font-size: 0.9rem; color: #8B949E; font-weight: 600; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# 2. 세션 상태 데이터 초기화
if "current_hour" not in st.session_state:
    st.session_state.current_hour = 18  # 초저녁(18시) 기본값
if "current_phase" not in st.session_state:
    st.session_state.current_phase = 47 # 초기 위치 기본값 (동방최대이각)

# [버그 킬러] 슬라이더 조작 즉시 세션 상태를 안전하게 동기화하는 콜백 함수
def update_phase_from_slider():
    st.session_state.current_phase = st.session_state.slider_val

# 3. 사이드바 제어 패널
st.sidebar.title("🔭 Astro Control")
st.sidebar.markdown("---")

target_mode = st.sidebar.selectbox(
    "1. 관측 핵심 주제 선택", 
    ["내행성의 운동 (금성)", "일식 (달의 운동)", "월식 (달의 운동)", "외행성의 운동 (화성)"]
)

direction = st.sidebar.radio("2. 바라보는 방위 선택", ["동 (East)", "서 (West)", "남 (South)", "북 (North)"], index=1)

# 4. 정밀 기하 천문 수식 연산 (북극 상공 시점: 지구 6시 방향, 반시계 구조)
rotation_angle = ((st.session_state.current_hour - 12) / 12) * np.pi 

sun_x, sun_y = 50, 50      
earth_x, earth_y = 50, 80  

# 자전축 시선 바늘 끝점 계산
pointer_x = earth_x + 12 * np.sin(rotation_angle)
pointer_y = earth_y - 12 * np.cos(rotation_angle)

# 낮과 밤에 따른 하늘 배경색 결정
if 6 <= st.session_state.current_hour <= 18:
    sky_gradient = "linear-gradient(180deg, #1D4ED8 0%, #3B82F6 100%)"
else:
    sky_gradient = "linear-gradient(180deg, #090D16 0%, #0F1420 100%)"

# 5. 메인 대시보드 렌더링
st.markdown('<p class="main-header">Cosmic Orbital Diagnostics</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">지구과학I 천체 기하학·위상 변화 메커니즘 시뮬레이터 (교과 원리 완전 교정본)</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# --- [좌측 카드] 지구 관측 시점 위상 그래픽 (Sky View) ---
with col1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:15px;'>👀 지구 관측 시점 (Sky View)</h3>", unsafe_allow_html=True)
    
    pos_status = "정상 위상 관계"
    celestial_graphics = ""
    
    dark_side_color = "#2A3142"  
    dark_side_stroke = "rgba(255,255,255,0.2)" 
    
    phase_angle = st.session_state.current_phase % 360
    
    if "내행성" in target_mode:
        target_color = "#FB923C"
        # [방위 교정] 우측(0~180도)이 동방구역(오른쪽이 밝음), 좌측(180~360도)이 서방구역(왼쪽이 밝음)
        phase_ratio = (1 + np.cos(np.radians(phase_angle))) / 2
        is_lit_right = (phase_angle < 180) 
        rx_val = abs(45 * (2 * phase_ratio - 1))
        ellipse_fill = dark_side_color if phase_ratio > 0.5 else target_color
        
        celestial_graphics = f"""
        <circle cx="50" cy="50" r="45" fill="{dark_side_color}" stroke="{dark_side_stroke}" stroke-width="1" />
        <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
        <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ellipse_fill}" />
        """
        if phase_angle == 0:
            pos_status = "내합 (시직경 최대, 관찰 불가/삭)"
        elif phase_angle == 180:
            pos_status = "외합 (시직경 최소, 관찰 불가/망)"
        elif 40 <= phase_angle <= 55:
            pos_status = "동방최대이각 (초저녁 서쪽하늘, 오른쪽 반달)"
        elif 305 <= phase_angle <= 320:
            pos_status = "서방최대이각 (새벽 동쪽하늘, 왼쪽 반달)"
            
    elif "일식" in target_mode:
        target_color = "#FBBF24"
        phase_ratio = (1 - np.cos(np.radians(phase_angle))) / 2
        is_lit_right = (phase_angle < 180)
        rx_val = abs(45 * (2 * phase_ratio - 1))
        ellipse_fill = dark_side_color if phase_ratio < 0.5 else target_color
        
        if phase_angle == 0:
            celestial_graphics = '<circle cx="50" cy="50" r="45" fill="none" stroke="#FBBF24" stroke-width="3"/><circle cx="50" cy="50" r="44.5" fill="#05070A" />'
            pos_status = "개기일식 현상 발생 (달이 태양을 완전히 가림)"
        else:
            celestial_graphics = f"""
            <circle cx="50" cy="50" r="45" fill="{dark_side_color}" stroke="{dark_side_stroke}" stroke-width="1" />
            <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
            <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ellipse_fill}" />
            """
            pos_status = "일식 범위 외 (달의 일반 위상 상태)"

    elif "월식" in target_mode:
        target_color = "#FBBF24"
        if phase_angle == 180:
            celestial_graphics = '<circle cx="50" cy="50" r="45" fill="#991B1B" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>'
            pos_status = "개기월식 현상 발생 (지구 본그림자 진입 / 블러드문)"
        else:
            phase_ratio = (1 - np.cos(np.radians(phase_angle))) / 2
            is_lit_right = (phase_angle < 180)
            rx_val = abs(45 * (2 * phase_ratio - 1))
            ellipse_fill = dark_side_color if phase_ratio < 0.5 else target_color
            celestial_graphics = f"""
            <circle cx="50" cy="50" r="45" fill="{dark_side_color}" stroke="{dark_side_stroke}" stroke-width="1" />
            <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
            <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ellipse_fill}" />
            """
            pos_status = "월식 범위 외 (달의 일반 위상 상태)"
            
    else: # 외행성 모드
        target_color = "#EF4444"
        
        # 지구(50,80), 태양(50,50), 외행성(반지름 42) 사이의 거리 연산에 따른 동적 크기 매핑
        rad_calc = np.radians(90 - phase_angle)
        ex = 50 + 42 * np.cos(rad_calc)
        ey = 50 + 42 * np.sin(rad_calc)
        dist_to_earth = np.sqrt((ex - 50)**2 + (ey - 80)**2)
        
        # 충(지구와 최소거리 12) -> 크기 최대(45) / 합(지구와 최대거리 72) -> 크기 최소(18)
        dynamic_r = 18 + (45 - 18) * (1.0 - (dist_to_earth - 12) / 60)
        
        # 외행성의 미세한 차구 위상 변화율 연산 (동구/서구 영역에서 미세하게 위상이 깎임)
        ell_ratio = 0.88 + 0.12 * abs(np.cos(np.radians(phase_angle)))
        is_lit_right = (phase_angle < 180)
        rx_val = abs(dynamic_r * (2 * ell_ratio - 1))
        ellipse_fill = dark_side_color if ell_ratio > 0.5 else target_color
        
        celestial_graphics = f"""
        <circle cx="50" cy="50" r="{dynamic_r}" fill="{dark_side_color}" stroke="{dark_side_stroke}" stroke-width="1" />
        <path d="M 50 {50-dynamic_r} A {dynamic_r} {dynamic_r} 0 0 {1 if is_lit_right else 0} 50 {50+dynamic_r} Z" fill="{target_color}" />
        <ellipse cx="50" cy="50" rx="{rx_val}" ry="{dynamic_r}" fill="{ellipse_fill}" />
        """
        if phase_angle == 0: pos_status = "충 (자정 남중, 시직경 최대 보름달 모양)"
        elif phase_angle == 90: pos_status = "동구 (초저녁 남중, 좌측이 미세하게 깎임)"
        elif phase_angle == 180: pos_status = "합 (관측 불가, 시직경 최소 보름달 모양)"
        elif phase_angle == 270: pos_status = "서구 (새벽 남중, 우측이 미세하게 깎임)"

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
        st.markdown(f"<div style='padding-top:6px; font-size:0.95rem;'>지구 기준 시각: <b>{st.session_state.current_hour:02d}:00</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- [우측 카드] 우주 공간 위치 관계 (Orbit View) ---
with col2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:15px;'>🌌 우주 공간 위치 관계 (Orbit View)</h3>", unsafe_allow_html=True)
    
    shadow_overlay = ""
    if "내행성" in target_mode:
        orbit_radius = 16
        rad = np.radians(90 - st.session_state.current_phase)
        obj_x = sun_x + orbit_radius * np.cos(rad)
        obj_y = sun_y + orbit_radius * np.sin(rad)
        obj_color = "#FB923C"
    elif "일식" in target_mode:
        orbit_radius = 10
        rad = np.radians(90 - st.session_state.current_phase)
        obj_x = earth_x + orbit_radius * np.cos(rad)
        obj_y = earth_y + orbit_radius * np.sin(rad)
        obj_color = "#FBBF24"
    elif "월식" in target_mode:
        orbit_radius = 10
        rad = np.radians(90 - st.session_state.current_phase)
        obj_x = earth_x + orbit_radius * np.cos(rad)
        obj_y = earth_y + orbit_radius * np.sin(rad)
        obj_color = "#FBBF24"
        shadow_overlay = f'<polygon points="{earth_x-3.5},{earth_y} {earth_x+3.5},{earth_y} {earth_x+7},100 {earth_x-7},100" fill="rgba(239, 68, 68, 0.15)" stroke="rgba(239,68,68,0.3)" stroke-width="0.3" stroke-dasharray="1" />'
    else: 
        orbit_radius = 42 
        rad = np.radians(90 - st.session_state.current_phase)
        obj_x = sun_x + orbit_radius * np.cos(rad)
        obj_y = sun_y + orbit_radius * np.sin(rad)
        obj_color = "#EF4444"

    orbit_html = f"""
    <div style="background-color:#090D16; border-radius:12px; padding:20px; text-align:center;">
        <svg width="100%" height="250" viewBox="0 0 100 100" style="max-width:270px; margin:0 auto; display:block;">
            {shadow_overlay}
            <circle cx="{sun_x}" cy="{sun_y}" r="5" fill="#EA580C" />
            <circle cx="{earth_x if "달" in target_mode or "식" in target_mode else sun_x}" cy="{earth_y if "달" in target_mode or "식" in target_mode else sun_y}" r="{orbit_radius}" fill="none" stroke="#21262D" stroke-width="0.4" stroke-dasharray="1.5" />
            <circle cx="{obj_x}" cy="{obj_y}" r="2.5" fill="{obj_color}" />
            <circle cx="{earth_x}" cy="{earth_y}" r="4" fill="#2563EB" />
            <path d="M 46 80 A 4 4 0 0 0 54 80 Z" fill="#05070A" />
            <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#10B981" stroke-width="0.8" marker-end="url(#arrow)" />
            <defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#10B981"/></marker></defs>
        </svg>
    </div>
    """
    components.html(orbit_html, height=310)

    # [더블 터치 버그 완벽 수정] 콜백 함수 연동을 이용해 드래그 즉시 적용되게 구조 개편
    st.markdown('<p class="control-label">🔄 공전 각도 정밀 제어 (즉각적인 실시간 리렌더링)</p>', unsafe_allow_html=True)
    st.slider(
        "공전 각도 조절 (°)", min_value=0, max_value=359, 
        value=int(st.session_state.current_phase), 
        key="slider_val", on_change=update_phase_from_slider
    )
    
    st.markdown('<p class="control-label">🌌 천체 공전 위치 퀵 매핑 (PPT 주요 개념)</p>', unsafe_allow_html=True)
    if "내행성" in target_mode:
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        with p_col1:
            if st.button("💥 내합 (0°)", key="p_naehap"): st.session_state.current_phase = 0; st.rerun()
        with p_col2:
            if st.button("📈 동방최대 (47°)", key="p_east_max"): st.session_state.current_phase = 47; st.rerun()
        with p_col3:
            if st.button("☀️ 외합 (180°)", key="p_oehap"): st.session_state.current_phase = 180; st.rerun()
        with p_col4:
            if st.button("📉 서방최대 (313°)", key="p_west_max"): st.session_state.current_phase = 313; st.rerun()
    elif "일식" in target_mode:
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            if st.button("🌑 삭 (일식 위치 / 0°)", key="p_sax_e"): st.session_state.current_phase = 0; st.rerun()
        with p_col2:
            if st.button("🌓 상현달 (90°)", key="p_sang_e"): st.session_state.current_phase = 90; st.rerun()
    elif "월식" in target_mode:
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            if st.button("🌕 망 (월식 위치 / 180°)", key="p_mang_m"): st.session_state.current_phase = 180; st.rerun()
        with p_col2:
            if st.button("🌗 하현달 (270°)", key="p_ha_m"): st.session_state.current_phase = 270; st.rerun()
    else: 
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        with p_col1:
            if st.button("🔴 충 (0°)", key="p_choong"): st.session_state.current_phase = 0; st.rerun()
        with p_col2:
            if st.button("📐 동구 (90°)", key="p_donggu"): st.session_state.current_phase = 90; st.rerun()
        with p_col3:
            if st.button("☀️ 합 (180°)", key="p_hap"): st.session_state.current_phase = 180; st.rerun()
        with p_col4:
            if st.button("📐 서구 (270°)", key="p_seogu"): st.session_state.current_phase = 270; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 하단 교과 원리 가이드 리포트
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:12px;'>📘 지구과학I 천체 파트 교과 기하 원리 가이드</h3>", unsafe_allow_html=True)

if "내행성" in target_mode:
    st.markdown("""
    * **동방최대이각 (47° 부근 - 오른쪽 배치):** 태양-지구 선 기준 우측에 위치합니다. 저녁 18시에 관측자가 서쪽 하늘을 바라볼 때 태양이 지고 난 후 서쪽 지평선 위에 남아있으므로 **초저녁 서쪽 하늘**에서 **오른쪽 면이 밝은 상현달 모양(반달)**으로 관측됩니다.
    * **서방최대이각 (313° 부근 - 왼쪽 배치):** 태양-지구 선 기준 좌측에 위치합니다. 새벽 6시에 동쪽 하늘을 바라볼 때 태양보다 먼저 떠올라 위치하므로 **새벽 동쪽 하늘**에서 **왼쪽 면이 밝은 하현달 모양(반달)**으로 관측됩니다.
    """)
elif "일식" in target_mode:
    st.markdown("""
    * **일식(Solar Eclipse):** 달이 태양과 지구 사이인 **삭(0°)** 정렬에 도달하여 달의 본그림자가 지구를 가릴 때 일어납니다. 태양-달-지구 순서의 기하 배치입니다.
    """)
elif "월식" in target_mode:
    st.markdown("""
    * **월식(Lunar Eclipse):** 달이 지구 반대편인 **망(180°)** 정렬에 도달하여 지구의 본그림자 속으로 완전히 들어갈 때 일어납니다. 태양-지구-달 순서의 배치이며, 붉은색 빛이 굴절되어 달에 닿기 때문에 **블러드문** 현상이 성립합니다.
    """)
else:
    st.markdown("""
    * **충 (0°):** 외행성이 지구와 가장 가까워지는 위치로, 지구-태양 일직선 바깥 방향(아래쪽)에 정렬합니다. 자정(24시)에 남중하므로 한밤중에 가장 크게 보름달(망) 모양 구조로 관측됩니다.
    * **동구 (90° - 우측) / 서구 (270° - 좌측):** 태양-지구 연결선과 외행성이 이루는 각도가 정확히 **직각($90^\circ$)**을 이룰 때를 의미합니다. 동구 위치일 때는 초저녁(18시)에 남중하고, 서구 위치일 때는 새벽(6시)에 남중하는 기하학적 특징을 가집니다.
    """)
st.markdown('</div>', unsafe_allow_html=True)
