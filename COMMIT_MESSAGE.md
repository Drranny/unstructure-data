# 커밋 메시지

## 제목
리팩토링: app.py 모듈화 및 품질 지표 개선

## 본문

### 주요 변경사항

#### 1. 코드 리팩토링
- **app.py 모듈화**: 2,476줄 → 40줄로 대폭 축소 (약 98% 감소)
- **src/ui/ 디렉토리 추가**: 탭별 모듈로 분리
  - `common.py`: 사이드바, CSS 스타일, 샘플 데이터 생성
  - `tab1_single.py`: 단일 파일 분석 탭 (약 400줄)
  - `tab2_batch.py`: 데이터셋 배치 분석 탭 (약 950줄)
  - `tab3_labeling.py`: 라벨링 기반 평가 탭 (약 420줄)
  - `tab4_guide.py`: 품질 지표 가이드 탭 (약 460줄)

#### 2. 기능 추가
- **라벨링 기반 품질 평가 모듈** (`src/quality_evaluator.py`)
  - 정확성, 일관성, 완전성, 유효성, 다양성, 안전성 평가
- **품질 지표 임계값 설정** (`config/quality_thresholds.json`)
- **품질 지표 가이드 탭** 추가 (각 분석 모드별 지표 설명)

#### 3. 품질 지표 이름 변경
- **텍스트**: 
  - `정확성(오탈자비율)` → `형식 정확성`
  - `중복도(유사도역비율)` → `다양성`
- **이미지**: 
  - `선명도`, `노이즈` → `유효성` (통합)
  - `중복도` → `다양성`
- 관련 파일 업데이트: `text_quality.py`, `image_quality.py`, `dataset_analyzer.py`, `utils.py`

#### 4. 문서 업데이트
- `README.md`: 프로젝트 구조 및 코드 이해 순서 업데이트
- `PROJECT_SUMMARY.md`: 리팩토링 내용 반영, 코드 통계 업데이트
- `REFACTORING_PLAN.md`: 리팩토링 완료 보고서 작성
- `IMPROVEMENTS_NEEDED.md`: 개선 사항 목록 추가
- `METRICS_MAPPING.md`: 품질 지표 매핑 가이드 추가
- `QUALITY_METRICS_COMPARISON.md`: 품질 지표 비교 문서 추가
- `TECHNOLOGY_STACK.md`: 기술 스택 정리 문서 추가

#### 5. 의존성 업데이트
- `requirements.txt`: 라벨링 기반 평가용 패키지 추가
  - `rouge-score`: ROUGE 점수 계산
  - `nltk`: BLEU 점수 계산
  - `jiwer`: CER 계산
  - `pandas`: 데이터프레임 처리

#### 6. 파일 정리
- `MINIO_SETUP.md` 삭제 (불필요)
- `TEXT_QUALITY_TODO.md` 삭제 (불필요)

### 개선 효과
- ✅ 가독성 향상: 각 탭이 독립 파일로 관리
- ✅ 유지보수 용이: 특정 탭만 수정 가능
- ✅ 협업 효율: 파일 충돌 가능성 감소
- ✅ 확장성: 새 탭 추가 용이
- ✅ 테스트 용이: 각 모듈 독립 테스트 가능

### 변경된 파일
- 수정: `app.py`, `requirements.txt`, `src/dataset_analyzer.py`, `src/image_quality.py`, `src/text_quality.py`, `src/utils.py`, `README.md`, `PROJECT_SUMMARY.md`
- 추가: `src/ui/` (5개 모듈), `src/quality_evaluator.py`, `config/quality_thresholds.json`, 문서 5개
- 삭제: `MINIO_SETUP.md`, `TEXT_QUALITY_TODO.md`

