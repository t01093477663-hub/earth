import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# 1. 페이지 기본 설정 및 스타일 정의
st.set_page_config(page_title="지구과학I 천체 운동 시뮬레이터", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #0E1117;
    }
    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #5DADE2 0%, #A569BD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #AEB6BF;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .info-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 제어 패널
st.sidebar.title("🪐 천체 관측 핵심 제어")
st.sidebar.markdown("---")

# 교과 자료 기반 핵심 타겟 설정
target_mode = st.sidebar.selectbox(
    "1. 학습 주제 선택", 
    [
        "일식과 월식 (Eclipse)", 
        "내행성의 운동 (금성)", 
        "외행성의 운동 (화성)"
    ]
)

selected_hour = st.sidebar.slider("2. 관측 시각 설정 (지구 자전)", min_value=0, max_value=24, value=22, step=1, format="%d:00")
orbit_phase = st.sidebar.slider("3. 천체 공전 위치 조정", min_value=0, max_value=360, value=90, step=15, format="%d°")

# 3. 천문 기하학적 각도 계산 (라디안 변환)
# 관측 시각에 따른 자전 방향 각도 (태양 기준 시선 계산)
rotation_angle = ((selected_hour - 12) / 12) * np.pi 
# 천체의 공전 각도
alpha = (orbit_phase / 180) * np.pi

# 4. 좌표계 매핑 및 위상 기하 구조 연동 계산
sun_x, sun_y = 50, 50      # 태양 중심 좌표
earth_x, earth_y = 50, 80  # 지구 중심 좌표

# 관측자 시선 벡터 계산 (초록색 화살표선)
pointer_x = earth_x + 12 * np.sin(rotation_angle)
pointer_y = earth_y - 12 * np.cos(rotation_angle)

# 기본 변수 초기화
obj_x, obj_y = 50, 50
orbit_radius = 0
orbit_center_x, orbit_center_y = 50, 50
label_text = ""
target_color = "#FFFFFF"
phase_ratio = 0.5  # 지구에서 보이는 천체의 위상 위도 비 (0~1)
is_lit_right = True # 햇빛을 받는 방향 지표

if "일식과 월식" in target_mode:
    # 달은 지구를 중심으로 공전함 (교과 내용 반영)
    orbit_radius = 14
    orbit_center_x, orbit_center_y = earth_x, earth_y
    # 태양-지구-달 구조 기하 계산
    obj_x = earth_x + orbit_radius * np.sin(alpha)
    obj_y = earth_y - orbit_radius * np.cos(alpha)
    label_text = "MOON"
    target_color = "#F4D03F"
    
    # 달의 본그림자 및 위상 변화 수학적 동기화
    phase_ratio = (1 + np.cos(alpha)) / 2
    is_lit_right = (np.sin(alpha) >= 0)

elif "내행성" in target_mode:
    # 금성은 수성 안쪽/지구 안쪽 궤도 (태양 중심 공전)
    orbit_radius = 18
    orbit_center_x, orbit_center_y = sun_x, sun_y
    obj_x = sun_x + orbit_radius * np.sin(alpha)
    obj_y = sun_y + orbit_radius * np.cos(alpha)
    label_text = "VENUS"
    target_color = "#EB984E"
    
    # 내행성의 내합/외합 및 위상 크기 변화 (지구와의 거리에 따라 시직경 변화 반영)
    dist_to_earth = np.sqrt((obj_x - earth_x)**2 + (obj_y - earth_y)**2)
    phase_ratio = (1 + np.cos(alpha)) / 2
    is_lit_right = (np.sin(alpha) >= 0)

else:
    # 화성 등 외행성은 지구 바깥쪽 궤도 (태양 중심 공전)
    orbit_radius = 40
    orbit_center_x, orbit_center_y = sun_x, sun_y
    obj_x = sun_x + orbit_radius * np.sin(alpha)
    obj_y = sun_y + orbit_radius * np.cos(alpha)
    label_text = "MARS"
    target_color = "#EC7063"
    
    # 외행성은 항상 보름달 모양에 가깝게 보임 (이각이 크고 외합/충 부근에서 보임)
    phase_ratio = 0.85 + (np.cos(alpha) * 0.15)
    is_lit_right = (np.sin(alpha) >= 0)

# 5. UI 화면 레이아웃 구성
st.markdown('<p class="main-header">지구과학I 천체 위치 관계 시뮬레이터</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">교과 과정: 태양계 천체의 관측과 운동 (일식·월식·행성의 이각)</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

# [좌측] 지구 시점 관측 위상 그래픽 (이모티콘 없이 순수 SVG 원형 기하로 표현)
with col1:
    st.subheader("👀 지구 관측 시점 (Sky Phase View)")
    st.caption("교과 자료의 천구 투영 원리 반영: 지구 관측자가 바라보는 실제 천체의 광학 위상")
    
    # SVG 타원 형태 렌더링 공식 계산
    rx_val = abs(45 * (2 * phase_ratio - 1))
    base_fill = target_color if phase_ratio > 0.5 else "#1A252C"
    shadow_fill = "#1A252C" if phase_ratio > 0.5 else target_color
    
    # 일식/월식 특수 기하 현상 처리
    eclipse_overlay = ""
    if "일식과 월식" in target_mode:
        # 삭 위치 (태양-달-지구 일직선) 일때 개기일식 구현
        if 165 <= orbit_phase <= 195: 
            eclipse_overlay = '<circle cx="50" cy="50" r="45" fill="#090D10" stroke="#F4D03F" stroke-width="1.5"/><text x="50" y="54" fill="#F4D03F" font-size="8" text-anchor="middle">개기일식</text>'
        # 망 위치 (태양-지구-달 일직선) 일때 개기월식(붉은 달) 구현 (교과 p.144 내용 반영)
        elif orbit_phase <= 15 or orbit_phase >= 345:
            eclipse_overlay = '<circle cx="50" cy="50" r="45" fill="#922B21"/><text x="50" y="54" fill="#FADBD8" font-size="8" text-anchor="middle">개기월식(붉은달)</text>'

    # 하늘 배경색 및 상태 제어
    sky_color = "#0B1017"
    if 6 <= selected_hour <= 17:
        sky_color = "#3498DB" # 주간 하늘 환경
        
    sky_html = f"""
    <div style="background-color: {sky_color}; border-radius: 16px; padding: 30px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
        <div style="color: white; font-weight: 600; margin-bottom: 15px; font-size:1.1rem;">지평선 기준 투영 위상</div>
        <svg width="140" height="140" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="#1A252C" />
            <path d="M 50 5 A 45 45 0 0 {1 if is_lit_right else 0} 50 95 Z" fill="{target_color}" />
            <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{shadow_fill if (phase_ratio > 0.5) else base_fill}" />
            {eclipse_overlay}
        </svg>
        <div style="margin-top: 15px; font-size: 0.9rem; color: #BDC3C7;">
            시각: {selected_hour:02d}:00 | 위상 면적 비율: {phase_ratio*100:.1f}%
        </div>
    </div>
    """
    components.html(sky_html, height=340)

# [우측] 우주 시점 위치 관계도 그래픽 (순수 원, 선, 점선, 기하 화살표 구조)
with col2:
    st.subheader("🌌 우주 공간 시점 (Space Orbit Position)")
    st.caption("태양, 지구, 천체의 공전 궤도면과 자전 방향선 간의 기하학적 위치 관계도")

    # 월식 본그림자/반그림자 가이드선 생성 영역 (일식/월식 모드 전용)
    shadow_lines = ""
    if "일식과 월식" in target_mode:
        shadow_lines = f"""
        <polygon points="{earth_x-4},{earth_y} {earth_x+4},{earth_y} {earth_x+10},0 {earth_x-10},0" fill="rgba(255,255,255,0.04)" />
        <line x1="{earth_x}" y1="{earth_y}" x2="{earth_x}" y2="0" stroke="rgba(231, 76, 60, 0.4)" stroke-width="0.5" stroke-dasharray="2" />
        """

    orbit_html = f"""
    <div style="background-color: #0F141D; border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.1);">
        <svg width="100%" height="280" viewBox="0 0 100 100" style="max-width:300px; margin:0 auto; display:block;">
            <line x1="0" y1="0" x2="100" y2="0" stroke="rgba(255,241,118 ,0.05)" stroke-width="200" />
            
            {shadow_lines}

            <circle cx="{sun_x}" cy="{sun_y}" r="6" fill="#F39C12" />
            <circle cx="{sun_x}" cy="{sun_y}" r="9" fill="#F1C40F" opacity="0.15" />
            <text x="{sun_x}" y="{sun_y-8}" fill="#F1C40F" font-size="3" font-weight="bold" text-anchor="middle">SUN</text>

            <circle cx="{orbit_center_x}" cy="{orbit_center_y}" r="{orbit_radius}" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="0.4" stroke-dasharray="1" />

            <circle cx="{earth_x}" cy="{earth_y}" r="5" fill="#3498DB" />
            <path d="M {earth_x-5} {earth_y} A 5 5 0 0 0 {earth_x+5} {earth_y} Z" fill="#0B1017" opacity="0.9" />
            <text x="{earth_x}" y="{earth_y+9}" fill="#3498DB" font-size="3" font-weight="bold" text-anchor="middle">EARTH</text>

            <line x1="{earth_x}" y1="{earth_y}" x2="{pointer_x}" y2="{pointer_y}" stroke="#2ECC71" stroke-width="0.7" marker-end="url(#arrow-head)" />
            <circle cx="{pointer_x}" cy="{pointer_y}" r="0.6" fill="#2ECC71" />

            <circle cx="{obj_x}" cy="{obj_y}" r="3" fill="{target_color}" />
            <path d="M {obj_x-3} {obj_y} A 3 3 0 0 0 {obj_x+3} {obj_y} Z" fill="#0B1017" opacity="0.7" transform="rotate(180 {obj_x} {obj_y})" />
            <text x="{obj_x}" y="{obj_y-4}" fill="{target_color}" font-size="2.5" font-weight="bold" text-anchor="middle">{label_text}</text>

            <defs>
                <marker id="arrow-head" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#2ECC71"/>
                </marker>
            </defs>
        </svg>
        <div style="text-align: center; font-size: 0.8rem; color: #2ECC71; font-weight: 600; margin-top: 10px;">
            💚 초록색 지표선 방향 = 현재 시간의 지구 관측자 시야 방향 (남중 방향)
        </div>
    </div>
    """
    components.html(orbit_html, height=330)

# 6. 하단 지구과학 교과 개념 요약 카드 (업로드 자료 매핑)
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.subheader("📘 지구과학I 천체 파트 교과 원리 매칭")

if "일식과 월식" in target_mode:
    st.markdown("""
    * **일식 원리:** 달이 **삭(태양-달-지구)** 위치에 오고 천구상 시직경이 일치할 때 달의 본그림자 영역에서 개기일식이 일어납니다.
    * **월식 원리:** 달이 **망(태양-지구-달)** 위치에서 지구 본그림자에 완전히 들어가면 개기월식이 일어납니다. 이때 태양빛이 지구 대기를 통과하며 붉은 파장의 빛이 굴절되어 달에 도달하기 때문에 **붉은 달(Blood Moon)**로 관측됩니다.
    """)
elif "내행성" in target_mode:
    st.markdown("""
    * **이각과 내합/외합:** 내행성(금성)은 지구보다 공전 속도가 빠르며, 태양 기준 안쪽에서 공전하므로 최대 이각 범위 내에서만 움직입니다. 
    * **위상 및 시직경:** 지구와 가장 가까운 **내합** 근처에서는 역행이 나타나고 시직경이 커지며 초승달/그믐달 위상을 띱니다. 가장 먼 **외합** 근처에서는 시직경이 작고 보름달에 가까운 위상 관계로 관측됩니다.
    """)
else:
    st.markdown("""
    * **외행성의 위치 관계:** 외행성(화성)은 이각이 $0^\circ \sim 180^\circ$까지 다양하게 나타나며, 태양의 정반대편에 위치하는 **충(Opposition)** 지역에 도달할 때 지구와 가장 가까워져 역행을 일으키고 밤새도록 한밤중에 관측이 가능해집니다.
    """)
st.markdown('</div>', unsafe_allow_html=True)
