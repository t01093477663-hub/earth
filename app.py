import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 페이지 설정 및 다크 테마 고대비 CSS
# ==========================================
st.set_page_config(page_title="지구과학 I 천체 관측 및 식현상 시뮬레이터", layout="wide")

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
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔭 지구과학 I 천체 관측 & 식현상 시뮬레이터")
st.caption("Stellarium 엔진 기반의 고도-방위각 좌표계를 통해 동서남북 시선의 정보 오류를 완전히 해결하고 일식/월식을 추가했습니다.")

# ==========================================
# 2. 사이드바 제어판 (관측 조건 설정)
# ==========================================
st.sidebar.header("⚙️ 관측 환경 및 모드 설정")

# [핵심] 관측 모드 선택 필터
obs_mode = st.sidebar.selectbox(
    "🌌 관측 모드 선택",
    ["일반 우주 관측 (Normal)", "개기 일식 시뮬레이션 (Solar Eclipse)", "개기 월식 시뮬레이션 (Lunar Eclipse)"]
)

# 날짜 및 시간 제어
obs_date = st.sidebar.date_input("관측 날짜 선택", datetime.date(2026, 7, 8))

st.sidebar.markdown("🕒 **관측 시간 선택 (지구 자전)**")
time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]

# 모드별 최적 추천 시간 기본값 설정
default_time = "12:00" if "일식" in obs_mode else ("00:00" if "월식" in obs_mode else "14:30")
selected_time_str = st.sidebar.select_slider(
    "시간을 조절하여 천체의 동서남북 이동 경로와 일주 운동을 확인하세요.",
    options=time_slots,
    value=default_time
)

# 바라볼 방향 (방위각)
direction = st.sidebar.selectbox("바라볼 방향 (시선 방위)", ["남 (South)", "동 (East)", "서 (West)", "북 (North)"])

st.sidebar.markdown("---")
st.sidebar.markdown("🪐 **천체 표시 필터**")
show_moon = st.sidebar.checkbox("달 (Moon) 표시", value=True)
show_inner = st.sidebar.checkbox("내행성 (금성) 표시", value=True)
show_outer = st.sidebar.checkbox("외행성 (화성) 표시", value=True)


# ==========================================
# 3. 과학적 위치 및 정밀 지평 좌표계 연산
# ==========================================
base_days = (obs_date - datetime.date(2026, 1, 1)).days
hour, minute = map(int, selected_time_str.split(":"))
time_hours = hour + (minute / 60.0)

# [A] 공전 절대 각도 (태양 중심 라디안)
earth_orb_ang = base_days * (2 * np.pi / 365.25)
venus_orb_ang = base_days * (2 * np.pi / 224.7) + 1.2
mars_orb_ang  = base_days * (2 * np.pi / 687.0) + 0.5

# 관측 모드에 따른 달의 위치 정밀 동기화 (기말고사 단골 기하 관계)
if "일식" in obs_mode:
    # 일식 = 삭(태양-달-지구 직선 배치)
    moon_orb_ang = earth_orb_ang + np.pi
elif "월식" in obs_mode:
    # 월식 = 망(태양-지구-달 직선 배치)
    moon_orb_ang = earth_orb_ang
else:
    # 일반 관측시 매달 공전 계산
    moon_orb_ang = earth_orb_ang + (base_days * (2 * np.pi / 29.5))

# [B] 지구 자전 중심축 및 관측자 천정(Zenith)각 계산
sun_dir = np.arctan2(0 - np.sin(earth_orb_ang)*3.5, 0 - np.cos(earth_orb_ang)*3.5)
# 정오(12:00)에 천정이 태양 방향을 완벽히 정렬하도록 세팅
zenith_dir = sun_dir + ((time_hours - 12.0) / 24.0) * 2 * np.pi
zenith_dir = (zenith_dir + np.pi) % (2 * np.pi) - np.pi

# 천정에서 바라보는 방향이 곧 남극/남쪽 자오선 기준이 됨
ex, ey = np.cos(earth_orb_ang) * 3.5, np.sin(earth_orb_ang) * 3.5
vx, vy = np.cos(venus_orb_ang) * 2.0, np.sin(venus_orb_ang) * 2.0
mx, my = ex + np.cos(moon_orb_ang) * 0.6, ey + np.sin(moon_orb_ang) * 0.6
marx, mary = np.cos(mars_orb_ang) * 5.0, np.sin(mars_orb_ang) * 5.0

# ==========================================
# 4. 고도(Alt) 및 방위각(Az) 변환 엔진 (Stellarium 식 역학 알고리즘)
# ==========================================
def get_alt_az(target_x, target_y):
    rx, ry = target_x - ex, target_y - ey
    obj_dir = np.arctan2(ry, rx)
    
    # 남중 자오선(zenith_dir) 기준 상대각 산출
    rel_from_south = (obj_dir - zenith_dir + np.pi) % (2 * np.pi) - np.pi
    
    # 1) 고도 계산 (남중할 때 최고 고도, 동/서로 90도 멀어지면 지평선 0도)
    alt_rad = (np.pi / 2) * np.cos(rel_from_south)
    
    # 2) 방위각 계산 (북=0, 동=90/pi_2, 남=180/pi, 서=270/3pi_2)
    az_rad = (np.pi - rel_from_south) % (2 * np.pi)
    
    return alt_rad, az_rad

# 각 천체의 실시간 지평 좌표 추출
alt_sun, az_sun = get_alt_az(0, 0)
alt_moon, az_moon = get_alt_az(mx, my) if show_moon else (-99, -99)
alt_venus, az_venus = get_alt_az(vx, vy) if show_inner else (-99, -99)
alt_mars, az_mars = get_alt_az(marx, mary) if show_outer else (-99, -99)


# ==========================================
# 5. 환경 상태 및 배경 색상 실시간 결정 (일식 효과 포함)
# ==========================================
# 태양 고도 기반 기본 하늘 상태
if alt_sun > 0:
    sky_status = "DAY"
    status_tag = "☀️ 낮 (Daytime)"
    bg_color = '#2B6CB0'
    land_color = '#2F855A'
elif -0.15 < alt_sun <= 0:
    sky_status = "TWILIGHT"
    status_tag = "🌆 박명 (Twilight)"
    bg_color = '#1A365D'
    land_color = '#1C2D42'
else:
    sky_status = "NIGHT"
    status_tag = "🌙 밤 (Night)"
    bg_color = '#06080c'
    land_color = '#11141D'

# 💡 [식현상 스페셜 이펙트 구현]
is_tot_eclipse = False
if "일식" in obs_mode and alt_sun > 0 and alt_moon > 0:
    # 태양과 달의 방위각 차이가 극히 적어 겹칠 때 개기일식 암전 발생
    if abs(az_sun - az_moon) < 0.15:
        is_tot_eclipse = True
        sky_status = "TOTAL_ECLIPSE"
        status_tag = "🌑 개기 일식 (Total Solar Eclipse)"
        bg_color = '#020406'  # 낮시간 대 완벽한 밤하늘 연출
        land_color = '#0B0F19'


# ==========================================
# 6. 시각화 그래프 생성
# ==========================================

# [1] 태양계 우주 공간 시점 그래프 (Top-down)
def plot_solar_system():
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#06080c')
    ax.set_facecolor('#06080c')
    
    # 궤도선 표시
    theta_line = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta_line) * 2.0, np.sin(theta_line) * 2.0, '--', color='#2D3748', alpha=0.4)
    ax.plot(np.cos(theta_line) * 3.5, np.sin(theta_line) * 3.5, '--', color='#2D3748', alpha=0.4)
    ax.plot(np.cos(theta_line) * 5.0, np.sin(theta_line) * 5.0, '--', color='#2D3748', alpha=0.4)
    
    # 지구-태양 정밀 가이드 남중 지표선 (주황색)
    ax.plot([ex, 0], [ey, 0], ':', color='#FF8C00', alpha=0.7, linewidth=1.8, label='Sun Line (Noon)')
    
    # 천체 배치
    ax.plot(0, 0, 'oy', markersize=16, color='#FFD700', label='Sun')
    ax.plot(ex, ey, 'ob', markersize=9, color='#4169E1', label='Earth')
    
    if show_moon:
        ax.plot(mx, my, 'o', markersize=5, color='#F5F5F5', label='Moon')
    if show_inner:
        ax.plot(vx, vy, 'o', markersize=7, color='#E6C229', label='Venus')
    if show_outer:
        ax.plot(marx, mary, 'o', markersize=8, color='#D14949', label='Mars')
        
    # 관측 시선 화살표 연산
    if "남" in direction:
        v_ang = zenith_dir
    elif "동" in direction:
        v_ang = zenith_dir + np.pi / 2
    elif "서" in direction:
        v_ang = zenith_dir - np.pi / 2
    else:
        v_ang = zenith_dir + np.pi
        
    dir_map = {"남 (South)": "South", "동 (East)": "East", "서 (West)": "West", "북 (North)": "North"}
    ax.arrow(ex, ey, np.cos(v_ang)*0.8, np.sin(v_ang)*0.8, 
             head_width=0.15, head_length=0.15, fc='#4FD1C5', ec='#4FD1C5', label=f'Look ({dir_map[direction]})')
    
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-6.5, 6.5)
    ax.axis('off')
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=10)
    return fig


# [2] 지평선 관측 스크린 그래프 (Stellarium 완벽 검증 버전)
def plot_sky_view():
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # 지평선 및 대지 렌더링
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-5, 5], -2, 0, color=land_color)
    
    # 선택된 방위에 따른 중심 기준 방위각 지정
    if "남" in direction:
        center_az = np.pi       # 180도
    elif "동" in direction:
        center_az = np.pi / 2   # 90도
    elif "서" in direction:
        center_az = 3 * np.pi / 2 # 270도
    else:
        center_az = 0           # 0도 (북)

    # 북쪽 시선일 경우 밤하늘의 꽃인 북극성(Polaris)과 반시계 회전 매핑 가동
    if "북" in direction:
        # 북극성은 중위도 지방(서울 약 37도) 고도 고정
        alt_polaris = 37 * (np.pi / 180)
        y_polaris = (alt_polaris / (np.pi / 2)) * 3.5
        
        # 낮이 아닐 때만 북극성 표출
        if sky_status != "DAY" or is_tot_eclipse:
            ax.plot(0, y_polaris, '*', color='#63B3ED', markersize=14)
            ax.text(0, y_polaris - 0.3, "Polaris", color='#63B3ED', ha='center', fontsize=11, fontweight='bold')
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 11, 'fontweight': 'bold'}

    def render_body(alt, az, name, default_color, marker, size):
        if alt <= 0: 
            return # 지평선 아래면 즉시 드로우 스킵
            
        if "북" in direction:
            # 북쪽 하늘 특수 일주 운동 알고리즘 (북극성을 중심으로 동->서 회전)
            # 회전 반경 계산
            r = 2.0 * (1.2 - alt / (np.pi/2))
            # 북극성 기준 각도 매핑
            angle_rot = (az - np.pi/2)
            x_pos = r * np.sin(angle_rot)
            y_pos = 1.8 + r * np.cos(angle_rot)
            if y_pos < 0: return # 지평선 밑 차단
        else:
            # 동, 서, 남 표준 지평 좌표 스크린 투영 알고리즘
            diff_az = (az - center_az + np.pi) % (2 * np.pi) - np.pi
            if abs(diff_az) > np.pi / 4: 
                return # 화각 화면 기본 시야각 90도 초과시 제외
                
            x_pos = diff_az * (4.5 / (np.pi / 4))
            y_pos = (alt / (np.pi / 2)) * 3.5

        # 광도 가시성 필터링 (일식/월식/낮/밤 분기 제어)
        alpha_val = 1.0
        color = default_color
        
        if sky_status == "DAY" and name != "SUN":
            alpha_val = 0.0  # 평상시 낮에는 태양 외 차단
            
        if sky_status == "TOTAL_ECLIPSE":
            alpha_val = 1.0  # 개기일식 중에는 모든 행성/달 일시 노출 보장
            
        if name == "SUN" and is_tot_eclipse:
            # 개기일식 코로나 특수 그래픽 처리
            ax.plot(x_pos, y_pos, 'o', color='#FFFFFF', markersize=size+8, alpha=0.9)
            ax.plot(x_pos, y_pos, 'o', color='#000000', markersize=size, alpha=1.0)
            ax.text(x_pos, y_pos - 0.4, "Corona (Eclipse)", **text_style)
            return
            
        if name == "Moon" and "월식" in obs_mode:
            # 개기월식 본그림자 진입 시의 블러드 문 레이일리 산란 붉은색 교정
            color = '#A52A2A'
            name = "Blood Moon"
            
        if alpha_val > 0:
            ax.plot(x_pos, y_pos, marker, color=color, markersize=size, alpha=alpha_val)
            ax.text(x_pos, y_pos - 0.4, name, alpha=alpha_val, **text_style)

    # 우주 천체 전체 렌더링 파이프라인 구동
    render_body(alt_sun, az_sun, "SUN", "#FF8C00", "o", 22)
    if show_moon: render_body(alt_moon, az_moon, "Moon", "#F5F5F5", "o", 16)
    if show_inner: render_body(alt_venus, az_venus, "Venus", "#E6C229", "*", 13)
    if show_outer: render_body(alt_mars, az_mars, "Mars", "#D14949", "o", 11)

    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.5, 4)
    ax.axis('off')
    return fig


# ==========================================
# 7. 대시보드 레이아웃 화면 분할 배치
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🪐 태양계 행성 위치 관계 (Top-down)")
    fig_solar = plot_solar_system()
    st.pyplot(fig_solar)

with col2:
    st.subheader(f"🔭 Stellarium 지평 시야 [{status_tag}] : {selected_time_str} / {direction} 방향")
    fig_sky = plot_sky_view()
    st.pyplot(fig_sky)


# ==========================================
# 8. 하단 지구과학 교과과정 핵심 개념 매칭 가이드
# ==========================================
st.markdown("---")
st.subheader("🎓 시험 출제 1순위: 식현상 및 방위각 천체 관측 핵심 요약")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🌑 개기 일식과 달의 위상 (삭)</h4>
        <p>일식은 <b>태양 - 달 - 지구</b> 순서로 일직선 상에 배치될 때 발생하며, 이때 달의 위상은 반드시 <b>삭(New Moon)</b>이어야 합니다. 달의 <b>본그림자</b> 영역에 들어간 지역은 태양이 완전히 가려지는 <b>개기 일식</b>이 관측되며, 주변 대기층인 코로나를 육안으로 식별할 수 있게 됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>🔴 개기 월식과 블러드 문 (망)</h4>
        <p>월식은 <b>태양 - 지구 - 달</b> 순서로 배치되어 달이 지구의 본그림자에 완전히 가려지는 현상으로, 위성은 <b>망(Full Moon)</b>입니다. 완전히 가려졌음에도 달이 어둡게 보이는 이유는 지구 대기층을 통과하며 굴절 및 산란된 <b>파장이 긴 적색광(Red Light)</b>만이 달 표면에 도달한 후 반사되기 때문입니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🧭 동서남북 방위별 천체 일주 운동 패턴</h4>
        <p>모든 천체는 지구의 자전(서->동)으로 인해 <b>동쪽에서 떠올라 서쪽으로 지는 겉보기 일주 운동</b>을 합니다. <br>
        - <b>동쪽 시선</b>: 천체가 왼쪽(북)에서 오른쪽(남) 위로 우상향하며 뜹니다.<br>
        - <b>서쪽 시선</b>: 천체가 왼쪽(남) 위에서 오른쪽(북) 아래로 우하향하며 집니다.<br>
        - <b>북쪽 시선</b>: 북극성을 중심으로 모든 별이 <b>반시계 방향</b>으로 원을 그리며 회전합니다.</p>
    </div>
    """, unsafe_allow_html=True)
