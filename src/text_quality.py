"""
텍스트 데이터 품질진단 모듈
정확성, 중복도, 완전성 지표를 계산합니다.
"""
from sentence_transformers import SentenceTransformer, util
import numpy as np
import re
import torch

# 모델은 처음 로드 시에만 초기화
_model = None

def get_model():
    """SentenceTransformer 모델을 싱글톤으로 로드"""
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        except Exception as e:
            # 영어 모델로 fallback
            try:
                _model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
            except Exception:
                raise Exception(f"모델 로드 실패: {e}")
    return _model

def analyze_text_quality(text: str):
    """
    텍스트 품질을 분석하여 지표를 반환합니다.
    
    Args:
        text: 분석할 텍스트 문자열
        
    Returns:
        dict: 품질 지표 딕셔너리
    """
    if not text or len(text.strip()) == 0:
        return {
            "정확성(오탈자비율)": 0.0,
            "중복도(유사도역비율)": 0.0,
            "완전성(문장충실도)": 0.0,
        }
    
    # 문장 단위로 분리
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    sentences = []
    for line in lines:
        # 문장 단위로 추가 분리 (., !, ? 기준)
        parts = re.split(r'[.!?]+\s+', line)
        sentences.extend([s.strip() for s in parts if len(s.strip()) > 0])
    
    if len(sentences) == 0:
        return {
            "정확성(오탈자비율)": 0.0,
            "중복도(유사도역비율)": 0.0,
            "완전성(문장충실도)": 0.0,
        }
    
    # 1. 정확성: 간단한 오탈자 패턴 검사 (한글/영문 혼용, 공백 오류 등)
    # 실제 hanspell은 API 호출이 필요하므로, 기본 패턴 체크로 대체
    # 한글 문장 구조, 영문 오탈자 패턴 등을 확인
    accuracy_score = check_text_accuracy(text)
    
    # 2. 중복도: 문장 임베딩 유사도 분석
    duplication_score = check_text_duplication(sentences)
    
    # 3. 완전성: 의미 있는 문장의 비율 (최소 길이 이상인 문장)
    min_length = 10  # 최소 문장 길이
    meaningful_sentences = [s for s in sentences if len(s) >= min_length]
    completeness_score = len(meaningful_sentences) / max(len(sentences), 1)
    completeness_score = min(completeness_score, 1.0)
    
    return {
        "정확성(오탈자비율)": round(accuracy_score, 3),
        "중복도(유사도역비율)": round(duplication_score, 3),
        "완전성(문장충실도)": round(completeness_score, 3),
    }

def check_text_accuracy(text: str) -> float:
    """
    텍스트 정확성을 체크합니다.
    실제 hanspell API는 외부 의존성이므로, 기본 패턴 기반 검사를 수행합니다.
    """
    if len(text) == 0:
        return 0.0
    
    # 기본적인 오류 패턴 체크
    error_patterns = [
        r'\s{2,}',  # 연속된 공백
        r'[가-힣]+[a-zA-Z]+[가-힣]+',  # 한글-영문 혼용 (의도된 경우 제외)
    ]
    
    error_count = 0
    for pattern in error_patterns:
        matches = re.findall(pattern, text)
        error_count += len(matches)
    
    # 한글 비율 체크 (한글이 너무 적으면 문제일 수 있음)
    korean_chars = len(re.findall(r'[가-힣]', text))
    total_chars = len(text.replace(' ', ''))
    korean_ratio = korean_chars / max(total_chars, 1)
    
    # 오류 점수 계산 (오류가 적을수록 높은 점수)
    error_ratio = min(error_count / max(len(text.split()), 1), 1.0)
    accuracy = 1.0 - error_ratio
    
    # 한글이 너무 적으면 패널티 (한국어 텍스트 가정)
    if korean_ratio < 0.3 and total_chars > 50:
        accuracy *= 0.9
    
    return max(accuracy, 0.0)

def check_text_duplication(sentences: list) -> float:
    """
    문장 간 중복도를 체크합니다.
    SentenceTransformer를 사용하여 문장 유사도를 계산합니다.
    """
    if len(sentences) < 2:
        return 1.0  # 문장이 하나면 중복 없음
    
    try:
        model = get_model()
        
        # 문장이 너무 많으면 샘플링 (성능 최적화)
        max_sentences = 50
        if len(sentences) > max_sentences:
            import random
            sentences = random.sample(sentences, max_sentences)
        
        # 문장 임베딩 생성
        embeddings = model.encode(sentences, convert_to_tensor=True, show_progress_bar=False)
        
        # 코사인 유사도 계산
        cosine_sim = util.pytorch_cos_sim(embeddings, embeddings)
        
        # 자기 자신과의 유사도(1.0) 제외한 평균 유사도 계산
        mask = torch.eye(len(sentences), dtype=torch.bool)
        cosine_sim_masked = cosine_sim.masked_fill(mask, 0)
        
        # 상삼각 행렬만 사용하여 중복 계산 방지
        triu_indices = torch.triu_indices(len(sentences), len(sentences), offset=1)
        similarities = cosine_sim_masked[triu_indices[0], triu_indices[1]]
        
        if len(similarities) > 0:
            avg_similarity = similarities.mean().item()
            # 유사도가 높을수록 중복도가 높으므로 역수로 변환
            duplication_score = 1.0 - avg_similarity
        else:
            duplication_score = 1.0
        
        return max(duplication_score, 0.0)
    
    except Exception as e:
        # 모델 로드 실패 시 기본값 반환
        print(f"중복도 계산 실패: {e}")
        # 간단한 문자열 유사도로 대체
        if len(sentences) >= 2:
            # 첫 문장과 나머지 문장들의 간단한 유사도
            first = sentences[0]
            similarities = []
            for s in sentences[1:]:
                # 간단한 Jaccard 유사도
                set1 = set(first)
                set2 = set(s)
                if len(set1 | set2) > 0:
                    jaccard = len(set1 & set2) / len(set1 | set2)
                    similarities.append(jaccard)
            
            if similarities:
                avg_sim = sum(similarities) / len(similarities)
                return max(1.0 - avg_sim, 0.0)
        
        return 0.5  # 기본값

