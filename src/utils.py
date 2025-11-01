"""
공통 유틸리티 함수 모듈
점수 계산 및 등급 변환 등의 공통 기능을 제공합니다.
"""

def calc_total_score(result_dict: dict) -> float:
    """
    품질 지표 딕셔너리에서 평균 점수를 계산합니다.
    
    Args:
        result_dict: 품질 지표 딕셔너리 (값은 0-1 범위의 float)
        
    Returns:
        float: 평균 품질 점수 (0-1)
    """
    if not result_dict:
        return 0.0
    
    scores = [float(score) for score in result_dict.values() if isinstance(score, (int, float))]
    
    if len(scores) == 0:
        return 0.0
    
    return sum(scores) / len(scores)

def get_grade(score: float) -> str:
    """
    품질 점수를 등급으로 변환합니다.
    
    Args:
        score: 품질 점수 (0-1)
        
    Returns:
        str: 품질 등급 (A, B, C, D)
    """
    if score >= 0.8:
        return "A"
    elif score >= 0.6:
        return "B"
    elif score >= 0.4:
        return "C"
    else:
        return "D"

def format_score(score: float, decimals: int = 3) -> str:
    """
    점수를 포맷팅하여 반환합니다.
    
    Args:
        score: 점수 (float)
        decimals: 소수점 자릿수
        
    Returns:
        str: 포맷팅된 점수 문자열
    """
    return f"{score:.{decimals}f}"

def get_grade_description(grade: str) -> str:
    """
    등급에 대한 설명을 반환합니다.
    
    Args:
        grade: 품질 등급 (A, B, C, D)
        
    Returns:
        str: 등급 설명
    """
    descriptions = {
        "A": "우수한 품질입니다. AI 학습에 바로 사용할 수 있습니다.",
        "B": "양호한 품질입니다. 일부 개선이 필요할 수 있습니다.",
        "C": "보통 품질입니다. 품질 개선이 권장됩니다.",
        "D": "품질 개선이 시급합니다. 데이터 정제가 필요합니다.",
    }
    return descriptions.get(grade, "알 수 없는 등급입니다.")

