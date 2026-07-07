import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 페이지 기본 설정 및 고대비(High Contrast) CSS 디자인
# ==========================================
st.set_page_config(page_title="우주 천체 관측 시뮬레이터", layout="wide")

st.markdown("""
    <style>
    /* 배경은 깊은 블랙, 기본 글씨는 완전한 흰색으로 변경하여 가독성 극대화 */
    .stApp {
        background-color: #06080c;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #111622;
        border-right: 1px solid #2D3748;
    }
    /* 사이드바 글씨 색상 흰색으로 강조 */
    [data-testid="stSidebar"] .stMarkdown p {
        color: #FFFFFF !important;
    }
    /* 헤더 스타일: 밝고 선명한 네온 블루 */
    h1, h2, h3, h4 {
        color: #4FD1C5 !important;
        font-weight: 700;
    }
    /* 하단 카드 디자인: 글씨가 잘 보이도록 배경을 조금 더 밝게, 텍스트는 흰색 */
    .metric-card {
        background-color: #171E2E;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #63B3ED;
        margin-bottom: 15px;
        color: #FFFFFF !important;
    }
    .metric-card p {
        color: #E2E8F0 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌌 천체 위치 및 위상 시뮬레이터")
st.caption("날짜와 시간을 슬라이더로 조절하며 행성의 위치 관계와 밤하늘 위상을 확인하세요.")

# ==========================================
# 사이드바 제어판
# ==========================================
st.sidebar.header("⏰ 관측 설정")

# 날짜 선택
obs_date = st.sidebar.date_input("관측 날짜 선택", datetime.date.today())

# 시간 선택 (슬라이더 방식)
st.sidebar.markdown("📂 **관측 시간 선택**")
time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]
selected_time_str = st.sidebar.select_slider(
    "시간 슬라이더를 움직여보세요",
    options=time_slots,
    value="22:00"
)

# 방위 선택
direction = st.sidebar.selectbox("바라볼 방향 (방위)", ["남 (South)", "동 (East)", "서 (West)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("📂 **천체 표시 필터**")
show_moon = st.sidebar.checkbox("달 (Moon) 표시", value=True)
show_inner = st.sidebar.checkbox("내행성 (수성, 금성) 표시", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성, 목성) 표시", value=True)

# 시간 계산 로직
hour, minute = map(int, selected_time_str.split(":"))
total_hours = hour + (minute / 60.0)
days = (obs_date - datetime.date(2026, 1, 1)).days + (total_hours / 24.0)


# ==========================================
# 시각화 그래프 생성 함수 (영문+이모지 조합으로 깨짐 100% 방지)
# ==========================================

# 1. 태양계 궤도 위치 관계 그래프
def plot_solar_system():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 태양 (중심)
    ax.plot(0, 0, 'oy', markersize=16, label='Sun ☀️', color='#FFD700')
    
    # 지구
    earth_angle = days * (2 * np.pi / 365)
    ex, ey = np.cos(earth_angle) * 3, np.sin(earth_angle) * 3
    ax.plot(ex, ey, 'ob', markersize=9, label='Earth 🌍', color='#4169E1')
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 3, np.sin(np.linspace(0, 2*np.pi, 100)) * 3, '--', color='#2D3748', alpha=0.4)
    
    # 달 (지구 주위)
    if show_moon:
        moon_angle = days * (2 * np.pi / 29.5)
        mx, my = ex + np.cos(moon_angle) * 0.5, ey + np.sin(moon_angle) * 0.5
        ax.plot(mx, my, 'o', markersize=4, label='Moon 🌙', color='#F5F5F5')
    
    # 내행성 (금성)
    if show_inner:
        v_angle = days * (2 * np.pi / 225)
        vx, vy = np.cos(v_angle) * 1.8, np.sin(v_angle) * 1.8
        ax.plot(vx, vy, 'o', markersize=7, label='Venus ✨', color='#E6C229')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 1.8, np.sin(np.linspace(0, 2*np.pi, 100)) * 1.8, '--', color='#2D3748', alpha=0.4)

    # 외행성 (화성)
    if show_outer:
        m_angle = days * (2 * np.pi / 687)
        mar_x, mar_y = np.cos(m_angle) * 4.5, np.sin(m_angle) * 4.5
        ax.plot(mar_x, mar_y, 'o', markersize=8, label='Mars 🔴', color='#D14949')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 4.5, np.sin(np.linspace(0, 2*np.pi, 100)) * 4.5, '--', color='#2D3748', alpha=0.4)
        
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.axis('off')
    
    # 범례 글씨를 깨지지 않는 영문+이모지로만 표기하고 색상을 흰색으로 지정
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=11)
        
    return fig

# 2. 지평선 방위별 밤하늘 위상 그래프
def plot_sky_view(dir_setting):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 지평선과 땅 표현
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color='#11141D')
    
    # 이모지는 폰트 설정과 상관없이 리눅스 엔진에서도 깨지지 않고 잘 나옵니다.
    if "남" in dir_setting:
        ax.text(0, 2, "🌙", fontsize=35, ha='center', va='center')
        ax.text(0, 1.2, "Moon", color='#FFFFFF', ha='center', fontsize=12, fontweight='bold')
        if show_outer:
            ax.text(2.5, 1.8, "🔴", fontsize=18, ha='center', va='center')
            ax.text(2.5, 1.2, "Mars", color='#FFFFFF', ha='center', fontsize=12, fontweight='bold')
    elif "동" in dir_setting:
        ax.text(3, 1.5, "🪐", fontsize=32, ha='center', va='center')
        ax.text(3, 0.9, "Jupiter (Rising)", color='#FFFFFF', ha='center', fontsize=12, fontweight='bold')
    elif "서" in dir_setting:
        if show_inner:
            ax.text(-3, 1.2, "✨", fontsize=28, ha='center', va='center', color='#FFD700')
            ax.text(-3, 0.6, "Venus (Setting)", color='#FFFFFF', ha='center', fontsize=12, fontweight='bold')
    elif "북" in dir_setting:
        ax.text(0, 2.5, "⭐", fontsize=24, ha='center', va='center', color='#63B3ED')
        ax.text(0, 2.0, "Polaris", color='#63B3ED', ha='center', fontsize=12, fontweight='bold')
        
    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.5, 4)
    ax.axis('off')
    return fig


# ==========================================
# 대시보드 화면 레이아웃 분할 배치
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
# 하단 행성 특징 가이드 디자인 (한글 가독성 강화)
# ==========================================
st.markdown("---")
st.subheader("🪐 천체별 관측 특징 요약")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🌙 위성: 달 (Moon)</h4>
        <p>지구 주위를 약 29.5일 주기로 공전하며, 위치 관계에 따라 위상(모양)이 계속해서 변화합니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>✨ 내행성 (수성 · 금성)</h4>
        <p>지구 안쪽 궤도를 돌기 때문에 한밤중에는 볼 수 없고, 주로 초저녁 서쪽이나 새벽녘 동쪽 하늘에서만 보입니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🔴 외행성 (화성 · 목성 · 토성)</h4>
        <p>지구 바깥쪽 궤도를 돌며, 지구-태양-행성이 일직선이 되는 '충'의 위치일 때 밤새도록 가장 밝게 빛납니다.</p>
    </div>
    """, unsafe_allow_html=True)
