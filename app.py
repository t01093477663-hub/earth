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

st.title("🔭 지구과학 I 천체 관측 시뮬레이터 (태양 가시성 동적 반영)")
st.caption("태양이 지평선 위에 존재하면 방위와 관계없이 낮으로 판정하여 태양 빛의 간섭을 현실적으로 표현합니다.")

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
    "시간을 조절하면 태양의 실제 고도에 따라 낮/밤 환경이 실시간 연동됩니다.",
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

# [A] 공전 각도 계산 (태양 중심 절대 라디안)
earth_orb_ang = base_days * (2 * np.pi / 365.25)
venus_orb_ang = base_days * (2 * np.pi / 224.7) + 1.2
mars_orb_ang  = base_days * (2 * np.pi / 687.0) + 0.5
moon_orb_ang  = earth_orb_ang + (base_days * (2 * np.pi / 29.5))

# [B] 지구 자전 각도 계산
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
        
    # 관측자 방향 화살표 표시
    arrow_len = 0.8
    ax.arrow(ex, ey, np.cos(rotation_angle)*arrow_len, np.sin(rotation_angle)*arrow_len, 
             head_width=0.15, head_length=0.15, fc='#4FD1C5', ec='#4FD1C5', label='Observer (South)')
    
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-6.5, 6.5)
    ax.axis('off')
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=10)
    return fig


# [2] 지평선 관측 시야 그래프 (태양 가시성 버그 수정본)
def plot_sky_view(dir_setting):
    def get_altitude_and_azimuth(target_x, target_y):
        rx, ry = target_x - ex, target_y - ey
        target_abs_ang = np.arctan2(ry, rx)
        ang_diff = target_abs_ang - rotation_angle
        return (ang_diff + np.pi) % (2 * np.pi) - np.pi

    # 천체별 상대 방위각 계산
    ang_sun   = get_altitude_and_azimuth(0, 0)
    ang_moon  = get_altitude_and_azimuth(mx, my)
    ang_venus = get_altitude_and_azimuth(vx, vy)
    ang_mars  = get_altitude_and_azimuth(marx, mary)

    # 💡 [버그 수정 핵심] 관측 시간대별 '실제 태양 고도'를 추적하여 낮/밤 판정
    # 전체 360도 하늘 중 태양이 수평선 위(관측자의 시야 반구 범위 내)에 위치하는지 계산
    # 시간이 대략 06시 ~ 18시 영역에 있을 때 지평선 위에 존재하게 됩니다.
    sun_visible_global = (6.0 <= time_hours <= 18.0)

    # 태양이 떠있으면 스크린 무조건 '낮' 배경화면 처리
    if sun_visible_global:
        sky_status = "DAY"
        bg_color = '#2B6CB0'      # 완연한 낮 (밝은 파란색)
        land_color = '#2F855A'
    elif (4.8 <= time_hours < 6.0) or (18.0 < time_hours <= 19.2):
        sky_status = "TWILIGHT"
        bg_color = '#1A365D'      # 여명/황혼 박명 (푸르스름한 상태)
        land_color = '#1C2D42'
    else:
        sky_status = "NIGHT"
        bg_color = '#06080c'      # 순수한 밤 (깊은 블랙)
        land_color = '#11141D'
    
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # 지평선 구조
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color=land_color)
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 13, 'fontweight': 'bold'}

    # 2D 스크린 매핑 함수
    def draw_object(ang, target_ang_sun, name, color, marker, size, y_pos=1.8, force_visible=False):
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
            # 태양과 너무 겹치는 '합' 위치 체크 (이각 10도 미만)
            elongation = abs(ang - target_ang_sun)
            elongation = (elongation + np.pi) % (2 * np.pi) - np.pi
            if abs(elongation) < 0.17 and not force_visible:
                return

            # 태양 가시성 상태에 따른 최종 천체 투명도 조절
            if sky_status == "DAY" and not force_visible:
                alpha_val = 0.0  # 낮에는 태양 외 천체는 가시성 0 (숨김)
            elif sky_status == "TWILIGHT" and not force_visible:
                alpha_val = 0.45 if name == "Venus" or name == "Moon" else 0.0 # 박명엔 금성/달만 살짝 허용
            else:
                alpha_val = 1.0  # 완전한 밤에는 100% 선명
                
            if alpha_val > 0:
                ax.plot(x_pos, y_pos, marker, color=color, markersize=size, alpha=alpha_val)
                ax.text(x_pos, y_pos - 0.5, name, alpha=alpha_val, **text_style)

    # 방위 필터 처리 및 천체 출력
    if "북" in dir_setting:
        # 북쪽 하늘 배경색도 전역 태양 상태와 동기화
        alpha_polaris = 0.0 if sky_status == "DAY" else (0.3 if sky_status == "TWILIGHT" else 1.0)
        if alpha_polaris > 0:
            ax.plot(0, 2.3, '*', color='#63B3ED', markersize=14, alpha=alpha_polaris)
            ax.text(0, 1.7, "Polaris", color='#63B3ED', ha='center', fontsize=13, fontweight='bold', alpha=alpha_polaris)
    else:
        # 1. 태양 (현재 보고 있는 방위 스크린 영역 안에 들어올 때만 출력)
        draw_object(ang_sun, ang_sun, "SUN", "#FF8C00", "o", 24, y_pos=2.5, force_visible=True)
        
        # 2. 기타 행성 및 위성 (태양 광 간섭 통제 적용)
        if show_moon:
            draw_object(ang_moon, ang_sun, "Moon", "#F5F5F5", "o", 18, y_pos=2.0)
        if show_inner:
            draw_object(ang_venus, ang_sun, "Venus", "#E6C229", "*", 14, y_pos=1.3)
        if show_outer:
            draw_object(ang_mars, ang_sun, "Mars", "#D14949", "o", 11, y_pos=1.7)
            
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
    if 6.0 <= time_hours <= 18.0:
        status_tag = "☀️ 낮 (Daytime)"
    elif (4.5 <= time_hours < 6.0) or (18.0 < time_hours <= 19.2):
        status_tag = "🌆 박명 (Twilight)"
    else:
        status_tag = "🌙 밤 (Night)"
        
    st.subheader(f"🔭 시야 [{status_tag}] : {selected_time_str} / {direction} 하늘")
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)


# ==========================================
# 6. 하단 지구과학 핵심 개념 매칭 가이드
# ==========================================
st.markdown("---")
st.subheader("🎓 태양 광학 연동 알고리즘 가이드")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🚨 전역 태양 감지 시스템 반영</h4>
        <p>수정된 버전에서는 관측자가 현재 동쪽을 보든 서쪽을 보든 관계없이, <b>태양이 지구의 지평선 위(06시~18시)에 떠 있기만 하면 전체 대기 시스템이 자동으로 '낮(DAY)' 상태</b>로 동기화됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>🌤️ 태양이 보이면 낮이 되는 상식 구현</h4>
        <p>시간을 낮 12시(정오)로 두고 방위를 '동(East)'으로 바꾸면 태양 자체는 정남쪽에 있어 화면에 안 보일 수 있지만, <b>지평선 위 환경은 여전히 파란색 낮 배경</b>을 유지하며 태양 빛의 산란 효과가 정상 작동합니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🔭 실시간 이각 측정 시각화</h4>
        <p>태양이 지평선 아래로 완전히 떨어져 깜깜한 밤이 되었을 때에만 밤하늘 모드가 켜지며 숨겨진 화성, 금성, 달이 방위각 계산 수식에 맞춰 정확한 고도로 화면에 리렌더링됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
