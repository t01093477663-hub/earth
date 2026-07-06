import streamlit as st
import pandas as pd
import numpy as np

# 1. 웹페이지 제목 설정
st.title("🎈 나의 첫 스트림릿 웹사이트")
st.write("깃허브와 스트림릿을 연동하여 만든 웹앱입니다.")

# 2. 사이드바 만들기
st.sidebar.header("설정 메뉴")
user_name = st.sidebar.text_input("이름을 입력하세요:", "홍길동")

# 3. 사용자 상호작용 버튼
if st.button("환영 인사 받기"):
    st.balloons()  # 화면에 풍선이 날아다니는 효과
    st.success(f"🎉 {user_name}님, 환영합니다! 웹사이트가 성공적으로 작동 중입니다.")

---

# 4. 간단한 데이터 차트 그리기
st.subheader("📊 샘플 데이터 차트")

# 무작위 데이터 생성 (10행 3열)
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['라인 A', '라인 B', '라인 C']
)

# 스트림릿 전용 라인 차트 출력
st.line_chart(chart_data)
