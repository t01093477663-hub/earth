import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 페이지 설정 및 고대비 다크 CSS 디자인
# ==========================================
st.set_page_config(page_title="우주 천체 관측 시뮬레이터", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #06080c;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111622;
        border-right: 1px solid #2D3748;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    h1, h2, h3, h4 {
        color: #4FD1C5 !important;
        font-weight: 700;
    }
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
# 2. 사이드바 제어판
# ==========================================
st.sidebar.header("⏰ 관측 설정")

# 날짜 선택
obs_date = st.sidebar.date_input("관측 날짜 선택", datetime.date.today())

# 시간 선택 (슬라이더 방식)
st.sidebar.markdown("🕒 **관측 시간 선택**")
time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]
selected_time_str = st.sidebar.select_slider(
    "슬라이더를 좌우로 드래그하면 행성들이 실시간으로 회전합니다.",
    options=time_slots,
    value="22:00"
)

# 방위 선택
direction = st.sidebar.selectbox("바라볼 방향 (방위)", ["남 (South)", "동 (East)", "서 (West)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("🪐 **천체 표시 필터**")
show_moon = st.sidebar.checkbox("달 (Moon) 표시", value=True)
show_inner = st.sidebar.checkbox("내행성 (금성) 표시", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성) 표시", value=True)

# 💡 [핵심 수정] 시간 변화를 눈으로 볼 수 있도록 가중치 기반 시뮬레이션 타임라인 계산
# 기본 날짜값에 '선택한 시간 인덱스'를 크게 반영하여 실시간 움직임을 연출합니다.
base_days = (obs_date - datetime.date(2026, 1, 1)).days
time_index = time_slots.index(selected_time_str)

# 날짜에 의한 위치 + 시간에 따른 궤도 회전 속도 가중치 부여
sim_time_earth = base_days + (time_index * 1.5)
sim_time_venus = base_days + (time_index * 2.5)
sim_time_mars = base_days + (time_index * 0.8)
sim_time_moon = base_days + (time_index * 5.0) # 달은 지구 주변을 빠르게 돌도록 설정


# ==========================================
# 3. 그래프 시각화 (100% 영문 구조)
# ==========================================

# [1] 태양계 위치 관계 그래프
def plot_solar_system():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 태양 (Sun)
    ax.plot(0, 0, 'oy', markersize=16, label='Sun', color='#FFD700')
    
    # 지구 (Earth)
    earth_angle = sim_time_earth * (2 * np.pi / 365)
    ex, ey = np.cos(earth_angle) * 3, np.sin(earth_angle) * 3
    ax.plot(ex, ey, 'ob', markersize=9, label='Earth', color='#4169E1')
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 3, np.sin(np.linspace(0, 2*np.pi, 100)) * 3, '--', color='#2D3748', alpha=0.4)
    
    # 달 (Moon) - 지구를 중심으로 공전
    if show_moon:
        moon_angle = sim_time_moon * (2 * np.pi / 29.5)
        mx, my = ex + np.cos(moon_angle) * 0.5, ey + np.sin(moon_angle) * 0.5
        ax.plot(mx, my, 'o', markersize=4, label='Moon', color='#F5F5F5')
    
    # 내행성 (Venus)
    if show_inner:
        v_angle = sim_time_venus * (2 * np.pi / 225)
        vx, vy = np.cos(v_angle) * 1.8, np.sin(v_angle) * 1.8
        ax.plot(vx, vy, 'o', markersize=7, label='Venus', color='#E6C229')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 1.8, np.sin(np.linspace(0, 2*np.pi, 100)) * 1.8, '--', color='#2D3748', alpha=0.4)

    # 외행성 (Mars)
    if show_outer:
        m_angle = sim_time_mars * (2 * np.pi / 687)
        mar_x, mar_y = np.cos(m_angle) * 4.5, np.sin(m_angle) * 4.5
        ax.plot(mar_x, mar_y, 'o', markersize=8, label='Mars', color='#D14949')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 4.5, np.sin(np.linspace(0, 2*np.pi, 100)) * 4.5, '--', color='#2D3748', alpha=0.4)
        
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.axis('off')
    
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=12)
    return fig

# [2] 밤하늘 방위별 시야 그래프 (시간 슬라이더에 따라 천체 고도 이동)
def plot_sky_view(dir_setting):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 지평선 구조선 및 지면
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color='#11141D')
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 14, 'fontweight': 'bold'}
    
    # 💡 슬라이더 값(time_index)에 따라 천체가 동에서 서로 움직이도록 위치 좌표에 애니메이션 효과 반영
    # 시간 인덱스는 0부터 47까지 변하므로 이를 변위로 활용합니다.
    shift = (time_index - 24) * 0.15 
    
    if "남" in dir_setting:
        # 시간이 흐를수록 남쪽 하늘의 달과 화성이 서쪽(왼쪽)으로 이동
        ax.plot(0 - shift, 2.2, 'o', color='#F5F5F5', markersize=20)
        ax.text(0 - shift, 1.5, "Moon", **text_style)
        if show_outer:
            ax.plot(2.5 - shift, 1.8, 'o', color='#D14949', markersize=12)
            ax.text(2.5 - shift, 1.3, "Mars", **text_style)
            
    elif "동" in dir_setting:
        # 시간이 흐를수록 새로운 행성(목성)이 지평선 아래에서 위로 떠오름
        height = 0.2 + (time_index * 0.05)
        ax.plot(2, height, 'o', color='#DEB887', markersize=16)
        ax.text(2, height - 0.5, "Jupiter", **text_style)
        
    elif "서" in dir_setting:
        # 시간이 흐를수록 금성이 지평선 아래로 가라앉음
        height = 3.0 - (time_index * 0.06)
        if show_inner and height > 0:
            ax.plot(-2, height, '*', color='#FFD700', markersize=15)
            ax.text(-2, height - 0.5, "Venus", **text_style)
            
    elif "북" in dir_setting:
        # 북극성은 고정되어 있고 주위 주극성들이 회전하는 연출
        ax.plot(0, 2.5, '*', color='#63B3ED', markersize=12)
        ax.text(0, 1.9, "Polaris", color='#63B3ED', ha='center', fontsize=14, fontweight='bold')
        
        # 북두칠성 대용 지표성 회전 연출
        rot_angle = time_index * (2 * np.pi / 48)
        rx, ry = np.cos(rot_angle) * 1.5, 2.5 + np.sin(rot_angle) * 1.5
        ax.plot(rx, ry, 'o', color='#FFFFFF', markersize=5)
        ax.text(rx, ry - 0.3, "Star", color='#A0AEC0', ha='center', fontsize=10)
        
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
# 5. 하단 텍스트 설명 카드
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
