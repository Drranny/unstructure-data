import streamlit as st
from src.text_quality import analyze_text_quality
from src.image_quality import analyze_image_quality
from src.utils import (
    calc_total_score, 
    get_grade,
    generate_text_report_pdf,
    generate_image_report_pdf,
    generate_dataset_report_pdf
)
from datetime import datetime
from src.dataset_analyzer import (
analyze_dataset_images,
analyze_dataset_texts,
load_cifar10,
load_tid2013,
load_custom_dataset,
load_huggingface_dataset,
load_huggingface_text_dataset
)
from src.dataset_finder import (
search_huggingface_datasets,
get_popular_datasets,
get_predefined_datasets
)

st.set_page_config(
    page_title="비정형 데이터 품질진단 프로그램",
    page_icon=None,
    layout="wide"
)

#블루/화이트테마CSS적용
# 블루/화이트 테마 CSS 적용
st.markdown("""
<style>
/*전반적인블루/화이트테마*/
.main{
background-color: #FFFFFF;
}

/*제목스타일*/
h1{
color: #1f4e79;
b der-bottom: 3px solid#4472c4;
padding-bottom: 10px;
margin-bottom: 20px;
}

h2,h3{
color: #2e75b6;
}

/*버튼스타일*/
.stButton>button{
background-color: #4472c4;
color:white;
b der: none;
b der-radius: 5px;
padding: 10px 20px;
font-weight: 500;
}

.stButton>button:hover{
background-color: #2e75b6;
}

/*메트릭카드스타일*/[data-testid = "stMetricValue"]{
color: #2e75b6;
font-weight: bold;
}

/*테이블헤더스타일*/
theadth{
background-color: #d9e2f3;
color: #1f4e79;
}

/*성공/정보메시지스타일*/
.stSuccess{
background-color: #d9e8f5;
b der-left: 4px solid#4472c4;
}

.stInfo{
background-color: #e8f0f8;
b der-left: 4px solid#2e75b6;
}

/*경고메시지*/
.stWarning{
background-color: #fff4e6;
b der-left: 4px solid#ffa500;
}

/*탭스타일*/
.stTabs[data-baseweb = "tab-list"]{
gap: 8px;
}

.stTabs[data-baseweb = "tab"]{
color: #2e75b6;
b der: 1px solid#d9e2f3;
background-color: #f5f8fb;
}

.stTabs[aria-selected = "true"]{
background-color: #4472c4;
color:white;
}

/*파일업로더스타일*/
.uploadedFile{
background-color: #e8f0f8;
b der: 1px solid#d9e2f3;
}
</style>
""",unsafe_allow_html = True)

st.title("AI 학습용 비정형데이터 품질진단 프로그램")
st.caption("텍스트 또는 이미지를 업로드하면 품질점수를 자동으로 계산합니다.")

#탭생성
tab1, tab2 = st.tabs(["단일 파일 분석", "데이터셋 배치 분석"])

# 사이드바에 샘플 데이터 테스트 옵션 추가
with st.sidebar:
    st.header("빠른 테스트")
    st.markdown("샘플 데이터로 테스트해보세요!")
    
    if st.button("샘플 텍스트 테스트"):
        sample_text_path = "data/test_texts/sample_text.txt"
        try:
            with open(sample_text_path, "r", encoding="utf-8") as f:
                sample_text = f.read()
                st.session_state['sample_text'] = sample_text
                st.success("샘플 텍스트를 불러왔습니다!")
        except FileNotFoundError:
            st.error("샘플 파일을 찾을 수 없습니다.")

# ========== 탭 1: 단일 파일 분석 ==========
with tab1:
    st.header("파일 업로드 및 분석")
    
    # Step 1: 파일 업로드
    uploaded_file = st.file_uploader(
        "Step 1: 파일 선택",
        type=["txt", "jpg", "jpeg", "png", "gif", "bmp"],
        help="분석할 텍스트 또는 이미지 파일을 선택하세요"
    )
    
    # Step 2: 파일 타입 선택
    if uploaded_file is not None:
        st.success(f"파일 업로드 완료: {uploaded_file.name}")
        
        # 파일 타입 추측
        file_ext = uploaded_file.name.lower()
        is_text_file = file_ext.endswith('.txt')
        is_image_file = any(file_ext.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp'])
        
        st.subheader("Step 2: 파일 타입 선택")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("텍스트 파일로 분석", use_container_width=True, type="primary" if is_text_file else "secondary"):
                st.session_state['file_type'] = 'text'
                st.session_state['uploaded_file'] = uploaded_file
                st.rerun()
        
        with col2:
            if st.button("이미지 파일로 분석", use_container_width=True, type="primary" if is_image_file else "secondary"):
                st.session_state['file_type'] = 'image'
                st.session_state['uploaded_file'] = uploaded_file
                st.rerun()
    
        # 파일 타입이 선택되었는지 확인
        if 'file_type' not in st.session_state:
            if is_text_file:
                st.info("이 파일은 텍스트 파일로 보입니다. '텍스트 파일로 분석' 버튼을 클릭하세요.")
            elif is_image_file:
                st.info("이 파일은 이미지 파일로 보입니다. '이미지 파일로 분석' 버튼을 클릭하세요.")
            else:
                st.warning("파일 형식을 확인할 수 없습니다. 타입을 선택해주세요.")
    
    # Step 3: 분석 실행
    if 'file_type' in st.session_state and 'uploaded_file' in st.session_state:
        st.divider()
        st.subheader("Step 3: 분석 실행")
        
        uploaded_file = st.session_state['uploaded_file']
        file_type = st.session_state['file_type']
    
        if file_type == 'text':
            st.info("**텍스트 파일 분석 모드**")
            
            if st.button("텍스트 품질 분석 시작", type="primary", use_container_width=True):
                with st.spinner("텍스트 품질을 분석 중입니다..."):
                    text = uploaded_file.read().decode("utf-8")
                    text_scores = analyze_text_quality(text)
                
                # 결과를 세션에 저장
                total = calc_total_score(text_scores)
                grade = get_grade(total)
                st.session_state['last_text_analysis'] = {
                    'scores': text_scores,
                    'total': total,
                    'grade': grade,
                    'file_name': uploaded_file.name
                }
                
                # 결과 표시
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("분석 결과")
                    st.dataframe(
                        text_scores,
                        use_container_width=True
                    )
                    st.text_area("분석된 텍스트 내용", text, height=150, disabled=True)
                
                with col2:
                    st.metric("종합 품질 점수", f"{total:.3f}")
                    st.metric("품질 등급", grade)
                    
                    if grade == "A":
                        st.success("우수한 품질입니다!")
                    elif grade == "B":
                        st.info("양호한 품질입니다.")
                    elif grade == "C":
                        st.warning("개선이 필요합니다.")
                    else:
                        st.error("품질 개선이 시급합니다.")
                
                st.subheader("상세 품질 지표 분석")
                st.bar_chart(text_scores)
                
                # PDF 다운로드 버튼
                st.divider()
                dataset_name = uploaded_file.name if uploaded_file else None
                pdf_buffer = generate_text_report_pdf(text_scores, total, grade, dataset_name=dataset_name)
                filename = f"text_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                st.download_button(
                    label="📄 PDF 보고서 다운로드",
                    data=pdf_buffer.getvalue(),
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
                # 새 분석 버튼
                if st.button("새 파일로 분석하기"):
                    if 'file_type' in st.session_state:
                        del st.session_state['file_type']
                    if 'uploaded_file' in st.session_state:
                        del st.session_state['uploaded_file']
                    if 'last_text_analysis' in st.session_state:
                        del st.session_state['last_text_analysis']
                    st.rerun()
    
        elif file_type == 'image':
            st.info("**이미지 파일 분석 모드**")
            
            # 이미지 미리보기
            from PIL import Image
            import io
            
            uploaded_file.seek(0)  # 파일 포인터 리셋
            img = Image.open(io.BytesIO(uploaded_file.read()))
            
            col_preview, col_button = st.columns([2, 1])
            
            with col_preview:
                st.image(img, caption=f"업로드된 이미지: {uploaded_file.name}", use_container_width=True)
            
            with col_button:
                if st.button("이미지 품질 분석 시작", type="primary", use_container_width=True):
                    uploaded_file.seek(0)  # 파일 포인터 리셋
                    img = Image.open(io.BytesIO(uploaded_file.read()))
                    
                    with st.spinner("이미지 품질을 분석 중입니다..."):
                        image_scores = analyze_image_quality(img)
    
                    # 결과를 세션에 저장
                    total = calc_total_score(image_scores)
                    grade = get_grade(total)
                    st.session_state['last_image_analysis'] = {
                        'scores': image_scores,
                        'total': total,
                        'grade': grade,
                        'file_name': uploaded_file.name
                    }
    
                    # 결과 표시
                    st.subheader("분석 결과")
                    
                    result_col1, result_col2 = st.columns([1, 1])
                    
                    with result_col1:
                        st.dataframe(
                            image_scores,
                            use_container_width=True
                        )
                    
                    with result_col2:
                        st.metric("종합 품질 점수", f"{total:.3f}")
                        st.metric("품질 등급", grade)
                        
                        if grade == "A":
                            st.success("우수한 품질입니다!")
                        elif grade == "B":
                            st.info("양호한 품질입니다.")
                        elif grade == "C":
                            st.warning("개선이 필요합니다.")
                        else:
                            st.error("품질 개선이 시급합니다.")
                    
                    st.subheader("상세 품질 지표 분석")
                    st.bar_chart(image_scores)
                    
                    # PDF 다운로드 버튼
                    st.divider()
                    dataset_name = uploaded_file.name if uploaded_file else None
                    pdf_buffer = generate_image_report_pdf(image_scores, total, grade, dataset_name=dataset_name)
                    filename = f"image_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label="📄 PDF 보고서 다운로드",
                        data=pdf_buffer.getvalue(),
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # 새 분석 버튼
                    if st.button("새 파일로 분석하기", use_container_width=True):
                        if 'file_type' in st.session_state:
                            del st.session_state['file_type']
                        if 'uploaded_file' in st.session_state:
                            del st.session_state['uploaded_file']
                        if 'last_image_analysis' in st.session_state:
                            del st.session_state['last_image_analysis']
                        st.rerun()
    
    # 세션에 저장된 샘플 텍스트가 있으면 처리
    elif 'sample_text' in st.session_state:
        st.info("**샘플 텍스트 분석 모드**")
        text = st.session_state['sample_text']
        
        if st.button("텍스트 품질 분석 시작", type="primary", use_container_width=True):
            with st.spinner("텍스트 품질을 분석 중입니다..."):
                text_scores = analyze_text_quality(text)
            
            # 결과를 세션에 저장
            total = calc_total_score(text_scores)
            grade = get_grade(total)
            st.session_state['last_text_analysis'] = {
                'scores': text_scores,
                'total': total,
                'grade': grade,
                'file_name': 'sample_text.txt'
            }
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("분석 결과")
                st.dataframe(
                    text_scores,
                    use_container_width=True
                )
                st.text_area("분석된 텍스트 내용", text, height=150, disabled=True)
            
            with col2:
                st.metric("종합 품질 점수", f"{total:.3f}")
                st.metric("품질 등급", grade)
                
                if grade == "A":
                    st.success("우수한 품질입니다!")
                elif grade == "B":
                    st.info("양호한 품질입니다.")
                elif grade == "C":
                    st.warning("개선이 필요합니다.")
                else:
                    st.error("품질 개선이 시급합니다.")
            
            st.subheader("상세 품질 지표 분석")
            st.bar_chart(text_scores)
            
            # PDF 다운로드 버튼
            st.divider()
            dataset_name = st.session_state.get('last_text_analysis', {}).get('file_name', None)
            pdf_buffer = generate_text_report_pdf(text_scores, total, grade, dataset_name=dataset_name)
            filename = f"text_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            st.download_button(
                label="📄 PDF 보고서 다운로드",
                data=pdf_buffer.getvalue(),
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        
        # 세션 상태 초기화 버튼
        if st.button("새 파일로 분석하기"):
            if 'sample_text' in st.session_state:
                del st.session_state['sample_text']
            if 'last_text_analysis' in st.session_state:
                del st.session_state['last_text_analysis']
            st.rerun()
    
    else:
        st.info("**사용 방법**:\n1. 위에서 파일을 업로드하세요\n2. 파일 타입(텍스트/이미지)을 선택하세요\n3. 분석 버튼을 클릭하세요")
        st.divider()
    
# ========== 탭 2: 데이터셋 배치 분석 ==========
with tab2:
    st.header("데이터셋 배치 분석")
    st.markdown("CIFAR-10, TID2013 등 데이터셋을 자동으로 다운로드하여 품질을 분석합니다.")
    
    # 데이터 타입 선택
    data_type = st.radio(
        "데이터 타입",
        ["이미지", "텍스트"],
        horizontal=True
    )
    
    # 데이터셋 소스 선택 (미리 탑재된 샘플 vs Hugging Face 검색)
    dataset_source = st.radio(
        "데이터셋 소스",
        ["미리 탑재된 샘플 데이터셋", "Hugging Face에서 검색"],
        horizontal=True,
        help="미리 탑재된 샘플 데이터셋을 사용하거나 Hugging Face에서 검색하여 다운로드할 수 있습니다."
    )
    
    if data_type == "이미지":
        if dataset_source == "미리 탑재된 샘플 데이터셋":
            dataset_option = st.selectbox(
                "분석할 이미지 데이터셋 선택",
                [
                    "CIFAR-10 (torchvision)",
                    "Hugging Face: beans (콩 질병 분류)",
                    "Hugging Face: food101 (음식 이미지)",
                    "Hugging Face: cifar10",
                    "TID2013 (로컬)",
                    "커스텀 폴더"
                ]
            )
        else:  # Hugging Face 검색
            dataset_option = "Hugging Face: 검색"
    else:  # 텍스트
        if dataset_source == "미리 탑재된 샘플 데이터셋":
            dataset_option = st.selectbox(
                "분석할 텍스트 데이터셋 선택",
                [
                    "Hugging Face: imdb (영화 리뷰)",
                    "Hugging Face: yelp_review_full (리뷰)",
                    "Hugging Face: ag_news (뉴스 분류)"
                ]
            )
        else:  # Hugging Face 검색
            dataset_option = "Hugging Face: 검색"
    
    # Hugging Face 검색인 경우 먼저 검색 UI 표시
    if dataset_option == "Hugging Face: 검색":
        st.subheader("Hugging Face 데이터셋 검색")
        
        if data_type == "이미지":
            # 이미지 데이터셋 인기 목록 및 검색
            col_info, col_search = st.columns([2, 3])
            
            with col_info:
                st.markdown("### 인기 이미지 데이터셋 목록")
                try:
                    popular_list = get_predefined_datasets("image-classification")
                    if popular_list:
                        st.dataframe({
                            "데이터셋 ID": [d["id"] for d in popular_list[:20]],
                            "작성자": [d.get("author", "-") for d in popular_list[:20]],
                            "다운로드 수": [f"{d.get('downloads', 0):,}" for d in popular_list[:20]],
                        },
                        use_container_width=True,
                        height=300,
                        key="img_popular_list"
                        )
                except Exception as e:
                    st.info(f"목록을 불러올 수 없습니다: {e}")
            
            with col_search:
                search_query = st.text_input(
                    "검색어 입력",
                    placeholder="예: cats, dogs, classification",
                    help="이미지 데이터셋 검색",
                    key="img_search_main"
                )
                
                if st.button("검색", key="img_search_btn_main", use_container_width=True):
                    st.session_state['img_search_active'] = True
                
                if st.session_state.get('img_search_active', False) or search_query:
                    try:
                        with st.spinner("검색 중..."):
                            if search_query:
                                results = search_huggingface_datasets(
                                    query=search_query,
                                    task="image-classification",
                                    max_results=30
                                )
                            else:
                                results = get_popular_datasets(
                                    task="image-classification",
                                    max_results=30
                                )
                        
                        if results:
                            st.success(f"{len(results)}개 데이터셋을 찾았습니다!")
                            dataset_df = st.dataframe({
                                "데이터셋 ID": [d["id"] for d in results],
                                "작성자": [d.get("author", "-") for d in results],
                                "다운로드 수": [f"{d.get('downloads', 0):,}" for d in results],
                            },
                            use_container_width=True,
                            height=300,
                            key="img_search_results"
                            )
                            
                            # 선택된 데이터셋 표시
                            selected_id = st.text_input(
                                "분석할 데이터셋 ID 입력",
                                value=st.session_state.get('selected_img_dataset', ''),
                                help="위 목록에서 데이터셋 ID를 복사하여 입력하세요",
                                key="img_dataset_id_input"
                            )
                            if selected_id:
                                st.session_state['selected_img_dataset'] = selected_id
                        else:
                            if search_query:
                                st.warning(f"'{search_query}'에 대한 검색 결과가 없습니다. 다른 검색어를 시도해보세요.")
                            else:
                                st.info("인기 데이터셋 목록을 불러올 수 없습니다.")
                    except Exception as e:
                        st.error(f"검색 실패: {e}")
        else:  # 텍스트
            # 텍스트 데이터셋 인기 목록 및 검색
            col_info, col_search = st.columns([2, 3])
            
            with col_info:
                st.markdown("### 인기 텍스트 데이터셋 목록")
                try:
                    popular_list = get_predefined_datasets("text-classification")
                    if popular_list:
                        st.dataframe({
                            "데이터셋 ID": [d["id"] for d in popular_list[:20]],
                            "작성자": [d.get("author", "-") for d in popular_list[:20]],
                            "다운로드 수": [f"{d.get('downloads', 0):,}" for d in popular_list[:20]],
                        },
                        use_container_width=True,
                        height=300,
                        key="text_popular_list"
                        )
                except Exception as e:
                    st.info(f"목록을 불러올 수 없습니다: {e}")
            
            with col_search:
                search_query = st.text_input(
                    "검색어 입력",
                    placeholder="예: sentiment, review, classification",
                    help="텍스트 데이터셋 검색",
                    key="text_search_main"
                )
                
                if st.button("검색", key="text_search_btn_main", use_container_width=True):
                    st.session_state['text_search_active'] = True
                
                if st.session_state.get('text_search_active', False) or search_query:
                    try:
                        with st.spinner("검색 중..."):
                            if search_query:
                                results = search_huggingface_datasets(
                                    query=search_query,
                                    task="text-classification",
                                    max_results=30
                                )
                            else:
                                results = get_popular_datasets(
                                    task="text-classification",
                                    max_results=30
                                )
                        
                        if results:
                            st.success(f"{len(results)}개 데이터셋을 찾았습니다!")
                            dataset_df = st.dataframe({
                                "데이터셋 ID": [d["id"] for d in results],
                                "작성자": [d.get("author", "-") for d in results],
                                "다운로드 수": [f"{d.get('downloads', 0):,}" for d in results],
                            },
                            use_container_width=True,
                            height=300,
                            key="text_search_results"
                            )
                            
                            # 선택된 데이터셋 표시
                            selected_id = st.text_input(
                                "분석할 데이터셋 ID 입력",
                                value=st.session_state.get('selected_text_dataset', ''),
                                help="위 목록에서 데이터셋 ID를 복사하여 입력하세요",
                                key="text_dataset_id_input"
                            )
                            if selected_id:
                                st.session_state['selected_text_dataset'] = selected_id
                        else:
                            if search_query:
                                st.warning(f"'{search_query}'에 대한 검색 결과가 없습니다. 다른 검색어를 시도해보세요.")
                            else:
                                st.info("인기 데이터셋 목록을 불러올 수 없습니다.")
                    except Exception as e:
                        st.error(f"검색 실패: {e}")
        
        st.divider()
    
    # 다운로드 설정
    download_mode = st.radio(
        "다운로드 방식",
        ["샘플 개수 지정", "전체 데이터셋 퍼센티지", "전체 다운로드"],
        help="일부만 다운로드하여 빠른 테스트 가능"
    )
    
    if download_mode == "샘플 개수 지정":
        num_samples = st.slider("분석할 샘플 개수", min_value=10, max_value=500, value=100, step=10)
        download_percentage = None
        download_full = False
    elif download_mode == "전체 다운로드":
        st.info("전체 데이터셋을 다운로드합니다. (시간이 많이 걸릴 수 있습니다)")
        num_samples = None
        download_percentage = None
        download_full = True
    else:  # 퍼센티지 모드
        download_percentage = st.slider(
            "다운로드할 데이터셋 비율 (%)",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            help="예: 10% = 전체 데이터셋의 10%만 다운로드, 100% = 전체 다운로드"
        )
        if download_percentage == 100:
            st.info("100% 선택 = 전체 데이터셋 다운로드")
        num_samples = None  # 퍼센티지 사용 시 샘플 개수는 자동 계산
        download_full = False
    
    if st.button("데이터셋 분석 시작", type="primary", use_container_width=True):
        try:
            with st.spinner(f"{dataset_option} 데이터셋을 로드하고 분석 중입니다..."):
                images = []
                texts = []
                
                if dataset_option == "CIFAR-10 (torchvision)":
                    dataset_option = "CIFAR-10"  # 처리 로직 호환성
                
                if dataset_option == "CIFAR-10":
                    if download_full:
                        # 전체 다운로드: CIFAR-10은 총 50,000장
                        st.info("CIFAR-10 전체 데이터셋 (50,000장) 다운로드 중... (시간이 걸릴 수 있습니다)")
                        images = load_cifar10(50000)
                    elif download_percentage:
                        # 퍼센티지 기반: CIFAR-10은 총 50,000장이므로 계산
                        total_cifar = 50000
                        calculated_samples = int(total_cifar * download_percentage / 100)
                        st.info(f"CIFAR-10 데이터셋의 {download_percentage}% ({calculated_samples}장) 다운로드합니다.")
                        images = load_cifar10(calculated_samples)
                    else:
                        st.info("CIFAR-10 데이터셋을 다운로드합니다. (첫 실행 시 시간이 걸립니다)")
                        images = load_cifar10(num_samples)
                    st.success(f"CIFAR-10 데이터셋 {len(images)}개 이미지 로드 완료!")
    
                elif dataset_option == "Hugging Face: 검색":
                    # 검색으로 선택한 데이터셋 사용
                    if data_type == "이미지":
                        hf_dataset_name = st.session_state.get('selected_img_dataset', '')
                        if not hf_dataset_name:
                            st.error("데이터셋 ID를 입력해주세요.")
                            st.stop()
                        split_name = st.selectbox("Split 선택", ["train", "test", "validation", "val"], index=0, key="img_split_search")
                    else:  # 텍스트
                        hf_dataset_name = st.session_state.get('selected_text_dataset', '')
                        if not hf_dataset_name:
                            st.error("데이터셋 ID를 입력해주세요.")
                            st.stop()
                        split_name = st.selectbox("Split 선택", ["train", "test", "validation", "val"], index=0, key="text_split_search")
                    
                    # 검색으로 선택한 데이터셋 다운로드
                    if download_full:
                        if data_type == "이미지":
                            st.info(f"{hf_dataset_name} 전체 데이터셋 다운로드 중... (시간이 많이 걸릴 수 있습니다)")
                            images = load_huggingface_dataset(
                                hf_dataset_name,
                                num_samples=None,
                                split=split_name,
                                download_full=True
                            )
                            st.success(f"Hugging Face '{hf_dataset_name}' 이미지 데이터셋 {len(images)}개 로드 완료!")
                        else:
                            st.info(f"{hf_dataset_name} 전체 데이터셋 다운로드 중... (시간이 많이 걸릴 수 있습니다)")
                            texts = load_huggingface_text_dataset(
                                hf_dataset_name,
                                num_samples=None,
                                split=split_name,
                                download_full=True
                            )
                            st.success(f"Hugging Face '{hf_dataset_name}' 텍스트 데이터셋 {len(texts)}개 로드 완료!")
                    elif download_percentage:
                        if data_type == "이미지":
                            st.info(f"{hf_dataset_name} 데이터셋의 {download_percentage}% 다운로드 중...")
                            images = load_huggingface_dataset(
                                hf_dataset_name,
                                num_samples=None,
                                split=split_name,
                                download_percentage=download_percentage
                            )
                            st.success(f"Hugging Face '{hf_dataset_name}' 이미지 데이터셋 {len(images)}개 로드 완료!")
                        else:
                            st.info(f"{hf_dataset_name} 데이터셋의 {download_percentage}% 다운로드 중...")
                            texts = load_huggingface_text_dataset(
                                hf_dataset_name,
                                num_samples=None,
                                split=split_name,
                                download_percentage=download_percentage
                            )
                            st.success(f"Hugging Face '{hf_dataset_name}' 텍스트 데이터셋 {len(texts)}개 로드 완료!")
                    else:
                        if data_type == "이미지":
                            st.info(f"{hf_dataset_name} 데이터셋 다운로드 중...")
                            images = load_huggingface_dataset(
                                hf_dataset_name,
                                num_samples=num_samples,
                                split=split_name
                            )
                            st.success(f"Hugging Face '{hf_dataset_name}' 이미지 데이터셋 {len(images)}개 로드 완료!")
                        else:
                            st.info(f"{hf_dataset_name} 데이터셋 다운로드 중...")
                            texts = load_huggingface_text_dataset(
                                hf_dataset_name,
                                num_samples=num_samples,
                                split=split_name
                            )
                            st.success(f"Hugging Face '{hf_dataset_name}' 텍스트 데이터셋 {len(texts)}개 로드 완료!")
                
                elif dataset_option.startswith("Hugging Face:"):
                    hf_dataset_name = None
                    hf_text_dataset_name = None
                    split_name = "train"
                    
                    if data_type == "이미지":
                        if "beans" in dataset_option:
                            hf_dataset_name = "beans"
                            if download_percentage:
                                st.info(f"Beans 데이터셋의 {download_percentage}% 다운로드 중... (콩 질병 분류 이미지)")
                            else:
                                st.info("Beans 데이터셋 다운로드 중... (콩 질병 분류 이미지)")
                        elif "food101" in dataset_option:
                            hf_dataset_name = "food101"
                            if download_percentage:
                                st.info(f"Food-101 데이터셋의 {download_percentage}% 다운로드 중... (음식 이미지)")
                            else:
                                st.info("Food-101 데이터셋 다운로드 중... (음식 이미지)")
                        elif "cifar10" in dataset_option:
                            hf_dataset_name = "cifar10"
                            if download_percentage:
                                st.info(f"CIFAR-10 (Hugging Face) 데이터셋의 {download_percentage}% 다운로드 중...")
                            else:
                                st.info("CIFAR-10 (Hugging Face) 다운로드 중...")
                        
                        # 이미지 데이터셋 다운로드 처리
                        if hf_dataset_name:
                            split_name = st.selectbox("Split 선택", ["train", "test", "validation", "val"], index=0, key="img_split_predefined")
                            if download_full:
                                images = load_huggingface_dataset(
                                    hf_dataset_name,
                                    num_samples=None,
                                    split=split_name,
                                    download_full=True
                                )
                                st.info(f"{hf_dataset_name} 전체 데이터셋 다운로드 중... (시간이 많이 걸릴 수 있습니다)")
                            elif download_percentage:
                                images = load_huggingface_dataset(
                                    hf_dataset_name,
                                    num_samples=None,
                                    split=split_name,
                                    download_percentage=download_percentage
                                )
                            else:
                                images = load_huggingface_dataset(
                                    hf_dataset_name,
                                    num_samples=num_samples,
                                    split=split_name
                                )
                            st.success(f"Hugging Face '{hf_dataset_name}' 데이터셋 {len(images)}개 이미지 로드 완료!")
                    
                    elif data_type == "텍스트":
                        if "imdb" in dataset_option:
                            hf_text_dataset_name = "imdb"
                            if download_percentage:
                                st.info(f"IMDB 데이터셋의 {download_percentage}% 다운로드 중... (영화 리뷰 텍스트)")
                            elif download_full:
                                st.info("IMDB 전체 데이터셋 다운로드 중... (영화 리뷰 텍스트)")
                            else:
                                st.info("IMDB 데이터셋 다운로드 중... (영화 리뷰 텍스트)")
                        elif "yelp" in dataset_option:
                            hf_text_dataset_name = "yelp_review_full"
                            if download_percentage:
                                st.info(f"Yelp Review 데이터셋의 {download_percentage}% 다운로드 중... (리뷰 텍스트)")
                            elif download_full:
                                st.info("Yelp Review 전체 데이터셋 다운로드 중... (리뷰 텍스트)")
                            else:
                                st.info("Yelp Review 데이터셋 다운로드 중... (리뷰 텍스트)")
                        elif "ag_news" in dataset_option:
                            hf_text_dataset_name = "ag_news"
                            if download_percentage:
                                st.info(f"AG News 데이터셋의 {download_percentage}% 다운로드 중... (뉴스 분류 텍스트)")
                            elif download_full:
                                st.info("AG News 전체 데이터셋 다운로드 중... (뉴스 분류 텍스트)")
                            else:
                                st.info("AG News 데이터셋 다운로드 중... (뉴스 분류 텍스트)")
                        
                        # 텍스트 데이터셋 다운로드 처리
                        if hf_text_dataset_name:
                            split_name = st.selectbox("Split 선택", ["train", "test", "validation", "val"], index=0, key="text_split_predefined")
                            if download_full:
                                texts = load_huggingface_text_dataset(
                                    hf_text_dataset_name,
                                    num_samples=None,
                                    split=split_name,
                                    download_full=True
                                )
                            elif download_percentage:
                                texts = load_huggingface_text_dataset(
                                    hf_text_dataset_name,
                                    num_samples=None,
                                    split=split_name,
                                    download_percentage=download_percentage
                                )
                            else:
                                texts = load_huggingface_text_dataset(
                                    hf_text_dataset_name,
                                    num_samples=num_samples,
                                    split=split_name
                                )
                            st.success(f"Hugging Face '{hf_text_dataset_name}' 텍스트 데이터셋 {len(texts)}개 로드 완료!")
    
                elif dataset_option == "TID2013 (로컬)":
                    # 커스텀 경로 입력 옵션
                    use_custom_path = st.checkbox("커스텀 경로 사용", key="tid_custom_path")
                    custom_path = None
                    if use_custom_path:
                        custom_path = st.text_input(
                            "TID2013 데이터셋 경로 입력",
                            value="./data/TID2013",
                            help="TID2013 폴더 또는 reference_images 폴더의 상위 경로"
                        )
                    
                    # TID2013은 로컬 파일이므로 퍼센티지는 샘플 개수로 변환
                    if download_percentage:
                        # TID2013 reference 이미지는 보통 25개 정도
                        total_tid = 25
                        calculated_samples = max(1, int(total_tid * download_percentage / 100))
                        st.info(f"TID2013 데이터셋의 {download_percentage}% ({calculated_samples}장) 로드합니다.")
                        images = load_tid2013(calculated_samples, custom_path=custom_path if use_custom_path else None)
                    else:
                        images = load_tid2013(num_samples, custom_path=custom_path if use_custom_path else None)
                    st.success(f"TID2013 데이터셋 {len(images)}개 이미지 로드 완료!")
                
                elif dataset_option == "커스텀 폴더":
                    folder_path = st.text_input("이미지 폴더 경로 입력", value="./data/images")
                    if folder_path:
                        # 커스텀 폴더는 퍼센티지 계산이 어려우므로 샘플 개수 사용
                        if download_percentage:
                            st.warning("커스텀 폴더는 퍼센티지 대신 샘플 개수를 사용합니다.")
                            images = load_custom_dataset(folder_path, num_samples if num_samples else 100)
                        else:
                            images = load_custom_dataset(folder_path, num_samples)
                        st.success(f"커스텀 폴더에서 {len(images)}개 이미지 로드 완료!")
                    else:
                        st.warning("폴더 경로를 입력해주세요.")
                        images = []
    
                # 이미지 분석
                if images:
                    # 배치 분석 실행
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = analyze_dataset_images(images, max_samples=num_samples)
                    
                    progress_bar.progress(100)
                    status_text.text("분석 완료!")
                    
                    # 결과 표시
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("전체 통계")
                        st.dataframe({
                            "지표": list(results.keys()),
                            "값": list(results.values())
                        },
                        use_container_width=True
                        )
                    
                    with col2:
                        avg_score = results.get("평균 종합 점수", 0.0)
                        grade = get_grade(avg_score)
                        
                        st.metric("평균 품질 점수", f"{avg_score:.3f}")
                        st.metric("품질 등급", grade)
                        
                        if grade == "A":
                            st.success("우수한 품질의 데이터셋입니다!")
                        elif grade == "B":
                            st.info("양호한 품질의 데이터셋입니다.")
                        elif grade == "C":
                            st.warning("품질 개선이 권장됩니다.")
                        else:
                            st.error("품질 개선이 시급합니다.")
                    
                    # 상세 지표 시각화
                    st.subheader("품질 지표 상세")
                    
                    metrics_data = {
                        "평균 해상도": results["평균 해상도"],
                        "평균 선명도": results["평균 선명도"],
                        "평균 노이즈": results["평균 노이즈"],
                        "평균 중복도": results["평균 중복도"],
                    }
                    
                    st.bar_chart(metrics_data)
                    
                    # 해상도 분포 정보 표시
                    if "해상도 분포" in results:
                        st.subheader("선택된 이미지 해상도 정보")
                        resolution_info = results["해상도 분포"]
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("최소 해상도", resolution_info["최소"])
                        with col2:
                            st.metric("최대 해상도", resolution_info["최대"])
                        with col3:
                            st.metric("평균 해상도", resolution_info["평균"])
                        with col4:
                            st.metric("중앙값 해상도", resolution_info["중앙값"])
                        
                        st.info(f"평균 픽셀 수: {resolution_info['평균 픽셀 수']} 픽셀")
                        
                        # 해상도 목록 표시 (확장 가능)
                        with st.expander("선택된 이미지들의 실제 해상도 목록 (전체 보기)"):
                            if "해상도 목록" in results:
                                # 해상도별 그룹화하여 표시
                                from collections import Counter
                                resolution_counts = Counter(results["해상도 목록"])
                                st.write("**해상도별 개수:**")
                                for res, count in sorted(resolution_counts.items(), key=lambda x: x[1], reverse=True):
                                    st.write(f"- {res}: {count}개")
                            
                            # 전체 목록도 표시
                            st.write(f"\n**전체 {len(results.get('해상도 목록', []))}개 이미지 해상도:**")
                            st.text(", ".join(results.get("해상도 목록", [])))
                    
                    # 샘플 이미지 미리보기 (전체 표시)
                    if len(images) > 0:
                        st.subheader(f"선택된 이미지 전체 ({len(images)}개)")
                        
                        # 5열 그리드로 표시
                        num_cols = 5
                        num_rows = (len(images) + num_cols - 1) // num_cols  # 올림 계산
                        
                        for row in range(num_rows):
                            cols = st.columns(num_cols)
                            for col_idx in range(num_cols):
                                img_idx = row * num_cols + col_idx
                                if img_idx < len(images):
                                    with cols[col_idx]:
                                        st.image(images[img_idx], use_container_width=True)
                                        if "해상도 목록" in results and img_idx < len(results["해상도 목록"]):
                                            st.caption(f"#{img_idx+1} ({results['해상도 목록'][img_idx]})")
                                        else:
                                            st.caption(f"#{img_idx+1}")
                    
                    # 개별 점수 표시 (토글)
                    if "개별 점수" in results and len(results["개별 점수"]) > 0:
                        with st.expander("개별 이미지 점수 상세 보기", expanded=False):
                            import pandas as pd
                            
                            # 개별 점수 데이터프레임 생성
                            df_scores = pd.DataFrame(results["개별 점수"])
                            df_scores.index = df_scores.index + 1  # 인덱스를 1부터 시작
                            df_scores.index.name = "이미지 번호"
                            
                            # 정렬 옵션 추가
                            col_sort1, col_sort2 = st.columns(2)
                            with col_sort1:
                                sort_by = st.selectbox("정렬 기준", ["종합점수", "해상도", "선명도", "노이즈", "중복도"], key="img_sort")
                            with col_sort2:
                                sort_order = st.selectbox("정렬 방향", ["내림차순", "오름차순"], key="img_order")
                            
                            ascending = (sort_order == "오름차순")
                            df_scores_sorted = df_scores.sort_values(by=sort_by, ascending=ascending)
                            
                            # 데이터프레임 표시
                            st.dataframe(df_scores_sorted, use_container_width=True)
                            
                            # 통계 요약
                            st.caption(f"총 {len(df_scores)}개 이미지 | 평균 종합점수: {results['평균 종합 점수']:.3f} | 최소: {results['최소 종합 점수']:.3f} | 최대: {results['최대 종합 점수']:.3f}")
                    
                    # PDF 다운로드 버튼
                    st.divider()
                    pdf_buffer = generate_dataset_report_pdf(results, "이미지", dataset_option)
                    filename = f"image_dataset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label="📄 PDF 보고서 다운로드",
                        data=pdf_buffer.getvalue(),
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                
                # 텍스트 분석
                elif texts:
                    # 배치 분석 실행
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = analyze_dataset_texts(texts, max_samples=len(texts))
                    
                    progress_bar.progress(100)
                    status_text.text("분석 완료!")
                    
                    # 결과 표시
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("전체 통계")
                        st.dataframe({
                            "지표": list(results.keys()),
                            "값": list(results.values())
                        },
                        use_container_width=True
                        )
                    
                    with col2:
                        avg_score = results.get("평균 종합 점수", 0.0)
                        grade = get_grade(avg_score)
                        
                        st.metric("평균 품질 점수", f"{avg_score:.3f}")
                        st.metric("품질 등급", grade)
                        
                        if grade == "A":
                            st.success("우수한 품질의 데이터셋입니다!")
                        elif grade == "B":
                            st.info("양호한 품질의 데이터셋입니다.")
                        elif grade == "C":
                            st.warning("품질 개선이 권장됩니다.")
                        else:
                            st.error("품질 개선이 시급합니다.")
                    
                    # 상세 지표 시각화 (메인)
                    st.subheader("품질 지표 상세")
                    
                    metrics_data = {
                        "평균 정확성": results["평균 정확성"],
                        "평균 중복도": results["평균 중복도"],
                        "평균 완전성": results["평균 완전성"],
                    }
                    
                    st.bar_chart(metrics_data)
                    
                    # 개별 점수 표시 (토글)
                    if "개별 점수" in results and len(results["개별 점수"]) > 0:
                        with st.expander("개별 텍스트 점수 상세 보기", expanded=False):
                            import pandas as pd
                            
                            # 개별 점수 데이터프레임 생성
                            df_scores = pd.DataFrame(results["개별 점수"])
                            df_scores.index = df_scores.index + 1  # 인덱스를 1부터 시작
                            df_scores.index.name = "텍스트 번호"
                            
                            # 정렬 옵션 추가
                            col_sort1, col_sort2 = st.columns(2)
                            with col_sort1:
                                sort_by = st.selectbox("정렬 기준", ["종합점수", "정확성", "중복도", "완전성"], key="text_sort")
                            with col_sort2:
                                sort_order = st.selectbox("정렬 방향", ["내림차순", "오름차순"], key="text_order")
                            
                            ascending = (sort_order == "오름차순")
                            df_scores_sorted = df_scores.sort_values(by=sort_by, ascending=ascending)
                            
                            # 데이터프레임 표시
                            st.dataframe(df_scores_sorted, use_container_width=True)
                            
                            # 통계 요약
                            st.caption(f"총 {len(df_scores)}개 텍스트 | 평균 종합점수: {results['평균 종합 점수']:.3f} | 최소: {results['최소 종합 점수']:.3f} | 최대: {results['최대 종합 점수']:.3f}")
                    
                    # 선택된 텍스트 전체 표시 (토글)
                    if len(texts) > 0:
                        with st.expander(f"선택된 텍스트 전체 보기 ({len(texts)}개)", expanded=False):
                            for i, text in enumerate(texts):
                                # 개별 점수 정보 가져오기
                                score_info = ""
                                if "개별 점수" in results and i < len(results["개별 점수"]):
                                    score = results["개별 점수"][i]
                                    score_info = f" | 정확성: {score.get('정확성', 0):.3f}, 중복도: {score.get('중복도', 0):.3f}, 완전성: {score.get('완전성', 0):.3f}, 종합: {score.get('종합점수', 0):.3f}"
                                
                                with st.expander(f"텍스트 #{i+1} (길이: {len(text)}자{score_info})", expanded=False):
                                    st.text(text[:1000] + "..." if len(text) > 1000 else text)
                    
                    # PDF 다운로드 버튼
                    st.divider()
                    pdf_buffer = generate_dataset_report_pdf(results, "텍스트", dataset_option)
                    filename = f"text_dataset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label="📄 PDF 보고서 다운로드",
                        data=pdf_buffer.getvalue(),
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
    
        except ImportError as e:
            st.error(f"필요한 패키지가 설치되어 있지 않습니다.\n`pip install torchvision`을 실행하세요.\n\n에러: {e}")
        except FileNotFoundError as e:
            st.error(f"데이터셋을 찾을 수 없습니다.\n\n에러: {e}")
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다.\n\n에러: {e}")
            st.exception(e)
    
    # 사용 가이드
    with st.expander("데이터셋 분석 가이드"):
        st.markdown("""
        ### 지원 파일 형식
        - **텍스트**: `.txt` 파일
        - **이미지**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`
        
        ### 품질 지표 설명
        #### 텍스트 데이터
        - **정확성**: 오탈자 및 맞춤법 오류 비율
        - **중복도**: 문장 간 유사도 분석 (낮을수록 중복 많음)
        - **완전성**: 의미 있는 문장의 비율
        
        #### 이미지 데이터
        - **해상도**: 이미지 크기 기준 충족 여부
        - **선명도**: 이미지 선명함 정도 (Laplacian Variance)
        - **노이즈**: 이미지 노이즈 수준
        - **중복도**: 중복 이미지 비율
        
        ### 품질 등급
        - **A**: 0.8 이상 (우수)
        - **B**: 0.6 이상 (양호)
        - **C**: 0.4 이상 (보통)
        - **D**: 0.4 미만 (개선 필요)
        """)
    
