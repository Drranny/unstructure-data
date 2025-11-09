# 품질 지표 기준표 비교 및 코드 변경 영향 분석

## 📊 현재 프로그램 vs 제공된 기준표 비교

### 현재 프로그램의 품질 지표

#### 텍스트 데이터 (탭 1, 2)
- **형식 정확성**: 패턴 기반 오탈자 검사
- **다양성**: Sentence Transformer 기반 문장 유사도 (중복이 적을수록 높음)
- **완전성**: 의미 있는 문장 비율

#### 이미지 데이터 (탭 1, 2)
- **해상도**: 이미지 크기 기준 (512x512 이상)
- **유효성**: 선명도(Laplacian Variance)와 노이즈(Gaussian Blur 차이) 통합
- **다양성**: ImageHash 기반 중복 검사 (단일 이미지 분석 시 제외)

#### 라벨링 기반 평가 (탭 3)
- **정확성 (semantic_accuracy)**: F1-Score, IOU, mAP
- **일관성 (consistency)**: Cohen's Kappa, IRR
- **완전성 (completeness)**: MissingRate, NullRate
- **유효성 (validity)**: ROUGE, BLEU, CER
- **다양성 (diversity)**: CategoryVariance, Entropy
- **안전성 (safety)**: ToxicityRate

### 제공된 기준표의 품질 지표

#### 정확성 (Accuracy)
- **의미 정확성**: mAP, IOU, F1-Score (라벨링 정확성)
- **형식 정확성**: 형식 오류율

#### 일관성 (Consistency)
- **라벨링 일관성**: Cohen's Kappa, IRR (평가자 간 일관성)
- **속성값 일관성**: 불일치율

#### 완전성 (Completeness)
- **누락 데이터율**: MissingRate (필수 필드)
- **결측치 비율**: NullRate (비필수 필드)

#### 유효성 (Validity)
- **모델 기여도**: F1, ROUGE, BLEU, CER (모델 성능)

#### 다양성 (Diversity)
- **데이터 분포**: CategoryVariance, Entropy (클래스 분포)

#### 안전성 (Safety)
- **유해/편향 데이터**: 유해 표현 검출률

---

## 🔍 핵심 차이점

| 구분 | 현재 프로그램 | 제공된 기준표 |
|------|------------|------------|
| **접근 방식** | 내재적 품질 측정 (라벨링 불필요) | 라벨링 기반 품질 측정 (Ground Truth 필요) |
| **입력 데이터** | 단일 파일 또는 데이터셋 | 데이터셋 + 라벨링 정보 + Ground Truth |
| **측정 대상** | 데이터 자체의 품질 (해상도, 오탈자 등) | 라벨링 정확성, 모델 성능, 데이터 구조 |
| **평가자 정보** | 불필요 | 필요 (일관성 측정용) |
| **모델 정보** | 불필요 | 필요 (유효성 측정용) |

---

## 📝 코드 변경 영향 분석

### 1. **데이터 입력 구조 변경** ⚠️ **대규모 변경**

#### 현재
```python
# 단일 파일 업로드
uploaded_file = st.file_uploader("파일 선택")
text = uploaded_file.read().decode("utf-8")
scores = analyze_text_quality(text)  # 라벨링 불필요
```

#### 변경 필요
```python
# 데이터셋 + 라벨링 정보 필요
dataset = {
    "data": [...],  # 실제 데이터
    "labels": [...],  # 라벨링 정보
    "ground_truth": [...],  # Ground Truth (선택적)
    "metadata": {...}  # 메타데이터
}
scores = evaluate_quality_with_labels(dataset)  # 라벨링 필수
```

**변경 범위**: 
- `app.py`: 파일 업로드 UI → 데이터셋 + 라벨링 업로드 UI
- `src/dataset_analyzer.py`: 데이터셋 로드 로직 전면 수정

---

### 2. **품질 지표 계산 로직 변경** ⚠️ **대규모 변경**

#### 현재: `src/text_quality.py`
```python
def analyze_text_quality(text: str):
    # 오탈자 검사 (패턴 기반)
    accuracy_score = check_text_accuracy(text)
    # 중복도 (임베딩 기반)
    duplication_score = check_text_duplication(sentences)
    # 완전성 (문장 구조 기반)
    completeness_score = check_completeness(sentences)
    return {"정확성": accuracy_score, ...}
```

#### 변경 필요: 새로운 모듈 생성
```python
# src/quality_evaluator.py (새로 생성)
def evaluate_semantic_accuracy(predictions, ground_truth):
    """의미 정확성: mAP, IOU, F1-Score"""
    f1 = calculate_f1_score(predictions, ground_truth)
    iou = calculate_iou(predictions, ground_truth)
    map_score = calculate_map(predictions, ground_truth)
    return {"F1": f1, "IOU": iou, "mAP": map_score}

def evaluate_consistency(labels_by_raters):
    """일관성: Cohen's Kappa"""
    kappa = calculate_cohens_kappa(labels_by_raters)
    return {"Kappa": kappa}

def evaluate_validity(model_predictions, ground_truth):
    """유효성: ROUGE, BLEU, CER"""
    rouge = calculate_rouge(model_predictions, ground_truth)
    bleu = calculate_bleu(model_predictions, ground_truth)
    cer = calculate_cer(model_predictions, ground_truth)
    return {"ROUGE": rouge, "BLEU": bleu, "CER": cer}

def evaluate_diversity(labels):
    """다양성: CategoryVariance, Entropy"""
    variance = calculate_category_variance(labels)
    entropy = calculate_entropy(labels)
    return {"Variance": variance, "Entropy": entropy}

def evaluate_safety(data):
    """안전성: 유해 표현 검출"""
    toxicity_rate = detect_toxic_content(data)
    return {"ToxicityRate": toxicity_rate}
```

**변경 범위**:
- `src/text_quality.py`: 대부분의 함수 재작성 또는 새 모듈로 분리
- `src/image_quality.py`: 라벨링 기반 평가 추가
- **새 모듈 생성**: `src/quality_evaluator.py`, `src/labeling_evaluator.py`

---

### 3. **데이터셋 구조 처리 변경** ⚠️ **중규모 변경**

#### 현재
```python
# 단순 이미지/텍스트 리스트
images = [Image.open(f) for f in image_files]
texts = [open(f).read() for f in text_files]
```

#### 변경 필요
```python
# 구조화된 데이터셋 (JSON/CSV 형식)
dataset = {
    "items": [
        {
            "id": "001",
            "data": "텍스트 또는 이미지 경로",
            "label": "긍정",
            "ground_truth": "긍정",
            "metadata": {"source": "...", "date": "..."}
        },
        ...
    ],
    "schema": {
        "label_field": "label",
        "data_field": "data",
        ...
    }
}
```

**변경 범위**:
- `src/dataset_analyzer.py`: 데이터셋 로드 로직 수정
- JSON/CSV 파서 추가
- 라벨링 정보 추출 로직 추가

---

### 4. **UI 변경** ⚠️ **중규모 변경**

#### 현재: `app.py`
```python
# 단일 파일 업로드
uploaded_file = st.file_uploader("파일 선택")
```

#### 변경 필요
```python
# 데이터셋 + 라벨링 업로드
col1, col2 = st.columns(2)
with col1:
    dataset_file = st.file_uploader("데이터셋 파일 (JSON/CSV)")
with col2:
    labels_file = st.file_uploader("라벨링 파일 (JSON/CSV)", optional=True)
    
# Ground Truth 선택적 업로드
ground_truth_file = st.file_uploader("Ground Truth 파일 (선택사항)")

# 평가자 정보 입력 (일관성 측정용)
num_raters = st.number_input("평가자 수", min_value=1, max_value=10)
```

**변경 범위**:
- `app.py`: UI 구조 전면 수정 (약 200-300줄 변경)
- 결과 표시 로직 변경 (새로운 지표 표시)

---

### 5. **점수 계산 로직 변경** ⚠️ **중규모 변경**

#### 현재: `src/utils.py`
```python
def calc_total_score(result_dict: dict) -> float:
    # 단순 평균
    return sum(scores) / len(scores)
```

#### 변경 필요
```python
def calc_total_score_with_thresholds(result_dict: dict, thresholds: dict) -> dict:
    """임계값 기반 평가"""
    results = {}
    for metric_name, value in result_dict.items():
        threshold = thresholds.get(metric_name, {}).get("threshold", 0.0)
        status = "PASS ✅" if value >= threshold else "FAIL ❌"
        results[metric_name] = {
            "value": value,
            "threshold": threshold,
            "status": status
        }
    return results
```

**변경 범위**:
- `src/utils.py`: 점수 계산 로직 수정
- 임계값 설정 파일 추가 (`config/quality_thresholds.json`)

---

### 6. **보고서 생성 변경** ⚠️ **소규모 변경**

#### 현재: `src/utils.py`
```python
def generate_text_report_pdf(text_scores, total_score, grade):
    # 현재 지표만 표시
```

#### 변경 필요
```python
def generate_quality_report_pdf(quality_results, thresholds):
    # 모든 지표 + 임계값 + PASS/FAIL 상태 표시
    # mAP, IOU, F1, Kappa, ROUGE, BLEU, CER 등 모두 포함
```

**변경 범위**:
- `src/utils.py`: PDF 보고서 생성 함수 수정
- 새로운 지표 표시 로직 추가

---

## 📊 변경 범위 요약

| 모듈 | 변경 규모 | 변경 내용 | 예상 코드 변경량 |
|------|---------|---------|----------------|
| `app.py` | ⚠️ **대규모** | UI 전면 수정 (파일 업로드 → 데이터셋+라벨링 업로드) | ~300줄 |
| `src/text_quality.py` | ⚠️ **대규모** | 라벨링 기반 평가 로직 추가 | ~400줄 (새 함수) |
| `src/image_quality.py` | ⚠️ **대규모** | 라벨링 기반 평가 로직 추가 | ~300줄 (새 함수) |
| `src/dataset_analyzer.py` | ⚠️ **대규모** | 데이터셋 구조 처리 변경 | ~200줄 |
| `src/utils.py` | ⚠️ **중규모** | 점수 계산 및 보고서 생성 로직 수정 | ~150줄 |
| **새 모듈** | ⚠️ **신규** | `src/quality_evaluator.py` 생성 | ~500줄 |
| **새 모듈** | ⚠️ **신규** | `src/labeling_evaluator.py` 생성 | ~300줄 |
| **설정 파일** | ⚠️ **신규** | `config/quality_thresholds.json` 생성 | ~50줄 |

**총 예상 변경량**: 약 **2,200줄** (기존 코드 수정 + 신규 코드)

---

## 🎯 핵심 변경 사항

### 1. **입력 데이터 형식 변경**
- **현재**: 단일 파일 (텍스트/이미지)
- **변경 후**: 구조화된 데이터셋 (JSON/CSV) + 라벨링 정보

### 2. **평가 방식 변경**
- **현재**: 데이터 자체의 품질 (내재적 품질)
- **변경 후**: 라벨링 정확성, 모델 성능, 데이터 구조 품질

### 3. **필수 입력 정보 추가**
- 라벨링 정보 (필수)
- Ground Truth (선택적, 유효성 측정용)
- 평가자 정보 (일관성 측정용)
- 모델 예측 결과 (유효성 측정용)

### 4. **새로운 의존성 추가**
```python
# requirements.txt에 추가 필요
scikit-learn>=1.3.0  # Cohen's Kappa 계산
rouge-score>=0.1.2   # ROUGE 점수
nltk>=3.8            # BLEU 점수
jiwer>=3.0           # CER (Character Error Rate)
toxicity-detector    # 유해 표현 검출 (선택적)
```

---

## 💡 마이그레이션 전략

### 옵션 1: 완전 교체 (권장하지 않음)
- 기존 코드를 모두 새 기준표에 맞게 교체
- **단점**: 기존 기능 완전 손실, 개발 시간 많이 소요

### 옵션 2: 하이브리드 접근 (권장) ✅
- 기존 내재적 품질 측정 유지
- 새 라벨링 기반 평가를 **추가 모드**로 구현
- 사용자가 선택 가능:
  ```python
  evaluation_mode = st.radio(
      "평가 모드 선택",
      ["내재적 품질 측정", "라벨링 기반 평가"]
  )
  ```

### 옵션 3: 점진적 통합
- 1단계: 기존 기능 유지
- 2단계: 라벨링 기반 평가 모듈 추가 (별도 탭)
- 3단계: 두 모드를 통합 리포트로 생성

---

## ⚠️ 주의사항

1. **라벨링 데이터 필수**: 새 기준표는 라벨링 정보가 없으면 대부분의 지표를 계산할 수 없음
2. **Ground Truth 필요**: 유효성 측정을 위해서는 Ground Truth 또는 모델 예측 결과 필요
3. **평가자 정보 필요**: 일관성 측정을 위해서는 여러 평가자의 라벨링 정보 필요
4. **데이터 형식 표준화**: JSON/CSV 형식의 데이터셋 구조 정의 필요

---

## 📋 결론

**코드 변경 범위**: **대규모** (약 2,200줄)

**주요 변경 사항**:
1. 입력 데이터 구조 전면 변경 (단일 파일 → 구조화된 데이터셋)
2. 품질 지표 계산 로직 대부분 재작성
3. UI 전면 수정
4. 새로운 의존성 추가
5. 새로운 모듈 생성 (quality_evaluator, labeling_evaluator)

**권장 접근 방식**: **하이브리드 접근** ✅ **구현 완료**
- 기존 내재적 품질 측정 기능 유지 (탭 1, 2)
- 라벨링 기반 평가 기능 추가 (탭 3)
- 품질 지표 가이드 추가 (탭 4)
- 품질 지표 이름 통일 (형식 정확성, 다양성, 유효성)

---

**작성일**: 2024년  
**프로젝트**: AI 학습용 비정형데이터 품질진단 프로그램

