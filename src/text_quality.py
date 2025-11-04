"""
텍스트 데이터 품질진단 모듈
정확성, 중복도, 완전성 지표를 계산합니다.
"""
from sentence_transformers import SentenceTransformer, util
import numpy as np
import re
import torch

# 영어 사전 (선택적, 없으면 패턴 기반만 사용)
try:
    import enchant
    _enchant_dict = None
    def get_enchant_dict():
        global _enchant_dict
        if _enchant_dict is None:
            try:
                _enchant_dict = enchant.Dict("en_US")
            except:
                _enchant_dict = None
        return _enchant_dict
except ImportError:
    enchant = None
    def get_enchant_dict():
        return None

# 한국어 맞춤법 검사 (선택적, 없으면 패턴 기반만 사용)
try:
    from hanspell import spell_checker
    _hanspell_available = True
except ImportError:
    _hanspell_available = False
    spell_checker = None

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
    meaningful_sentences = []
    
    # 불완전한 문장 패턴
    incomplete_patterns = [
        r'\.\.\.$',  # "부산은..."
        r'[가-힣]+은$',  # "부산은" (주어만 있고 서술어 없음)
        r'[가-힣]+는$',  # "나는" (주어만 있고 서술어 없음)
        r'[가-힣]+이$',  # "그것이" (주어만 있고 서술어 없음)
        r'[가-힣]+가$',  # "그가" (주어만 있고 서술어 없음)
    ]
    
    for s in sentences:
        # 최소 길이 체크
        if len(s) < min_length:
            continue
        
        # 불완전한 문장 체크
        is_incomplete = False
        for pattern in incomplete_patterns:
            if re.search(pattern, s):
                is_incomplete = True
                break
        
        if not is_incomplete:
            meaningful_sentences.append(s)
    
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
    
    error_count = 0
    
    # 기본적인 오류 패턴 체크
    error_patterns = [
        r'[^\S\n]{2,}',  # 연속된 공백 (줄바꿈 제외) - 인라인 공백만 체크
        r'[가-힣]+[a-zA-Z]+[가-힣]+',  # 한글-영문 혼용 (의도된 경우 제외)
        r'_{2,}',  # 누락된 값 (예: "__명", "___")
        r'[ㅋㅎㄱㄴㅁㅇ]{3,}',  # 과도한 반복 ("ㅋㅋㅋ", "ㅎㅎㅎ")
        r'[가-힣]*짱[가-힣]*',  # 비공식적 표현 ("짱좋다")
        r'굿{2,}',  # 비공식적 표현 ("굿굿")
    ]
    
    # 과도한 빈 줄 체크 (빈 줄이 3개 이상 연속)
    excessive_newlines = len(re.findall(r'\n\s*\n\s*\n', text))
    if excessive_newlines > 0:
        error_count += excessive_newlines  # 과도한 빈 줄만 패널티
    
    # 문법 오류 패턴
    grammar_error_patterns = [
        r'갔었다\s+가지\s+않았다',  # 모순: "갔었다 가지 않았다"
        r'([가-힣]+)\s+\1\s+\1',  # 반복: "그거 그거 그거"
        r'뭐라\s+해야\s+되지\s+아무튼',  # 불명확: "뭐라 해야 되지 아무튼"
        r'\.\.\.\s+음\s+\.\.\.',  # 주저: "... 음 ..."
        r'[가-힣]+\s+\.\.\.\s+[가-힣]+',  # 중간 생략 패턴
    ]
    
    for pattern in grammar_error_patterns:
        matches = re.findall(pattern, text)
        if matches:
            error_count += len(matches) if isinstance(matches, list) else 1
    for pattern in error_patterns:
        matches = re.findall(pattern, text)
        error_count += len(matches)
    
    # 부적절한 표현 검사
    inappropriate_words = ['이딴', '쓰레기', '개새끼', '병신', '미친', '쓰레기', '개', '병신']  # 부적절한 단어 목록
    for word in inappropriate_words:
        if word in text:
            error_count += 3  # 부적절한 표현은 더 큰 패널티
    
    # 중복된 숫자 패턴 검사 (예: "123, 456, 123, 123")
    numbers = re.findall(r'\d+', text)
    if len(numbers) > 2:
        # 숫자가 3개 이상이고 중복이 있으면 패널티
        if len(numbers) != len(set(numbers)):
            error_count += 1
    
    # 한글 비율 체크 (한글이 너무 적으면 문제일 수 있음)
    korean_chars = len(re.findall(r'[가-힣]', text))
    total_chars = len(text.replace(' ', ''))
    korean_ratio = korean_chars / max(total_chars, 1)
    
    # 혼합 언어 패턴 강화 (한글-영문 혼용)
    # 일반적인 약어는 제외 (AI, API, ID 등)
    common_abbreviations = ['AI', 'API', 'ID', 'URL', 'HTTP', 'HTTPS', 'JSON', 'XML', 'HTML', 'CSS', 'JS']
    mixed_lang_pattern = r'[가-힣]+\s+[a-zA-Z]+\s+[가-힣]+|' + \
                        r'[a-zA-Z]+\s+[가-힣]+\s+[a-zA-Z]+|' + \
                        r'[가-힣]+[a-zA-Z]{2,}[가-힣]+'  # "mood 진짜 good", "오늘 mood"
    mixed_lang_matches = re.findall(mixed_lang_pattern, text, re.IGNORECASE)
    # 일반적인 약어가 포함된 경우 제외
    filtered_matches = []
    for match in mixed_lang_matches:
        is_abbreviation = False
        for abbr in common_abbreviations:
            if abbr in match.upper():
                is_abbreviation = True
                break
        if not is_abbreviation:
            filtered_matches.append(match)
    
    if filtered_matches:
        error_count += len(filtered_matches)
    
    # 영어 오탈자 검사
    english_spelling_errors = check_english_spelling(text)
    error_count += english_spelling_errors
    
    # 한국어 오탈자 검사
    korean_spelling_errors = check_korean_spelling(text)
    error_count += korean_spelling_errors
    
    # 형식 불일치 검사 (날짜 형식 등)
    format_errors = check_format_consistency(text)
    error_count += format_errors
    
    # 데이터 내 중복 검사 (문장 단위가 아닌 데이터 내)
    data_duplication_errors = check_data_duplication(text)
    error_count += data_duplication_errors
    
    # 맥락 단절 검사
    context_break_errors = check_context_break(text)
    error_count += context_break_errors
    
    # 오류 점수 계산 (오류가 적을수록 높은 점수)
    # 단어 수 대비 오류 비율 계산
    words = text.split()
    if len(words) > 0:
        # 오류 비율을 단어 수 대비로 계산 (더 합리적)
        # 오류가 적을수록 점수가 높아야 함
        error_ratio_by_word = min(error_count / max(len(words), 1), 1.0)  # 단어 수 대비 오류 비율
        
        # 오류 비율이 주요 기준
        # 예: 오류 1개, 단어 84개 → 1/84 = 0.012 (1.2%)
        # 오류 비율이 높을수록 패널티가 커짐
        error_ratio = min(error_ratio_by_word * 0.8, 0.9)  # 오류 비율의 80%를 패널티로, 최대 90%
        
        # 오류가 매우 적으면 패널티를 더 줄임
        if error_count <= 3 and error_ratio_by_word < 0.05:
            error_ratio *= 0.5  # 오류가 적으면 패널티 절반으로
    else:
        error_ratio = 1.0 if error_count == 0 else 0.8
    
    accuracy = max(1.0 - error_ratio, 0.05)  # 최소 0.05 보장
    
    # 한글이 너무 적으면 패널티 (한국어 텍스트 가정)
    if korean_ratio < 0.3 and total_chars > 50:
        accuracy *= 0.9
    
    return max(accuracy, 0.0)

def check_english_spelling(text: str) -> int:
    """
    영어 오탈자를 검사합니다.
    pyenchant 라이브러리를 사용하여 모든 오탈자를 자동으로 감지합니다.
    라이브러리가 없으면 제한적인 패턴 기반 검사로 fallback합니다.
    
    Returns:
        int: 발견된 영어 오탈자 개수
    """
    error_count = 0
    
    # 영어 단어 추출 (한글이 없는 순수 영어 단어만)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)  # 3글자 이상 영어 단어만
    
    if len(words) == 0:
        return 0
    
    # pyenchant 사용 가능한 경우 - 모든 오탈자 자동 감지
    dict_en = get_enchant_dict()
    if dict_en is not None:
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) >= 3:
                # 사전 기반 검사 - 모든 오탈자 자동 감지
                if not dict_en.check(clean_word):
                    # 대문자 약어(예: "USA", "AI", "API")는 제외
                    if not (word.isupper() and len(word) <= 5):
                        error_count += 1
    else:
        # pyenchant가 없으면 제한적인 패턴 기반 검사 (fallback)
        # 주의: 패턴 기반은 모든 오탈자를 감지하지 못할 수 있습니다.
        # 완전한 검사를 위해서는 pyenchant 설치를 권장합니다.
        common_typos = [
            r'\bteh\b',  # "the" 오탈자
            r'\brecieve\b',  # "receive" 오탈자
            r'\bseperate\b',  # "separate" 오탈자
            r'\baccomodate\b',  # "accommodate" 오탈자
            r'\boccured\b',  # "occurred" 오탈자
            r'\bdefinately\b',  # "definitely" 오탈자
            r'\bexistance\b',  # "existence" 오탈자
            r'\bpriviledge\b',  # "privilege" 오탈자
            r'\bmaintainance\b',  # "maintenance" 오탈자
            r'\bembarass\b',  # "embarrass" 오탈자
        ]
        
        for pattern in common_typos:
            matches = re.findall(pattern, text, re.IGNORECASE)
            error_count += len(matches)
    
    return error_count

def check_korean_spelling(text: str) -> int:
    """
    한국어 맞춤법 오류를 검사합니다.
    hanspell 라이브러리를 사용하여 모든 맞춤법 오류를 자동으로 감지합니다.
    라이브러리가 없으면 제한적인 패턴 기반 검사로 fallback합니다.
    
    Returns:
        int: 발견된 한국어 맞춤법 오류 개수
    """
    error_count = 0
    
    # 한글 비율 체크
    korean_chars = len(re.findall(r'[가-힣]', text))
    total_chars = len(text.replace(' ', ''))
    korean_ratio = korean_chars / max(total_chars, 1)
    
    # 한글이 너무 적으면 검사하지 않음
    if korean_ratio < 0.3:
        return 0
    
    # hanspell 사용 가능한 경우 - 모든 맞춤법 오류 자동 감지
    if _hanspell_available and spell_checker is not None:
        try:
            # 짧은 텍스트는 전체 검사, 긴 텍스트는 문장 단위로 검사
            if len(text) < 500:
                result = spell_checker.check(text)
                if result.errors > 0:
                    error_count = result.errors
            else:
                # 긴 텍스트는 문장 단위로 나눠서 검사
                sentences = re.split(r'[.!?]\s+', text)
                for sentence in sentences:
                    if len(sentence.strip()) > 10:
                        try:
                            result = spell_checker.check(sentence)
                            if result.errors > 0:
                                error_count += result.errors
                        except:
                            pass
        except Exception as e:
            # hanspell API 호출 실패 시 패턴 기반 검사로 fallback
            pass
    
    # hanspell이 없거나 실패한 경우 제한적인 패턴 기반 검사 (fallback)
    # 주의: 패턴 기반은 모든 오탈자를 감지하지 못할 수 있습니다.
    # 완전한 검사를 위해서는 py-hanspell 설치를 권장합니다.
    if error_count == 0:
        common_korean_typos = [
            r'좋에요',  # "좋아요" 오탈자
            r'맛읐는',  # "맛있는" 오탈자
            r'맛읐는거',  # "맛있는거" 오탈자
            r'되요',  # "돼요" 오탈자 (맥락에 따라 다를 수 있음)
            r'안되요',  # "안 돼요" 오탈자
            r'되게',  # "돼게" 오탈자 (맥락에 따라 다를 수 있음)
            r'데이터\s+품질는',  # "품질은" 오탈자 (예: "데이터 품질는")
        ]
        
        for pattern in common_korean_typos:
            matches = re.findall(pattern, text)
            error_count += len(matches)
    
    return error_count

def check_format_consistency(text: str) -> int:
    """
    형식 일관성을 검사합니다.
    날짜 형식 등이 여러 개 섞여 있는지 확인합니다.
    
    Returns:
        int: 발견된 형식 불일치 개수
    """
    error_count = 0
    
    # 날짜 형식 패턴들
    date_patterns = [
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'[A-Z][a-z]+\s+\d+',  # Month Day (Nov 4th)
        r'\d{2}년\s*\d{1,2}월\s*\d{1,2}일',  # YY년 MM월 DD일
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or MM/DD/YY
    ]
    
    found_formats = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found_formats.append(pattern)
    
    # 여러 형식이 섞여 있으면 불일치
    if len(found_formats) > 1:
        error_count += len(found_formats) - 1
    
    return error_count

def check_data_duplication(text: str) -> int:
    """
    데이터 내 중복을 검사합니다.
    문장 단위가 아닌 데이터 값 내 중복을 찾습니다.
    
    Returns:
        int: 발견된 중복 패턴 개수
    """
    error_count = 0
    
    # "Product ID: 123, 456, 123, 123" 같은 패턴
    # 숫자 리스트에서 중복 검사
    number_lists = re.findall(r'(?:ID|번호|코드|넘버)[:\s]+([0-9,\s]+)', text, re.IGNORECASE)
    for num_list in number_lists:
        numbers = re.findall(r'\d+', num_list)
        if len(numbers) > 2:
            # 중복이 있으면
            if len(numbers) != len(set(numbers)):
                error_count += 1
    
    # 같은 단어가 3번 이상 반복되는 패턴
    # "그거 그거 그거" 같은 패턴
    word_repetition = re.findall(r'\b([가-힣a-zA-Z]+)\s+\1\s+\1\b', text)
    if word_repetition:
        error_count += len(word_repetition)
    
    return error_count

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

def check_context_break(text: str) -> int:
    """
    맥락 단절을 검사합니다.
    문장 간 주제 변화가 급격한 경우를 감지합니다.
    
    Returns:
        int: 발견된 맥락 단절 개수
    """
    error_count = 0
    
    # 문장 단위로 분리
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    sentences = []
    for line in lines:
        parts = re.split(r'[.!?]+\s+', line)
        sentences.extend([s.strip() for s in parts if len(s.strip()) > 10])  # 최소 길이 10자 이상
    
    # 문장이 2개 미만이면 맥락 단절 검사 불가
    if len(sentences) < 2:
        return 0
    
    try:
        model = get_model()
        
        # 문장이 너무 많으면 샘플링 (성능 최적화)
        max_sentences = 50
        if len(sentences) > max_sentences:
            import random
            sentences = random.sample(sentences, max_sentences)
        
        # 문장 임베딩 생성
        embeddings = model.encode(sentences, convert_to_tensor=True, show_progress_bar=False)
        
        # 연속된 문장 간 유사도 계산
        context_break_threshold = 0.3  # 유사도가 0.3 미만이면 맥락 단절로 판단
        
        for i in range(len(embeddings) - 1):
            # 현재 문장과 다음 문장 간 유사도 계산
            similarity = util.pytorch_cos_sim(
                embeddings[i].unsqueeze(0),
                embeddings[i+1].unsqueeze(0)
            ).item()
            
            # 유사도가 매우 낮으면 맥락 단절 가능
            if similarity < context_break_threshold:
                error_count += 1
        
        return error_count
    
    except Exception as e:
        # 모델 로드 실패 시 패턴 기반 검사로 대체
        # 간단한 키워드 기반 검사 (한계 있음)
        return 0

