import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 페이지 설정 및 다크 테마 고대비 CSS
# ==========================================
st.set_page_config(page_title="지구과학 I 천체 관측 시뮬레이터", layout="wide")

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
        border-left: 5px solid #4FD1C5;
        margin-bottom: 15px;
    }
    .metric-card h4 {
        color: #63B3ED !important;
        margin-top: 0;
    }
    .metric-card p {
        color: #E2E8F0 !important;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔭 지구과학 I 천체 위치 및 관측 시뮬레이터")
st.caption("날짜에 따른 행성 위치와 지구 자전(시간)에 따른 지평선 시야를 과학적 원리로 시뮬레이션합니다.")

# ==========================================
# 2. 사이드바 제어판 (관측 조건 설정)
# ==========================================
st.sidebar.header("⏰ 관측 조건 설정")

# 날짜 선택
obs_date = st.sidebar.date_input("관측 날짜 선택", datetime.date(2026, 7, 8))

# 시간 선택 (30분 단위 슬라이더)
st.sidebar.markdown("🕒 **관측 시간 선택 (지구 자전)**")
time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]
selected_time_str = st.sidebar.select_slider(
    "시간을 조절하면 지구 자전축 방향과 관측 시야가 실시간 연동됩니다.",
    options=time_slots,
    value="22:00"
)

# 바라볼 방향 (방위)
direction = st.sidebar.selectbox("바라볼 방향 (방위각)", ["남 (South)", "동 (East)", "서 (West)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("🪐 **천체 표시 필터**")
show_moon = st.sidebar.checkbox("달 (Moon) 표시", value=True)
show_inner = st.sidebar.checkbox("내행성 (금성) 표시", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성) 표시", value=True)

# ==========================================
# 3. 과학적 위치 및 각도 계산 (물리/천문 수식)
# ==========================================
# 2026년 1월 1일 기준 경과일 계산
base_days = (obs_date - datetime.date(2026, 1, 1)).days
hour, minute = map(int, selected_time_str.split(":"))
time_hours = hour + (minute / 60.0)

# [A] 공전 각도 계산 (태양 기준 절대 각도, 라디안)
# 실제 공전 주기를 반영하여 날짜에 따른 위치 결정
earth_orb_ang = base_days * (2 * np.pi / 365.25)
venus_orb_ang = base_days * (2 * np.pi / 224.7) + 1.2 # 초기 위상 오프셋 부여
mars_orb_ang  = base_days * (2 * np.pi / 687.0) + 0.5
moon_orb_ang  = earth_orb_ang + (base_days * (2 * np.pi / 29.5)) # 지구 기준 공전

# [B] 지구 자전 각도 계산 (6시: 일출, 12시: 남중, 18시: 일몰, 24시: 한밤중)
# 태양 방향을 0도(아래쪽 정렬 기준 연산)로 잡고, 시간에 따른 자전각 계산
# 12시(정오)일 때 태양을 바라봄, 24시(자정)일 때 태양 반대편을 바라봄
rotation_angle = earth_orb_ang + np.pi + (time_hours / 24.0) * 2 * np.pi

# 각 천체의 실제 위치 좌표 (태양 중심)
ex, ey = np.cos(earth_orb_ang) * 3.5, np.sin(earth_orb_ang) * 3.5
vx, vy = np.cos(venus_orb_ang) * 2.0, np.sin(venus_orb_ang) * 2.0
mx, my = ex + np.cos(moon_orb_ang) * 0.6, ey + np.sin(moon_orb_ang) * 0.6
marx, mary = np.cos(mars_orb_ang) * 5.0, np.sin(mars_orb_ang) * 5.0


# ==========================================
# 4. 시각화 그래프 생성
# ==========================================

# [1] 태양계 위치 관계 그래프
def plot_solar_system():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 궤도선 그리기
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 2.0, np.sin(np.linspace(0, 2*np.pi, 100)) * 2.0, '--', color='#2D3748', alpha=0.4)
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 3.5, np.sin(np.linspace(0, 2*np.pi, 100)) * 3.5, '--', color='#2D3748', alpha=0.4)
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 5.0, np.sin(np.linspace(0, 2*np.pi, 100)) * 5.0, '--', color='#2D3748', alpha=0.4)
    
    # 천체 플로팅
    ax.plot(0, 0, 'oy', markersize=16, label='Sun', color='#FFD700') # 태양
    ax.plot(ex, ey, 'ob', markersize=9, label='Earth', color='#4169E1') # 지구
    
    if show_moon:
        ax.plot(mx, my, 'o', markersize=4, label='Moon', color='#F5F5F5')
    if show_inner:
        ax.plot(vx, vy, 'o', markersize=7, label='Venus', color='#E6C229')
    if show_outer:
        ax.plot(marx, mary, 'o', markersize=8, label='Mars', color='#D14949')
        
    # 💡 지구과학 핵심: 현재 관측자의 지평선(시야 방향) 화살표 표시
    # 자전각(rotation_angle) 방향이 곧 관측자의 '남중(South)' 방향이 됩니다.
    arrow_len = 0.8
    ax.arrow(ex, ey, np.cos(rotation_angle)*arrow_len, np.sin(rotation_angle)*arrow_len, 
             head_width=0.15, head_length=0.15, fc='#4FD1C5', ec='#4FD1C5', label='Observer (South)')
    
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-6.5, 6.5)
    ax.axis('off')
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=10)
    return fig


# [2] 지평선 기준 관측 시야 그래프 (실제 이각 및 남중고도 원리 연동)
def plot_sky_view(dir_setting):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 지평선 구조
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color='#11141D')
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 13, 'fontweight': 'bold'}
    
    # 지구에서 각 천체를 바라보는 상대 벡터 및 절대 기하 각도 구하기
    def get_altitude_and_azimuth(target_x, target_y):
        # 지구 기준 상대 좌표
        rx, ry = target_x - ex, target_y - ey
        target_abs_ang = np.arctan2(ry, rx)
        
        # 관측자의 자전 방향(남쪽)과의 각도차(이각 개념 확장) 계산
        ang_diff = target_abs_ang - rotation_angle
        # 각도를 -pi에서 pi 범위로 정규화
        ang_diff = (ang_diff + np.pi) % (2 * np.pi) - np.pi
        
        # 지평좌표계 매핑: 남쪽을 바라볼 때 ang_diff가 0이면 정중앙(남중)
        # 서쪽 시야는 남쪽 기준 오른쪽(+), 동쪽 시야는 남쪽 기준 왼쪽(-)
        return ang_diff

    # 천체별 남쪽 기준 상대 각도(라디안) 계산
    ang_sun   = get_altitude_and_azimuth(0, 0)
    ang_moon  = get_altitude_and_azimuth(mx, my)
    ang_venus = get_altitude_and_azimuth(vx, vy)
    ang_mars  = get_altitude_and_azimuth(marx, mary)

    # 방위(남, 동, 서, 북) 필터에 따라 지평선 스크린(X축 -4 ~ +4)에 천체 배치
    # 자전에 의해 천체는 동(왼쪽)에서 떠서 서(오른쪽)로 지는 메커니즘
    def draw_object(ang, name, color, marker, size, y_pos=1.8):
        # 바라보는 방위에 맞춰 X축 도메인 필터링
        x_pos = None
        if "남" in dir_setting:   # 중심이 남쪽 (ang = 0)
            if -np.pi/4 <= ang <= np.pi/4: x_pos = -ang * (4 / (np.pi/4))
        elif "서" in dir_setting: # 중심이 서쪽 (ang = -np.pi/2)
            # 남쪽 기준 우측 90도 부근
            offset_ang = ang + np.pi/2
            offset_ang = (offset_ang + np.pi) % (2 * np.pi) - np.pi
            if -np.pi/4 <= offset_ang <= np.pi/4: x_pos = -offset_ang * (4 / (np.pi/4))
        elif "동" in dir_setting: # 중심이 동쪽 (ang = np.pi/2)
            # 남쪽 기준 좌측 90도 부근
            offset_ang = ang - np.pi/2
            offset_ang = (offset_ang + np.pi) % (2 * np.pi) - np.pi
            if -np.pi/4 <= offset_ang <= np.pi/4: x_pos = -offset_ang * (4 / (np.pi/4))
            
        # 지평선 위에 있을 때만(태양과의 고도 및 밤시간대 체크 시뮬레이션 단순화) 그리기
        if x_pos is not None:
            ax.plot(x_pos, y_pos, marker, color=color, markersize=size)
            ax.text(x_pos, y_pos - 0.5, name, **text_style)

    # 각 천체 렌더링 호출
    # 태양 고도에 따라 낮밤이 결정되므로, 밤하늘 시야에서는 태양이 지평선 아래에 있을 때만 다른 천체들이 강조됩니다.
    if "북" in dir_setting:
        # 북쪽 하늘은 북극성이 고정 배치됨 (지구과학 기본)
        ax.plot(0, 2.3, '*', color='#63B3ED', markersize=14)
        ax.text(0, 1.7, "Polaris", color='#63B3ED', ha='center', fontsize=13, fontweight='bold')
    else:
        if show_moon:
            draw_object(ang_moon, "Moon", "#F5F5F5", "o", 18, y_pos=2.2)
        if show_inner:
            # 금성은 태양 이각이 48도를 넘지 않으므로 서쪽/동쪽 시야 조건에 과학적으로만 배치됨
            draw_object(ang_venus, "Venus", "#E6C229", "*", 14, y_pos=1.5)
        if show_outer:
            draw_object(ang_mars, "Mars", "#D14949", "o", 11, y_pos=1.9)
            
    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.5, 4)
    ax.axis('off')
    return fig


# ==========================================
# 5. 대시보드 레이아웃 화면 분할 배치
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("☀️ 태양계 행성 위치 및 관측자 방향 (Top-down)")
    fig_solar = plot_solar_system()
    st.pyplot(fig_solar)

with col2:
    st.subheader(f"🔭 현재 시간 {selected_time_str} / {direction} 하늘 시야")
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)


# ==========================================
# 6. 하단 지구과학 핵심 개념 매칭 가이드
# ==========================================
st.markdown("---")
st.subheader("🎓 지구과학 I 천체 관측 핵심 탐구 가이드")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🔄 지구 자전과 시간 (Time & Rotation)</h4>
        <p>왼쪽 태양계 그래프의 <b>청록색 화살표</b>는 현재 시간 관측자가 서 있는 위치와 남쪽(정면) 하늘 방향을 가리킵니다. 시간이 흐름에 따라 화살표가 반시계 방향으로 자전하는 것을 확인할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>📐 내행성의 최대 이각 (Venus Observation)</h4>
        <p>금성(Venus)은 지구 안쪽 궤도에서 공전하므로 태양과의 이각이 항상 일정 각도 이하로 제한됩니다. 따라서 <b>한밤중(예: 22시~자정)에는 지평선 밑으로 내려가 절대 관측할 수 없으며</b>, 일몰 직후 서쪽 하늘이나 일출 직전 동쪽 하늘에서만 시뮬레이터에 등장하게 설계되었습니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🔴 외행성의 위치 관계 (Mars Observation)</h4>
        <p>화성(Mars) 같은 외행성은 태양-지구-행성이 일직선이 되는 <b>'충(Opposition)'</b> 부근에 위치할 때, 관측자 화살표가 태양 반대편(한밤중 24시)을 향할 때 정남쪽에 남중하므로 밤새도록 가장 밝고 길게 관측 가능합니다.</p>
    </div>
    """, unsafe_allow_html=True)
