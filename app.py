import streamlit as st
import numpy as np

# 1. 페이지 기본 설정 및 고급 다크모드 디자인 (Custom CSS)
st.set_page_config(page_title="SkyWatcher Pro: 천체 시뮬레이터", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #0E1117;
    }
    
    /* 관측창(Sky View) 스타일 */
    .sky-container {
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        min-height: 380px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
    }
    
    /* 대시보드 카드 스타일 */
    .info-card {
        background: rgba(255, 255, 255, 0.04);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 16px;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #8bc34a 0%, #00a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 10px;
    }
    
    /* 텍스트 다이어그램 박스 */
    .diagram-box {
        background: rgba(0, 0, 0, 0.3);
        border: 1px dashed rgba(255, 255, 255, 0.2);
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
        white-space: pre;
        color: #00f2fe;
        font-size: 0.9rem;
        line-height: 1.4;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 컨트롤러 (편리한 시간 및 관측 설정)
st.sidebar.title("🔭 천체 관측 제어 패널")
st.sidebar.markdown("---")

# 관측 대상 설정
target = st.sidebar.selectbox("1. 관측 대상 선택", ["달 (The Moon)", "금성 (Venus, 내행성)", "화성 (Mars, 외행성)"])

# 00시 ~ 24시 직관적인 시간 선택 슬라이더 (숫자 변환 처리)
selected_hour = st.sidebar.slider(
    "2. 관측 시간 설정 (00시 ~ 24시)",
    min_value=0,
    max_value=24,
    value=22,
    step=1,
    format="%d:00"
)

# 방위 선택
direction = st.sidebar.radio("3. 바라보는 방위", ["동 (East)", "남 (South)", "서 (West)", "북 (North)"], index=1)

# 3. 시간 변환에 따른 천문학적 위상 및 위치 자동 계산 알고리즘
time_progress = (selected_hour / 24.0) * 2 * np.pi  # 시간에 따른 일주 각도

if target.startswith("달"):
    calculated_angle = (7 / 28) * 2 * np.pi + (time_progress * 0.1)
    badge_text = "위상 변동 주기: 약 29.5일"
    badge_bg = "rgba(244, 208, 63, 0.2)"
    badge_color = "#F4D03F"
elif target.startswith("금성"):
    calculated_angle = np.sin(time_progress) * (np.pi / 4) 
    badge_text = "내행성 특징: 최대 이각 존재 (자정 관측 불가)"
    badge_bg = "rgba(0, 168, 255, 0.2)"
    badge_color = "#00a8ff"
else:
    calculated_angle = time_progress + np.pi
    badge_text = "외행성 특징: 역행 가능 및 자정 남중 가능"
    badge_bg = "rgba(231, 76, 60, 0.2)"
    badge_color = "#E74C3C"

# 4. 메인 화면 레이아웃
st.markdown('<p class="main-header">SkyWatcher 천체 관측 웹앱</p>', unsafe_allow_html=True)
st.markdown(f'<span class="status-badge" style="background: {badge_bg}; color: {badge_color};">{badge_text}</span>', unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# 시간대별 24시간 실시간 하늘 배경 그래픽 처리
if 6 <= selected_hour < 11:
    current_sky = "linear-gradient(180deg, #74ebd5 0%, #ACB6E5 100%)" 
    is_visible = False if target.startswith("화성") else True
    sky_status = "☀️ 낮 시간대로 태양빛에 의해 관측이 어렵습니다."
elif 11 <= selected_hour < 17:
    current_sky = "linear-gradient(180deg, #4facfe 0%, #00f2fe 100%)" 
    is_visible = False
    sky_status = "☀️ 태양이 중천에 떠 있어 천체가 가려집니다."
elif 17 <= selected_hour < 20:
    current_sky = "linear-gradient(180deg, #ff9a9e 0%, #fecfef 99%, #feada6 100%)" 
    is_visible = True
    sky_status = "🌅 개기일몰 및 초저녁 관측 가능 시간대입니다."
else:
    current_sky = "linear-gradient(180deg, #050505 0%, #111122 100%)" 
    is_visible = False if target.startswith("금성") and (20 <= selected_hour or selected_hour <= 2) else True
    sky_status = "🌌 밤하늘 상태로 우수한 천체 관측 환경입니다."

# 5. 그래픽 인터페이스 렌더링 영역
with col1:
    def generate_celestial_svg():
        ratio = np.cos(calculated_angle)
        color = "#F4D03F" if target.startswith("달") else ("#E67E22" if target.startswith("금성") else "#E74C3C")
        rx_val = abs(ratio) * 45
        ell_color = '#2c3e50' if ratio < 0 else color
        
        if not is_visible:
            return '<circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4" /><text x="50" y="55" fill="rgba(255,255,255,0.4)" font-size="10" text-anchor="middle">지평선 아래</text>'
            
        return f"""
        <circle cx="50" cy="50" r="45" fill="#2c3e50" />
        <path d="M 50 5 A 45 45 0 0 1 50 95" fill="{color}" />
        <ellipse cx="50" cy="50" rx="{rx_val}" ry="45" fill="{ell_color}" />
        """

    sky_html = f"""
    <div class="sky-container" style="background: {current_sky};">
        <div style="font-size: 1.4rem; color: white; font-weight: 600; margin-bottom: 20px;">
            {selected_hour:02d}:00 | {direction}쪽 하늘 관측 시야
        </div>
        <div style="margin: 40px auto; width: 120px; height: 120px;">
            <svg width="120" height="120" viewBox="0 0 100 100">
                {generate_celestial_svg()}
            </svg>
        </div>
        <div style="color: white; font-size: 1.05rem; background: rgba(0,0,0,0.4); display: inline-block; padding: 8px 16px; border-radius: 8px;">
            {sky_status}
        </div>
    </div>
    """
    st.markdown(sky_html, unsafe_allow_html=True)

# 6. 우측 요약 대시보드 및 구조 가이드 (에러 원인 st.image를 텍스트 구조도로 변경)
with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("🪐 공간적 기하 관계 이해")
    st.write("태양-지구-천체의 공전 궤도상 위치 관계를 직관적으로 나타낸 배치도입니다.")
    
    # 🚨 에러가 발생하던 st.image 대신 안정적인 마크다운 텍스트 다이어그램 배치
    if target.startswith("금성"):
        st.write("**[내행성 위치 관계도]**")
        st.markdown("""
        <div class="diagram-box">
(외합) ── 금성 (태양 반대편)
   │
☀️ 태양
   │
(내합) ── 금성 (지구와 가까움)
   │
🌍 지구 (관측자 시점)
        </div>
        """, unsafe_allow_html=True)
        st.caption("태양 중심 금성의 기하학적 배치도 (내합/외합)")
    elif target.startswith("화성"):
        st.write("**[외행성 위치 관계도]**")
        st.markdown("""
        <div class="diagram-box">
🪐 화성 (합 - 태양 뒤편)
   │
☀️ 태양
   │
🌍 지구 (관측자 시점)
   │
🪐 화성 (충 - 지구와 최고 인접)
        </div>
        """, unsafe_allow_html=True)
        st.caption("태양 중심 외행성 기하학적 배치도 (충/합)")
    else:
        st.write("**[태양-지구-달 위상 관계도]**")
        st.markdown("""
        <div class="diagram-box">
       🌙 상현달 (지구 위쪽)
              │
☀️ 태양 ─── 🌍 지구 ─── 🌕 망 (보름달)
              │
       🌙 하현달 (지구 아래쪽)
        </div>
        """, unsafe_allow_html=True)
        st.caption("달의 공전 위치별 위상 관계 가이드")
        
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("📊 실시간 데이터 요약")
    st.write(f"• **현재 시각:** {selected_hour:02d}:00 시각 적용")
    st.write(f"• **관측 고도 상태:** {'관측 가능 범위 내' if is_visible else '관측 불가능 (지평선 아래 또는 태양빛 간섭)'}")
    st.markdown('</div>', unsafe_allow_html=True)

# 7. 하단 개념 탐구 탭
st.markdown("---")
st.markdown("### 📚 천체별 핵심 특징 돋보기")
tabs = st.tabs(["달의 위상 특징", "내행성의 관측 특징", "외행성의 관측 특징"])
with tabs[0]:
    st.markdown("""
    - **시간에 따른 변화:** 달은 서쪽에서 동쪽으로 공전하므로 매일 같은 시간에 관측하면 위치가 동쪽으로 이동해 있습니다.
    - **지평선 연동:** 상현달은 오후 6시 무렵 남쪽 하늘에 오고, 보름달은 한밤중인 24시에 남쪽 하늘에 위치합니다.
    """)
with tabs[1]:
    st.markdown("""
    - **금성의 특징:** 금성은 지구보다 안쪽 궤도를 돌기 때문에 태양과 항상 가까이 붙어 다닙니다.
    - **자정 관측 불가 원인:** 태양이 지구 반대편을 비추는 한밤중(22시~02시)에는 금성이 지구 그림자나 지평선 아래에 무조건 숨게 되므로 관측할 수 없습니다. 위 코드는 이 원리가 정확히 시뮬레이션되어 22시 설정 시 지평선 아래로 사라집니다.
    """)
with tabs[2]:
    st.markdown("""
    - **화성의 특징:** 화성은 지구 바깥쪽을 돌기 때문에 태양-지구-화성이 일직선이 되는 **'충'** 위치에 올 수 있습니다.
    - **한밤중 관측 가능:** '충'일 때는 태양이 질 때(18시) 동쪽에서 떠올라 한밤중(24시)에 남쪽 하늘 가장 높은 곳에 도달하므로 자정에도 아주 잘 보입니다.
    """)
