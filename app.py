import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# 1. 페이지 설정 및 고급 천문 대시보드 스타일 (Modern Minimal CSS)
st.set_page_config(page_title="지구과학I 천체 운동 시뮬레이터", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Pretendard:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #0A0C10;
        color: #E2E8F0;
    }
    
    /* 세련된 글래스모피즘 카드 디자인 */
    .dashboard-card {
        background: rgba(20, 24, 33, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(10px);
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
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.8rem;
    }
    
    /* 상태 뱃지 스타일 */
    .status-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(56, 189, 248, 0.1);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 제어 패널 (불필요한 슬라이더 전면 제거)
st.sidebar.title("🔭 천체 관측 제어")
st.sidebar.markdown("---")

target_mode = st.sidebar.selectbox(
    "1. 학습 주제 선택", 
    ["일식과 월식 (달의 운동)", "내행성의 운동 (금성)", "외행성의 운동 (화성)"]
)

st.sidebar.markdown("### 2. 관측 시각 조절 (지구 자전)")
# 세션 상태(Session State)를 활용한 버튼식 시간 제어 구현
if "current_hour" not in st.st.session_state:
    st.session_state.current_hour = 22

t_col1, t_col2 = st.sidebar.columns(2)
with t_col1:
    if st.button("⏰ -1시간"):
        st.session_state.current_hour = (st.session_state.current_hour - 1) % 25
with t_col2:
    if st.button("⏰ +1시간"):
        st.session_state.current_hour = (st.session_state.current_hour + 1) % 25

st.sidebar.markdown(f"**현재 설정 시각:** `{st.session_state.current_hour:02d}:00`")

# 3. 천문학적 핵심 위치 퀵 버튼 (원클릭 위치 제어)
st.sidebar.markdown("### 3. 천체 공전 위치 퀵 매핑")
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

direction = st.sidebar.radio("4. 바라보는 방위", ["동 (East)", "남 (South)", "서 (West)"], index=1)

# 4. 수식 연산 파트
rotation_angle = ((st.session_state.current_hour - 12) / 12) * np.pi 
alpha = (st.session_state.current_phase / 180) * np.pi

sun_x, sun_y = 50, 50      
earth_x, earth_y = 50, 78  
pointer_x = earth_x + 12 * np.sin(rotation_angle)
pointer_y = earth_y - 12 * np.cos(rotation_angle)

sky_color = "#07090E" if (st.session_state.current_hour < 6 or st.session_state.current_hour > 18) else "#1D4ED8"
sky_msg = "🌌 밤하늘 (Optimal Night)" if (st.session_state.current_hour < 6 or st.session_state.current_hour > 18) else "☀️ 낮하늘 (Daylight)"

# 5. 메인 레이아웃 출력
st.markdown('<p class="main-header">Orbit Dynamics & Phases</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">지구과학I 교과 연동 실시간 기하 시뮬레이터</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# [좌측] 지구 시점 위상 그래픽 (의미 없는 글자 제거, 실제 코로나 광학 그래픽화)
with col1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("👀 지구 관측 시점 (Sky View)")
    
    phase_ratio = (1 + np.cos(alpha)) / 2
    is_lit_right = (np.sin(alpha) >= 0)
    rx_val = abs(45 * (2 * phase_ratio - 1))
    
    target_color = "#F4D03F" if "일식" in target_mode else ("#EB984E" if "내행성" in target_mode else "#EC7063")
    base_fill = target_color if phase_ratio > 0.5 else "#141923"
    shadow_fill = "#141923" if phase_ratio > 0.5 else target_color

    # 특수 일식/월식 광학 레이어 드로잉 (글자 박기 제거)
    celestial_graphics = f"""
    <circle cx="50" cy="50" r="45" fill="#141923" />
    <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
    <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{shadow_fill}" />
    """
    
    pos_status = "일반 위상 변화"
    if "일식과 월식" in target_mode:
        if 175 <= st.session_state.current_phase <= 185:
            # 개기일식: 태양이 검은 달 뒤로 숨으며 발생하는 황금빛 코로나 링 그래픽 구현
            celestial_graphics = """
            <circle cx="50" cy="50" r="46" fill="none" stroke="#F5B041" stroke-width="3" filter="drop-shadow(0px 0px 6px #F39C12)"/>
            <circle cx="50" cy="50" r="45" fill="#0A0C10" />
            """
            pos_status = "개기일식 (Corona Phase)"
        elif 155 <= st.session_state.current_phase <= 205:
            pos_status = "부분일식 (Partial Eclipse)"
        elif st.session_state.current_phase <= 5 or st.session_state.current_phase >= 355:
            # 개기월식: 지구 그림자에 필터링된 블러드문(붉은 달) 광학 묘사
            celestial_graphics = '<circle cx="50" cy="50" r="45" fill="#7B241C" filter="drop-shadow(0px 0px 4px #922B21)"/>'
            pos_status = "개기월식 (Blood Moon)"
    elif "내행성" in target_mode:
        if 175 <= st.session_state.current_phase <= 185: pos_status = "내합 (시직경 최대, 역행 시작)"
        elif st.session_state.current_phase <= 5 or st.session_state.current_phase >= 355: pos_status = "외합 (시직경 최소)"
    else:
        if st.session_state.current_phase <= 5 or st.session_state.current_phase >= 355: pos_status = "충 (자정 남중, 최적 관측기, 역행)"

    sky_html = f"""
    <div style="background:{sky_color}; border-radius:14px; padding:35px; text-align:center; transition: all 0.3s;">
        <div style="color:#FFF; font-weight:600; margin-bottom:20px; font-size:1.05rem;">{st.session_state.current_hour:02d}:00 | {direction}쪽 시야 위상</div>
        <svg width="140" height="140" viewBox="0 0 100 100" style="filter: drop-shadow(0px 4px 12px rgba(0,0,0,0.5));">
            {celestial_graphics}
        </svg>
        <div style="margin-top:20px;"><span class="status-pill">{pos_status}</span></div>
    </div>
    """
    components.html(sky_html, height=310)
    st.markdown('</div>', unsafe_allow_html=True)

# [우측] 우주 시점 기하 관계도 (의미 없는 검은색 막대 전면 제거, 정돈된 라인 가이드)
with col2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("🌌 우주 공간 위치 관계 (Orbit View)")
    
    # 모드별 타겟 천체 기하 좌표 바인딩
    if "일식과 월식" in target_mode:
        orbit_radius = 13
        obj_x = earth_x + orbit_radius * np.sin(alpha)
        obj_y = earth_y - orbit_radius * np.cos(alpha)
        label_text = "MOON"
        obj_color = "#F4D03F"
        # 월식 지구 그림자 영역 가이드 (세련된 단일 투명 레이어로 처리)
        shadow_overlay = f'<polygon points="{earth_x-4.5},{earth_y} {earth_x+4.5},{earth_y} {earth_x+10},0 {earth_x-10},0" fill="rgba(231, 76, 60, 0.06)" />'
    elif "내행성" in target_mode:
        orbit_radius = 18
        obj_x = sun_x + orbit_radius * np.sin(alpha)
        obj_y = sun_y + orbit_radius * np.cos(alpha)
        label_text = "VENUS"
        obj_color = "#EB984E"
        shadow_overlay = ""
    else:
        orbit_radius = 38
        obj_x = sun_x + orbit_radius * np.sin(alpha)
        obj_y = sun_y + orbit_radius * np.cos(alpha)
        label_text = "MARS"
        obj_color = "#EC7063"
        shadow_overlay = ""

    orbit_html = f"""
    <div style="background-color:#0E1118; border-radius:14px; padding:20px; border:1px solid rgba(255,255,255,0.03);">
        <svg width="100%" height="250" viewBox="0 0 100 100" style="max-width:280px; margin:0 auto; display:block;">
            {shadow_overlay}

            <circle cx="{sun_x}" cy="{sun_y}" r="5.5" fill="#E67E22" />
            <circle cx="{sun_x}" cy="{sun_y}" r="8" fill="#F1C40F" opacity="0.15" />

            <circle cx="{earth_x if "일식" in target_mode else sun_x}" cy="{earth_y if "일식" in target_mode else sun_y}" r="{orbit_radius}" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="0.3" stroke-dasharray="1" />

            <circle cx="{earth_x}" cy="{earth_y}" r="4.5" fill="#2980B9" />
            <path d="M {earth_x-4.5} {earth_y} A 4.5 4.5 0 0 0 {earth_x+4.5} {earth_y} Z" fill="#06090F" />

            <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#10B981" stroke-width="0.7" marker-end="url(#arrow-pointer)" />

            <circle cx="{obj_x}" cy="{obj_y}" r="2.5" fill="{obj_color}" />
            <path d="M {obj_x-2.5} {obj_y} A 2.5 2.5 0 0 0 {obj_x+2.5} {obj_y} Z" fill="#06090F" opacity="0.7" transform="rotate(180 {obj_x} {obj_y})" />

            <defs>
                <marker id="arrow-pointer" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#10B981"/></marker>
            </defs>
        </svg>
    </div>
    """
    components.html(orbit_html, height=310)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 하단 교과 원리 분석 가이드 리포트
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.subheader("📘 지구과학I 천체 파트 교과 핵심 분석")

if "일식과 월식" in target_mode:
    st.markdown(f"""
    * **일식 원리:** 달이 태양과 지구 사이에 배치되는 <span style="color:#38BDF8; font-weight:600;">삭(각도 180°)</span> 구간에서 달의 본그림자가 지구를 가릴 때 개기일식이 성립합니다. 위 그래픽과 같이 태양이 완전히 가려지면 주위에 개기일식의 상징인 **황금빛 코로나(Corona)**가 관측됩니다.
    * **월식 원리:** 달이 지구 반대편인 <span style="color:#38BDF8; font-weight:600;">망(각도 0°)</span> 부근에서 지구의 본그림자 영역 속에 완벽하게 정렬되면 개기월식이 일어나 어둡고 붉은 **블러드문(Blood Moon)**이 관측됩니다.
    """), unsafe_allow_html=True)
elif "내행성" in target_mode:
    st.markdown(f"""
    * **내행성(금성)의 운동 특징:** 금성은 지구 안쪽 트궤도에서 공전하므로 태양과 일정한 사잇각인 <span style="color:#38BDF8; font-weight:600;">최대이각</span> 범위 내에서 왕복 운동을 반복하는 겉보기 운동을 보입니다. 내합 부근 퀵 버튼을 누르면 지구와 가까워져 가장 큰 시직경의 그믐달/초승달 위상을 확인할 수 있습니다.
    """), unsafe_allow_html=True)
else:
    st.markdown(f"""
    * **외행성(화성)의 운동 특징:** 화성이 지구와 태양 일직선 바깥쪽 방향인 <span style="color:#38BDF8; font-weight:600;">충(각도 0°)</span> 위치에 올 때 시직경이 가장 크게 관측되며, 관측자의 녹색 시선 바늘이 밤 24시 정면을 향하므로 한밤중에 정남쪽 하늘에서 가장 오랫동안 밝게 관측할 수 있습니다.
    """), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
