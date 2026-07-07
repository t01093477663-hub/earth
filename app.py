import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 페이지 설정 및 가독성 높은 다크 CSS 디자인
# ==========================================
st.set_page_config(page_title="우주 천체 관측 시뮬레이터", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경을 깊은 블랙으로 설정하고 모든 기본 글씨를 완전한 흰색으로 강제 */
    .stApp {
        background-color: #06080c;
        color: #FFFFFF !important;
    }
    /* 사이드바 스타일 정의 */
    [data-testid="stSidebar"] {
        background-color: #111622;
        border-right: 1px solid #2D3748;
    }
    /* 사이드바 안의 일반 텍스트들도 전부 완전한 흰색으로 변경 */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    /* 제목 및 헤더 스타일: 선명한 네온 블루 */
    h1, h2, h3, h4 {
        color: #4FD1C5 !important;
        font-weight: 700;
    }
    /* 하단 가이드 카드 디자인: 가독성을 위해 밝은 네이비 배경에 흰색 글씨 */
    .metric-card {
        background-color: #171E2E;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #63B3ED;
        margin-bottom: 15px;
    }
    .metric-card h4 {
        color: #63B3ED !important;
        margin-top: 0;
    }
    .metric-card p {
        color: #F8FAFC !important;
        font-size: 14px;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌌 천체 위치 및 위상 시뮬레이터")
st.caption("날짜와 시간을 슬라이더로 조절하며 행성의 위치 관계와 밤하늘 위상을 확인하세요.")

# ==========================================
# 2. 사이드바 제어판 (슬라이더 방식 적용)
# ==========================================
st.sidebar.header("⏰ 관측 설정")

# 날짜 선택
obs_date = st.sidebar.date_input("관측 날짜 선택", datetime.date.today())

# 시간 선택 (편리한 슬라이더 인터페이스)
st.sidebar.markdown("🕒 **관측 시간 선택**")
time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]
selected_time_str = st.sidebar.select_slider(
    "슬라이더를 좌우로 드래그하여 시간을 조절하세요.",
    options=time_slots,
    value="22:00"  # 기본값 밤 10시
)

# 방위 선택
direction = st.sidebar.selectbox("바라볼 방향 (방위)", ["남 (South)", "동 (East)", "서 (West)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("🪐 **천체 표시 필터**")
show_moon = st.sidebar.checkbox("달 (Moon) 표시", value=True)
show_inner = st.sidebar.checkbox("내행성 (금성) 표시", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성) 표시", value=True)

# 시뮬레이션 계산용 시간 변환
hour, minute = map(int, selected_time_str.split(":"))
total_hours = hour + (minute / 60.0)
days = (obs_date - datetime.date(2026, 1, 1)).days + (total_hours / 24.0)


# ==========================================
# 3. 그래프 시각화 (서버에서 절대 안 깨지는 100% 영문 구조)
# ==========================================

# [1] 태양계 위치 관계 그래프
def plot_solar_system():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 태양 (Sun)
    ax.plot(0, 0, 'oy', markersize=16, label='Sun', color='#FFD700')
    
    # 지구 (Earth)
    earth_angle = days * (2 * np.pi / 365)
    ex, ey = np.cos(earth_angle) * 3, np.sin(earth_angle) * 3
    ax.plot(ex, ey, 'ob', markersize=9, label='Earth', color='#4169E1')
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 3, np.sin(np.linspace(0, 2*np.pi, 100)) * 3, '--', color='#2D3748', alpha=0.4)
    
    # 달 (Moon)
    if show_moon:
        moon_angle = days * (2 * np.pi / 29.5)
        mx, my = ex + np.cos(moon_angle) * 0.5, ey + np.sin(moon_angle) * 0.5
        ax.plot(mx, my, 'o', markersize=4, label='Moon', color='#F5F5F5')
    
    # 내행성 (Venus)
    if show_inner:
        v_angle = days * (2 * np.pi / 225)
        vx, vy = np.cos(v_angle) * 1.8, np.sin(v_angle) * 1.8
        ax.plot(vx, vy, 'o', markersize=7, label='Venus', color='#E6C229')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 1.8, np.sin(np.linspace(0, 2*np.pi, 100)) * 1.8, '--', color='#2D3748', alpha=0.4)

    # 외행성 (Mars)
    if show_outer:
        m_angle = days * (2 * np.pi / 687)
        mar_x, mar_y = np.cos(m_angle) * 4.5, np.sin(m_angle) * 4.5
        ax.plot(mar_x, mar_y, 'o', markersize=8, label='Mars', color='#D14949')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 4.5, np.sin(np.linspace(0, 2*np.pi, 100)) * 4.5, '--', color='#2D3748', alpha=0.4)
        
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.axis('off')
    
    # 범례 설정 (이모지를 지우고 깔끔하게 영문으로만 표기하여 에러 차단)
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=12)
    return fig

# [2] 밤하늘 방위별 시야 그래프
def plot_sky_view(dir_setting):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 지평선 구조선 및 지면 배치
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color='#11141D')
    
    # 텍스트 공통 스타일 지정 (글자색은 완전한 흰색)
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 14, 'fontweight': 'bold'}
    
    # 깨질 수 있는 특수 기호 대신 점(marker)과 영문자로만 오브젝트 배치
    if "남" in dir_setting:
        ax.plot(0, 2, 'o', color='#F5F5F5', markersize=20) # 달 표시 대체
        ax.text(0, 1.3, "Moon", **text_style)
        if show_outer:
            ax.plot(2.5, 1.8, 'o', color='#D14949', markersize=12) # 화성 표시 대체
            ax.text(2.5, 1.3, "Mars", **text_style)
    elif "동" in dir_setting:
        ax.plot(3, 1.5, 'o', color='#DEB887', markersize=16) # 목성 표시 대체
        ax.text(3, 0.9, "Jupiter (Rising)", **text_style)
    elif "서" in dir_setting:
        if show_inner:
            ax.plot(-3, 1.2, '*', color='#FFD700', markersize=15) # 금성 표시 대체
            ax.text(-3, 0.6, "Venus (Setting)", **text_style)
    elif "북" in dir_setting:
        ax.plot(0, 2.5, '*', color='#63B3ED', markersize=12) # 북극성 표시 대체
        ax.text(0, 1.9, "Polaris", color='#63B3ED', ha='center', fontsize=14, fontweight='bold')
        
    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.5, 4)
    ax.axis('off')
    return fig


# ==========================================
# 4. 웹 화면 레이아웃 배치 영역
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("☀️ 태양계 행성 위치 관계 (Top-down View)")
    fig_solar = plot_solar_system()
    st.pyplot(fig_solar)

with col2:
    st.subheader(f"🔭 {direction} 밤하늘 관측 시야 (Horizon View)")
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)


# ==========================================
# 5. 하단 텍스트 설명 카드 (선명한 흰색 가독성)
# ==========================================
st.markdown("---")
st.subheader("🪐 천체별 관측 특징 요약")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🌙 위성: 달 (Moon)</h4>
        <p>지구 주위를 약 29.5일 주기로 공전하며, 태양-지구-달의 궤도 상 위치 관계에 따라 보름달, 반달, 초승달 등 위상(모양)이 매일 변화합니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>✨ 내행성 (수성 · 금성)</h4>
        <p>지구 안쪽 궤도를 도는 행성들입니다. 밤중에 하늘 한가운데 뜰 수 없으며, 주로 초저녁 서쪽 하늘(Setting)이나 새벽녘 동쪽 하늘에서만 반짝이며 관측됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🔴 외행성 (화성 · 목성 · 토성)</h4>
        <p>지구 바깥쪽 궤도를 도는 행성들입니다. 한밤중에도 남쪽 하늘 높이 떠오를 수 있으며, 지구와 일직선상에 가까워질수록 훨씬 밝고 크게 관측됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
