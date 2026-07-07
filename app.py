import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ==========================================
# [수정] 시스템 내장 한글 폰트 자동 검색 로직
# ==========================================
@st.cache_data
def find_hangul_font():
    # 리눅스/윈도우/맥 시스템 폰트 중에서 한글 표현이 가능한 폰트 검색
    font_list = fm.findSystemFonts()
    # 스트림릿 서버(리눅스)에 기본 탑재된 Nanum, Un, DejaVu 등 검색
    target_fonts = [f for f in font_list if any(name in f.lower() for name in ['nanum', 'un', 'gothic', 'malgun', 'sans'])]
    
    if target_fonts:
        return target_fonts[0] # 가장 먼저 발견된 폰트 경로 반환
    return None

font_path = find_hangul_font()

if font_path:
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
    plt.rc('axes', unicode_minus=False) # 마이너스 기호 깨짐 방지
    font_available = True
else:
    font_available = False

# ==========================================
# 페이지 기본 설정 및 다크모드 CSS 디자인
# ==========================================
st.set_page_config(page_title="우주 천체 관측 시뮬레이터", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    [data-testid="stSidebar"] {
        background-color: #1A202C;
        border-right: 1px solid #2D3748;
    }
    h1, h2, h3, h4 {
        color: #63B3ED !important;
    }
    .metric-card {
        background-color: #1A202C;
        padding: 20px;
        border-radius: 12px;
        border-top: 4px solid #4FD1C5;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌌 천체 위치 및 위상 시뮬레이터")
st.caption("날짜와 시간을 슬라이더로 조절하며 행성의 위치 관계와 밤하늘 위상을 확인하세요.")

# ==========================================
# 사이드바 제어판 (UI 개선)
# ==========================================
st.sidebar.header("⏰ 관측 설정")

# 날짜 선택
obs_date = st.sidebar.date_input("관측 날짜 선택", datetime.date.today())

# 시간 선택 (슬라이더 방식으로 개선: 30분 단위 탐색)
st.sidebar.markdown("**관측 시간 선택 (슬라이더)**")
time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]
selected_time_str = st.sidebar.select_slider(
    "시간을 좌우로 움직여보세요",
    options=time_slots,
    value="22:00" # 기본값을 밤 10시로 설정
)

# 방위 선택
direction = st.sidebar.selectbox("바라볼 방향 (방위)", ["남 (South)", "동 (East)", "서 (West)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🪐 천체 표시 필터")
show_moon = st.sidebar.checkbox("달 (Moon) 표시", value=True)
show_inner = st.sidebar.checkbox("내행성 (수성, 금성) 표시", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성, 목성) 표시", value=True)

# 시간 문자열을 숫자로 변환 (시뮬레이션 계산용)
hour, minute = map(int, selected_time_str.split(":"))
total_hours = hour + (minute / 60.0)
days = (obs_date - datetime.date(2026, 1, 1)).days + (total_hours / 24.0)

# ==========================================
# 시각화 그래프 생성 함수
# ==========================================

# 1. 태양계 궤도 위치 관계 그래프
def plot_solar_system():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#0B0E14')
    ax.set_facecolor('#0B0E14')
    
    # 태양 (중심)
    ax.plot(0, 0, 'oy', markersize=16, label='태양 (Sun)', color='#FFD700')
    
    # 지구
    earth_angle = days * (2 * np.pi / 365)
    ex, ey = np.cos(earth_angle) * 3, np.sin(earth_angle) * 3
    ax.plot(ex, ey, 'ob', markersize=9, label='지구 (Earth)', color='#4169E1')
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 3, np.sin(np.linspace(0, 2*np.pi, 100)) * 3, '--', color='#2D3748', alpha=0.5)
    
    # 달 (지구 주위)
    if show_moon:
        moon_angle = days * (2 * np.pi / 29.5)
        mx, my = ex + np.cos(moon_angle) * 0.5, ey + np.sin(moon_angle) * 0.5
        ax.plot(mx, my, 'o', markersize=4, label='달 (Moon)', color='#F5F5F5')
    
    # 내행성 (금성 예시)
    if show_inner:
        v_angle = days * (2 * np.pi / 225)
        vx, vy = np.cos(v_angle) * 1.8, np.sin(v_angle) * 1.8
        ax.plot(vx, vy, 'o', markersize=7, label='금성 (내행성)', color='#E6C229')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 1.8, np.sin(np.linspace(0, 2*np.pi, 100)) * 1.8, '--', color='#2D3748', alpha=0.5)

    # 외행성 (화성 예시)
    if show_outer:
        m_angle = days * (2 * np.pi / 687)
        mar_x, mar_y = np.cos(m_angle) * 4.5, np.sin(m_angle) * 4.5
        ax.plot(mar_x, mar_y, 'o', markersize=8, label='화성 (외행성)', color='#D14949')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 4.5, np.sin(np.linspace(0, 2*np.pi, 100)) * 4.5, '--', color='#2D3748', alpha=0.5)
        
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.axis('off')
    
    # 한글 폰트가 적용 가능할 때만 prop 인자 설정
    if font_available:
        ax.legend(loc='upper right', facecolor='#1A202C', edgecolor='#2D3748', labelcolor='white', prop=font_prop)
    else:
        ax.legend(loc='upper right', facecolor='#1A202C', edgecolor='#2D3748', labelcolor='white')
        
    return fig

# 2. 지평선 방위별 밤하늘 위상 그래프
def plot_sky_view(dir_setting):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#0B0E14')
    ax.set_facecolor('#0B0E14')
    
    # 지평선과 땅 표현
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color='#11141D')
    
    # 방위에 따른 텍스트 및 천체 디자인
    text_kwargs = {'color': '#FFF', 'ha': 'center'}
    if font_available:
        text_kwargs['fontproperties'] = font_prop

    if "남" in dir_setting:
        ax.text(0, 2, "🌙", fontsize=32, ha='center', va='center')
        ax.text(0, 1.3, "남중한 달 (Moon)", **text_kwargs)
        if show_outer:
            ax.text(2.5, 1.8, "🔴", fontsize=16, ha='center', va='center')
            ax.text(2.5, 1.3, "화성 (Mars)", **text_kwargs)
    elif "동" in dir_setting:
        ax.text(3, 1.2, "🪐", fontsize=28, ha='center', va='center')
        ax.text(3, 0.6, "떠오르는 목성", **text_kwargs)
    elif "서" in dir_setting:
        if show_inner:
            ax.text(-3, 1.0, "✨", fontsize=24, ha='center', va='center', color='#FFD700')
            ax.text(-3, 0.5, "지는 금성 (초저녁)", **text_kwargs)
    elif "북" in dir_setting:
        ax.text(0, 2.5, "⭐", fontsize=20, ha='center', va='center', color='#63B3ED')
        ax.text(0, 2.1, "북극성 (Polaris)", color='#63B3ED', ha='center', fontproperties=font_prop if font_available else None)
        
    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.5, 4)
    ax.axis('off')
    return fig


# ==========================================
# 대시보드 화면 레이아웃 분할 배치
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("☀️ 태양계 행성 위치 관계")
    fig_solar = plot_solar_system()
    st.pyplot(fig_solar)

with col2:
    st.subheader(f"🔭 {direction} 밤하늘 관측 시야")
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)

# ==========================================
# 하단 행성 특징 가이드 디자인
# ==========================================
st.markdown("---")
st.subheader("🪐 천체별 관측 특징 요약")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🌙 위성: 달 (Moon)</h4>
        <p style='font-size: 14px; color: #A0AEC0;'>지구 주위를 약 29.5일 주기로 공전하며, 위치 관계에 따라 위상(모양)이 계속해서 변화합니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>✨ 내행성 (수성 · 금성)</h4>
        <p style='font-size: 14px; color: #A0AEC0;'>지구 안쪽 궤도를 돌기 때문에 한밤중에는 볼 수 없고, 주로 초저녁 서쪽이나 새벽녘 동쪽 하늘에서만 보입니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🔴 외행성 (화성 · 목성 · 토성)</h4>
        <p style='font-size: 14px; color: #A0AEC0;'>지구 바깥쪽 궤도를 돌며, 지구-태양-행성이 일직선이 되는 '충'의 위치일 때 밤새도록 가장 밝게 빛납니다.</p>
    </div>
    """, unsafe_allow_html=True)
