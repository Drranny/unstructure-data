# 🧠 AI 비정형 데이터 품질진단 프로그램 - 개발 완료 보고서

## 📋 프로젝트 개요

**프로젝트명**: AI 학습용 비정형 데이터 품질진단 프로그램  
**개발 목적**: 텍스트 및 이미지 데이터의 품질을 자동으로 진단하고 점수화  
**프레임워크**: Streamlit 웹 애플리케이션  
**배포 환경**: 로컬 실행 (SSH 서버 연결 지원)

---

## ✅ 주요 기능

### 1. **단일 파일 분석 (탭 1)**
- 샘플 데이터 테스트 기능 추가 (사이드바)

#### 파일 업로드 및 분석
- **Step 1**: 파일 업로드
  - 지원 형식: `.txt` (텍스트), `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp` (이미지)
  - 드래그 앤 드롭 또는 파일 선택 방식

- **Step 2**: 파일 타입 선택
  - 명시적 버튼 클릭 방식 ("텍스트 파일로 분석" / "이미지 파일로 분석")
  - 파일 확장자 기반 자동 추정 및 안내

- **Step 3**: 분석 실행
  - 전용 분석 버튼 클릭 ("텍스트 품질 분석 시작" / "이미지 품질 분석 시작")
  - 실시간 분석 진행 상태 표시 (Spinner)

#### 분석 결과 표시
- **품질 지표 표**: 각 지표별 점수 (0-1 범위)
- **종합 품질 점수**: 전체 지표의 평균 점수
- **품질 등급**: A (0.8+), B (0.6+), C (0.4+), D (0.4 미만)
- **등급별 피드백**: 우수/양호/개선 필요/시급 메시지
- **상세 지표 차트**: Bar chart로 시각화
- **원본 데이터 미리보기**: 분석된 텍스트/이미지 표시
- **PDF 보고서 다운로드**: 분석 결과를 PDF 형식으로 다운로드 가능
  - 데이터셋/파일명 정보 포함
  - 분석 일시, 품질 점수, 등급, 상세 지표 포함

### 3. **라벨링 기반 평가 (탭 3)**
- CSV/JSON 파일 업로드 (예측 라벨 + 실제 라벨)
- 작업 타입 선택 (classification, detection, generation, qa)
- 품질 지표 평가:
  - 정확성 (semantic_accuracy): F1-Score, IOU, mAP
  - 일관성 (consistency): Cohen's Kappa, IRR
  - 완전성 (completeness): MissingRate, NullRate
  - 유효성 (validity): ROUGE, BLEU, CER
  - 다양성 (diversity): CategoryVariance, Entropy
  - 안전성 (safety): ToxicityRate
- 임계값 기반 PASS/FAIL 판정
- 샘플 데이터 생성 및 테스트 기능 (사이드바)

### 4. **품질 지표 가이드 (탭 4)**
- 각 분석 모드별 품질 지표 설명
- 기준 점수 및 등급 기준 안내
- 임계값 설정 파일 위치 안내

---

### 2. **데이터셋 배치 분석 (탭 2)**
- 전체 통계 표에서 긴 리스트 제외 (개별 점수, 해상도 목록)
- 해상도 분포 요약 정보만 표시

#### 데이터 타입 선택
- 이미지 / 텍스트 라디오 버튼 선택

#### 데이터셋 소스 선택
- **미리 탑재된 샘플 데이터셋**
  - 이미지: CIFAR-10, Hugging Face beans, food101, cifar10, 커스텀 폴더
  - 텍스트: Hugging Face imdb, yelp_review_full, ag_news (3개)

- **Hugging Face에서 검색**
  - 인기 데이터셋 목록 자동 표시 (좌측 열)
  - 검색어 입력 및 검색 기능 (우측 열)
  - 검색 결과에서 데이터셋 ID 선택
  - 이미지/텍스트 각각의 데이터셋 목록 제공

#### 다운로드 옵션
- **샘플 개수 지정**: 10~500개 슬라이더로 선택
- **전체 데이터셋 퍼센티지**: 1~100% 슬라이더로 선택
- **전체 다운로드**: 전체 데이터셋 다운로드 옵션

#### 배치 분석 결과
- **전체 통계**: 각 품질 지표별 평균, 최소, 최대, 표준편차
- **평균 품질 점수 및 등급**
- **품질 지표 상세 차트**
- **샘플 데이터 미리보기**: 이미지 5개 / 텍스트 3개
- **PDF 보고서 다운로드**: 데이터셋 배치 분석 결과를 PDF로 다운로드
  - 데이터셋 이름 정보 포함
  - 전체 통계 및 평균 지표 포함

---

## 🔬 품질 진단 알고리즘

### 텍스트 품질 진단 (`src/text_quality.py`)

#### 1. 형식 정확성 (Format Accuracy)
- **방법**: 패턴 기반 오류 검사
- **검사 항목**:
  - 연속된 공백 (double space)
  - 한글/영문 혼용 패턴
  - 특수문자 비율
  - 한글 문자 비율 검증

#### 2. 다양성 (Diversity)
- **방법**: Sentence Transformer 기반 문장 유사도 분석
- **모델**: `paraphrase-multilingual-MiniLM-L12-v2` (또는 `paraphrase-MiniLM-L6-v2`)
- **알고리즘**:
  - 각 문장을 임베딩 벡터로 변환
  - 문장 간 코사인 유사도 계산
  - 평균 유사도를 역비율로 변환 (중복이 적을수록 높은 점수)

#### 3. 완전성 (Completeness)
- **방법**: 의미 있는 문장 비율 계산
- **기준**: 최소 길이 이상의 문장 비율
- **계산**: `의미있는 문장 수 / 전체 문장 수`

---

### 이미지 품질 진단 (`src/image_quality.py`)

#### 1. 해상도 (Resolution)
- **기준**: 최소 512x512 픽셀
- **계산 방식**:
  - 512x512 이상: 기본 점수 1.0
  - 종횡비 4:1 초과 시 패널티 (-10%)
  - 최소 차원 기준 점수 계산
  - 2048픽셀 이상 시 보너스 (+10%)

#### 2. 유효성 (Validity)
- **구성**: 선명도와 노이즈를 통합한 지표
- **선명도 (Sharpness)**:
  - **방법**: Laplacian Variance 알고리즘
  - **절차**:
    1. 이미지를 Grayscale로 변환
    2. Laplacian 필터 적용 (엣지 감지)
    3. 분산(Variance) 계산
    4. 분산값을 0-1 점수로 정규화
- **노이즈 (Noise)**:
  - **방법**: Gaussian Blur 차이 분석
  - **절차**:
    1. 원본 이미지에 Gaussian Blur (5x5 커널) 적용
    2. 원본과 블러 이미지의 절대 차이 계산
    3. 차이의 평균값으로 노이즈 수준 측정
    4. 노이즈 수준을 점수로 변환 (노이즈 많을수록 낮은 점수)
- **통합**: 선명도와 노이즈 점수의 평균으로 유효성 점수 계산

#### 3. 다양성 (Diversity)
- **방법**: ImageHash 기반 비교
- **알고리즘**: `imagehash.average_hash` 사용
- **배치 분석 시**: 해시값 비교를 통한 중복 이미지 감지
- **주의**: 단일 이미지 분석 시에는 제외 (N/A)

---

## 📁 프로젝트 구조

```
unstructure/
├── app.py                          # Streamlit 메인 애플리케이션
├── requirements.txt                # Python 패키지 의존성 목록
├── README.md                       # 프로젝트 설명서
│
├── src/                            # 핵심 분석 모듈
│   ├── __init__.py
│   ├── text_quality.py            # 텍스트 품질 진단 알고리즘
│   ├── image_quality.py           # 이미지 품질 진단 알고리즘
│   ├── utils.py                   # 공통 함수 (점수 계산, 등급 산출, PDF 보고서 생성)
│   ├── dataset_analyzer.py        # 데이터셋 로드 및 배치 분석
│   ├── dataset_finder.py          # Hugging Face 데이터셋 검색
│   ├── quality_evaluator.py       # 라벨링 기반 품질 평가 모듈
│   │
│   └── ui/                        # UI 모듈 
│       ├── __init__.py
│       ├── common.py              # 사이드바, CSS 스타일 (약 150줄)
│       ├── tab1_single.py         # 단일 파일 분석 탭 (약 400줄)
│       ├── tab2_batch.py          # 데이터셋 배치 분석 탭 (약 950줄)
│       ├── tab3_labeling.py      # 라벨링 기반 평가 탭 (약 420줄)
│       └── tab4_guide.py          # 품질 지표 가이드 탭 (약 460줄)
│
├── config/                        # 설정 파일
│   └── quality_thresholds.json   # 품질 지표 임계값 설정
│
├── sample_data/                   # 샘플 테스트 데이터
│   └── sample_text.txt
│
├── data/                          # 다운로드된 데이터셋 저장소
│   └── cifar-10-batches-py/      # CIFAR-10 데이터셋 (자동 다운로드)
│
└── docs/
    ├── PROJECT_SUMMARY.md        # 전체 기능 상세 설명 (현재 파일)
    ├── ALGORITHM_DESCRIPTION.md  # 알고리즘 상세 설명
    ├── HUGGINGFACE_DATASETS.md   # Hugging Face 사용 가이드
    ├── SSH_SERVER_GUIDE.md       # SSH 서버 실행 가이드
    ├── TECHNOLOGY_STACK.md       # 기술 스택택 설명
    ├── METRICS_MAPPING.md        # 품질 지표 설명
    └── LOCAL_USE_ONLY.md         # 로컬 사용 가이드
```

---

## 🎨 사용자 인터페이스

### 디자인 테마
- **색상**: 화이트 & 블루 계열
- **주요 색상**:
  - 기본 블루: `#4472c4`
  - 진한 블루: `#2e75b6`
  - 다크 블루: `#1f4e79`
  - 배경: `#FFFFFF` (화이트)
  - 강조 색상: `#d9e2f3`, `#e8f0f8`

### UI 구성 요소
- **탭 구조**: 단일 파일 분석 / 데이터셋 배치 분석 / 라벨링 기반 평가 / 품질 지표 가이드
- **사이드바**: 샘플 데이터 테스트 버튼 (텍스트, 이미지, 라벨링 데이터)
- **명시적 버튼**: 파일 타입 선택 및 분석 시작
- **인터랙티브 위젯**: 슬라이더, 라디오 버튼, 검색 입력

---

## 📦 주요 패키지 및 의존성 참고자료

**[TECHNOLOGY_STACK.md](TECHNOLOGY_STACK.md)**

---

## 🚀 핵심 기능 상세

### 데이터셋 로드 기능 (`src/dataset_analyzer.py`)

#### 이미지 데이터셋
1. **CIFAR-10** (`load_cifar10`)
   - `torchvision.datasets` 사용
   - 자동 다운로드 지원
   - 샘플 개수 지정 가능

2. **Hugging Face 이미지** (`load_huggingface_dataset`)
   - Streaming 모드 지원 (부분 다운로드)
   - 퍼센티지 기반 다운로드
   - 전체 다운로드 옵션
   - 이미지 컬럼 자동 감지

3. **커스텀 폴더** (`load_custom_dataset`)
   - 로컬 폴더에서 이미지 파일 로드
   - 지원 형식: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`

#### 텍스트 데이터셋
1. **Hugging Face 텍스트** (`load_huggingface_text_dataset`)
   - Streaming 모드 지원
   - 퍼센티지 기반 다운로드
   - 전체 다운로드 옵션
   - 텍스트 컬럼 자동 감지

### 데이터셋 검색 기능 (`src/dataset_finder.py`)

1. **검색 기능** (`search_huggingface_datasets`)
   - Hugging Face Hub API 사용
   - 검색어, 작업 타입, 결과 개수 필터링
   - **정확한 데이터셋 ID 직접 조회**: `사용자명/데이터셋명` 형식으로 바로 검색 가능
   - **task 필터 완화**: 모든 텍스트/이미지 데이터셋 검색 가능 (필터 없이 먼저 시도)
   - **자동 재시도**: API 실패 시 최대 3회 재시도 (지수 백오프)
   - **폴백 처리**: API 실패 시 미리 정의된 목록에서 검색어 매칭

2. **인기 데이터셋** (`get_popular_datasets`)
   - 인기 데이터셋 목록 조회
   - 작업 타입별 필터링
   - **재시도 로직**: 최대 2회 재시도
   - **폴백 처리**: 실패 시 미리 정의된 목록 반환

3. **미리 정의된 목록** (`get_predefined_datasets`)
   - 폴백용 하드코딩된 인기 데이터셋 목록
   - 이미지 데이터셋 10개, 텍스트 데이터셋 10개

---

## 📊 분석 결과 형식

### 단일 파일 분석 결과
```python
# 텍스트
{
    "형식 정확성": 0.85,
    "다양성": 0.73,
    "완전성": 0.92
}
# 이미지
{
    "해상도": 0.95,
    "유효성": 0.85,  # 선명도와 노이즈 통합
    "다양성": None  # 단일 이미지 분석 시 제외
}
```

### 배치 분석 결과 (데이터셋)
```python
# 텍스트
{
    "평균 형식 정확성": 0.83,
    "최소 형식 정확성": 0.65,
    "최대 형식 정확성": 0.95,
    "표준편차 형식 정확성": 0.12,
    "평균 다양성": 0.71,
    ...
    "평균 종합 점수": 0.79
}
# 이미지
{
    "평균 해상도": 0.90,
    "평균 유효성": 0.82,
    "평균 다양성": 0.75,  # 전체 데이터셋 통계
    ...
    "평균 종합 점수": 0.82
}
```

---

## 🎯 사용 시나리오

### 시나리오 1: 단일 텍스트 파일 분석
1. "단일 파일 분석" 탭 선택
2. `.txt` 파일 업로드
3. "텍스트 파일로 분석" 버튼 클릭
4. "텍스트 품질 분석 시작" 버튼 클릭
5. 결과 확인 (점수, 등급, 차트)

### 시나리오 2: 이미지 데이터셋 배치 분석 (미리 탑재)
1. "데이터셋 배치 분석" 탭 선택
2. 데이터 타입: "이미지" 선택
3. 데이터셋 소스: "미리 탑재된 샘플 데이터셋" 선택
4. 데이터셋: "Hugging Face: beans" 선택
5. 다운로드 방식: "샘플 개수 지정" → 100개 선택
6. "데이터셋 분석 시작" 버튼 클릭
7. 배치 분석 결과 확인

### 시나리오 3: Hugging Face 검색 후 분석
1. "데이터셋 배치 분석" 탭 선택
2. 데이터 타입: "텍스트" 선택
3. 데이터셋 소스: "Hugging Face에서 검색" 선택
4. 인기 목록 확인 (좌측) 또는 검색어 입력 (우측)
5. 검색 결과에서 데이터셋 ID 확인
6. "분석할 데이터셋 ID 입력" 필드에 ID 입력
7. 다운로드 방식 선택 및 분석 시작

---

## 🔧 기술적 특징

### 메모리 효율성
- **Streaming 모드**: Hugging Face 데이터셋을 전체 다운로드하지 않고 필요 시 로드
- **부분 다운로드**: 퍼센티지 기반 다운로드로 메모리 사용 최소화
- **배치 처리**: 데이터셋 분석 시 샘플 개수 제한 가능

### 사용자 경험
- **명시적 UI**: 파일 타입을 버튼으로 명확히 선택
- **3단계 프로세스**: 업로드 → 타입 선택 → 분석 시작
- **실시간 피드백**: 진행 상태, 에러 메시지, 성공 알림
- **시각화**: 차트 및 테이블로 결과 직관적 표시

### 확장성
- **모듈화된 구조**: 각 기능별 독립 모듈
- **Hugging Face 통합**: 다양한 데이터셋 확장 가능
- **커스텀 데이터셋**: 로컬 폴더 및 파일 지원

---

## 📝 파일별 역할

### `app.py` 
- Streamlit 웹 애플리케이션 메인 파일
- 탭 생성 및 각 탭 모듈 호출만 담당
- 2,476줄 → 40줄로 대폭 축소 (2024년 12월 리팩토링)
- 각 탭 로직은 `src/ui/` 모듈로 분리

### `src/text_quality.py`
- 텍스트 품질 진단 알고리즘 구현
- `analyze_text_quality(text: str)` 함수
- Sentence Transformer 모델 로드 및 관리

### `src/image_quality.py`
- 이미지 품질 진단 알고리즘 구현
- `analyze_image_quality(img: Image.Image)` 함수
- OpenCV 기반 이미지 처리

### `src/utils.py` 
- 공통 유틸리티 함수
- `calc_total_score()`: 종합 점수 계산
- `get_grade()`: 점수 → 등급 변환
- **PDF 보고서 생성**: `generate_text_report_pdf()`, `generate_image_report_pdf()`, `generate_dataset_report_pdf()`
  - 한글 폰트 지원 (NotoSansKR)
  - 데이터셋/파일명 정보 포함

### `src/dataset_analyzer.py` 
- 데이터셋 로드 및 배치 분석
- CIFAR-10, Hugging Face, 커스텀 폴더 지원
- 텍스트/이미지 데이터셋 배치 분석 함수
- Streaming 및 퍼센티지 다운로드 지원
- 개별 점수 계산 시 다양성 제외 처리 (이미지)

### `src/dataset_finder.py`
- Hugging Face 데이터셋 검색 기능
- 인기 데이터셋 목록 조회
- 검색 결과 필터링 및 정렬
- 정확한 데이터셋 ID 직접 조회
- 자동 재시도 및 폴백 처리

### `src/quality_evaluator.py`
- 라벨링 기반 품질 평가 모듈
- `evaluate_semantic_accuracy()`: 정확성 평가 (F1, IOU, mAP)
- `evaluate_consistency()`: 일관성 평가 (Cohen's Kappa, IRR)
- `evaluate_completeness()`: 완전성 평가 (MissingRate, NullRate)
- `evaluate_validity()`: 유효성 평가 (ROUGE, BLEU, CER)
- `evaluate_diversity()`: 다양성 평가 (CategoryVariance, Entropy)
- `evaluate_safety()`: 안전성 평가 (ToxicityRate)
- `evaluate_quality_with_thresholds()`: 임계값 기반 종합 평가

### `src/ui/` 
- **`common.py`**: 사이드바, CSS 스타일, 샘플 데이터 생성 함수
- **`tab1_single.py`**: 단일 파일 분석 탭 UI 로직
- **`tab2_batch.py`**: 데이터셋 배치 분석 탭 UI 로직
- **`tab3_labeling.py`**: 라벨링 기반 평가 탭 UI 로직
- **`tab4_guide.py`**: 품질 지표 가이드 탭 UI 로직

### `config/quality_thresholds.json` 
- 품질 지표 임계값 설정 파일
- 각 지표별 임계값 및 설명 포함

---

## 🌟 주요 성과

### 구현 완료 사항
단일 파일 분석 기능 (텍스트/이미지)  
데이터셋 배치 분석 기능  
Hugging Face 데이터셋 통합 (검색 + 다운로드)  
3가지 다운로드 방식 (샘플 개수/퍼센티지/전체)  
명시적 UI 플로우 (3단계 프로세스)  
인기 데이터셋 목록 표시  
화이트 & 블루 테마 적용  
샘플 데이터 테스트 기능  
PDF 보고서 다운로드 기능 (데이터셋/파일명 정보 포함)
개선된 데이터셋 검색 기능 (정확한 ID 검색, 자동 재시도, 넓은 검색 범위)  

### 기술적 성과
메모리 효율적인 Streaming 다운로드  
퍼센티지 기반 부분 다운로드  
다양한 데이터셋 소스 통합  
모듈화된 코드 구조  

---

## 🚦 실행 방법

### 로컬 실행
```bash
cd /home/yjjang/unstructure
pip install -r requirements.txt
streamlit run app.py
```

### SSH 서버 실행
```bash
# 서버에서 실행
cd /home/yjjang/unstructure
streamlit run app.py --server.headless true

# 로컬에서 포트 포워딩
ssh -L 8501:localhost:8501 사용자명@서버주소

# 브라우저에서 접속
http://localhost:8501
```


---

## 🎓 프로젝트 활용 방법

### 학습 목적
- 데이터 품질 진단 개념 학습
- Streamlit 웹 앱 개발 학습
- Hugging Face 데이터셋 활용 학습

### 실무 활용
- AI 학습 데이터 품질 검증
- 데이터셋 전처리 전 품질 확인
- 품질 기준 설정 및 평가

---

**최종 업데이트**: 2025년 11월  
**개발 상태**: ✅ 완료 (프로토타입 버전)

