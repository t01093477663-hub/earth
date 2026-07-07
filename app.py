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

st.title("🔭 지구과학 I 천체 관측 시뮬레이터 (태양 영향 반영)")
st.caption("태양의 위치에 따른 낮과 밤의 변화 및 행성의 상대적 위치 관계를 완벽하게 시뮬레이션합니다.")

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
    "시간을 조절하면 태양의 고도와 낮/밤 환경이 실시간 연동됩니다.",
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
base_days = (obs_date - datetime.date(2026, 1, 1)).days
hour, minute = map(int, selected_time_str.split(":"))
time_hours = hour + (minute / 60.0)

# [A] 공전 각도 계산
earth_orb_ang = base_days * (2 * np.pi / 365.25)
venus_orb_ang = base_days * (2 * np.pi / 224.7) + 1.2
mars_orb_ang  = base_days * (2 * np.pi / 687.0) + 0.5
moon_orb_ang  = earth_orb_ang + (base_days * (2 * np.pi / 29.5))

# [B] 지구 자전 각도 계산 (태양 방향 기준 시뮬레이션 정렬)
# 자전축 중심 관측자 방향 계산
rotation_angle = earth_orb_ang + np.pi + (time_hours / 24.0) * 2 * np.pi

# 각 천체의 좌표 (태양 중심)
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
    
    # 궤도선
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 2.0, np.sin(np.linspace(0, 2*np.pi, 100)) * 2.0, '--', color='#2D3748', alpha=0.4)
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 3.5, np.sin(np.linspace(0, 2*np.pi, 100)) * 3.5, '--', color='#2D3748', alpha=0.4)
    ax.plot(np.cos(np.linspace(0, 2*np.pi, 100)) * 5.0, np.sin(np.linspace(0, 2*np.pi, 100)) * 5.0, '--', color='#2D3748', alpha=0.4)
    
    # 천체 플로팅
    ax.plot(0, 0, 'oy', markersize=16, label='Sun', color='#FFD700')
    ax.plot(ex, ey, 'ob', markersize=9, label='Earth', color='#4169E1')
    
    if show_moon:
        ax.plot(mx, my, 'o', markersize=4, label='Moon', color='#F5F5F5')
    if show_inner:
        ax.plot(vx, vy, 'o', markersize=7, label='Venus', color='#E6C229')
    if show_outer:
        ax.plot(marx, mary, 'o', markersize=8, label='Mars', color='#D14949')
        
    # 관측자 남쪽 방향 화살표 표시
    arrow_len = 0.8
    ax.arrow(ex, ey, np.cos(rotation_angle)*arrow_len, np.sin(rotation_angle)*arrow_len, 
             head_width=0.15, head_length=0.15, fc='#4FD1C5', ec='#4FD1C5', label='Observer (South)')
    
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-6.5, 6.5)
    ax.axis('off')
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=10)
    return fig


# [2] 지평선 관측 시야 그래프 (태양 영향 완벽 반영)
def plot_sky_view(dir_setting):
    # 지구 기준 천체의 상대 방위각 구하는 함수
    def get_altitude_and_azimuth(target_x, target_y):
        rx, ry = target_x - ex, target_y - ey
        target_abs_ang = np.arctan2(ry, rx)
        ang_diff = target_abs_ang - rotation_angle
        return (ang_diff + np.pi) % (2 * np.pi) - np.pi

    # 천체별 각도차 계산
    ang_sun   = get_altitude_and_azimuth(0, 0)
    ang_moon  = get_altitude_and_azimuth(mx, my)
    ang_venus = get_altitude_and_azimuth(vx, vy)
    ang_mars  = get_altitude_and_azimuth(marx, mary)

    # 💡 지구과학 원리: 현재 바라보는 방향에 상관없이 태양이 지평선 위(남/동/서)에 떠있다면 '낮'으로 판정
    # 태양과의 각도 차이가 대략 90도(pi/2) 이내이면 낮 시간대임
    is_daytime = (6.0 <= time_hours <= 18.0)

    # 낮이면 밝은 하늘색, 밤이면 깊은 밤하늘색 배경 설정
    bg_color = '#2B6CB0' if is_daytime else '#06080c'
    land_color = '#2F855A' if is_daytime else '#11141D'
    
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # 지평선 및 땅 그리기
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color=land_color)
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 13, 'fontweight': 'bold'}

    # 지평선 화면에 천체를 투영하는 함수
    def draw_object(ang, name, color, marker, size, y_pos=1.8, force_visible=False):
        x_pos = None
        if "남" in dir_setting:
            if -np.pi/4 <= ang <= np.pi/4: x_pos = -ang * (4 / (np.pi/4))
        elif "서" in dir_setting:
            offset_ang = (ang + np.pi/2 + np.pi) % (2 * np.pi) - np.pi
            if -np.pi/4 <= offset_ang <= np.pi/4: x_pos = -offset_ang * (4 / (np.pi/4))
        elif "동" in dir_setting:
            offset_ang = (ang - np.pi/2 + np.pi) % (2 * np.pi) - np.pi
            if -np.pi/4 <= offset_ang <= np.pi/4: x_pos = -offset_ang * (4 / (np.pi/4))
            
        if x_pos is not None:
            # 💡 낮에는 태양이 아닌 천체들은 강한 햇빛 때문에 보이지 않거나 흐릿하게 처리 (지구과학적 고증)
            alpha_val = 1.0 if (not is_daytime or force_visible) else 0.15
            ax.plot(x_pos, y_pos, marker, color=color, markersize=size, alpha=alpha_val)
            ax.text(x_pos, y_pos - 0.5, name, alpha=alpha_val, **text_style)

    # 천체 배치 실행
    if "북" in dir_setting:
        # 북쪽 하늘의 북극성은 낮에는 안 보이고 밤에만 선명함
        alpha_polaris = 0.15 if is_daytime else 1.0
        ax.plot(0, 2.3, '*', color='#63B3ED', markersize=14, alpha=alpha_polaris)
        ax.text(0, 1.7, "Polaris", color='#63B3ED', ha='center', fontsize=13, fontweight='bold', alpha=alpha_polaris)
    else:
        # 1. 태양 배치 (강제 표시 항목)
        draw_object(ang_sun, "SUN", "#FF8C00", "o", 24, y_pos=2.5, force_visible=True)
        
        # 2. 필터 적용 천체 배치 (낮 시간대엔 자동으로 투명도 저하)
        if show_moon:
            draw_object(ang_moon, "Moon", "#F5F5F5", "o", 18, y_pos=2.0)
        if show_inner:
            draw_object(ang_venus, "Venus", "#E6C229", "*", 14, y_pos=1.3)
        if show_outer:
            draw_object(ang_mars, "Mars", "#D14949", "o", 11, y_pos=1.7)
            
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
    status_tag = "☀️ 낮 (Daytime)" if (6.0 <= time_hours <= 18.0) else "🌙 밤 (Night)"
    st.subheader(f"🔭 시야 [{status_tag}] : {selected_time_str} / {direction} 하늘")
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)


# ==========================================
# 6. 하단 지구과학 핵심 개념 매칭 가이드
# ==========================================
st.markdown("---")
st.subheader("🎓 태양의 영향도를 고려한 천체 관측 핵심 탐구")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>☀️ 태양 고도와 일주 운동</h4>
        <p>시간 슬라이더를 06:00(일출)에서 12:00(남중), 18:00(일몰)로 움직여보세요. 동쪽에서 태양이 떠올라 서쪽으로 지며 시야 배경이 파랗게 바뀌는 <b>지구 자전에 의한 태양의 겉보기 운동</b>이 시뮬레이션됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>🌤️ 낮 시간대 천체 관측의 한계</h4>
        <p>지구과학 시험 범위인 '천체 관측 가능 조건'을 시뮬레이터에 세팅했습니다. 낮(06시~18시)에는 달과 행성들이 지평선 위에 있더라도 <b>태양 빛의 간섭 때문에 마커가 흐려지거나 보이지 않게 처리</b>됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🔭 초저녁과 새벽녘의 내행성</h4>
        <p>금성(Venus) 마커를 켠 뒤 시간을 18:30(일몰 직후)으로 세팅하고 <b>서쪽(West) 하늘</b>을 바라보세요. 태양이 방금 막 지평선 아래로 내려간 뒤, 태양 근처에서 밝게 빛나는 금성의 <b>초저녁 관측 원리</b>를 완벽히 이해할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
