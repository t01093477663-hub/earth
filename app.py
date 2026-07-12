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
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔭 지구과학 I 천체 관측 시뮬레이터")
st.caption("시점 화살표의 방향과 2D 관측 시야 스크린의 가시 영역을 기하학적으로 100% 동기화하여 오류를 해결했습니다.")

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

# [B] 지구 자전 및 관측자 방위각 정밀 연동
# 태양 방향 절대각 = earth_orb_ang + np.pi
# 정오(12:00)일 때 자전각이 정확히 태양(남쪽)을 향하도록 정렬
rotation_angle = (earth_orb_ang + np.pi) + ((time_hours - 12.0) / 24.0) * 2 * np.pi
rotation_angle = (rotation_angle + np.pi) % (2 * np.pi) - np.pi

# 선택한 시선 방향의 절대 각도 설정
if "남" in direction:
    view_angle = rotation_angle
elif "동" in direction:
    view_angle = rotation_angle + np.pi / 2
elif "서" in direction:
    view_angle = rotation_angle - np.pi / 2
else:  # 북
    view_angle = rotation_angle + np.pi
view_angle = (view_angle + np.pi) % (2 * np.pi) - np.pi

# 각 천체의 좌표 (태양 중심)
ex, ey = np.cos(earth_orb_ang) * 3.5, np.sin(earth_orb_ang) * 3.5
vx, vy = np.cos(venus_orb_ang) * 2.0, np.sin(venus_orb_ang) * 2.0
mx, my = ex + np.cos(moon_orb_ang) * 0.6, ey + np.sin(moon_orb_ang) * 0.6
marx, mary = np.cos(mars_orb_ang) * 5.0, np.sin(mars_orb_ang) * 5.0


# ==========================================
# 4. 태양 고도 기반 낮/밤/박명 상태 실시간 결정
# ==========================================
rx_sun, ry_sun = 0 - ex, 0 - ey
ang_sun = np.arctan2(ry_sun, rx_sun)
# 태양의 머리 위(Zenith=rotation_angle) 기준 상대 각도 계산
rel_zenith_sun = (ang_sun - rotation_angle + np.pi) % (2 * np.pi) - np.pi

if abs(rel_zenith_sun) <= np.pi / 2:
    sky_status = "DAY"
    status_tag = "☀️ 낮 (Daytime)"
    bg_color = '#2B6CB0'      # 밝은 파란색
    land_color = '#2F855A'
elif np.pi / 2 < abs(rel_zenith_sun) <= (np.pi / 2 + 0.15):
    sky_status = "TWILIGHT"
    status_tag = "🌆 박명 (Twilight)"
    bg_color = '#1A365D'      # 어두운 푸른색
    land_color = '#1C2D42'    # 들여쓰기 오류 수정 완료 부분
else:
    sky_status = "NIGHT"
    status_tag = "🌙 밤 (Night)"
    bg_color = '#06080c'      # 완전한 블랙
    land_color = '#11141D'


# ==========================================
# 5. 시각화 그래프 생성
# ==========================================

# [1] 태양계 위치 관계 그래프 (Top-down)
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
        
    # 시점 화살표 (관측자가 선택한 방위를 가리킴)
    arrow_len = 0.8
    ax.arrow(ex, ey, np.cos(view_angle)*arrow_len, np.sin(view_angle)*arrow_len, 
             head_width=0.15, head_length=0.15, fc='#4FD1C5', ec='#4FD1C5', label=f'Observer ({direction.split()[0]})')
    
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-6.5, 6.5)
    ax.axis('off')
    ax.legend(loc='upper right', facecolor='#111622', edgecolor='#2D3748', labelcolor='white', fontsize=10)
    return fig


# [2] 지평선 관측 시야 그래프 (완벽한 하드웨어식 화살표 시야 동기화)
def plot_sky_view(dir_setting):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # 지평선 구조
    ax.axhline(0, color='#4A5568', linewidth=2)
    ax.fill_between([-5, 5], -2, 0, color=land_color)
    
    text_style = {'color': '#FFFFFF', 'ha': 'center', 'fontsize': 13, 'fontweight': 'bold'}

    # 2D 동적 스크린 매핑 함수
    def draw_object(target_x, target_y, name, color, marker, size):
        # 지구에서 천체를 바라보는 절대 방향 각도
        rx, ry = target_x - ex, target_y - ey
        angle_from_earth = np.arctan2(ry, rx)
        
        # ① 지평선 필터 (고도 계산)
        # 관측자 천정(rotation_angle)과의 각도 격차 측정
        rel_zenith = (angle_from_earth - rotation_angle + np.pi) % (2 * np.pi) - np.pi
        if abs(rel_zenith) > np.pi / 2:
            return  # 지평선 아래에 있으므로 즉시 렌더링 제외
            
        # 고도각 정규화 계산 (0=지평선, 1=천정)
        alt_ratio = (np.pi/2 - abs(rel_zenith)) / (np.pi/2)
        y_pos = 0.3 + 3.2 * alt_ratio
        
        # ② 시야 범위 필터 (방위각 계산)
        # 관측자가 바라보는 정면 시선각(view_angle)과의 차이 계산
        rel_view = (angle_from_earth - view_angle + np.pi) % (2 * np.pi) - np.pi
        
        # 양측 45도(총 90도 화각)를 벗어나면 절대 그리지 않음 (화살표 시선과 100% 일치)
        if abs(rel_view) > np.pi / 4:
            return
            
        # 화면의 가로 축(-4.5에서 4.5)으로 매핑 (좌우 반전 교정)
        x_pos = - rel_view * (4.5 / (np.pi / 4))
        
        # ③ 태양빛 광도에 따른 가시성 조건 제어
        if name == "SUN":
            alpha_val = 1.0
        elif sky_status == "DAY":
            alpha_val = 0.0  # 낮에는 태양 이외 차단
        elif sky_status == "TWILIGHT":
            alpha_val = 0.6 if name in ["Venus", "Moon"] else 0.0
        else:
            alpha_val = 1.0  # 완전한 밤에는 노출
            
        if alpha_val > 0:
            ax.plot(x_pos, y_pos, marker, color=color, markersize=size, alpha=alpha_val)
            ax.text(x_pos, y_pos - 0.4, name, alpha=alpha_val, **text_style)

    # 방위 및 천체 렌더링 호출
    if "북" in dir_setting:
        alpha_polaris = 0.0 if sky_status == "DAY" else (0.4 if sky_status == "TWILIGHT" else 1.0)
        if alpha_polaris > 0:
            ax.plot(0, 2.3, '*', color='#63B3ED', markersize=14, alpha=alpha_polaris)
            ax.text(0, 1.8, "Polaris", color='#63B3ED', ha='center', fontsize=13, fontweight='bold', alpha=alpha_polaris)
    else:
        # 천체별 배치 연산 수행
        draw_object(0, 0, "SUN", "#FF8C00", "o", 24)
        if show_moon:
            draw_object(mx, my, "Moon", "#F5F5F5", "o", 18)
        if show_inner:
            draw_object(vx, vy, "Venus", "#E6C229", "*", 14)
        if show_outer:
            draw_object(marx, mary, "Mars", "#D14949", "o", 11)
            
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
st.subheader("🎓 지구과학 I 기말고사 천체 관측 핵심 정리")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h4>🪐 행성의 순행과 역행 (겉보기 운동)</h4>
        <p>행성이 배경 별자리를 기준으로 <b>서쪽에서 동쪽</b>으로 이동하면 <b>순행</b>, <b>동쪽에서 서쪽</b>으로 이동하면 <b>역행</b>이라 합니다. 내행성은 지구와 가장 가까운 <b>내합</b> 부근에서 역행을 보이며, 외행성은 태양의 정반대편인 <b>충</b> 부근에서 지구와의 공전 속도 차이로 인해 역행 현상이 뚜렷하게 관찰됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <h4>🔭 내행성과 외행성의 관측 시간과 위치</h4>
        <p><b>내행성(금성 등)</b>은 공전 궤도가 지구 안쪽에 있어 태양와 이루는 이각이 항상 제한적입니다. 따라서 한밤중에는 볼 수 없고 주로 <b>초저녁(동방최대이각, 서쪽 하늘)</b>이나 <b>새벽녘(서방최대이각, 동쪽 하늘)</b>에 잠시 관측됩니다. 반면 <b>외행성(화성 등)</b>은 <b>충 위치에 있을 때 남중하여 밤새도록 관측</b>이 가능합니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🌗 일식과 월식이 매달 일어나지 않는 이유</h4>
        <p>일식은 <b>삭(태양-달-지구)</b>일 때 달이 태양을 가리고, 월식은 <b>망(태양-지구-달)</b>일 때 달이 지구 본그림자에 잠기는 현상입니다. 이들이 매달 관측되지 않는 과학적 이유는 <b>지구 공전 궤도면(황도)과 달 공전 궤도면(백도)이 약 5° 정밀하게 기울어져 있기 때문</b>이며, 두 궤도면의 교선 위에서만 현상이 성립합니다.</p>
    </div>
    """, unsafe_allow_html=True)
