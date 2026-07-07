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

# 2. 세션 상태 데이터 초기화 및 슬라이더 버그 방지 고정
if "current_hour" not in st.session_state:
    st.session_state.current_hour = 18  # 초저녁(18시) 기본값
if "current_phase" not in st.session_state:
    st.session_state.current_phase = 47 # 초기 위치 기본값 (동방최대이각)

# 슬라이더 조작 시 세션 상태 즉시 동기화 콜백
def update_phase_from_slider():
    st.session_state.current_phase = st.session_state.slider_val

# 3. 사이드바 제어 패널
st.sidebar.title("🔭 Astro Control")
st.sidebar.markdown("---")

target_mode = st.sidebar.selectbox(
    "1. 관측 핵심 주제 선택", 
    ["내행성의 운동 (금성)", "일식 (달의 운동)", "월식 (달의 운동)", "외행성의 운동 (화성)"]
)

direction = st.sidebar.radio("2. 바라보는 방위 선택", ["동 (East)", "서 (West)", "남 (South)", "북 (North)"], index=2) # 기본값 남쪽

# 4. 정밀 기하 천문 수식 연산 (북극 상공 시점)
rotation_angle = ((st.session_state.current_hour - 12) / 12) * np.pi 

sun_x, sun_y = 50, 50      
earth_x, earth_y = 50, 80  

# 자전축 시선 바늘 끝점 계산
pointer_x = earth_x + 12 * np.sin(rotation_angle)
pointer_y = earth_y - 12 * np.cos(rotation_angle)

# 낮과 밤 판정 (06시~18시 사이는 낮, 그 외는 밤)
is_daytime = 6 <= st.session_state.current_hour < 18
if is_daytime:
    sky_gradient = "linear-gradient(180deg, #1E40AF 0%, #3B82F6 100%)" # 푸른 낮 하늘
else:
    sky_gradient = "linear-gradient(180deg, #05070A 0%, #0F1420 100%)" # 어두운 밤 하늘

# 5. 메인 대시보드 렌더링
st.markdown('<p class="main-header">Cosmic Orbital Diagnostics</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">지구과학I 천체 기하학·위상 변화 메커니즘 시뮬레이터 (교과 원리 완전 교정본)</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# --- [좌측 카드] 지구 관측 시점 위상 및 하늘 위치 그래픽 (Sky View) ---
with col1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:15px;'>👀 지구 관측 시점 (Sky View)</h3>", unsafe_allow_html=True)
    
    pos_status = "정상 위상 관계"
    celestial_graphics = ""
    
    dark_side_color = "#2A3142"  
    dark_side_stroke = "rgba(255,255,255,0.2)" 
    
    phase_angle = st.session_state.current_phase % 360
    
    # 낮일 때는 점선 스타일 유도, 밤일 때는 실선 구조
    visibility_stroke = "stroke-dasharray='3,3' opacity='0.4'" if is_daytime else "stroke-width='1'"
    planet_opacity = "opacity='0.3'" if is_daytime else "opacity='1'"
    
    # [방위 위치 계산 연산] 남쪽 하늘 기준: 동쪽이 왼쪽(X=20), 서쪽이 오른쪽(X=80)
    if "내행성" in target_mode:
        tgt_x = 50 - 30 * np.sin(np.radians(phase_angle)) 
        tgt_y = 50 
        
        target_color = "#FB923C"
        phase_ratio = (1 + np.cos(np.radians(phase_angle))) / 2
        is_lit_right = (phase_angle < 180) 
        
        r_val = 15
        rx_val = abs(r_val * (2 * phase_ratio - 1))
        ellipse_fill = dark_side_color if phase_ratio > 0.5 else target_color
        
        # 중괄호 문법 오류 방지를 위해 명확하게 공백 분리하여 대입
        scale_val = r_val / 50
        trans_x = tgt_x - r_val
        trans_y = tgt_y - r_val
        lit_flag = 1 if is_lit_right else 0
        sun_opacity = "0.8" if is_daytime else "0.1"
        
        celestial_graphics = f"""
        <circle cx="50" cy="50" r="10" fill="#EF4444" opacity="{sun_opacity}" />
        <g transform="translate({trans_x}, {trans_y}) scale({scale_val})" {planet_opacity}>
            <circle cx="50" cy="50" r="45" fill="{dark_side_color}" stroke="{dark_side_stroke}" {visibility_stroke} />
            <path d="M 50 5 A 45 45 0 0 {lit_flag} 50 95 Z" fill="{target_color}" />
            <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ellipse_fill}" />
        </g>
        """
        if phase_angle == 0: pos_status = "내합 (태양과 겹침, 관찰 불가)"
        elif phase_angle == 180: pos_status = "외합 (태양 뒤편, 관찰 불가)"
        elif 40 <= phase_angle <= 55: pos_status = "동방최대이각 (왼쪽/동쪽 위치, 초저녁 서쪽하늘 반달)"
        elif 305 <= phase_angle <= 320: pos_status = "서방최대이각 (오른쪽/서쪽 위치, 새벽 동쪽하늘 반달)"
            
    elif "일식" in target_mode or "월식" in target_mode:
        tgt_x = 50 - 35 * np.sin(np.radians(phase_angle))
        tgt_y = 50
        target_color = "#FBBF24" if "일식" in target_mode else "#991B1B" if phase_angle == 180 else "#FBBF24"
        
        r_val = 14
        phase_ratio = (1 - np.cos(np.radians(phase_angle))) / 2
        is_lit_right = (phase_angle < 180)
        rx_val = abs(r_val * (2 * phase_ratio - 1))
        ellipse_fill = dark_side_color if phase_ratio < 0.5 else target_color
        
        if "일식" in target_mode and phase_angle == 0:
            celestial_graphics = f'<circle cx="50" cy="50" r="15" fill="none" stroke="#FBBF24" stroke-width="3" />'
            pos_status = "개기일식 (달이 태양을 차폐)"
        else:
            scale_val = r_val / 50
            trans_x = tgt_x - r_val
            trans_y = tgt_y - r_val
            lit_flag = 1 if is_lit_right else 0
            
            celestial_graphics = f"""
            <g transform="translate({trans_x}, {trans_y}) scale({scale_val})" {planet_opacity}>
                <circle cx="50" cy="50" r="45" fill="{dark_side_color}" stroke="{dark_side_stroke}" {visibility_stroke} />
                <path d="M 50 5 A 45 45 0 0 {lit_flag} 50 95 Z" fill="{target_color}" />
                <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ellipse_fill}" />
            </g>
            """
            pos_status = "일식/월식 범위 외 일반 달 위상"
            
    else: # 외행성 모드
        tgt_x = 50 - 35 * np.sin(np.radians(phase_angle))
        tgt_y = 50
        target_color = "#EF4444"
        
        rad_calc = np.radians(90 - phase_angle)
        ex = 50 + 42 * np.cos(rad_calc)
        ey = 50 + 42 * np.sin(rad_calc)
        dist_to_earth = np.sqrt((ex - 50)**2 + (ey - 80)**2)
        dynamic_r = 12 + (22 - 12) * (1.0 - (dist_to_earth - 12) / 60)
        
        ell_ratio = 0.88 + 0.12 * abs(np.cos(np.radians(phase_angle)))
        is_lit_right = (phase_angle < 180)
        rx_val = abs(dynamic_r * (2 * ell_ratio - 1))
        ellipse_fill = dark_side_color if ell_ratio > 0.5 else target_color
        
        # [SyntaxError 완전 해결 핵심] 변수를 f-string 가독 영역 외부에서 먼저 연산 후 문자열 주입
        scale_val = dynamic_r / 50
        trans_x = tgt_x - dynamic_r
        trans_y = tgt_y - dynamic_r
        lit_flag = 1 if is_lit_right else 0
        
        celestial_graphics = f"""
        <g transform="translate({trans_x}, {trans_y}) scale({scale_val})" {planet_opacity}>
            <circle cx="50" cy="50" r="45" fill="{dark_side_color}" stroke="{dark_side_stroke}" {visibility_stroke} />
            <path d="M 50 5 A 45 45 0 0 {lit_flag} 50 95 Z" fill="{target_color}" />
            <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ellipse_fill}" />
        </g>
        """
        if phase_angle == 0: pos_status = "충 (정중앙 위치, 자정 남중 보름달 모양)"
        elif phase_angle == 90: pos_status = "동구 (왼쪽/동쪽 위치, 초저녁 남중)"
        elif phase_angle == 180: pos_status = "합 (태양 뒤편 위치, 관측 불가)"
        elif phase_angle == 270: pos_status = "서구 (오른쪽/서쪽 위치, 새벽 남중)"

    sky_html = f"""
    <div style="background:{sky_gradient}; border-radius:12px; padding:30px; text-align:center; position:relative;">
        <div style="color:#C9D1D9; font-weight:600; margin-bottom:10px; font-size:1rem;">
            {st.session_state.current_hour:02d}:00 | {direction} 지평선 시야 {"☀️ (주간 - 점선 표시)" if is_daytime else "🌙 (야간)"}
        </div>
        <svg width="240" height="150" viewBox="0 0 100 60" style="background:rgba(255,255,255,0.03); border-radius:8px;">
            <line x1="0" y1="52" x2="100" y2="52" stroke="#484F58" stroke-width="0.8" />
            <text x="8" y="58" fill="#8B949E" font-size="5" font-weight="bold">동(East) [왼쪽]</text>
            <text x="50" y="58" fill="#8B949E" font-size="5" text-anchor="middle">남(South)</text>
            <text x="92" y="58" fill="#8B949E" font-size="5" text-anchor="end">서(West) [오른쪽]</text>
            {celestial_graphics}
        </svg>
        <div style="margin-top:15px;"><span class="status-pill">{pos_status}</span></div>
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
        st.markdown(f"<div style='padding-top:6px; font-size:0.95rem;'>현재 내부 지정 시각: <b>{st.session_state.current_hour:02d}:00</b></div>", unsafe_allow_html=True)
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
    elif "일식" in target_mode or "월식" in target_mode:
        orbit_radius = 10
        rad = np.radians(90 - st.session_state.current_phase)
        obj_x = earth_x + orbit_radius * np.cos(rad)
        obj_y = earth_y + orbit_radius * np.sin(rad)
        obj_color = "#FBBF24"
        if "월식" in target_mode:
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

    st.markdown('<p class="control-label">🔄 공전 각도 정밀 제어 (즉각 연동)</p>', unsafe_allow_html=True)
    
    st.slider(
        "공전 각도 조절 (°)", min_value=0, max_value=359, 
        value=int(st.session_state.current_phase), 
        key="slider_val", on_change=update_phase_from_slider
    )
    
    st.markdown('<p class="control-label">🌌 천체 공전 위치 퀵 매핑</p>', unsafe_allow_html=True)
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
st.markdown("<h3 style='font-size:1.1rem; font-weight:600; color:#8B949E; margin-bottom:12px;'>📘 지구과학I 천체 파트 교과 기하 원리 가이드 (방위각 교정 완료)</h3>", unsafe_allow_html=True)

if "내행성" in target_mode:
    st.markdown("""
    * **동방최대이각 (47° 부근):** 관측 시야상 **왼쪽(동쪽)**에 위치하게 됩니다. 초저녁 서쪽 지평선을 바라볼 때 태양의 왼쪽(위쪽)에 남아 있으므로 해가 진 직후 잠깐 관측이 가능합니다.
    * **서방최대이각 (313° 부근):** 관측 시야상 **오른쪽(서쪽)**에 위치하게 됩니다. 새벽 동쪽 지평선을 바라볼 때 태양의 오른쪽(위쪽)에 먼저 떠오르므로 해가 뜨기 직전 관측 가능합니다.
    """)
else:
    st.markdown("""
    * **동구 (90°) / 서구 (270°):** 남쪽 하늘을 볼 때 동쪽(왼쪽)에서 떠올라 서쪽(오른쪽)으로 지는 천체의 겉보기 운동 경로 상에서 정밀 동기화됩니다.
    * **주간 음영 점선 효과:** 낮 시각(06:00 ~ 18:00)에는 대기 산란으로 인해 천체가 실제로 하늘에 떠 있더라도 관측이 어려우므로 점선 및 반투명 처리가 자동으로 활성화됩니다.
    """)
st.markdown('</div>', unsafe_allow_html=True)
