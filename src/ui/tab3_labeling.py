"""라벨링 기반 평가 탭"""
import streamlit as st
import pandas as pd
import json
from src.quality_evaluator import (
    evaluate_semantic_accuracy, evaluate_consistency,
    evaluate_completeness, evaluate_validity,
    evaluate_diversity, evaluate_safety,
    evaluate_quality_with_thresholds
)
from src.utils import load_quality_thresholds


def render_tab3(tab):
    st.header("라벨링 기반 품질 평가")
    st.markdown("""
    **라벨링 정보가 포함된 데이터셋의 품질을 평가합니다.**
    이 모드는 다음 지표를 평가합니다:
    - **정확성**: mAP, IOU, F1-Score (라벨링 정확성)
    - **일관성**: Cohen's Kappa, IRR (평가자 간 일관성)
    - **완전성**: MissingRate, NullRate (데이터 구조)
    - **유효성**: ROUGE, BLEU, CER (모델 성능)
    - **다양성**: CategoryVariance, Entropy (데이터 분포)
    - **안전성**: ToxicityRate (유해 표현 검출)
    """)
    # 평가 모드 선택
    evaluation_mode = st.radio(
        "평가 모드 선택",
        ["간단 평가 (CSV/JSON)", "고급 평가 (평가자 정보 포함)"],
        horizontal=True,
        help="간단 평가: 예측 라벨과 실제 라벨만 필요. 고급 평가: 여러 평가자의 라벨 정보 필요."
    )
    if evaluation_mode == "간단 평가 (CSV/JSON)":
        st.subheader("데이터셋 업로드")
        # 샘플 데이터 사용 옵션
        use_sample_data = False
        if 'sample_labeling_data' in st.session_state:
            col_sample, col_upload = st.columns([1, 2])
            with col_sample:
                if st.button("📊 샘플 데이터 사용", use_container_width=True, type="secondary"):
                    use_sample_data = True
                    st.session_state['use_sample_labeling_data'] = True
                    st.rerun()
            with col_upload:
                st.caption("또는 파일을 업로드하세요")
        col1, col2 = st.columns(2)
        with col1:
            dataset_file = st.file_uploader(
                "데이터셋 파일 (CSV/JSON)",
                type=["csv", "json"],
                help="예측 라벨과 실제 라벨이 포함된 파일"
            )
        with col2:
            task_type = st.selectbox(
                "작업 타입",
                ["classification", "detection", "generation", "qa"],
                help="데이터셋의 작업 타입을 선택하세요"
            )
        # 샘플 데이터 사용 여부 확인
        if 'use_sample_labeling_data' in st.session_state and st.session_state.get('use_sample_labeling_data', False):
            if 'sample_labeling_data' in st.session_state:
                sample_data = st.session_state['sample_labeling_data']
                df = sample_data['dataframe']
                task_type = sample_data['task_type']
                prediction_col = sample_data['prediction_col']
                ground_truth_col = sample_data['ground_truth_col']
                st.success(f"✅ 샘플 데이터 사용 중: {len(df)}개 항목 ({task_type} 작업)")
                st.info("💡 사이드바에서 다른 샘플 데이터를 생성하거나 파일을 업로드할 수 있습니다.")
                # 샘플 데이터 미리보기
                with st.expander("샘플 데이터 미리보기", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)
                # 자동으로 평가 실행
                with st.spinner("품질을 평가 중입니다..."):
                    try:
                        from src.quality_evaluator import (
                            evaluate_semantic_accuracy,
                            evaluate_completeness,
                            evaluate_validity,
                            evaluate_diversity,
                            evaluate_safety,
                            evaluate_quality_with_thresholds
                        )
                        from src.utils import load_quality_thresholds
                        predictions = df[prediction_col].tolist()
                        ground_truth = df[ground_truth_col].tolist()
                        # 데이터 타입 검증
                        if len(predictions) != len(ground_truth):
                            st.error("⚠️ 예측 라벨과 실제 라벨의 개수가 일치하지 않습니다.")
                        elif len(predictions) == 0:
                            st.error("⚠️ 평가할 데이터가 없습니다.")
                        else:
                            # 품질 평가 실행
                            quality_results = {}
                            # 1. 정확성 평가
                            accuracy_results = evaluate_semantic_accuracy(
                                predictions, ground_truth, task_type=task_type
                            )
                            quality_results["semantic_accuracy"] = accuracy_results
                            # 2. 완전성 평가
                            required_fields = [prediction_col, ground_truth_col]
                            completeness_results = evaluate_completeness(
                                df.to_dict('records'), required_fields
                            )
                            quality_results["completeness"] = completeness_results
                            # 3. 유효성 평가 (텍스트 작업인 경우)
                            if task_type in ["generation", "qa"]:
                                validity_results = evaluate_validity(
                                    [str(p) for p in predictions],
                                    [str(g) for g in ground_truth],
                                    task_type=task_type
                                )
                                quality_results["validity"] = validity_results
                            # 4. 다양성 평가
                            diversity_results = evaluate_diversity(ground_truth)
                            quality_results["diversity"] = diversity_results
                            # 5. 안전성 평가 (텍스트인 경우)
                            if task_type in ["generation", "qa", "classification"]:
                                safety_results = evaluate_safety([str(g) for g in ground_truth])
                                quality_results["safety"] = safety_results
                            # 임계값 기반 평가
                            thresholds = load_quality_thresholds()
                            evaluated_results = evaluate_quality_with_thresholds(
                                quality_results, thresholds
                            )
                            # 결과 저장
                            st.session_state['labeling_evaluation'] = {
                                'results': evaluated_results,
                                'raw_results': quality_results,
                                'dataset_name': '샘플 데이터'
                            }
                            # 결과 표시
                            st.success("평가 완료!")
                            st.session_state['use_sample_labeling_data'] = False  # 평가 후 플래그 리셋
                    except Exception as e:
                        st.error(f"⚠️ 평가 중 오류 발생: {e}")
                        st.exception(e)
        elif dataset_file is not None:
            try:
                import pandas as pd
                import json
                # 파일 읽기 (에러 처리 강화)
                try:
                    if dataset_file.name.endswith('.csv'):
                        df = pd.read_csv(dataset_file, encoding='utf-8')
                        st.success(f"CSV 파일 로드 완료: {len(df)}개 항목")
                    elif dataset_file.name.endswith('.json'):
                        dataset_file.seek(0)  # 파일 포인터 리셋
                        data = json.load(dataset_file)
                        if isinstance(data, list):
                            df = pd.DataFrame(data)
                        else:
                            df = pd.DataFrame([data])
                        st.success(f"JSON 파일 로드 완료: {len(df)}개 항목")
                    else:
                        st.error("⚠️ 지원하지 않는 파일 형식입니다. CSV 또는 JSON 파일을 업로드해주세요.")
                        df = None
                except UnicodeDecodeError:
                    st.error("⚠️ 파일 인코딩 오류가 발생했습니다. UTF-8 인코딩 파일을 사용해주세요.")
                    df = None
                except json.JSONDecodeError as e:
                    st.error(f"⚠️ JSON 파싱 오류: {e}")
                    df = None
                except Exception as e:
                    st.error(f"⚠️ 파일 읽기 오류: {e}")
                    df = None
                # 컬럼 선택 (데이터프레임이 로드된 경우에만)
                if df is not None and not df.empty:
                    st.subheader("컬럼 매핑")
                    col1, col2 = st.columns(2)
                    with col1:
                        prediction_col = st.selectbox(
                            "예측 라벨 컬럼",
                            df.columns.tolist(),
                            help="모델이 예측한 라벨 컬럼 선택"
                        )
                    with col2:
                        ground_truth_col = st.selectbox(
                            "실제 라벨 컬럼",
                            df.columns.tolist(),
                            help="실제 정답 라벨 컬럼 선택"
                        )
                    # 컬럼 검증
                    if prediction_col == ground_truth_col:
                        st.warning("⚠️ 예측 라벨과 실제 라벨 컬럼이 동일합니다. 다른 컬럼을 선택해주세요.")
                    # 데이터 미리보기
                    with st.expander("데이터 미리보기"):
                        try:
                            st.dataframe(df[[prediction_col, ground_truth_col]].head(10))
                        except KeyError as e:
                            st.error(f"⚠️ 컬럼 오류: {e}")
                else:
                    st.warning("⚠️ 데이터를 로드할 수 없습니다. 파일을 확인해주세요.")
                # 평가 실행 (데이터프레임과 컬럼 검증 후)
                if df is not None and not df.empty:
                    # prediction_col과 ground_truth_col이 정의되어 있는지 확인
                    if 'prediction_col' in locals() and 'ground_truth_col' in locals():
                        if prediction_col in df.columns and ground_truth_col in df.columns:
                            if st.button("품질 평가 시작", type="primary", use_container_width=True):
                                with st.spinner("품질을 평가 중입니다..."):
                                    try:
                                        from src.quality_evaluator import (
                                            evaluate_semantic_accuracy,
                                            evaluate_completeness,
                                            evaluate_validity,
                                            evaluate_diversity,
                                            evaluate_safety,
                                            evaluate_quality_with_thresholds
                                        )
                                        from src.utils import load_quality_thresholds
                                        predictions = df[prediction_col].tolist()
                                        ground_truth = df[ground_truth_col].tolist()
                                        # 데이터 타입 검증
                                        if len(predictions) != len(ground_truth):
                                            st.error("⚠️ 예측 라벨과 실제 라벨의 개수가 일치하지 않습니다.")
                                        elif len(predictions) == 0:
                                            st.error("⚠️ 평가할 데이터가 없습니다.")
                                        else:
                                            # 품질 평가 실행
                                            quality_results = {}
                                            # 1. 정확성 평가
                                            accuracy_results = evaluate_semantic_accuracy(
                                                predictions, ground_truth, task_type=task_type
                                            )
                                            quality_results["semantic_accuracy"] = accuracy_results
                                            # 2. 완전성 평가
                                            required_fields = [prediction_col, ground_truth_col]
                                            completeness_results = evaluate_completeness(
                                                df.to_dict('records'), required_fields
                                            )
                                            quality_results["completeness"] = completeness_results
                                            # 3. 유효성 평가 (텍스트 작업인 경우)
                                            if task_type in ["generation", "qa"]:
                                                validity_results = evaluate_validity(
                                                    [str(p) for p in predictions],
                                                    [str(g) for g in ground_truth],
                                                    task_type=task_type
                                                )
                                                quality_results["validity"] = validity_results
                                            # 4. 다양성 평가
                                            diversity_results = evaluate_diversity(ground_truth)
                                            quality_results["diversity"] = diversity_results
                                            # 5. 안전성 평가 (텍스트인 경우)
                                            if task_type in ["generation", "qa", "classification"]:
                                                safety_results = evaluate_safety([str(g) for g in ground_truth])
                                                quality_results["safety"] = safety_results
                                            # 임계값 기반 평가
                                            thresholds = load_quality_thresholds()
                                            evaluated_results = evaluate_quality_with_thresholds(
                                                quality_results, thresholds
                                            )
                                            # 결과 저장
                                            st.session_state['labeling_evaluation'] = {
                                                'results': evaluated_results,
                                                'raw_results': quality_results,
                                                'dataset_name': dataset_file.name
                                            }
                                            # 결과 표시
                                            st.success("평가 완료!")
                                    except Exception as e:
                                        st.error(f"⚠️ 평가 중 오류 발생: {e}")
                                        st.exception(e)
            except Exception as e:
                st.error(f"⚠️ 처리 중 오류 발생: {e}")
                st.exception(e)
        # 샘플 데이터 사용 후 결과 표시도 포함
        # 결과 표시 (평가가 성공한 경우)
        if 'labeling_evaluation' in st.session_state:
            evaluated_results = st.session_state['labeling_evaluation']['results']
            st.divider()
            # 결과를 카테고리별로 표시
            for category, metrics in evaluated_results.items():
                st.subheader(f"📊 {category.replace('_', ' ').title()}")
                # 메트릭별 표시
                metric_data = []
                for metric_name, metric_info in metrics.items():
                    if isinstance(metric_info, dict) and "value" in metric_info:
                        value = metric_info.get("value")
                        threshold = metric_info.get("threshold")
                        status = metric_info.get("status", "N/A")
                        metric_display = metric_info.get("metric_display", metric_name)
                        if value is not None:
                            metric_data.append({
                                "지표": metric_display,
                                "값": f"{value:.3f}" if isinstance(value, (int, float)) else str(value),
                                "임계값": f"{threshold:.3f}" if threshold is not None else "N/A",
                                "상태": status
                            })
                if metric_data:
                    import pandas as pd
                    df_metrics = pd.DataFrame(metric_data)
                    st.dataframe(df_metrics, use_container_width=True)
                    # 통계 요약
                    pass_count = sum(1 for m in metric_data if "✅" in m["상태"])
                    total_count = len(metric_data)
                    st.metric("통과 지표", f"{pass_count}/{total_count}")
                else:
                    st.info("계산 가능한 지표가 없습니다.")
                st.divider()
    else:  # 고급 평가
        st.subheader("고급 평가 (평가자 정보 포함)")
        st.info("""
        **고급 평가 모드**는 여러 평가자의 라벨링 정보를 사용하여 일관성을 평가합니다.
        필요 정보:
        - 여러 평가자의 라벨 파일 (CSV/JSON)
        - 각 평가자별 라벨 컬럼
        """)
        num_raters = st.number_input(
            "평가자 수",
            min_value=2,
            max_value=10,
            value=2,
            help="일관성 평가를 위한 평가자 수"
        )
        rater_files = []
        rater_names = []
        for i in range(num_raters):
            col1, col2 = st.columns([3, 1])
            with col1:
                file = st.file_uploader(
                    f"평가자 {i+1} 라벨 파일",
                    type=["csv", "json"],
                    key=f"rater_{i}"
                )
            with col2:
                name = st.text_input(f"평가자 {i+1} 이름", value=f"Rater{i+1}", key=f"name_{i}")
            if file:
                rater_files.append(file)
                rater_names.append(name)
        if len(rater_files) == num_raters and st.button("일관성 평가 시작", type="primary"):
            try:
                import pandas as pd
                import json
                from src.quality_evaluator import evaluate_consistency
                labels_by_raters = []
                for file in rater_files:
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:
                        data = json.load(file)
                        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
                    # 첫 번째 컬럼을 라벨로 사용 (또는 사용자 선택)
                    label_col = df.columns[0]
                    labels = df[label_col].tolist()
                    labels_by_raters.append(labels)
                with st.spinner("일관성을 평가 중입니다..."):
                    consistency_results = evaluate_consistency(
                        labels_by_raters, rater_names
                    )
                st.success("평가 완료!")
                st.subheader("일관성 평가 결과")
                if "error" in consistency_results:
                    st.error(consistency_results["error"])
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        if consistency_results.get("kappa") is not None:
                            kappa = consistency_results["kappa"]
                            threshold = 0.8
                            status = "PASS ✅" if kappa >= threshold else "FAIL ❌"
                            st.metric("Cohen's Kappa", f"{kappa:.3f}", delta=None)
                            st.caption(f"임계값: {threshold} | 상태: {status}")
                    with col2:
                        if consistency_results.get("irr") is not None:
                            irr = consistency_results["irr"]
                            threshold = 0.8
                            status = "PASS ✅" if irr >= threshold else "FAIL ❌"
                            st.metric("IRR", f"{irr:.3f}", delta=None)
                            st.caption(f"임계값: {threshold} | 상태: {status}")
                    if consistency_results.get("kappa_pairs"):
                        st.info(f"평가자 쌍 수: {consistency_results['kappa_pairs']}개")
            except Exception as e:
                st.error(f"오류 발생: {e}")
                st.exception(e)
