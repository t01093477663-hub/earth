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
st.caption("방위 선택에 따른 시점 화살표 동적 연동 및 태양 고도 계산 공식을 적용하여 시각적 정밀도를 극대화했습니다.")

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

# [B] 지구 자전 각도 계산
# 관측자가 정오(12:00)일 때 태양을 정면(남중)으로 바라보도록 기준 정렬
rotation_angle = earth_orb_ang + ((time_hours - 12.0) / 24.0) * 2 * np.pi

# 각 천체의 좌표 (태양 중심)
ex, ey = np.cos(earth_orb_ang) * 3.5, np.sin(earth_orb_ang) * 3.5
vx, vy = np.cos(venus_orb_ang) * 2.0, np.sin(venus_orb_ang) * 2.0
mx, my = ex + np.cos(moon_orb_ang) * 0.6, ey + np.sin(moon_orb_ang) * 0.6
marx, mary = np.cos(mars_orb_ang) * 5.0, np.sin(mars_orb_ang) * 5.0


# ==========================================
# 4. 상대 방위각 및 실시간 낮/밤 상태 연동
# ==========================================
def get_altitude_and_azimuth(target_x, target_y):
    rx, ry = target_x - ex, target_y - ey
    target_abs_ang = np.arctan2(ry, rx)
    ang_diff = target_abs_ang - rotation_angle
    # -pi에서 pi 사이로 정규화
    return (ang_diff + np.pi) % (2 * np.pi) - np.pi

# 천체별 상대 각도 결정
ang_sun   = get_altitude_and_azimuth(0, 0)
ang_moon  = get_altitude_and_azimuth(mx, my)
ang_venus = get_altitude_and_azimuth(vx, vy)
ang_mars  = get_altitude_and_azimuth(marx, mary)

# 낮/밤/박명 시간대 기준 판정
is_daytime_zone = (6.0 <= time_hours <= 18.0)

if is_daytime_zone:
    sky_status = "DAY"
    status_tag = "☀️ 낮 (Daytime)"
    bg_color = '#2B6CB0'      # 완연한 낮 (밝은 파란색)
    land_color = '#2F855A'
elif (4.5 <= time_hours < 6.0) or (18.0 < time_hours <= 19.5):
    sky_status = "TWILIGHT"
    status_tag = "🌆 박명 (Twilight)"
    bg_color = '#1A365D'      # 노을/새벽 박명 (어두운 푸른색)
    land_color = '#1C2D42'
else:
    sky_status = "NIGHT"
    status_tag = "🌙 밤 (Night)"
    bg_color = '#06080c'      # 완전한 밤 (블랙)
    land_color = '#11141D'


# ==========================================
# 5. 시각화 그래프 생성
# ==========================================

# [1] 태양계 위치 관계 그래프 (Top-down)
def plot_solar_system(dir_setting):
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
        
    # 💡 [피드백 반영 1]: 동서남북 시점 선택에 따른 관측자 시선 화살표 각도 동적 계산
    if "남" in dir_setting:
        arrow_angle = rotation_angle + np.pi      # 태양 방향 (남중 기준)
        label_dir = "South"
    elif "서" in dir_setting:
        arrow_angle = rotation_angle + np.pi/2    # 남쪽에서 우측으로 90도 회전
        label_dir = "West"
    elif "동" in dir_setting:
        arrow_angle = rotation_angle - np.pi/2    # 남쪽에서 좌측으로 90도 회전
        label_dir = "East"
    else:
        arrow_angle = rotation_angle              # 북극성 방향
        label_dir = "North"
        
    arrow_len = 0.8
    ax.arrow(ex, ey, np.cos(arrow_angle)*arrow_len, np.sin(arrow_angle)*arrow_len, 
             head_width=0.15, head_length=0.15, fc='#4FD1C5', ec='#4FD1C5', label=f'Observer ({label_dir})')
    
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
    def draw_object(ang, name, color, marker, size, y_pos=1.8):
        x_pos = None
        # 방위각 매핑 수식
        if "남" in dir_setting:
            if -np.pi/4 <= ang <= np.pi/4: x_pos = -ang * (4 / (np.pi/4))
        elif "서" in dir_setting:
            offset_ang = (ang + np.pi/2 + np.pi) % (2 * np.pi) - np.pi
            if -np.pi/4 <= offset_ang <= np.pi/4: x_pos = -offset_ang * (4 / (np.pi/4))
        elif "동" in dir_setting:
            offset_ang = (ang - np.pi/2 + np.pi) % (2 * np.pi) - np.pi
            if -np.pi/4 <= offset_ang <= np.pi/4: x_pos = -offset_ang * (4 / (np.pi/4))
            
        if x_pos is not None:
            # 태양과 가깝게 겹치는 합 위치의 타 천체 숨김 처리
            if name != "SUN":
                elongation = abs(ang - ang_sun)
                elongation = (elongation + np.pi) % (2 * np.pi) - np.pi
                if abs(elongation) < 0.17:
                    return

            # 💡 [피드백 반영 2]: 새벽 2시 등 밤 시간대에 태양이 하늘에 뜨던 오류 원천 해결
            # 낮/밤/박명 및 고도값(y_pos)에 따른 가시성(alpha) 제어 조건 구조 교정
            if name == "SUN":
                alpha_val = 1.0 if y_pos > 0 else 0.0
            elif sky_status == "DAY":
                alpha_val = 0.0  # 낮에는 태양 외 천체 가림
            elif sky_status == "TWILIGHT":
                alpha_val = 0.6 if name in ["Venus", "Moon"] else 0.0
            else:
                alpha_val = 1.0  # 완전한 밤에는 100% 노출 (지평선 위 천체만)
                
            # 최종 고도가 지평선(0)보다 높고 가시성이 유효할 때만 화면에 렌더링
            if alpha_val > 0 and y_pos > 0:
                ax.plot(x_pos, y_pos, marker, color=color, markersize=size, alpha=alpha_val)
                ax.text(x_pos, y_pos - 0.5, name, alpha=alpha_val, **text_style)

    # 방위 및 천체 렌더링 호출
    if "북" in dir_setting:
        alpha_polaris = 0.0 if sky_status == "DAY" else (0.3 if sky_status == "TWILIGHT" else 1.0)
        if alpha_polaris > 0:
            ax.plot(0, 2.3, '*', color='#63B3ED', markersize=14, alpha=alpha_polaris)
            ax.text(0, 1.7, "Polaris", color='#63B3ED', ha='center', fontsize=13, fontweight='bold', alpha=alpha_polaris)
    else:
        # 💡 [과학적 모델링 보완]: 태양의 고도를 시간축에 연동시켜 정밀 연산 (6시 일출, 12시 남중, 18시 일몰 기하 매핑)
        if 4.5 <= time_hours <= 19.5:
            sun_y = 0.1 + 2.9 * np.sin((time_hours - 6.0) / 12.0 * np.pi)
        else:
            sun_y = -1.0  # 새벽 및 심야 시간에는 지평선 아래(-1.0)로 강제 정렬하여 화면 미출력
            
        # 1. 태양 배치 (고도 수식 적용)
        draw_object(ang_sun, "SUN", "#FF8C00", "o", 24, y_pos=sun_y)
        
        # 2. 기타 필터 천체들
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
    fig_solar = plot_solar_system(direction)
    st.pyplot(fig_solar)

with col2:
    st.subheader(f"🔭 시야 [{status_tag}] : {selected_time_str} / {direction} 하늘")
    fig_sky = plot_sky_view(direction)
    st.pyplot(fig_sky)


# ==========================================
# 7. 하단 지구과학 핵심 개념 매칭 가이드 (피드백 반영 내용 전면 전개)
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
        <p><b>내행성(금성 등)</b>은 공전 궤도가 지구 안쪽에 있어 태양과 이루는 이각이 항상 제한적입니다. 따라서 한밤중에는 볼 수 없고 주로 <b>초저녁(동방최대이각, 서쪽 하늘)</b>이나 <b>새벽녘(서방최대이각, 동쪽 하늘)</b>에 잠시 관측됩니다. 반면 <b>외행성(화성 등)</b>은 <b>충 위치에 있을 때 남중하여 밤새도록 관측</b>이 가능합니다.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <h4>🌗 일식과 월식이 매달 일어나지 않는 이유</h4>
        <p>일식은 <b>삭(태양-달-지구)</b>일 때 달이 태양을 가리고, 월식은 <b>망(태양-지구-달)</b>일 때 달이 지구 본그림자에 잠기는 현상입니다. 이들이 매달 관측되지 않는 과학적 이유는 <b>지구 공전 궤도면(황도)과 달 공전 궤도면(백도)이 약 5° 정밀하게 기울어져 있기 때문</b>이며, 두 궤도면의 교선 위에서만 현상이 성립합니다.</p>
    </div>
    """, unsafe_allow_html=True)
