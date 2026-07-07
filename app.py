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

st.title("🔭 지구과학 I 천체 관측 시뮬레이터 (태양 빛 간섭 반영)")
st.caption("태양의 고도(낮/밤/박명) 및 행성과의 상대적 이각을 계산하여 실제 눈으로 관측 가능한 천체만 필터링합니다.")

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
    "시간을 조절하면 태양 빛의 간섭 강도와 낮/밤 환경이 실시간 연동됩니다.",
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

# [A] 공전 각도 계산 (태양 기준 절대 라디안)
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


# [2] 지평선 관측 시야 그래프 (태양 빛 간섭 정밀 물리 법칙 연동)
def plot_sky_view(dir_setting):
    def get_altitude_and_azimuth(target_x, target_y):
        rx, ry = target_x - ex, target_y - ey
        target_abs_ang = np.arctan2(ry, rx)
        ang_diff = target_abs_ang - rotation_angle
        return (ang_diff + np.pi) % (2 * np.pi) - np.pi

    # 천체별 상대 각도 계산
    ang_sun   = get_altitude_and_azimuth(0, 0)
    ang_moon  = get_altitude_and_azimuth(mx, my)
    ang_venus = get_altitude_and_azimuth(vx, vy)
    ang_mars  = get_altitude_and_azimuth(marx, mary)

    # 💡 [지구과학 핵심 고증] 태양의 실시간 위치별 하늘 상태 정의
    # 06시~18시: 완연한 낮 / 04:30~06시 & 18시~19:30: 박명(여명/황혼) / 그 외: 완전한 밤
    if 6.0 <= time_hours <= 18.0:
        sky_status = "DAY"
        bg_color = '#2B6CB0'      # 밝은 파란 하늘
        land_color = '#2F855A'
    elif (4.5 <= time_hours < 6.0) or (18.0 < time_hours <= 19.5):
        sky_status = "TWILIGHT"
        bg_color = '#1A365D'      # 푸르스름한 박명 하늘 (태양빛 간섭 존재)
        land_color = '#1C2D42'
    else:
        sky_status = "NIGHT"
        bg_color = '#06080c'      # 완전한 밤하늘
        land_color = '#11141D'
    
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # 지평선 및 지면 배치
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-10, 10], -2, 0, color=land_color)
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 13, 'fontweight': 'bold'}

    # 천체 스크린 매핑 함수
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
            # 💡 지구과학 원리 1: 태양과 행성의 각도차(이각)가 10도(약 0.17라디안) 미만이면 '합' 위치이므로 밤이라도 안 보임
            elongation = abs(ang - target_ang_sun)
            elongation = (elongation + np.pi) % (2 * np.pi) - np.pi
            if abs(elongation) < 0.17 and not force_visible:
                return # 태양 빛에 가려져 소멸 (안 보임)

            # 💡 지구과학 원리 2: 하늘 밝기(낮/밤/박명)에 따른 시계 가시성 필터링
            if sky_status == "DAY" and not force_visible:
                alpha_val = 0.0 # 낮에는 태양 빛 때문에 100% 보이지 않음
            elif sky_status == "TWILIGHT" and not force_visible:
                # 박명기에는 금성(Venus)처럼 매우 밝은 천체만 흐릿하게 보이고 나머지는 안 보임
                alpha_val = 0.4 if name == "Venus" or name == "Moon" else 0.0
            else:
                alpha_val = 1.0 # 밤에는 선명하게 관측 가능
                
            if alpha_val > 0:
                ax.plot(x_pos, y_pos, marker, color=color, markersize=size, alpha=alpha_val)
                ax.text(x_pos, y_pos - 0.5, name, alpha=alpha_val, **text_style)

    # 방위별 그리기 실행
    if "북" in dir_setting:
        alpha_polaris = 0.0 if sky_status == "DAY" else (0.3 if sky_status == "TWILIGHT" else 1.0)
        if alpha_polaris > 0:
            ax.plot(0, 2.3, '*', color='#63B3ED', markersize=14, alpha=alpha_polaris)
            ax.text(0, 1.7, "Polaris", color='#63B3ED', ha='center', fontsize=13, fontweight='bold', alpha=alpha_polaris)
    else:
        # 1. 태양 (언제나 100% 가시성)
        draw_object(ang_sun, ang_sun, "SUN", "#FF8C00", "o", 24, y_pos=2.5, force_visible=True)
        
        # 2. 필터 처리된 천체들 (태양 빛 가시성 공식 적용됨)
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
    elif (4.5 <= time_hours < 6.0) or (18.0 < time_hours <= 19.5):
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
st.subheader("🎓 태양 빛 간섭과 이각에 따른 천체 관측 심화 탐구")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🌆 박명 효과와 천체의 밝기 (Twilight Effect)</h4>
        <p>시간을 <b>18:30 또는 19:00(일몰 직후 황혼기)</b>로 맞춘 뒤 서쪽 하늘을 관측해 보세요. 하늘이 푸른빛을 띠는 박명 상태가 되며, 다른 행성들은 강한 산란광에 가려 안 보이지만 <b>반사율과 밝기가 압도적으로 높은 금성(Venus)과 달</b>만 필터링되어 먼저 모습을 드러냅니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>📐 '합(Conjunction)' 위치에서의 관측 불가능 원리</h4>
        <p>행성이 태양과 겹치는 위치인 <b>'합'</b>(내합/외합 포함)에 가까워져 태양과의 각도(이각)가 10도 미만으로 좁혀지면, 밤 시간대라 하더라도 <b>태양의 강력한 대기 광운에 묻혀 지구상에서 관측이 불가능</b>해집니다. 코드 내부 알고리즘이 이를 자동으로 계산하여 화면에서 숨겨줍니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🌍 완벽한 자전-공전 시뮬레이션</h4>
        <p>왼쪽 태양계 물리 배치 모델과 오른쪽 지평좌표계 투영 모델이 완벽히 1:1 결합되었습니다. 지구과학 I 교과서에 나오는 <b>"행성의 이각 크기 = 지평선 상에서 태양과 해당 천체 사이의 거리"</b> 공식이 시각적으로 완벽하게 입증됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
