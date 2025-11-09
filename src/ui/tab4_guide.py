"""품질 지표 가이드 탭"""
import streamlit as st
import pandas as pd
from src.utils import load_quality_thresholds


def render_tab4(tab):
    st.header("📚 품질 지표 가이드")
    st.markdown("""
    각 분석 모드별 품질 지표와 기준 점수를 확인할 수 있습니다.
    """)
    # 분석 모드 선택
    guide_mode = st.radio(
        "가이드 모드 선택",
        ["단일 파일 분석", "데이터셋 배치 분석", "라벨링 기반 평가"],
        horizontal=True
    )
    if guide_mode == "단일 파일 분석":
        st.subheader("📄 단일 파일 분석 품질 지표")
        col_text, col_image = st.columns(2)
        with col_text:
            st.markdown("### 📝 텍스트 데이터")
            st.markdown("""
            #### 품질 지표
            1. **형식 정확성** (0.0 ~ 1.0)
               - 오탈자 및 맞춤법 오류 검사
               - 패턴 기반 형식 오류 검출
               - 한글/영문 혼용, 공백 오류 등
               - **점수**: 오류가 적을수록 높음
            2. **다양성** (0.0 ~ 1.0)
               - 문장 간 유사도 분석
               - Sentence Transformer 기반 중복도 측정
               - 중복이 적을수록 다양성 높음
               - **점수**: 중복이 적을수록 높음
            3. **완전성** (0.0 ~ 1.0)
               - 의미 있는 문장의 비율
               - 최소 길이 이상인 문장 비율
               - 불완전한 문장 패턴 제외
               - **점수**: 완전한 문장이 많을수록 높음
            #### 종합 점수 계산
            - **계산 방식**: (형식 정확성 + 다양성 + 완전성) / 3
            - **등급 기준**:
              - **A 등급**: 0.8 이상 (우수)
              - **B 등급**: 0.6 ~ 0.8 (양호)
              - **C 등급**: 0.4 ~ 0.6 (보통)
              - **D 등급**: 0.4 미만 (개선 필요)
            """)
        with col_image:
            st.markdown("### 🖼️ 이미지 데이터")
            st.markdown("""
            #### 품질 지표
            1. **해상도** (0.0 ~ 1.0)
               - 이미지 크기 기준 충족 여부
               - 최소 기준: 512x512 픽셀
               - 고해상도 보너스 (2048px 이상)
               - 종횡비 극단적일 경우 패널티
               - **점수**: 해상도가 높을수록 높음
            2. **유효성** (0.0 ~ 1.0)
               - 선명도와 노이즈를 통합한 지표
               - 선명도: Laplacian Variance 기반
               - 노이즈: Gaussian Blur 차이 분석
               - **점수**: 선명하고 노이즈가 적을수록 높음
            3. **다양성** (단일 이미지: N/A)
               - 중복 이미지 비율 (배치 분석 시에만)
               - ImageHash 기반 중복 검사
               - 중복이 적을수록 다양성 높음
               - **점수**: 중복이 적을수록 높음
            #### 종합 점수 계산
            - **단일 이미지**: (해상도 + 유효성) / 2
            - **배치 분석**: (해상도 + 유효성 + (1 - 다양성)) / 3
            - **등급 기준**:
              - **A 등급**: 0.8 이상 (우수)
              - **B 등급**: 0.6 ~ 0.8 (양호)
              - **C 등급**: 0.4 ~ 0.6 (보통)
              - **D 등급**: 0.4 미만 (개선 필요)
            """)
        st.divider()
        st.markdown("### 💡 참고 사항")
        st.info("""
        - **단일 이미지 분석**에서는 다양성 지표를 제외합니다. (다양성은 여러 이미지 간 비교 지표)
        - 모든 점수는 0.0 ~ 1.0 범위로 정규화되어 있습니다.
        - 종합 점수는 각 지표의 평균으로 계산됩니다.
        """)
    elif guide_mode == "데이터셋 배치 분석":
        st.subheader("📊 데이터셋 배치 분석 품질 지표")
        st.markdown("""
        데이터셋 배치 분석은 단일 파일 분석과 동일한 지표를 사용하지만, 
        전체 데이터셋에 대한 통계를 제공합니다.
        """)
        col_text, col_image = st.columns(2)
        with col_text:
            st.markdown("### 📝 텍스트 데이터셋")
            st.markdown("""
            #### 품질 지표
            1. **평균 형식 정확성**
               - 각 텍스트의 형식 정확성 평균
               - 오탈자 및 맞춤법 오류 비율
            2. **평균 다양성**
               - 각 텍스트의 다양성 평균
               - 문장 간 유사도 분석
            3. **평균 완전성**
               - 각 텍스트의 완전성 평균
               - 의미 있는 문장 비율
            4. **평균 종합 점수**
               - 전체 데이터셋의 평균 품질 점수
            #### 추가 통계
            - 최소/최대 종합 점수
            - 표준편차
            - 개별 텍스트 점수 목록
            """)
        with col_image:
            st.markdown("### 🖼️ 이미지 데이터셋")
            st.markdown("""
            #### 품질 지표
            1. **평균 해상도**
               - 각 이미지의 해상도 점수 평균
            2. **평균 유효성**
               - 각 이미지의 유효성 점수 평균
               - 선명도와 노이즈 통합
            3. **평균 다양성**
               - 전체 데이터셋의 중복도
               - ImageHash 기반 중복 검사
               - **주의**: 개별 이미지 점수에는 포함되지 않음
            4. **평균 종합 점수**
               - 전체 데이터셋의 평균 품질 점수
            #### 추가 통계
            - 해상도 분포 (최소/최대/평균/중앙값)
            - 최소/최대 종합 점수
            - 표준편차
            - 개별 이미지 점수 목록
            """)
        st.divider()
        st.markdown("### 📈 종합 점수 계산 방식")
        st.markdown("""
        #### 텍스트 데이터셋
        - **개별 텍스트**: (형식 정확성 + 다양성 + 완전성) / 3
        - **데이터셋 평균**: 모든 개별 점수의 평균
        #### 이미지 데이터셋
        - **개별 이미지**: (해상도 + 유효성) / 2 (다양성 제외)
        - **데이터셋 평균**: (평균 해상도 + 평균 유효성 + (1 - 평균 다양성)) / 3
        #### 등급 기준
        - **A 등급**: 0.8 이상 (우수 - AI 학습에 바로 사용 가능)
        - **B 등급**: 0.6 ~ 0.8 (양호 - 일부 개선 필요)
        - **C 등급**: 0.4 ~ 0.6 (보통 - 품질 개선 권장)
        - **D 등급**: 0.4 미만 (개선 시급 - 데이터 정제 필요)
        """)
        st.divider()
        st.markdown("### 💡 참고 사항")
        st.info("""
        - **이미지 다양성**: 개별 이미지 점수에는 포함되지 않으며, 전체 데이터셋 통계에만 포함됩니다.
        - **샘플링**: 대용량 데이터셋의 경우 성능을 위해 일부만 샘플링하여 분석할 수 있습니다.
        - **Hugging Face 데이터셋**: 자동으로 다운로드하여 분석할 수 있습니다.
        """)
    else:  # 라벨링 기반 평가
        st.subheader("🏷️ 라벨링 기반 평가 품질 지표")
        st.markdown("""
        라벨링 기반 평가는 예측 라벨과 실제 라벨(Ground Truth)을 비교하여 
        라벨링 품질과 모델 성능을 평가합니다.
        """)
        # 임계값 로드
        from src.utils import load_quality_thresholds
        thresholds = load_quality_thresholds()
        st.markdown("### 📋 평가 카테고리")
        # 1. 정확성 (Semantic Accuracy)
        with st.expander("1️⃣ 정확성 (Semantic Accuracy)", expanded=True):
            st.markdown("""
            **의미 정확성**: 라벨이 실제 정답(Ground Truth)과 의미적으로 일치하는 정도를 측정합니다.
            """)
            if "semantic_accuracy" in thresholds:
                accuracy_metrics = thresholds["semantic_accuracy"]
                accuracy_data = []
                for metric_name, metric_info in accuracy_metrics.items():
                    threshold = metric_info.get("threshold", 0.0)
                    metric_display = metric_info.get("metric", metric_name)
                    description = metric_info.get("description", "")
                    if not description:
                        # description이 없으면 기본 설명 사용
                        desc_map = {
                            "f1_score": "F1 점수는 정밀도와 재현율의 조화 평균입니다.",
                            "iou": "Intersection over Union, 객체 탐지 정확도 지표입니다.",
                            "map": "mean Average Precision, 평균 정밀도입니다."
                        }
                        description = desc_map.get(metric_name, "")
                    accuracy_data.append({
                        "지표": metric_display,
                        "임계값": f"{threshold:.3f}",
                        "설명": description,
                        "PASS 기준": f"≥ {threshold:.3f}"
                    })
                import pandas as pd
                df_accuracy = pd.DataFrame(accuracy_data)
                st.dataframe(df_accuracy, use_container_width=True)
            st.markdown("""
            **작업 타입별 사용 지표**:
            - **분류 (classification)**: F1-Score, Accuracy
            - **탐지 (detection)**: IOU, mAP
            - **생성 (generation)**: F1-Score (선택적)
            - **질의응답 (qa)**: F1-Score (선택적)
            """)
        # 2. 일관성 (Consistency)
        with st.expander("2️⃣ 일관성 (Consistency)"):
            st.markdown("""
            **라벨링 일관성**: 평가자 간 라벨링 기준 일치 여부를 측정합니다.
            """)
            if "consistency" in thresholds:
                consistency_metrics = thresholds["consistency"]
                consistency_data = []
                for metric_name, metric_info in consistency_metrics.items():
                    threshold = metric_info.get("threshold", 0.0)
                    metric_display = metric_info.get("metric", metric_name)
                    description = metric_info.get("description", "")
                    if not description:
                        desc_map = {
                            "kappa": "평가자 간 일관성을 측정하는 지표입니다.",
                            "irr": "Inter-Rater Reliability, 평가자 간 신뢰도입니다."
                        }
                        description = desc_map.get(metric_name, "")
                    consistency_data.append({
                        "지표": metric_display,
                        "임계값": f"{threshold:.3f}",
                        "설명": description,
                        "PASS 기준": f"≥ {threshold:.3f}"
                    })
                import pandas as pd
                df_consistency = pd.DataFrame(consistency_data)
                st.dataframe(df_consistency, use_container_width=True)
            st.markdown("""
            **사용 시나리오**:
            - 여러 평가자가 동일한 데이터를 라벨링한 경우
            - 라벨링 품질 관리 및 평가자 교육
            - 고급 평가 모드에서 사용
            """)
        # 3. 완전성 (Completeness)
        with st.expander("3️⃣ 완전성 (Completeness)"):
            st.markdown("""
            **데이터 구조 완전성**: 필수 필드 누락 및 결측치 비율을 측정합니다.
            """)
            if "completeness" in thresholds:
                completeness_metrics = thresholds["completeness"]
                completeness_data = []
                for metric_name, metric_info in completeness_metrics.items():
                    threshold = metric_info.get("threshold", 0.0)
                    metric_display = metric_info.get("metric", metric_name)
                    description = metric_info.get("description", "")
                    if not description:
                        desc_map = {
                            "missing_rate": "필수 필드 누락 비율입니다. (낮을수록 좋음)",
                            "null_rate": "비필수 필드 결측치 비율입니다. (낮을수록 좋음)"
                        }
                        description = desc_map.get(metric_name, "")
                    completeness_data.append({
                        "지표": metric_display,
                        "임계값": f"{threshold:.3f}",
                        "설명": description,
                        "PASS 기준": f"≤ {threshold:.3f}"  # 낮을수록 좋음
                    })
                import pandas as pd
                df_completeness = pd.DataFrame(completeness_data)
                st.dataframe(df_completeness, use_container_width=True)
            st.markdown("""
            **측정 항목**:
            - **MissingRate**: 필수 필드 누락 비율 (목표: 0%)
            - **NullRate**: 비필수 필드 결측치 비율 (목표: ≤ 5%)
            """)
        # 4. 유효성 (Validity)
        with st.expander("4️⃣ 유효성 (Validity)"):
            st.markdown("""
            **모델 성능 유효성**: 모델 학습 목적에 부합하는 정도를 측정합니다.
            """)
            if "validity" in thresholds:
                validity_metrics = thresholds["validity"]
                validity_data = []
                for metric_name, metric_info in validity_metrics.items():
                    threshold = metric_info.get("threshold", 0.0)
                    metric_display = metric_info.get("metric", metric_name)
                    description = metric_info.get("description", "")
                    if not description:
                        desc_map = {
                            "f1_model": "모델 성능 평가를 위한 F1 점수입니다.",
                            "rouge_1": "ROUGE-1 점수, 단어 단위 겹침을 측정합니다.",
                            "rouge_2": "ROUGE-2 점수, 2-gram 겹침을 측정합니다.",
                            "rouge_l": "ROUGE-L 점수, 가장 긴 공통 부분 수열을 측정합니다.",
                            "bleu": "BLEU 점수, n-gram 정밀도를 측정합니다.",
                            "cer": "Character Error Rate, 문자 오류율입니다. (낮을수록 좋음)"
                        }
                        description = desc_map.get(metric_name, "")
                    # CER은 낮을수록 좋음
                    pass_criterion = f"≤ {threshold:.3f}" if metric_name == "cer" else f"≥ {threshold:.3f}"
                    validity_data.append({
                        "지표": metric_display,
                        "임계값": f"{threshold:.3f}",
                        "설명": description,
                        "PASS 기준": pass_criterion
                    })
                import pandas as pd
                df_validity = pd.DataFrame(validity_data)
                st.dataframe(df_validity, use_container_width=True)
            st.markdown("""
            **작업 타입별 사용 지표**:
            - **텍스트 생성 (generation)**: ROUGE, BLEU, CER
            - **질의응답 (qa)**: ROUGE, BLEU, CER
            - **분류 (classification)**: F1-Score (선택적)
            """)
        # 5. 다양성 (Diversity)
        with st.expander("5️⃣ 다양성 (Diversity)"):
            st.markdown("""
            **데이터 분포 다양성**: 클래스·주제별 분포 균형 여부를 측정합니다.
            """)
            if "diversity" in thresholds:
                diversity_metrics = thresholds["diversity"]
                diversity_data = []
                for metric_name, metric_info in diversity_metrics.items():
                    threshold = metric_info.get("threshold", 0.0)
                    metric_display = metric_info.get("metric", metric_name)
                    description = metric_info.get("description", "")
                    if not description:
                        desc_map = {
                            "category_variance": "카테고리별 분포의 분산입니다.",
                            "entropy": "엔트로피, 데이터 분포의 다양성을 측정합니다."
                        }
                        description = desc_map.get(metric_name, "")
                    diversity_data.append({
                        "지표": metric_display,
                        "임계값": f"{threshold:.3f}",
                        "설명": description,
                        "PASS 기준": f"분산 ≤ {threshold:.3f}" if "variance" in metric_name else "엔트로피 ≥ {threshold:.3f}"
                    })
                import pandas as pd
                df_diversity = pd.DataFrame(diversity_data)
                st.dataframe(df_diversity, use_container_width=True)
            st.markdown("""
            **측정 항목**:
            - **CategoryVariance**: 카테고리별 분포의 분산 (목표: ≤ 10%)
            - **Entropy**: 데이터 분포의 다양성 (엔트로피가 높을수록 다양함)
            """)
        # 6. 안전성 (Safety)
        with st.expander("6️⃣ 안전성 (Safety)"):
            st.markdown("""
            **유해/편향 데이터 검출**: 민감정보·편향 여부를 측정합니다.
            """)
            if "safety" in thresholds:
                safety_metrics = thresholds["safety"]
                safety_data = []
                for metric_name, metric_info in safety_metrics.items():
                    threshold = metric_info.get("threshold", 0.0)
                    metric_display = metric_info.get("metric", metric_name)
                    description = metric_info.get("description", "")
                    if not description:
                        desc_map = {
                            "toxicity_rate": "유해 표현 검출 비율입니다. (낮을수록 좋음)"
                        }
                        description = desc_map.get(metric_name, "")
                    safety_data.append({
                        "지표": metric_display,
                        "임계값": f"{threshold:.3f}",
                        "설명": description,
                        "PASS 기준": f"≤ {threshold:.3f}"  # 낮을수록 좋음
                    })
                import pandas as pd
                df_safety = pd.DataFrame(safety_data)
                st.dataframe(df_safety, use_container_width=True)
            st.markdown("""
            **측정 항목**:
            - **ToxicityRate**: 유해 표현 검출 비율 (목표: 0%)
            - 키워드 기반 검출 방식 사용
            """)
        st.divider()
        st.markdown("### 📊 종합 평가 기준")
        st.markdown("""
        #### PASS/FAIL 판정
        각 지표는 임계값과 비교하여 PASS/FAIL을 판정합니다:
        - **PASS ✅**: 지표값이 임계값 기준을 만족
        - **FAIL ❌**: 지표값이 임계값 기준을 만족하지 않음
        - **N/A**: 계산 불가 또는 해당 작업 타입에 적용되지 않음
        #### 종합 점수 계산
        - **계산 방식**: PASS 지표 수 / 전체 지표 수
        - **점수 범위**: 0.0 ~ 1.0
        - **등급 기준**:
          - **우수**: PASS 비율 80% 이상
          - **양호**: PASS 비율 60% ~ 80%
          - **보통**: PASS 비율 40% ~ 60%
          - **개선 필요**: PASS 비율 40% 미만
        """)
        st.divider()
        st.markdown("### 💡 참고 사항")
        st.info("""
        - **임계값 설정**: `config/quality_thresholds.json` 파일에서 임계값을 수정할 수 있습니다.
        - **작업 타입**: 작업 타입(classification, detection, generation, qa)에 따라 평가되는 지표가 다릅니다.
        - **선택적 의존성**: 일부 지표(ROUGE, BLEU, CER)는 선택적 패키지가 필요합니다.
        - **샘플 데이터**: 사이드바에서 샘플 데이터를 생성하여 테스트할 수 있습니다.
        """)
        # 임계값 파일 위치 안내
        st.markdown("### ⚙️ 임계값 설정 파일")
        st.code("config/quality_thresholds.json", language="text")
        st.markdown("이 파일에서 각 지표의 임계값을 수정할 수 있습니다.")
