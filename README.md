# 🧠 AI 비정형 데이터 품질진단 프로그램

텍스트 및 이미지 데이터를 업로드하면 AI 학습용 데이터 품질지표를 자동 계산하는 Streamlit 기반 웹 앱입니다.

## 🎯 처음 사용자 가이드

이 프로그램을 처음 접하는 경우, 다음 순서로 진행하시면 됩니다:

### 1단계: 빠른 시작 (5분)
1. **README.md** (현재 파일) 읽기
   - 프로젝트 개요와 주요 기능 확인
   - 실행 방법 따라하기
   
2. **프로그램 실행**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
   
3. **기본 기능 테스트**
   - 사이드바 "샘플 텍스트 테스트" 버튼 클릭
   - 또는 간단한 `.txt` 파일 업로드 후 분석

### 2단계: 기능 이해 (10-15분)
1. **단일 파일 분석**
   - 텍스트/이미지 파일 업로드 → 타입 선택 → 분석 시작
   - 품질 지표와 점수 확인

2. **데이터셋 배치 분석**
   - CIFAR-10 또는 Hugging Face 데이터셋 선택
   - 샘플 개수 10-20개로 테스트
   - 배치 분석 결과 확인

### 3단계: 알고리즘 이해 (선택사항)
1. **[ALGORITHM_DESCRIPTION.md](ALGORITHM_DESCRIPTION.md)** 읽기
   - 품질 진단 알고리즘 상세 설명
   - 각 지표의 계산 방법 이해

2. **코드 확인** (원하는 경우)
   - `src/text_quality.py` - 텍스트 품질 진단 코드
   - `src/image_quality.py` - 이미지 품질 진단 코드
   - `app.py` - UI 및 전체 구조

### 4단계: 고급 기능 (필요시)
- **[HUGGINGFACE_DATASETS.md](HUGGINGFACE_DATASETS.md)** - Hugging Face 데이터셋 사용
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 전체 기능 상세 설명
- **[SSH_SERVER_GUIDE.md](SSH_SERVER_GUIDE.md)** - 서버에서 실행하기

---

## 📋 프로젝트 개요

본 프로그램은 AI 학습에 사용되는 비정형 데이터(텍스트, 이미지)의 품질을 자동으로 진단하고 점수화합니다.
10일 단기 프로젝트로 개발된 프로토타입 버전입니다.

### 주요 기능

- ✅ **단일 파일 분석**: 텍스트/이미지 파일 업로드 후 품질 진단
- ✅ **데이터셋 배치 분석**: CIFAR-10, Hugging Face 데이터셋 대량 분석
- ✅ **텍스트 품질 진단**: 정확성, 중복도, 완전성 분석
- ✅ **이미지 품질 진단**: 해상도, 선명도, 노이즈, 중복도 분석
- ✅ **Hugging Face 통합**: 데이터셋 검색 및 다운로드 (Streaming 지원)
- ✅ **자동 점수화**: 0-1 범위의 품질 점수 및 A-D 등급 산출
- ✅ **시각화**: 대시보드를 통한 직관적인 결과 확인

## 🚀 실행 방법

### 1. 환경 설정

```bash
# Python 3.11 이상 권장
python --version

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행

#### 로컬 실행
```bash
streamlit run app.py
```

브라우저에서 자동으로 열리며, `http://localhost:8502`에서 접속할 수 있습니다.

#### SSH 서버 실행
```bash
# 서버에서 실행 (headless 모드)
streamlit run app.py --server.headless true

# 로컬에서 SSH 포트 포워딩
ssh -L 8501:localhost:8501 사용자명@서버주소

# 브라우저에서 접속
http://localhost:8501
```

자세한 내용은 [SSH_SERVER_GUIDE.md](SSH_SERVER_GUIDE.md)를 참고하세요.

## 📊 품질 지표 설명

### 텍스트 데이터

| 지표 | 설명 | 계산 방법 |
|------|------|-----------|
| **정확성** | 오탈자 및 맞춤법 오류 비율 | 패턴 기반 오류 검사 |
| **중복도** | 문장 간 유사도 분석 | Sentence Transformer 임베딩 기반 |
| **완전성** | 의미 있는 문장의 비율 | 최소 길이 이상 문장 비율 |

### 이미지 데이터

| 지표 | 설명 | 계산 방법 |
|------|------|-----------|
| **해상도** | 이미지 크기 기준 충족 여부 | 최소 512x512 기준 |
| **선명도** | 이미지 선명함 정도 | Laplacian Variance |
| **노이즈** | 이미지 노이즈 수준 | Gaussian Blur 차이 분석 |
| **중복도** | 중복 이미지 비율 | ImageHash 기반 비교 |

### 품질 등급

| 등급 | 점수 범위 | 설명 |
|------|----------|------|
| **A** | 0.8 이상 | 우수한 품질 |
| **B** | 0.6 이상 | 양호한 품질 |
| **C** | 0.4 이상 | 보통 품질 |
| **D** | 0.4 미만 | 개선 필요 |

## 🛠️ 기술 스택

| 구분 | 기술 | 용도 |
|------|------|------|
| 분석 언어 | Python 3.11+ | 메인 분석 및 통합 |
| 웹 프레임워크 | **Streamlit** | 웹 대시보드 및 UI |
| 텍스트 진단 | `sentence-transformers` | 문장 유사도 분석 (중복도) |
| 이미지 진단 | `opencv-python`, `imagehash`, `pillow` | 해상도, 선명도, 노이즈, 중복 분석 |
| 데이터셋 로드 | `torchvision`, `datasets`, `huggingface_hub` | CIFAR-10, Hugging Face 데이터셋 |
| 딥러닝 | `torch`, `transformers` | 모델 로드 및 임베딩 |
| 수치 연산 | `numpy`, `scikit-learn` | 통계 계산 및 유틸리티 |

## 📁 프로젝트 구조

```
unstructure/
├── app.py                        # ⭐ 메인 앱 (949줄) - UI 및 전체 흐름
├── requirements.txt              # Python 패키지 의존성 목록
│
├── src/                          # 핵심 분석 모듈
│   ├── __init__.py
│   ├── text_quality.py          # ⭐ 텍스트 품질진단 알고리즘
│   ├── image_quality.py         # ⭐ 이미지 품질진단 알고리즘
│   ├── utils.py                 # 공통 함수 (점수 계산, 등급 산출)
│   ├── dataset_analyzer.py      # 데이터셋 로드 및 배치 분석 (613줄)
│   └── dataset_finder.py        # Hugging Face 데이터셋 검색 (141줄)
│
├── sample_data/                 # 샘플 테스트 데이터
│   └── sample_text.txt
│
├── data/                        # 다운로드된 데이터셋 저장소 (자동 생성)
│   └── cifar-10-batches-py/     # CIFAR-10 데이터셋
│
└── 문서/
    ├── README.md                # ⭐ 프로젝트 개요 및 시작 가이드 (현재 파일)
    ├── PROJECT_SUMMARY.md        # 전체 기능 상세 설명
    ├── ALGORITHM_DESCRIPTION.md  # 알고리즘 상세 설명
    ├── HUGGINGFACE_DATASETS.md   # Hugging Face 사용 가이드
    ├── SSH_SERVER_GUIDE.md      # SSH 서버 실행 가이드
    └── LOCAL_USE_ONLY.md        # 로컬 사용 가이드
```

**코드 이해 순서**:
1. `app.py` - 전체 구조와 UI 흐름 파악
2. `src/text_quality.py`, `src/image_quality.py` - 핵심 알고리즘 이해
3. `src/dataset_analyzer.py` - 데이터셋 처리 로직

## 🧪 사용 방법

### 단일 파일 분석

1. "단일 파일 분석" 탭 선택
2. 텍스트 파일 (`.txt`) 또는 이미지 파일 (`.jpg`, `.png` 등) 업로드
3. 파일 타입 선택 버튼 클릭 ("텍스트 파일로 분석" / "이미지 파일로 분석")
4. 분석 시작 버튼 클릭
5. 결과 확인 (품질 점수, 등급, 차트)

### 데이터셋 배치 분석

1. "데이터셋 배치 분석" 탭 선택
2. 데이터 타입 선택 (이미지 / 텍스트)
3. 데이터셋 소스 선택:
   - **미리 탑재된 샘플 데이터셋**: CIFAR-10, Hugging Face beans/food101/imdb 등
   - **Hugging Face에서 검색**: 검색어 입력 또는 인기 목록에서 선택
   - **커스텀 폴더**: 로컬 폴더 경로 입력
4. 다운로드 방식 선택:
   - 샘플 개수 지정 (10~500개)
   - 전체 데이터셋 퍼센티지 (1~100%)
   - 전체 다운로드
5. "데이터셋 분석 시작" 버튼 클릭
6. 배치 분석 결과 확인 (평균, 최소, 최대, 표준편차)

### 샘플 데이터 테스트

- 사이드바의 "샘플 텍스트 테스트" 버튼 사용
- 또는 `sample_data/` 폴더에 직접 파일을 업로드

## 📝 개발 일정

| 일자 | 주요 작업 | 담당 |
|------|----------|------|
| 11/1 ~ 11/2 | 과제 구조 설계 및 품질지표 정의 | 윤정 |
| 11/3 ~ 11/5 | 품질진단 알고리즘 구현 | 윤정 / 성은 |
| 11/6 ~ 11/8 | 웹 UI 구축 및 통합 테스트 | 성은 |
| 11/9 | 샘플 데이터 테스트 및 점수 검증 | 윤정 |
| 11/10 | 결과 리포트 및 발표자료 초안 작성 | 윤정 / 성은 |

## 📚 참고자료

- [한국지능정보사회진흥원(NIA), 「인공지능 학습용 데이터 품질관리 가이드라인」(2024)](https://www.nia.or.kr)
- [ISO/IEC 25012, "Data Quality Model"](https://www.iso.org)
- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Hugging Face Datasets 문서](https://huggingface.co/docs/datasets)
- [Sentence Transformers 문서](https://www.sbert.net)

## 👥 팀 구성

- **장윤정** – as is 프로젝트 총괄 / to be 품질 진단 고도화 및 보고서 추출 기능
- **이성은** – to be 시스템 구현 및 UI / 외부 데이터셋 삽입 및 테스트 버그 픽스

## 📚 추가 문서

프로젝트를 더 깊이 이해하고 싶다면 다음 문서들을 참고하세요:

| 문서 | 설명 | 언제 읽을까? |
|------|------|------------|
| **[ALGORITHM_DESCRIPTION.md](ALGORITHM_DESCRIPTION.md)** | 품질 진단 알고리즘 상세 설명 | 알고리즘 작동 원리를 이해하고 싶을 때 |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | 개발 완료 보고서 (모든 기능 상세) | 전체 기능을 한눈에 파악하고 싶을 때 |
| **[HUGGINGFACE_DATASETS.md](HUGGINGFACE_DATASETS.md)** | Hugging Face 데이터셋 사용 가이드 | 다양한 데이터셋을 사용하고 싶을 때 |
| **[LOCAL_USE_ONLY.md](LOCAL_USE_ONLY.md)** | 로컬 사용 가이드 | 로컬에서만 실행할 때 (간단 버전) |
| **[SSH_SERVER_GUIDE.md](SSH_SERVER_GUIDE.md)** | SSH 서버 실행 가이드 | 서버에서 실행할 때 |

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

## 🐛 문제 해결

### 모델 다운로드 오류
- 인터넷 연결을 확인하세요.
- `sentence-transformers`가 제대로 설치되었는지 확인하세요.

### 메모리 부족 오류
- 이미지 크기를 줄이거나 배치 크기를 조정하세요.
- GPU가 있다면 PyTorch GPU 버전을 사용하세요.

### 파일 업로드 오류
- 지원되는 파일 형식인지 확인하세요.
- 파일 크기가 너무 크지 않은지 확인하세요.

### 데이터셋 다운로드 오류
- Hugging Face 데이터셋 다운로드 시 인터넷 연결이 필요합니다.
- Streaming 모드를 사용하면 메모리를 절약할 수 있습니다 (퍼센티지 다운로드).

### SSH 서버 실행 시 포트 오류
- 포트 8501이 이미 사용 중일 수 있습니다.
- `streamlit run app.py --server.port 8502`로 다른 포트 사용 가능합니다.

## 🔮 향후 확장 방향

- ✅ AI 기반 품질예측 모델 (BERTScore, CLIPScore) 적용
- ✅ PDF 리포트 자동 생성 기능
- ✅ 멀티모달(텍스트+이미지) 품질 상관분석
- ✅ 대용량 데이터 배치 처리 기능
- ✅ 실시간 데이터 품질 모니터링

