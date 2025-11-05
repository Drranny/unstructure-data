"""
이미지 데이터 품질진단 모듈
해상도, 선명도, 노이즈, 중복도 지표를 계산합니다.
"""
import cv2
import numpy as np
import imagehash
from PIL import Image

def analyze_image_quality(img: Image.Image):
    """
    이미지 품질을 분석하여 지표를 반환합니다.
    
    Args:
        img: PIL Image 객체
        
    Returns:
        dict: 품질 지표 딕셔너리
    """
    # PIL Image를 numpy 배열로 변환
    np_img = np.array(img)
    
    # RGB를 BGR로 변환 (OpenCV 형식)
    if len(np_img.shape) == 3 and np_img.shape[2] == 3:
        # RGB -> BGR 변환
        np_img_bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(np_img_bgr, cv2.COLOR_BGR2GRAY)
    elif len(np_img.shape) == 3 and np_img.shape[2] == 4:
        # RGBA 처리
        np_img_rgb = np_img[:, :, :3]
        np_img_bgr = cv2.cvtColor(np_img_rgb, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(np_img_bgr, cv2.COLOR_BGR2GRAY)
    else:
        # 이미 grayscale
        gray = np_img
    
    h, w = gray.shape
    
    # 1. 해상도 점수
    resolution_score = calculate_resolution_score(h, w)
    
    # 2. 선명도 (Laplacian Variance)
    sharpness_score = calculate_sharpness(gray)
    
    # 3. 노이즈 점수
    noise_score = calculate_noise_score(gray)
    
    # 4. 중복도 (기본값: 1.0, 실제 비교는 데이터셋 간 비교 시 사용)
    hash_val = imagehash.average_hash(img)
    duplication_score = 1.0  # 단일 이미지 분석 시에는 중복 없음으로 가정
    
    return {
        "해상도": round(resolution_score, 3),
        "선명도": round(sharpness_score, 3),
        "노이즈": round(noise_score, 3),
        "중복도": round(duplication_score, 3),
    }

def calculate_resolution_score(height: int, width: int) -> float:
    """
    해상도 점수를 계산합니다.
    기준: 최소 512x512 이상이면 1.0, 그 이하면 비례 점수
    """
    min_dimension = min(height, width)
    max_dimension = max(height, width)
    
    # 최소 크기 기준: 512x512
    min_standard = 512
    
    # 최소 차원 기준 점수
    min_score = min(min_dimension / min_standard, 1.0)
    
    # 종횡비 고려 (너무 극단적이면 패널티)
    aspect_ratio = max_dimension / max(min_dimension, 1)
    if aspect_ratio > 4:
        min_score *= 0.9  # 종횡비가 너무 극단적이면 패널티
    
    # 최대 차원도 고려 (고해상도 보너스)
    if max_dimension >= 2048:
        min_score = min(min_score * 1.1, 1.0)
    
    return max(min_score, 0.0)

def calculate_sharpness(gray_image: np.ndarray) -> float:
    """
    Laplacian Variance를 사용하여 선명도를 계산합니다.
    값이 높을수록 선명한 이미지입니다.
    """
    if gray_image is None or gray_image.size == 0:
        return 0.0
    
    try:
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        # Laplacian Variance 기준:
        # 0-100: 매우 흐림
        # 100-500: 보통
        # 500-1000: 선명
        # 1000+: 매우 선명
        
        # 정규화 (0-1 범위로)
        if laplacian_var >= 1000:
            sharpness_score = 1.0
        elif laplacian_var >= 500:
            sharpness_score = 0.7 + (laplacian_var - 500) / 500 * 0.3
        elif laplacian_var >= 100:
            sharpness_score = 0.4 + (laplacian_var - 100) / 400 * 0.3
        else:
            sharpness_score = 0.2 + (laplacian_var / 100) * 0.3  # 0~100 구간 → 0.2~0.5로 완화
        
        return min(max(sharpness_score, 0.0), 1.0)
    except Exception as e:
        print(f"선명도 계산 실패: {e}")
        return 0.5

def calculate_noise_score(gray_image: np.ndarray) -> float:
    """
    이미지 노이즈 수준을 계산합니다.
    Gaussian blur 후 원본과의 차이를 비교하여 노이즈를 측정합니다.
    """
    if gray_image is None or gray_image.size == 0:
        return 0.0
    
    try:
        # 블러 강도 줄임
        blur = cv2.GaussianBlur(gray_image, (3, 3), 0)
        diff = cv2.absdiff(gray_image, blur)

        # 평균 + 표준편차를 함께 사용 (작은 노이즈도 감지)
        noise_level = 0.6 * diff.std() + 0.4 * diff.mean()

        # 정규화 기준 낮춤 (노이즈 민감도 ↑)
        normalized_noise = np.clip(noise_level / 20, 0, 1)

        # 흐릿한 이미지 감점
        lap_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        blur_factor = np.clip(1 - lap_var / 500, 0, 1)

        # 노이즈가 많을수록 점수 ↓, 너무 부드러우면 감점
        noise_score = 1.0 - 0.8 * normalized_noise - 0.2 * blur_factor
        noise_score = float(np.clip(noise_score, 0.0, 1.0))

        return noise_score
    
    except Exception as e:
        print(f"노이즈 계산 실패: {e}")
        return 0.5

def calculate_duplication_score(image_hashes: list) -> float:
    """
    여러 이미지 간 중복도를 계산합니다.
    이미지 해시를 비교하여 중복 비율을 계산합니다.
    
    Args:
        image_hashes: ImageHash 객체 리스트
        
    Returns:
        float: 중복도 점수 (1.0 = 중복 없음, 0.0 = 모두 중복)
    """
    if len(image_hashes) < 2:
        return 1.0
    
    duplicate_count = 0
    total_comparisons = 0
    
    for i in range(len(image_hashes)):
        for j in range(i + 1, len(image_hashes)):
            total_comparisons += 1
            # 해시 차이 계산 (차이가 적으면 유사한 이미지)
            hash_diff = image_hashes[i] - image_hashes[j]
            if hash_diff <= 5:  # 임계값 설정
                duplicate_count += 1
    
    if total_comparisons == 0:
        return 1.0
    
    duplicate_ratio = duplicate_count / total_comparisons
    return max(1.0 - duplicate_ratio, 0.0)

