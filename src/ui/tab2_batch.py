"""데이터셋 배치 분석 탭"""
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
from src.utils import get_grade, generate_dataset_report_pdf
from src.dataset_analyzer import (
    analyze_dataset_images, analyze_dataset_texts,
    load_cifar10, load_tid2013, load_custom_dataset,
    load_huggingface_dataset, load_huggingface_text_dataset
)
from src.dataset_finder import (
    search_huggingface_datasets, get_popular_datasets, get_predefined_datasets
)


def render_tab2(tab):
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
                    "Hugging Face: cifar100 (100 클래스)",
                    "Hugging Face: mnist (손글씨 숫자)",
                    "Hugging Face: fashion_mnist (패션 아이템)",
                    "Hugging Face: imagenet-1k (대규모 이미지 분류)",
                    "Hugging Face: oxford-iiit-pet (반려동물)",
                    "Hugging Face: oxford_flowers102 (꽃 이미지)",
                    "Hugging Face: stanford-cars (자동차)",
                    "Hugging Face: celeba (인물 얼굴)",
                    "Hugging Face: coco (객체 탐지)",
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
                    "Hugging Face: ag_news (뉴스 분류)",
                    "Hugging Face: amazon_polarity (아마존 리뷰)",
                    "Hugging Face: sst2 (감정 분석)",
                    "Hugging Face: squad (질문 답변)",
                    "Hugging Face: nyu-mll/glue (GLUE 벤치마크)",
                    "Hugging Face: super_glue (SuperGLUE)",
                    "Hugging Face: wikitext (위키텍스트)",
                    "Hugging Face: emotion (감정 분류)",
                    "Hugging Face: rotten_tomatoes (영화 리뷰)",
                    "Hugging Face: tweet_eval (트위터 감정)",
                    "Hugging Face: multi_nli (자연어 추론)",
                    "Hugging Face: 20newsgroups (뉴스그룹)"
                ]
            )
        else:  # Hugging Face 검색
            dataset_option = "Hugging Face: 검색"
    # 미리 정의된 Hugging Face 데이터셋인 경우 split 선택 (다운로드 전)
    if dataset_option.startswith("Hugging Face:") and dataset_option != "Hugging Face: 검색":
        hf_dataset_name = None
        hf_text_dataset_name = None
        if data_type == "이미지":
            if "beans" in dataset_option:
                hf_dataset_name = "beans"
            elif "food101" in dataset_option:
                hf_dataset_name = "food101"
            elif "cifar10" in dataset_option and "cifar100" not in dataset_option:
                hf_dataset_name = "cifar10"
            elif "cifar100" in dataset_option:
                hf_dataset_name = "cifar100"
            elif "mnist" in dataset_option and "fashion" not in dataset_option:
                hf_dataset_name = "mnist"
            elif "fashion_mnist" in dataset_option or "fashion" in dataset_option:
                hf_dataset_name = "fashion_mnist"
            elif "imagenet" in dataset_option:
                hf_dataset_name = "imagenet-1k"
            elif "oxford-iiit-pet" in dataset_option or "pet" in dataset_option.lower():
                hf_dataset_name = "oxford-iiit-pet"
            elif "oxford_flowers" in dataset_option or "flowers" in dataset_option.lower():
                hf_dataset_name = "oxford_flowers102"
            elif "stanford-cars" in dataset_option or "cars" in dataset_option.lower():
                hf_dataset_name = "stanford-cars"
            elif "celeba" in dataset_option:
                hf_dataset_name = "celeba"
            elif "coco" in dataset_option:
                hf_dataset_name = "coco"
        else:  # 텍스트
            if "imdb" in dataset_option:
                hf_text_dataset_name = "imdb"
            elif "yelp" in dataset_option:
                hf_text_dataset_name = "yelp_review_full"
            elif "ag_news" in dataset_option:
                hf_text_dataset_name = "ag_news"
            elif "amazon_polarity" in dataset_option or ("amazon" in dataset_option and "polarity" in dataset_option):
                hf_text_dataset_name = "amazon_polarity"
            elif "sst2" in dataset_option:
                hf_text_dataset_name = "sst2"
            elif "squad" in dataset_option and "super" not in dataset_option:
                hf_text_dataset_name = "squad"
            elif "glue" in dataset_option and "super" not in dataset_option:
                hf_text_dataset_name = "nyu-mll/glue"
            elif "super_glue" in dataset_option or "superglue" in dataset_option.lower():
                hf_text_dataset_name = "super_glue"
            elif "wikitext" in dataset_option:
                hf_text_dataset_name = "wikitext"
            elif "emotion" in dataset_option:
                hf_text_dataset_name = "emotion"
            elif "rotten_tomatoes" in dataset_option or "rotten" in dataset_option.lower():
                hf_text_dataset_name = "rotten_tomatoes"
            elif "tweet_eval" in dataset_option or "tweet" in dataset_option.lower():
                hf_text_dataset_name = "tweet_eval"
            elif "multi_nli" in dataset_option or "nli" in dataset_option.lower():
                hf_text_dataset_name = "multi_nli"
            elif "20newsgroups" in dataset_option or "newsgroups" in dataset_option.lower():
                hf_text_dataset_name = "20newsgroups"
        # ========== Split 선택 기능 (현재 비활성화 - 주석 처리) ==========
        # Split은 자동으로 선택됩니다 (기본값: train, 없으면 자동으로 사용 가능한 split 선택)
        # 아래 코드를 주석 해제하면 split 선택 UI가 활성화됩니다
        # 
        # if hf_dataset_name or hf_text_dataset_name:
        #     dataset_name = hf_dataset_name or hf_text_dataset_name
        #     from src.dataset_analyzer import get_available_splits
        #     try:
        #         available_splits = get_available_splits(dataset_name)
        #         default_split = "train" if "train" in available_splits else available_splits[0] if available_splits else "train"
        #         split_index = available_splits.index(default_split) if default_split in available_splits else 0
        #         
        #         split_key = "img_split_predefined" if data_type == "이미지" else "text_split_predefined"
        #         selected_split = st.selectbox(
        #             "Split 선택 (다운로드 전에 선택)",
        #             available_splits,
        #             index=split_index,
        #             key=split_key,
        #             help="train: 학습용 데이터, test: 테스트용 데이터, validation/val: 검증용 데이터"
        #         )
        #         if data_type == "이미지":
        #             st.session_state['selected_img_split_predefined'] = selected_split
        #         else:
        #             st.session_state['selected_text_split_predefined'] = selected_split
        #     except Exception:
        #         available_splits = ["train", "test", "validation", "val"]
        #         split_key = "img_split_predefined" if data_type == "이미지" else "text_split_predefined"
        #         selected_split = st.selectbox(
        #             "Split 선택 (다운로드 전에 선택)",
        #             available_splits,
        #             index=0,
        #             key=split_key,
        #             help="train: 학습용 데이터, test: 테스트용 데이터, validation/val: 검증용 데이터"
        #         )
        #         if data_type == "이미지":
        #             st.session_state['selected_img_split_predefined'] = selected_split
        #         else:
        #             st.session_state['selected_text_split_predefined'] = selected_split
        st.divider()
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
                                # ========== Split 선택 기능 (현재 비활성화 - 주석 처리) ==========
                                # Split은 자동으로 선택됩니다 (기본값: train, 없으면 자동으로 사용 가능한 split 선택)
                                # 아래 코드를 주석 해제하면 split 선택 UI가 활성화됩니다
                                # 
                                # from src.dataset_analyzer import get_available_splits
                                # try:
                                #     available_splits = get_available_splits(selected_id)
                                #     default_split = "train" if "train" in available_splits else available_splits[0] if available_splits else "train"
                                #     split_index = available_splits.index(default_split) if default_split in available_splits else 0
                                #     
                                #     selected_split = st.selectbox(
                                #         "Split 선택 (다운로드 전에 선택)",
                                #         available_splits,
                                #         index=split_index,
                                #         key="img_split_preview",
                                #         help="train: 학습용 데이터, test: 테스트용 데이터, validation/val: 검증용 데이터"
                                #     )
                                #     st.session_state['selected_img_split'] = selected_split
                                # except Exception as e:
                                #     st.warning(f"Split 정보를 가져올 수 없습니다. 기본값(train)을 사용합니다: {e}")
                                #     st.session_state['selected_img_split'] = "train"
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
                                # ========== Split 선택 기능 (현재 비활성화 - 주석 처리) ==========
                                # Split은 자동으로 선택됩니다 (기본값: train, 없으면 자동으로 사용 가능한 split 선택)
                                # 아래 코드를 주석 해제하면 split 선택 UI가 활성화됩니다
                                # 
                                # from src.dataset_analyzer import get_available_splits
                                # try:
                                #     available_splits = get_available_splits(selected_id)
                                #     default_split = "train" if "train" in available_splits else available_splits[0] if available_splits else "train"
                                #     split_index = available_splits.index(default_split) if default_split in available_splits else 0
                                #     
                                #     selected_split = st.selectbox(
                                #         "Split 선택 (다운로드 전에 선택)",
                                #         available_splits,
                                #         index=split_index,
                                #         key="text_split_preview",
                                #         help="train: 학습용 데이터, test: 테스트용 데이터, validation/val: 검증용 데이터"
                                #     )
                                #     st.session_state['selected_text_split'] = selected_split
                                # except Exception as e:
                                #     st.warning(f"Split 정보를 가져올 수 없습니다. 기본값(train)을 사용합니다: {e}")
                                #     st.session_state['selected_text_split'] = "train"
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
                        # Split은 자동으로 선택됩니다 (기본값: train, 없으면 사용 가능한 split 자동 선택)
                        split_name = "train"  # 기본값, dataset_analyzer에서 자동 조정
                    else:  # 텍스트
                        hf_dataset_name = st.session_state.get('selected_text_dataset', '')
                        if not hf_dataset_name:
                            st.error("데이터셋 ID를 입력해주세요.")
                            st.stop()
                        # Split은 자동으로 선택됩니다 (기본값: train, 없으면 사용 가능한 split 자동 선택)
                        split_name = "train"  # 기본값, dataset_analyzer에서 자동 조정
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
                            # Split은 자동으로 선택됩니다 (기본값: train)
                            split_name = "train"  # 기본값, dataset_analyzer에서 자동 조정
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
                            # Split은 자동으로 선택됩니다 (기본값: train)
                            split_name = "train"  # 기본값, dataset_analyzer에서 자동 조정
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
                        # 긴 리스트는 제외하고 요약 정보만 표시
                        filtered_results = {}
                        exclude_keys = ["개별 점수", "해상도 목록"]  # 너무 긴 리스트 제외
                        for key, value in results.items():
                            if key not in exclude_keys:
                                # 해상도 분포 같은 딕셔너리는 표시
                                if isinstance(value, dict) and key == "해상도 분포":
                                    filtered_results[key] = str(value)
                                # 다른 긴 리스트는 제외
                                elif isinstance(value, list) and len(value) > 20:
                                    filtered_results[key] = f"{len(value)}개 항목"
                                else:
                                    filtered_results[key] = value
                        st.dataframe({
                            "지표": list(filtered_results.keys()),
                            "값": [str(v) for v in filtered_results.values()]
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
                        "평균 유효성": results["평균 유효성"],
                        "평균 다양성": results["평균 다양성"],
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
                        # 해상도 목록 표시 (확장 가능) - 요약 정보만
                        with st.expander("선택된 이미지들의 실제 해상도 목록 (전체 보기)", expanded=False):
                            if "해상도 목록" in results:
                                # 해상도별 그룹화하여 표시
                                from collections import Counter
                                resolution_counts = Counter(results["해상도 목록"])
                                st.write("**해상도별 개수:**")
                                for res, count in sorted(resolution_counts.items(), key=lambda x: x[1], reverse=True):
                                    st.write(f"- {res}: {count}개")
                            # 전체 목록은 너무 길어서 제외 (요약 정보만 표시)
                            total_count = len(results.get('해상도 목록', []))
                            if total_count > 0:
                                st.info(f"총 {total_count}개 이미지의 해상도 정보 (상세 목록은 생략)")
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
                                sort_by = st.selectbox("정렬 기준", ["종합점수", "해상도", "유효성"], key="img_sort")
                            with col_sort2:
                                sort_order = st.selectbox("정렬 방향", ["내림차순", "오름차순"], key="img_order")
                            ascending = (sort_order == "오름차순")
                            # 컬럼 존재 여부 확인 후 정렬
                            if sort_by in df_scores.columns:
                                df_scores_sorted = df_scores.sort_values(by=sort_by, ascending=ascending)
                            else:
                                st.warning(f"⚠️ 정렬 기준 '{sort_by}'를 찾을 수 없습니다. 기본 정렬을 사용합니다.")
                                df_scores_sorted = df_scores.sort_values(by="종합점수", ascending=False)
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
                        # 긴 리스트는 제외하고 요약 정보만 표시
                        filtered_results = {}
                        exclude_keys = ["개별 점수"]  # 너무 긴 리스트 제외
                        for key, value in results.items():
                            if key not in exclude_keys:
                                # 긴 리스트는 개수만 표시
                                if isinstance(value, list) and len(value) > 20:
                                    filtered_results[key] = f"{len(value)}개 항목"
                                else:
                                    filtered_results[key] = value
                        st.dataframe({
                            "지표": list(filtered_results.keys()),
                            "값": [str(v) for v in filtered_results.values()]
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
                        "평균 형식 정확성": results["평균 형식 정확성"],
                        "평균 다양성": results["평균 다양성"],
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
                                sort_by = st.selectbox("정렬 기준", ["종합점수", "형식 정확성", "다양성", "완전성"], key="text_sort")
                            with col_sort2:
                                sort_order = st.selectbox("정렬 방향", ["내림차순", "오름차순"], key="text_order")
                            ascending = (sort_order == "오름차순")
                            # 컬럼 존재 여부 확인 후 정렬
                            if sort_by in df_scores.columns:
                                df_scores_sorted = df_scores.sort_values(by=sort_by, ascending=ascending)
                            else:
                                st.warning(f"⚠️ 정렬 기준 '{sort_by}'를 찾을 수 없습니다. 기본 정렬을 사용합니다.")
                                df_scores_sorted = df_scores.sort_values(by="종합점수", ascending=False)
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
                                    score_info = f" | 형식 정확성: {score.get('형식 정확성', 0):.3f}, 다양성: {score.get('다양성', 0):.3f}, 완전성: {score.get('완전성', 0):.3f}, 종합: {score.get('종합점수', 0):.3f}"
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
        - **형식 정확성**: 오탈자 및 맞춤법 오류 비율
        - **다양성**: 문장 간 유사도 분석 (중복이 적을수록 다양성 높음)
        - **완전성**: 의미 있는 문장의 비율
        #### 이미지 데이터
        - **해상도**: 이미지 크기 기준 충족 여부
        - **유효성**: 이미지 품질 (선명도 및 노이즈 통합 지표)
        - **다양성**: 중복 이미지 비율 (중복이 적을수록 다양성 높음)
        ### 품질 등급
        - **A**: 0.8 이상 (우수)
        - **B**: 0.6 이상 (양호)
        - **C**: 0.4 이상 (보통)
        - **D**: 0.4 미만 (개선 필요)
        """)
