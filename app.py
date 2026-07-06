import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# 1. 페이지 기본 설정 및 고급 대시보드 UI 디자인 (CSS)
st.set_page_config(page_title="지구과학I 천체 운동 시뮬레이터", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&family=Pretendard:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    
    /* 전체 대시보드 카드 스타일 클래스 */
    .dashboard-card {
        background: linear-gradient(145deg, #131822, #1a2130);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4FACFE 0%, #00F2FE 50%, #00A8FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-header {
        color: #718096;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .accent-text {
        color: #00F2FE;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 제어 패널 (값 변경 시 즉각 반영되도록 최적화)
st.sidebar.title("🔭 천체 실시간 제어")
st.sidebar.markdown("---")

target_mode = st.sidebar.selectbox(
    "1. 관측 주제 선택", 
    ["일식과 월식 (달의 운동)", "내행성의 운동 (금성)", "외행성의 운동 (화성)"]
)

selected_hour = st.sidebar.slider(
    "2. 관측 시각 (지구 자전)", 
    min_value=0, max_value=24, value=22, step=1, format="%d:00"
)

orbit_phase = st.sidebar.slider(
    "3. 천체 공전 위치 (°)", 
    min_value=0, max_value=360, value=180, step=5, format="%d°"
)

direction = st.sidebar.radio("4. 바라보는 방위", ["동 (East)", "남 (South)", "서 (West)"], index=1)

# 3. 천문학 기하학 수식 연산 (라디안)
rotation_angle = ((selected_hour - 12) / 12) * np.pi 
alpha = (orbit_phase / 180) * np.pi

sun_x, sun_y = 50, 50      # 태양 좌표
earth_x, earth_y = 50, 78  # 지구 좌표
pointer_x = earth_x + 12 * np.sin(rotation_angle)
pointer_y = earth_y - 12 * np.cos(rotation_angle)

# 상태 기본값 지정
sky_color = "#080B11" if (selected_hour < 6 or selected_hour > 18) else "#2575FC"
sky_msg = "🌌 밤하늘 환경" if (selected_hour < 6 or selected_hour > 18) else "☀️ 낮 하늘 환경"

# 4. 레이아웃 타이틀 렌더링
st.markdown('<p class="main-header">Space Mechanics Simulator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">지구과학I 천체 운동 및 위치 관계 실시간 인터랙티브 대시보드</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# 5. 핵심 모드별 기하 구조 그래픽화 (이모티콘 전면 제거 및 세련된 원/선 드로잉)
if "일식과 월식" in target_mode:
    # 달 궤도 매핑
    orbit_radius = 14
    obj_x = earth_x + orbit_radius * np.sin(alpha)
    obj_y = earth_y - orbit_radius * np.cos(alpha)
    
    # 달 위상 계산
    phase_ratio = (1 + np.cos(alpha)) / 2
    is_lit_right = (np.sin(alpha) >= 0)
    rx_val = abs(45 * (2 * phase_ratio - 1))
    
    # 본그림자/반그림자 가이드 라인 및 특수 현상 매핑 (교과 자료 매칭)
    eclipse_overlay = ""
    status_summary = "정상 위상 변화 중"
    
    # 삭(180도 부근) -> 일식 기하 구조 검출
    if 170 <= orbit_phase <= 190:
        eclipse_overlay = '<circle cx="50" cy="50" r="45" fill="#04060A" stroke="#FFD700" stroke-width="2"/><circle cx="50" cy="50" r="43" fill="#0D1117" opacity="0.9"/><text x="50" y="54" fill="#FFD700" font-size="8" font-weight="bold" text-anchor="middle">개기일식(Solar Eclipse)</text>'
        status_summary = "개기일식 발생 (달이 태양을 완전히 차단)"
    elif 155 <= orbit_phase <= 205:
        eclipse_overlay = '<circle cx="50" cy="50" r="45" fill="#1A252C"/><path d="M 15 50 A 35 35 0 0 1 85 50 Z" fill="#FFD700" opacity="0.4"/><text x="50" y="54" fill="#FFF" font-size="7" text-anchor="middle">부분일식</text>'
        status_summary = "부분일식 발생 (달이 태양의 일부를 차단)"
    # 망(0도 혹은 360도 부근) -> 월식 기하 구조 검출
    elif orbit_phase <= 10 or orbit_phase >= 350:
        eclipse_overlay = '<circle cx="50" cy="50" r="45" fill="#5C1D16"/><text x="50" y="54" fill="#FADBD8" font-size="8" font-weight="bold" text-anchor="middle">개기월식(Blood Moon)</text>'
        status_summary = "개기월식 발생 (지구 본그림자에 진입하여 개기월식 붉은 달 관측)"

    # [좌측 렌더링] 지구 시점 위상
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("👀 지구 시점 위상 (Sky View)")
        
        sky_html = f"""
        <div style="background:{sky_color}; border-radius:12px; padding:30px; text-align:center; border:1px solid rgba(255,255,255,0.05);">
            <div style="color:#FFF; font-weight:600; margin-bottom:15px;">{selected_hour:02d}:00 | {direction}쪽 지평선 관측 시야</div>
            <svg width="130" height="130" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="#121721" />
                <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="#F4D03F" />
                <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{"#121721" if (phase_ratio > 0.5) else "#F4D03F"}" />
                {eclipse_overlay}
            </svg>
            <div style="color:#A0AEC0; font-size:0.85rem; margin-top:15px;">{sky_msg} | 상태: <span style="color:#00F2FE; font-weight:bold;">{status_summary}</span></div>
        </div>
        """
        components.html(sky_html, height=310)
        st.markdown('</div>', unsafe_allow_html=True)

    # [우측 렌더링] 우주 시점 기하 관계도 (이모티콘 없이 선과 영역으로 구현)
    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("🌌 우주 기하 구조 (Orbit Space View)")
        
        orbit_html = f"""
        <div style="background-color:#0D111A; border-radius:12px; padding:20px; border:1px solid rgba(255,255,255,0.05);">
            <svg width="100%" height="250" viewBox="0 0 100 100" style="max-width:280px; margin:0 auto; display:block;">
                <line x1="0" y1="0" x2="100" y2="0" stroke="rgba(255,235,59,0.03)" stroke-width="200" />
                
                <polygon points="{earth_x-5},{earth_y} {earth_x+5},{earth_y} {earth_x+12},0 {earth_x-12},0" fill="rgba(231, 76, 60, 0.08)" />
                <polygon points="{earth_x-5},{earth_y} {earth_x+5},{earth_y} {earth_x+25},0 {earth_x-25},0" fill="rgba(241, 196, 15, 0.03)" />
                <line x1="{earth_x}" y1="{earth_y}" x2="{earth_x}" y2="0" stroke="rgba(231, 76, 60, 0.3)" stroke-width="0.3" stroke-dasharray="1.5" />

                <circle cx="{sun_x}" cy="{sun_y}" r="6" fill="#E67E22" />
                <circle cx="{sun_x}" cy="{sun_y}" r="9" fill="#F1C40F" opacity="0.2" />
                <text x="{sun_x}" y="{sun_y-8}" fill="#F1C40F" font-size="3.5" font-weight="bold" text-anchor="middle">SUN</text>

                <circle cx="{earth_x}" cy="{earth_y}" r="{orbit_radius}" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="0.3" stroke-dasharray="1" />

                <circle cx="{earth_x}" cy="{earth_y}" r="4.5" fill="#2980B9" />
                <path d="M {earth_x-4.5} {earth_y} A 4.5 4.5 0 0 0 {earth_x+4.5} {earth_y} Z" fill="#06090F" />
                <text x="{earth_x}" y="{earth_y+8}" fill="#3498DB" font-size="3" font-weight="bold" text-anchor="middle">EARTH</text>

                <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#2ECC71" stroke-width="0.6" marker-end="url(#arrow)" />

                <circle cx="{obj_x}" cy="{obj_y}" r="2" fill="#F4D03F" />
                <path d="M {obj_x-2} {obj_y} A 2 2 0 0 0 {obj_x+2} {obj_y} Z" fill="#06090F" opacity="0.7" transform="rotate(180 {obj_x} {obj_y})" />
                <text x="{obj_x}" y="{obj_y-3.5}" fill="#F4D03F" font-size="2.5" font-weight="bold" text-anchor="middle">MOON</text>

                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#2ECC71"/></marker>
                </defs>
            </svg>
        </div>
        """
        components.html(orbit_html, height=310)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 6. 내행성(금성) 및 외행성(화성) 모드 분기 그래픽 연산
    is_inner = "내행성" in target_mode
    orbit_radius = 18 if is_inner else 38
    obj_x = sun_x + orbit_radius * np.sin(alpha)
    obj_y = sun_y + orbit_radius * np.cos(alpha)
    
    phase_ratio = (1 + np.cos(alpha)) / 2 if is_inner else 0.85 + (np.cos(alpha) * 0.15)
    is_lit_right = (np.sin(alpha) >= 0)
    rx_val = abs(45 * (2 * phase_ratio - 1))
    
    target_color = "#EB984E" if is_inner else "#EC7063"
    label_text = "VENUS" if is_inner else "MARS"
    
    # 위치에 따른 내합/외합, 충/합 정보 텍스트 동기화
    pos_status = ""
    if is_inner:
        if 165 <= orbit_phase <= 195: pos_status = "내합 (지구와 인접, 그믐달/역행)"
        elif orbit_phase <= 15 or orbit_phase >= 345: pos_status = "외합 (태양 반대편, 보름달/순행)"
        else: pos_status = "이각 이동 상태"
    else:
        if 165 <= orbit_phase <= 195: pos_status = "합 (태양 뒤편 관측 불가)"
        elif orbit_phase <= 15 or orbit_phase >= 345: pos_status = "충 (지구와 최인접 역행구간, 한밤중 남중)"
        else: pos_status = "구 위치 부근"

    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("👀 지구 시점 위상 (Sky View)")
        sky_html = f"""
        <div style="background:{sky_color}; border-radius:12px; padding:30px; text-align:center; border:1px solid rgba(255,255,255,0.05);">
            <div style="color:#FFF; font-weight:600; margin-bottom:15px;">{selected_hour:02d}:00 | {direction}쪽 지평선 관측 시야</div>
            <svg width="130" height="130" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="#121721" />
                <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
                <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{"#121721" if (phase_ratio > 0.5) else target_color}" />
            </svg>
            <div style="color:#A0AEC0; font-size:0.85rem; margin-top:15px;">상태: <span style="color:#00F2FE; font-weight:bold;">{pos_status}</span></div>
        </div>
        """
        components.html(sky_html, height=310)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("🌌 우주 기하 구조 (Orbit Space View)")
        orbit_html = f"""
        <div style="background-color:#0D111A; border-radius:12px; padding:20px; border:1px solid rgba(255,255,255,0.05);">
            <svg width="100%" height="250" viewBox="0 0 100 100" style="max-width:280px; margin:0 auto; display:block;">
                <line x1="0" y1="0" x2="100" y2="0" stroke="rgba(255,255,255,0.02)" stroke-width="200" />
                
                <circle cx="{sun_x}" cy="{sun_y}" r="5" fill="#E67E22" />
                <text x="{sun_x}" y="{sun_y-7}" fill="#F1C40F" font-size="3" font-weight="bold" text-anchor="middle">SUN</text>

                <circle cx="{sun_x}" cy="{sun_y}" r="{orbit_radius}" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="0.3" stroke-dasharray="1.5" />

                <circle cx="{earth_x}" cy="{earth_y}" r="4" fill="#2980B9" />
                <path d="M {earth_x-4} {earth_y} A 4 4 0 0 0 {earth_x+4} {earth_y} Z" fill="#06090F" />
                <text x="{earth_x}" y="{earth_y+8}" fill="#3498DB" font-size="3" font-weight="bold" text-anchor="middle">EARTH</text>

                <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#2ECC71" stroke-width="0.6" marker-end="url(#arrow)" />

                <circle cx="{obj_x}" cy="{obj_y}" r="2.5" fill="{target_color}" />
                <path d="M {obj_x-2.5} {obj_y} A 2.5 2.5 0 0 0 {obj_x+2.5} {obj_y} Z" fill="#06090F" opacity="0.75" transform="rotate(180 {obj_x} {obj_y})" />
                <text x="{obj_x}" y="{obj_y-4}" fill="{target_color}" font-size="2.5" font-weight="bold" text-anchor="middle">{label_text}</text>

                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#2ECC71"/></marker>
                </defs>
            </svg>
        </div>
        """
        components.html(orbit_html, height=310)
        st.markdown('</div>', unsafe_allow_html=True)

# 7. 하단 교과 가이드 리포트 영역
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
st.subheader("📘 지구과학I 천체 파트 교과 원리 분석 가이드")

if "일식과 월식" in target_mode:
    st.markdown(f"""
    * **일식(Solar Eclipse):** 달이 태양과 지구 사이에 정렬되어 <span class="accent-text">삭(위치 180° 부근)</span>에 도달할 때 발생합니다. 본그림자 영역에서는 태양이 전부 가려지는 개기일식이, 반그림자 영역에서는 부분일식이 관측됩니다.
    * **월식(Lunar Eclipse):** 달이 지구 뒤편의 <span class="accent-text">망(위치 0° 또는 360°)</span>에 도달하여 지구 본그림자 속으로 완전히 들어가면 개기월식이 일어납니다. 이때 지구 대기층을 통과하며 굴절된 붉은색 빛만 달에 도달하기 때문에 달이 어둡고 붉게 보입니다.
    """, unsafe_allow_html=True)
elif "내행성" in target_mode:
    st.markdown(f"""
    * **내합과 외합의 위상 관계:** 금성이 지구와 가장 가까운 <span class="accent-text">내합(위치 180°)</span>에 오면 시직경이 최대가 되며 초승달/그믐달 모양으로 얇아집니다. 반대로 <span class="accent-text">외합(위치 0°)</span>에 도달하면 크기는 가장 작아지지만 보름달 형태의 둥근 위상에 가까워집니다.
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    * **외행성의 충과 역행:** 화성이 지구와 태양 일직선 바깥쪽인 <span class="accent-text">충(위치 0° 또는 360°)</span>에 도달하면, 지구 자전축 시선 바늘(초록선)이 한밤중인 24시 방향을 가리킬 때 정면(남중)으로 매칭되어 밤새도록 가장 밝고 크게 관측할 수 있습니다.
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
