import streamlit as st
from src.ui.common import apply_custom_css, setup_sidebar
from src.ui.tab1_single import render_tab1
from src.ui.tab2_batch import render_tab2
from src.ui.tab3_labeling import render_tab3
from src.ui.tab4_guide import render_tab4

# 페이지 설정
st.set_page_config(
    page_title="비정형 데이터 품질진단 프로그램",
    page_icon=None,
    layout="wide"
)

# CSS 적용
apply_custom_css()

# 제목 및 설명
st.title("AI 학습용 비정형데이터 품질진단 프로그램")
st.caption("텍스트 또는 이미지를 업로드하면 품질점수를 자동으로 계산합니다.")

# 사이드바 설정
setup_sidebar()

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["단일 파일 분석", "데이터셋 배치 분석", "라벨링 기반 평가", "품질 지표 가이드"])

# 각 탭 렌더링 (with 컨텍스트 안에서 호출)
with tab1:
    render_tab1(tab1)

with tab2:
    render_tab2(tab2)

with tab3:
    render_tab3(tab3)

with tab4:
    render_tab4(tab4)
