import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 기본 설정 및 디자인 (CSS 커스텀)
st.set_page_config(page_title="우주 천체 관측 시뮬레이터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* 전체 배경을 우주 느낌의 깊은 네이비/블랙으로 설정 */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #1A202C;
        border-right: 1px solid #2D3748;
    }
    /* 타이틀 및 헤더 디자인 */
    h1, h2, h3 {
        color: #63B3ED !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* 카드 스타일 메트릭 */
    .metric-card {
        background-color: #2D3748;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4FD1C5;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 타이틀
st.title("🌌 천체 위치 및 위상 시뮬레이터")
st.caption("날짜와 시간에 따른 지구에서의 밤하늘 관측 및 태양계 행성 위치 관계")

# --- 사이드바 제어판 ---
st.sidebar.header("⏰ 관측 설정")
obs_date = st.sidebar.date_input("관측 날짜 선택", datetime.date.today())
obs_time = st.sidebar.time_input("관측 시간 선택", datetime.time(22, 00)) # 기본 밤 10시
direction = st.sidebar.selectbox("바라볼 방향 (방위)", ["동 (East)", "서 (West)", "남 (South)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🪐 행성 표시 설정")
show_inner = st.sidebar.checkbox("내행성 (수성, 금성) 보기", value=True)
show_moon = st.sidebar.checkbox("달 (Moon) 보기", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성, 목성, 토성) 보기", value=True)


# --- 데이터 계산 및 시각화 로직 (예시용 간이 오빗 계산) ---
# 실제 정밀 계산을 위해서는 astropy나 ephem 라이브러리를 연동하면 좋습니다.
# 여기서는 입력 시간에 비례해 움직이는 가상의 궤도를 생성합니다.
days = (obs_date - datetime.date(2026, 1, 1)).days + (obs_time.hour / 24.0)

# 태양계 위치 관계 그래프 생성 함수
def plot_solar_system():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#0B0E14')
    ax.set_facecolor('#0B0E14')
    
    # 태양 (중심)
    ax.plot(0, 0, 'oy', markersize=15, label='Sun (태양)', color='#FFD700')
    
    # 지구 (기준)
    earth_angle = days * (2 * np.pi / 365)
    ex, ey = np.cos(earth_angle)*3, np.sin(earth_angle)*3
    ax.plot(ex, ey, 'ob', markersize=8, label='Earth (지구)', color='#4169E1')
    ax.plot(np.cos(np.linspace(0,2*np.pi,100))*3, np.sin(np.linspace(0,2*np.pi,100))*3, '--', color='#2D3748', alpha=0.5)
    
    # 달 (지구 주변)
    if show_moon:
        moon_angle = days * (2 * np.pi / 29.5)
        mx, my = ex + np.cos(moon_angle)*0.4, ey + np.sin(moon_angle)*0.4
        ax.plot(mx, my, 'o', markersize=4, label='Moon (달)', color='#F5F5F5')
    
    # 내행성 (금성 예시)
    if show_inner:
        v_angle = days * (2 * np.pi / 225)
        vx, vy = np.cos(v_angle)*1.8, np.sin(v_angle)*1.8
        ax.plot(vx, vy, 'o', markersize=6, label='Venus (내행성:금성)', color='#E6C229')
        ax.plot(np.cos(np.linspace(0,2*np.pi,100))*1.8, np.sin(np.linspace(0,2*np.pi,100))*1.8, '--', color='#2D3748', alpha=0.5)

    # 외행성 (화성 예시)
    if show_outer:
        m_angle = days * (2 * np.pi / 687)
        mar_x, mar_y = np.cos(m_angle)*4.5, np.sin(m_angle)*4.5
        ax.plot(mar_x, mar_y, 'o', markersize=7, label='Mars (외행성:화성)', color='#D14949')
        ax.plot(np.cos(np.linspace(0,2*np.pi,100))*4.5, np.sin(np.linspace(0,2*np.pi,100))*4.5, '--', color='#2D3748', alpha=0.5)
        
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.axis('off')
    ax.legend(loc='upper right', facecolor='#1A202C', edgecolor='#2D3748', labelcolor='white')
    return fig

# 밤하늘 방위별 위상 그래프 생성 함수
def plot_sky_view(direction):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#0B0E14')
    ax.set_facecolor('#0B0E14')
    
    # 지평선 테두리
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color='#1A202C')
    
    # 시간에 따른 천체들의 고도/방위 임의 계산 (디자인 데모용)
    time_factor = (obs_time.hour + obs_time.minute/60.0) / 24.0
    
    # 방위에 따라 보이는 천체 다르게 연출
    if "남" in direction:
        # 남쪽 하늘에는 달과 행성들이 자주 지나감
        ax.text(0, 2, "🌙", fontsize=30, ha='center', va='center', color='#FFF')
        ax.text(0, 1.4, "달 (Moon)", color='#FFF', ha='center')
        if show_outer:
            ax.text(2, 1.5, "🔴", fontsize=15, ha='center', va='center')
            ax.text(2, 1.1, "화성", color='#FFF', ha='center')
    elif "동" in direction:
        # 동쪽은 떠오르는 천체들
        ax.text(3, 1, "🪐", fontsize=25, ha='center', va='center')
        ax.text(3, 0.7, "목성 (떠오름)", color='#FFF', ha='center')
    elif "서" in direction:
        # 서쪽은 지는 천체들, 개밥바라기별(금성) 연출
        if show_inner:
            ax.text(-3, 0.8, "✨", fontsize=20, ha='center', va='center', color='#FFD700')
            ax.text(-3, 0.5, "금성 (초저녁)", color='#FFF', ha='center')
    elif "북" in direction:
        # 북쪽은 북극성과 주극성
        ax.text(0, 2.5, "⭐", fontsize=18, ha='center', va='center', color='#63B3ED')
        ax.text(0, 2.2, "북극성 (Polaris)", color='#63B3ED', ha='center')
        
    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.5, 4)
    ax.axis('off')
    return fig


# --- 화면 레이아웃 분할 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("☀️ 태양 - 지구 - 행성 위치 관계")
    st.markdown("<p style='color:#A0AEC0;'>우주 상공에서 바라본 천체들의 공전 궤도 위치입니다.</p>", unsafe_allow_html=True)
    fig_solar = plot_solar_system()
    st.pyplot(fig_solar)

with col2:
    st.subheader(f"🔭 {direction} 밤하늘 관측 위상")
    st.markdown(f"<p style='color:#A0AEC0;'>{obs_date} {obs_time} 기준, 실제 지평선 위 시야입니다.</p>", unsafe_allow_html=True)
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)

# --- 하단 행성별 특징 가이드 (디자인 강화) ---
st.markdown("---")
st.subheader("📝 관측 타깃 행성별 특징 가이드")

c_moon, c_inner, c_outer = st.columns(3)

with c_moon:
    st.markdown("""
    <div class="metric-card">
        <h3>🌙 달 (Moon)</h3>
        <p>지구의 유일한 위성으로, <b>29.5일 주기</b>로 위상이 변화합니다. 태양-지구-달의 위치에 따라 삭, 상현, 망(보름달), 하현으로 관측됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c_inner:
    st.markdown("""
    <div class="metric-card">
        <h3>✨ 내행성 (수성 · 금성)</h3>
        <p>지구 궤도 안쪽에서 공전하므로, 한밤중에는 볼 수 없고 <b>새벽녘이나 초저녁 서쪽 하늘</b>에서만 잠깐 관측할 수 있는 특징이 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c_outer:
    st.markdown("""
    <div class="metric-card">
        <h3>🔴 외행성 (화성 · 목성 · 토성)</h3>
        <p>지구 외곽을 돌며, 태양-지구-외행성 순으로 배열되는 <b>'충(Opposition)'</b> 위치일 때 밤새도록 가장 밝고 크게 관측 가능합니다.</p>
    </div>
    """, unsafe_allow_html=True)
