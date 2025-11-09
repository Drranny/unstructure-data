# 품질 지표 항목명 매핑 가이드

## 현재 상태

### 기존 탭 (1, 2) - 내재적 품질 측정
- **텍스트**: 
  - `형식 정확성` (이전: 정확성/오탈자비율)
  - `다양성` (이전: 중복도/유사도역비율)
  - `완전성` (문장충실도)

- **이미지**:
  - `해상도` (변경 없음)
  - `유효성` (이전: 선명도 + 노이즈 통합)
  - `다양성` (이전: 중복도, 단일 이미지 분석 시 제외)

### 새 탭 (3) - 라벨링 기반 평가
- `semantic_accuracy` (의미 정확성)
- `consistency` (일관성)
- `completeness` (완전성)
- `validity` (유효성)
- `diversity` (다양성)
- `safety` (안전성)

## 새로운 기준표 항목명

제공된 기준표에 따른 표준 항목명:

1. **정확성 (Accuracy)**
   - 의미 정확성: `semantic_accuracy`
   - 형식 정확성: `format_accuracy`

2. **일관성 (Consistency)**
   - 라벨링 일관성: `labeling_consistency`
   - 속성값 일관성: `attribute_consistency`

3. **완전성 (Completeness)**
   - 누락 데이터율: `missing_rate`
   - 결측치 비율: `null_rate`

4. **유효성 (Validity)**
   - 모델 기여도: `model_contribution`

5. **다양성 (Diversity)**
   - 데이터 분포: `data_distribution`

6. **안전성 (Safety)**
   - 유해/편향 데이터: `harmful_content`

## 변경 필요 여부

현재는 **하이브리드 접근**을 사용:
- 기존 탭: 내재적 품질 측정 (기존 항목명 유지)
- 새 탭: 라벨링 기반 평가 (새 기준표 항목명 사용)

기존 탭의 항목명도 새 기준표에 맞게 변경하려면 추가 작업이 필요합니다.

