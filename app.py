import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 한글 폰트 설정 (Windows/Mac 대응)
plt.rcParams['font.family'] = 'Malgun Gothic' # Mac의 경우 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 태양계 데이터 정의
# 계산의 편의를 위해 원궤도로 단순화한 태양계 모형을 사용 (PPT p.149 참고)
r_earth = 1.0       # 지구 궤도 반지름 (AU)
r_venus = 0.72      # 금성 궤도 반지름 (AU)

# 금성의 최대이각 계산 (sin(θ) = r_venus / r_earth)
max_elongation_rad = np.arcsin(r_venus / r_earth)
max_elongation_deg = np.degrees(max_elongation_rad)

# 2. PPT 기준에 따른 정확한 최대이각 기하학적 위치 정의 (북극 상공에서 내려다본 기준)
# 지구는 (0, -r_earth) 위치에 고정되어 태양(0,0)을 정면으로 바라본다고 가정
# [오류 수정]: 지구에서 태양을 바라볼 때 '오른쪽'이 동방최대이각, '왼쪽'이 서방최대이각

# 동방최대이각 (지구-태양 선 기준 오른쪽 / 반시계 공전 방향의 앞쪽)
theta_east = -np.pi/2 + max_elongation_rad
x_east = r_venus * np.cos(theta_east)
y_east = r_venus * np.sin(theta_east)

# 서방최대이각 (지구-태양 선 기준 왼쪽 / 반시계 공전 방향의 뒤쪽)
theta_west = -np.pi/2 - max_elongation_rad
x_west = r_venus * np.cos(theta_west)
y_west = r_venus * np.sin(theta_west)

# 3. 시각화 그래프 설정
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_title("PPT 관측 기준 내행성(금성)의 궤도와 최대이각 위치", fontsize=14, fontweight='bold')

# 궤도 그리기 (반시계 방향 공전)
angles = np.linspace(0, 2*np.pi, 200)
ax.plot(r_earth * np.cos(angles), r_earth * np.sin(angles), 'b--', label='지구 궤도', alpha=0.6)
ax.plot(r_venus * np.cos(angles), r_venus * np.sin(angles), 'r-', label='금성 궤도', alpha=0.8)

# 천체 고정 위치 마커
ax.plot(0, 0, 'yo', markersize=15, label='태양')
ax.plot(0, -r_earth, 'go', markersize=10, label='지구 (관측자)')

# [정정된 위치 반영] 최대이각 포인트 plotted
ax.plot(x_east, y_east, 'ro', markersize=8, label=f'동방최대이각 (이각: {max_elongation_deg:.1f}°)')
ax.plot(x_west, y_west, 'mo', markersize=8, label=f'서방최대이각 (이각: {max_elongation_deg:.1f}°)')

# 지구에서 각 최대이각으로 향하는 시선(접선) 그리기
ax.plot([0, x_east], [-r_earth, y_east], 'r:', alpha=0.7)
ax.plot([0, x_west], [-r_earth, y_west], 'm:', alpha=0.7)

# PPT 핵심 관측 기준 가이드 텍스트 및 화살표 추가
ax.text(0.4, -0.6, "▶ 동방최대이각\n- 지구-태양 기준 오른쪽\n- 저녁(초저녁) 서쪽하늘 관찰", color='red', fontsize=9)
ax.text(-0.9, -0.6, "◀ 서방최대이각\n- 지구-태양 기준 왼쪽\n- 새벽 동쪽하늘 관찰", color='purple', fontsize=9)
ax.text(0, -1.15, "※ 북극에서 내려다봄 (모든 공전 및 자전은 반시계 방향)", color='black', fontsize=9, ha='center')

ax.legend(loc='upper right')

# 4. 애니메이션 구현: "동방최대이각 → 내합 → 서방최대이각 → 외합" 순서 시뮬레이션
# PPT p.149: 내행성이 더 빠르므로 이 순서대로 겉보기 운동이 진행됨
planet_marker, = ax.plot([], [], 'ko', markersize=9, label='행성의 실제 운동')
status_text = ax.text(-1.1, 1.0, '', fontsize=11, fontweight='bold', 
                      bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

# 동방최대이각에서 시작해서 반시계 방향으로 한 바퀴 도는 프레임 제어
# 시작 각도를 theta_east로 설정하여 PPT 진행 순서와 정렬
frame_angles = np.linspace(theta_east, theta_east + 2*np.pi, 120)

def update(frame):
    current_theta = frame_angles[frame]
    # 0 ~ 2π 범위로 정규화하여 상태 판별
    norm_theta = (current_theta + np.pi/2) % (2*np.pi)
    
    x = r_venus * np.cos(current_theta)
    y = r_venus * np.sin(current_theta)
    planet_marker.set_data([x], [y])
    
    # 궤도 상의 위치별 PPT 개념 매칭 텍스트 업데이트
    current_deg = np.degrees(norm_theta)
    if abs(current_deg - max_elongation_deg) < 3:
        status = "★ 동방최대이각 (저녁 관찰, 오른쪽 반달)"
    elif abs(current_deg - 90) < 3:
        status = "■ 내합 (관찰 불가 X, 지구와 가장 가까움)"
    elif abs(current_deg - (180 + (180 - max_elongation_deg))) < 3:
        status = "★ 서방최대이각 (새벽 관찰, 왼쪽 반달)"
    elif abs(current_deg - 270) < 3:
        status = "■ 외합 (관찰 불가 X, 지구와 가장 멂)"
    elif 0 < current_deg < 90:
        status = "동방최대이각 → 내합 진행 중 (저녁 관찰)"
    elif 90 < current_deg < 270:
        status = "내합 → 서방최대이각 → 외합 진행 중 (새벽 관찰)"
    else:
        status = "외합 → 동방최대이각 진행 중"
        
    status_text.set_text(f"현재 행성 상태:\n{status}")
    return planet_marker, status_text

ani = animation.FuncAnimation(fig, update, frames=len(frame_angles), interval=50, blit=True)

plt.show()
