
# AI Unstructured Data Quality Diagnosis Program

This is a Streamlit-based web application that automatically calculates data quality metrics for AI training by uploading text and image data.

## Quick Start Guide

### Step 1: Fast Start (5 min)

1. **Read README.md**: Check project overview and key features.
2. **Execute Program**: Run the following commands in your terminal.
```bash
pip install -r requirements.txt
streamlit run app.py

```


3. **Basic Testing**: Click "Sample Text Test" in the sidebar.

### Step 2: Understanding Features (15 min)

1. **Single File Analysis**: Upload text/image -> Select type -> Start analysis.
2. **Batch Analysis**: Test with 10-20 samples from CIFAR-10 or Hugging Face.

## Quality Metrics

### Text Data

| Metric | Description | Methodology |
| --- | --- | --- |
| **Format Accuracy** | Typos and grammar error rate | Pattern-based error detection |
| **Diversity** | Inter-sentence similarity | Sentence Transformer Embedding |
| **Completeness** | Ratio of meaningful sentences | Minimum length threshold filtering |

### Image Data

| Metric | Description | Methodology |
| --- | --- | --- |
| **Resolution** | Meeting size requirements | Standard: 512x512 |
| **Validity** | Sharpness and noise levels | Laplacian Variance analysis |
| **Diversity** | Duplicate image ratio | ImageHash comparison |

## Project Structure

```text
unstructure/
├── app.py                   # Main Streamlit Application
├── requirements.txt         # Python Dependencies
├── src/                     # Core Analysis Modules
│   ├── text_quality.py      # Text Quality Algorithms
│   ├── image_quality.py     # Image Quality Algorithms
│   ├── dataset_analyzer.py  # Batch Processing Logic
│   └── ui/                  # UI Components (Tabs 1-4)
├── config/                  # Configuration Files
└── docs/                    # Detailed Documentation

```

## Team

* **Jang Yoon-jeong**: Project Management, Quality Metric Advancement, Report Extraction Logic.
* **Lee Seong-eun**: UI Implementation, External Dataset Integration, System Testing & Bug Fixes.

---

# AI 비정형 데이터 품질진단 프로그램

텍스트 및 이미지 데이터를 업로드하면 AI 학습용 데이터 품질지표를 자동 계산하는 Streamlit 기반 웹 앱입니다.

## 처음 사용자 가이드

### 1단계: 빠른 시작 (5분)

1. **README.md 읽기**: 프로젝트 개요와 주요 기능 확인
2. **프로그램 실행**: 터미널에서 아래 명령어를 실행합니다.
```bash
pip install -r requirements.txt
streamlit run app.py

```


3. **기본 기능 테스트**: 사이드바의 "샘플 텍스트 테스트" 클릭

### 2단계: 기능 이해 (15분)

1. **단일 파일 분석**: 텍스트/이미지 업로드 -> 타입 선택 -> 분석 시작
2. **데이터셋 배치 분석**: CIFAR-10 또는 Hugging Face 데이터셋으로 테스트

## 품질 지표 설명

### 텍스트 데이터

| 지표 | 설명 | 계산 방법 |
| --- | --- | --- |
| **형식 정확성** | 오탈자 및 맞춤법 오류 비율 | 패턴 기반 오류 검사 |
| **다양성** | 문장 간 유사도 분석 | Sentence Transformer 임베딩 |
| **완전성** | 의미 있는 문장의 비율 | 최소 길이 임계값 필터링 |

### 이미지 데이터

| 지표 | 설명 | 계산 방법 |
| --- | --- | --- |
| **해상도** | 이미지 크기 기준 충족 여부 | 기본 기준: 512x512 |
| **유효성** | 선명도 및 노이즈 수준 | Laplacian Variance 분석 |
| **다양성** | 중복 이미지 비율 | ImageHash 비교 |

## 프로젝트 구조

```text
unstructure/
├── app.py                   # Streamlit 메인 애플리케이션
├── requirements.txt         # Python 패키지 의존성 목록
├── src/                     # 핵심 분석 모듈
│   ├── text_quality.py      # 텍스트 품질 진단 알고리즘
│   ├── image_quality.py     # 이미지 품질 진단 알고리즘
│   ├── dataset_analyzer.py  # 배치 처리 로직
│   └── ui/                  # UI 컴포넌트 (탭 1-4)
├── config/                  # 설정 파일
└── docs/                    # 상세 문서

```

## 팀 구성

* **장윤정**: 프로젝트 총괄, 품질 진단 고도화 및 보고서 추출 로직 담당.
* **이성은**: UI 구현, 외부 데이터셋 통합, 시스템 테스트 및 버그 수정 담당.

