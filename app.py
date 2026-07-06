import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 1. 스트림릿 페이지 설정
st.set_page_config(layout="wide", page_title="지구과학 천체 시각화")
st.title("🌙 달의 공전 궤도와 위상 변화 시각화 시뮬레이션")
st.write("태양-지구-달의 위치 관계에 따라 지구에서 달이 어떻게 보이는지 확인해 보세요.")

# 2. 사이드바 - 제어 패널
st.sidebar.header("🕹️ 컨트롤러")
# 음력 1일(삭)부터 28일(그믐)까지 조절하는 슬라이더
lunar_day = st.sidebar.slider("음력 날짜 선택 (공전 주기)", min_value=0.0, max_value=28.0, value=7.0, step=0.5)

# 날짜에 따른 달의 공전 각도 계산 (라디안)
# 음력 0일(삭)일 때 태양 방향(오른쪽)에 위치한다고 가정
angle = (lunar_day / 28.0) * 2 * np.pi

# 달의 이름 결정
if 0 <= lunar_day < 2 or 26 < lunar_day <= 28:
    moon_name = "삭 (New Moon) - 볼 수 없음"
elif 2 <= lunar_day < 6:
    moon_name = "초승달 (Waxing Crescent)"
elif 6 <= lunar_day < 9:
    moon_name = "상현달 (First Quarter) - 오른쪽 반달"
elif 9 <= lunar_day < 13:
    moon_name = "차오르는 달 (Waxing Gibbous)"
elif 13 <= lunar_day < 16:
    moon_name = "망 (Full Moon) - 보름달"
elif 16 <= lunar_day < 20:
    moon_name = "이지러지는 달 (Waning Gibbous)"
elif 20 <= lunar_day < 23:
    moon_name = "하현달 (Third Quarter) - 왼쪽 반달"
else:
    moon_name = "그믐달 (Waning Crescent)"

st.sidebar.subheader(f"📅 선택한 날짜: 음력 약 {lunar_day}일")
st.sidebar.info(f"현재 달의 상태:\n**{moon_name}**")

---

# 3. 메인 화면 - 2단 레이아웃 분할 (우주 시점 vs 지구 시점)
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌌 우주 시점 (Space View)")
    st.caption("북극 상공에서 태양계 조망 (태양빛은 오른쪽에서 평행하게 들어옴)")
    
    # Matplotlib으로 우주 시점 그리기
    fig_space, ax_space = plt.subplots(figsize=(6, 6))
    ax_space.set_facecolor('#0b0c10')
    fig_space.patch.set_facecolor('#0b0c10')
    
    # 궤도선 그리기
    orbit = plt.Circle((0, 0), 3, color='gray', fill=False, linestyle='--', alpha=0.5)
    ax_space.add_patch(orbit)
    
    # 중심의 지구 (Earth)
    earth = plt.Circle((0, 0), 0.6, color='#1f77b4', label='지구')
    ax_space.add_patch(earth)
    # 지구의 낮과 밤 표현 (오른쪽이 낮, 왼쪽이 밤)
    earth_night = plt.Rectangle((-0.6, -0.6), 0.6, 1.2, color='#050505', alpha=0.7)
    ax_space.add_patch(earth_night)
    
    # 공전하는 달 (Moon) 위치 계산
    moon_x = 3 * np.cos(angle)
    moon_y = 3 * np.sin(angle)
    
    # 달 그리기 (기본 구체)
    moon = plt.Circle((moon_x, moon_y), 0.3, color='#f1c40f')
    ax_space.add_patch(moon)
    
    # 달의 밤 부분 (태양 반대편인 왼쪽 절반을 항상 어둡게 처리)
    # 달의 중심 기준 왼쪽을 가리는 박스 생성
    moon_night = plt.Rectangle((moon_x - 0.3, moon_y - 0.3), 0.3, 0.6, color='#2c3e50', alpha=0.9)
    # 햇빛 방향에 맞게 달의 그림자 고정 (항상 왼쪽이 어두움)
    # 단, 간단한 시각화를 위해 사각형 대신 평행한 그림자 효과를 처리
    ax_space.add_patch(moon_night)
    
    # 관측자 시선 표시 (지구에서 달을 바라보는 방향 화살표)
    ax_space.arrow(0, 0, moon_x*0.7, moon_y*0.7, head_width=0.15, head_length=0.15, fc='white', ec='white', linestyle=':')
    
    # 태양빛 방향 표시
    ax_space.annotate('☀️ 태양빛', xy=(4.5, 0), xytext=(5.5, 0),
                arrowprops=dict(facecolor='yellow', shrink=0.05, width=2, headwidth=6))
    
    # 그래프 축 및 범위 정리
    ax_space.set_xlim(-5, 6)
    ax_space.set_ylim(-5, 5)
    ax_space.axis('off')
    
    st.pyplot(fig_space)

with col2:
    st.subheader("👀 지구 시점 (Earth View)")
    st.caption("지구에서 남중했을 때 바라본 달의 실제 위상 모양")
    
    fig_view, ax_view = plt.subplots(figsize=(6, 6))
    ax_view.set_facecolor('#0b0c10')
    fig_view.patch.set_facecolor('#0b0c10')
    
    # 달의 외곽선
    full_moon_outline = plt.Circle((0, 0), 2, color='#2c3e50', fill=True)
    ax_view.add_patch(full_moon_outline)
    
    # 이각(Phase Angle) 계산에 따른 차오름 표현
    # cos(angle) 값에 따라 위상의 형태가 바뀜
    vis_ratio = np.cos(angle)
    
    # 위상 기하학적 시각화 (단순화된 원호 채우기)
    # 각도에 따라 보이는 형태를 마스킹 처리하여 달 모양 유도
    t = np.linspace(-np.pi/2, np.pi/2, 100)
    x_right = 2 * np.cos(t)
    y_right = 2 * np.sin(t)
    
    if np.sin(angle) >= 0:
        # 상현달 계열 (오른쪽이 차오름)
        if vis_ratio >= 0: # 초승~상현
            x_inner = 2 * vis_ratio * np.cos(t)
            ax_view.fill_betweenx(y_right, x_inner, x_right, color='#f1c40f')
        else: # 상현~보름
            x_inner = 2 * vis_ratio * np.cos(t)
            ax_view.fill_betweenx(y_right, -2, x_right, color='#f1c40f')
            ax_view.fill_betweenx(y_right, -2, x_inner, color='#f1c40f')
    else:
        # 하현달 계열 (왼쪽이 차오름)
        if vis_ratio <= 0: # 보름~하현
            x_inner = 2 * vis_ratio * np.cos(t)
            ax_view.fill_betweenx(y_right, -2, x_inner, color='#f1c40f')
        else: # 하현~그믐
            x_inner = 2 * vis_ratio * np.cos(t)
            ax_view.fill_betweenx(y_right, x_inner, 0, color='#f1c40f')
            # 왼쪽 반원 영역 조정
            ax_view.fill_betweenx(y_right, -2 * vis_ratio * np.cos(t), 0, color='#f1c40f')

    ax_view.set_xlim(-3, 3)
    ax_view.set_ylim(-3, 3)
    ax_view.axis('off')
    
    st.pyplot(fig_view)

---

# 4. 하단 과학적 개념 원리 설명
st.markdown("### 💡 지구과학 탐구 가이드")
st.markdown("""
* **달의 위상 변화 원리:** 달은 스스로 빛을 내지 못하고 태양빛을 반사하기 때문에, 달의 공전 위치에 따라 지구에서 보는 '빛나는 부분'의 면적이 달라집니다.
* **상현달 vs 하현달:** * **음력 7~8일경(상현):** 우주 시점에서 달이 지구의 '위쪽'에 위치하며, 지구에서는 **오른쪽**이 찬 반달로 보입니다. (초저녁 남쪽 하늘 관측)
    * **음력 21~22일경(하현):** 우주 시점에서 달이 지구의 '아래쪽'에 위치하며, 지구에서는 **왼쪽**이 찬 반달로 보입니다. (새벽녘 남쪽 하늘 관측)
""")
