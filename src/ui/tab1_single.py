"""단일 파일 분석 탭"""
import streamlit as st
import pandas as pd
from PIL import Image
import io
from datetime import datetime
from src.text_quality import analyze_text_quality
from src.image_quality import analyze_image_quality
from src.utils import calc_total_score, get_grade, generate_text_report_pdf, generate_image_report_pdf
from src.dataset_analyzer import analyze_dataset_images


def render_tab1(tab):
    st.header("파일 업로드 및 분석")

    # 샘플 데이터 사용 옵션
    use_sample = False
    if st.session_state.get('use_sample_text', False):
        use_sample = True
        st.session_state['use_sample_text'] = False  # 플래그 리셋
    elif st.session_state.get('use_sample_image', False):
        use_sample = True
        st.session_state['use_sample_image'] = False  # 플래그 리셋

    # 샘플 텍스트 분석
    if 'sample_text' in st.session_state and use_sample:
        st.success("✅ 샘플 텍스트 분석 모드")
        text = st.session_state['sample_text']

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
        dataset_name = 'sample_text.txt'
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
            if 'sample_text' in st.session_state:
                del st.session_state['sample_text']
            if 'last_text_analysis' in st.session_state:
                del st.session_state['last_text_analysis']
            st.rerun()

    # 샘플 이미지 분석
    elif 'sample_image' in st.session_state and use_sample:
        st.success("✅ 샘플 이미지 분석 모드")
        img = st.session_state['sample_image']

        import pandas as pd

        col_preview, col_info = st.columns([2, 1])

        with col_preview:
            st.image(img, caption="샘플 이미지", use_container_width=True)

        with col_info:
            st.info("**샘플 이미지 정보**\n- 크기: 512x512\n- 색상: Light Blue\n\n💡 단색 이미지이므로 해상도는 높지만 선명도와 노이즈 지표는 제한적입니다.")

        with st.spinner("이미지 품질을 분석 중입니다..."):
            results = analyze_dataset_images(images=[img], max_samples=1)

            individual_scores = results.get("개별 점수", [])
            if individual_scores:
                image_scores = individual_scores[0]
            else:
                image_scores = {}
                st.error("⚠️ 분석 결과를 가져올 수 없습니다.")
            total = results.get('평균 종합 점수', 0.0)
            grade = get_grade(total)
            is_single_image_analysis = (results.get("단일 분석 여부") == "예")

        # 결과를 세션에 저장
        st.session_state['last_image_analysis'] = {
            'scores': image_scores,
            'total': total,
            'grade': grade,
            'file_name': 'sample_image.png',
            'is_single': is_single_image_analysis
        }

        # 결과 표시
        st.subheader("분석 결과")
        if is_single_image_analysis:
            st.warning("⚠️ **다양성 항목 제외 안내:** 단일 이미지 분석이므로 다양성 지표를 제외한 **2가지 주요 지표**를 기반으로 종합 점수를 산출했습니다. (다양성은 N/A로 표시됩니다.)")

        result_col1, result_col2 = st.columns([1, 1])

        scores_for_df = {k: [v] for k, v in image_scores.items()}
        df_to_show = pd.DataFrame(scores_for_df, index=["점수"])

        with result_col1:
            st.dataframe(df_to_show.T, use_container_width=True)

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
        chart_data = {
            k: v for k, v in image_scores.items() if v != "N/A"
        }
        st.bar_chart(chart_data)

        # PDF 다운로드 버튼
        st.divider()
        dataset_name = 'sample_image.png'
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
        if st.button("새 파일로 분석하기"):
            if 'sample_image' in st.session_state:
                del st.session_state['sample_image']
            if 'last_image_analysis' in st.session_state:
                del st.session_state['last_image_analysis']
            st.rerun()

    # 일반 파일 업로드
    else:
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
            import pandas as pd

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
                        # ------------------- 1. analyze_dataset_images 호출 -------------------
                        # 단일 이미지를 리스트로 묶어 dataset_analyzer.py로 전달
                        results = analyze_dataset_images(images=[img], max_samples=1)

                        # results에서 최종 결과 추출 (안전한 접근)
                        individual_scores = results.get("개별 점수", [])
                        if individual_scores:
                            image_scores = individual_scores[0]  # 단일 이미지이므로 첫 번째 개별 점수 사용
                        else:
                            image_scores = {}
                            st.error("⚠️ 분석 결과를 가져올 수 없습니다.")
                        total = results.get('평균 종합 점수', 0.0)
                        grade = get_grade(total)
                        is_single_image_analysis = (results.get("단일 분석 여부") == "예")

                    # 결과를 세션에 저장
                    st.session_state['last_image_analysis'] = {
                        'scores': image_scores,
                        'total': total,
                        'grade': grade,
                        'file_name': uploaded_file.name,
                        'is_single': is_single_image_analysis
                    }

                    # 결과 표시
                    st.subheader("분석 결과")
                    if is_single_image_analysis:
                        st.warning("⚠️ **다양성 항목 제외 안내:** 단일 이미지 분석이므로 다양성 지표를 제외한 **2가지 주요 지표**를 기반으로 종합 점수를 산출했습니다. (다양성은 N/A로 표시됩니다.)")

                    result_col1, result_col2 = st.columns([1, 1])

                    # st.dataframe에 사용할 데이터 준비 (중복도 N/A 처리 포함)
                    scores_for_df = {k: [v] for k, v in image_scores.items()}
                    df_to_show = pd.DataFrame(scores_for_df, index=["점수"])

                    with result_col1:
                        # 중복도 N/A가 포함된 데이터프레임 출력
                        st.dataframe(df_to_show.T, use_container_width=True)

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
                    chart_data = {
                        k: v for k, v in image_scores.items() if v != "N/A"
                    }
                    st.bar_chart(chart_data)

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

    else:
        st.info("**사용 방법**:\n1. 위에서 파일을 업로드하세요\n2. 파일 타입(텍스트/이미지)을 선택하세요\n3. 분석 버튼을 클릭하세요")
        st.divider()