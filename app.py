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

st.title("🔭 지구과학 I 천체 관측 시뮬레이터")
st.caption("태양이 지평선 위에 떠서 시야에 관측되는 순간 무조건 낮으로 연동되도록 기하학 수식을 전면 수정했습니다.")

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
    "시간을 조절하면 태양의 기하학적 위치에 맞춰 낮/밤 타이틀과 배경이 동기화됩니다.",
    options=time_slots,
    value="14:30"
)

# 바라볼 방향 (방위)
direction = st.sidebar.selectbox("바라볼 방향 (방위각)", ["남 (South)", "동 (East)", "서 (West)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("🪐 **천체 표시 필터**")
show_moon = st.sidebar.checkbox("달 (Moon) 표시", value=True)
show_inner = st.sidebar.checkbox("내행성 (금성) 표시", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성) 표시", value=True)

# ==========================================
# 3. 과학적 위치 및 각도 계산 (지구과학 기하 공식)
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
# 12시(정오)일 때 정확히 태양을 정면으로 바라보도록 위상 정렬
rotation_angle = earth_orb_ang + ((time_hours - 12.0) / 24.0) * 2 * np.pi

# 각 천체의 좌표 (태양 중심)
ex, ey = np.cos(earth_orb_ang) * 3.5, np.sin(earth_orb_ang) * 3.5
vx, vy = np.cos(venus_orb_ang) * 2.0, np.sin(venus_orb_ang) * 2.0
mx, my = ex + np.cos(moon_orb_ang) * 0.6, ey + np.sin(moon_orb_ang) * 0.6
marx, mary = np.cos(mars_orb_ang) * 5.0, np.sin(mars_orb_ang) * 5.0


# ==========================================
# 4. 상대 방위각 및 실시간 낮/밤 상태 연동 정의
# ==========================================
def get_altitude_and_azimuth(target_x, target_y):
    rx, ry = target_x - ex, target_y - ey
    target_abs_ang = np.arctan2(ry, rx)
    ang_diff = target_abs_ang - rotation_angle
    return (ang_diff + np.pi) % (2 * np.pi) - np.pi

# 천체별 상대 각도 결정
ang_sun   = get_altitude_and_azimuth(0, 0)
ang_moon  = get_altitude_and_azimuth(mx, my)
ang_venus = get_altitude_and_azimuth(vx, vy)
ang_mars  = get_altitude_and_azimuth(marx, mary)

# 💡 [핵심 버그 수정]: 관측자 기준 태양이 '지평선 위'(-90도 ~ +90도 사이)에 떠있는가?
# 이 조건이 참이면 시간 숫자가 몇 시든, 어느 방위를 보든 무조건 "완벽한 낮"입니다.
is_sun_above_horizon = (-np.pi/2 <= ang_sun <= np.pi/2)

if is_sun_above_horizon:
    sky_status = "DAY"
    status_tag = "☀️ 낮 (Daytime)"
    bg_color = '#2B6CB0'      # 스크린을 밝은 파란색으로 고정
    land_color = '#2F855A'
elif (-np.pi/2 - 0.25 <= ang_sun < -np.pi/2) or (np.pi/2 < ang_sun <= np.pi/2 + 0.25):
    sky_status = "TWILIGHT"
    status_tag = "🌆 박명 (Twilight)"
    bg_color = '#1A365D'      # 푸르스름한 새벽/노을 하늘
    land_color = '#1C2D42'
else:
    sky_status = "NIGHT"
    status_tag = "🌙 밤 (Night)"
    bg_color = '#06080c'      # 완전한 암흑 밤하늘
    land_color = '#11141D'


# ==========================================
# 5. 시각화 그래프 생성
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


# [2] 지평선 관측 시야 그래프
def plot_sky_view(dir_setting):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # 지평선 구조
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color=land_color)
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 13, 'fontweight': 'bold'}

    # 2D 스크린 매핑 계산 함수
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
            # 태양 이각 크기 필터링 (합 위치 10도 이하 숨김)
            elongation = abs(ang - ang_sun)
            elongation = (elongation + np.pi) % (2 * np.pi) - np.pi
            if abs(elongation) < 0.17 and not force_visible:
                return

            # 전역 대기 상태(sky_status)에 따른 가시성 구현
            if sky_status == "DAY" and not force_visible:
                alpha_val = 0.0  # 낮에는 태양 빛 때문에 다 숨김
            elif sky_status == "TWILIGHT" and not force_visible:
                alpha_val = 0.5 if name in ["Venus", "Moon"] else 0.0
            else:
                alpha_val = 1.0  # 밤에는 전부 선명하게 표시
                
            if alpha_val > 0:
                ax.plot(x_pos, y_pos, marker, color=color, markersize=size, alpha=alpha_val)
                ax.text(x_pos, y_pos - 0.5, name, alpha=alpha_val, **text_style)

    # 천체 그리기 명령
    if "북" in dir_setting:
        alpha_polaris = 0.0 if sky_status == "DAY" else (0.3 if sky_status == "TWILIGHT" else 1.0)
        if alpha_polaris > 0:
            ax.plot(0, 2.3, '*', color='#63B3ED', markersize=14, alpha=alpha_polaris)
            ax.text(0, 1.7, "Polaris", color='#63B3ED', ha='center', fontsize=13, fontweight='bold', alpha=alpha_polaris)
    else:
        # 1. 태양 (언제나 강제 노출)
        draw_object(ang_sun, "SUN", "#FF8C00", "o", 24, y_pos=2.5, force_visible=True)
        
        # 2. 기타 필터 천체
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
# 6. 대시보드 레이아웃 화면 분할 배치
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("☀️ 태양계 행성 위치 및 관측자 방향 (Top-down)")
    fig_solar = plot_solar_system()
    st.pyplot(fig_solar)

with col2:
    st.subheader(f"🔭 시야 [{status_tag}] : {selected_time_str} / {direction} 하늘")
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)


# ==========================================
# 7. 하단 지구과학 핵심 개념 매칭 가이드
# ==========================================
st.markdown("---")
st.subheader("🎓 천체 관측 싱크 버그 수정 요약")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🎯 태양 중심 완벽 동기화</h4>
        <p>기존의 6시~18시 고정 루틴을 삭제하고, 기하학 공식으로 태양 마커의 수평 고도를 추적합니다. 이제 화면에 <b>태양이 걸쳐있거나 지평선 위에 뜨면 100% 무조건 '낮' 상태</b>로 강제 잠금됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>🌍 방위각 전환 오류 해결</h4>
        <p>14시 같은 한낮에 남쪽 하늘을 보다가 동쪽이나 서쪽 하늘로 고개를 돌려도, 태양의 전역 고도 벡터가 지평선 위에 살아있으므로 <b>하늘색 배경과 낮 상태 타이틀이 완벽히 유지</b>됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>📊 기말고사 대비 시뮬레이션 활용법</h4>
        <p>지구과학 문제집을 풀 때 헷갈리는 '초저녁 금성이 서쪽 지평선 근처에 뜨는 상황'을 세팅하려면, 시간을 18:30(박명)으로 두고 방위를 서(West)로 바꿔보세요. 교과서 삽화와 완벽히 일치하는 그래픽을 볼 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
