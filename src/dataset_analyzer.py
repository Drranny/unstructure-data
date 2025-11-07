"""
데이터셋 배치 분석 모듈
CIFAR-10, TID2013 등의 데이터셋을 다운로드하고 배치로 분석합니다.
텍스트 및 이미지 데이터셋 모두 지원합니다.
"""
import numpy as np
from PIL import Image
import imagehash
from typing import List, Dict
from src.image_quality import analyze_image_quality, calculate_duplication_score
from src.text_quality import analyze_text_quality
from src.utils import calc_total_score

def analyze_dataset_images(images: List[Image.Image], max_samples: int = 100) -> Dict:
    """
    여러 이미지의 품질을 배치로 분석합니다.
    
    Args:
        images: PIL Image 객체 리스트
        max_samples: 최대 분석할 이미지 개수 (성능 고려)
        
    Returns:
        dict: 전체 데이터셋의 품질 통계
    """
    if len(images) == 0:
        return {
            "총 이미지 수": 0,
            "평균 해상도": 0.0,
            "평균 선명도": 0.0,
            "평균 노이즈": 0.0,
            "평균 중복도": 0.0,
            "평균 종합 점수": 0.0,
        }
    
    # 샘플링 (너무 많으면 일부만)
    # 참고: random.sample을 사용하여 무작위로 선택하므로,
    # 해상도가 다른 이미지들이 골고루 선택될 수 있습니다.
    is_single_image = (len(images) == 1)
    
    original_count = len(images)
    if len(images) > max_samples:
        import random
        images = random.sample(images, max_samples)
    
    all_scores = {
        "해상도": [],
        "선명도": [],
        "노이즈": [],
        "중복도": [],
        "종합점수": []
    }
    
    # 실제 해상도 정보 저장 (width x height)
    actual_resolutions = []  # (width, height) 튜플 리스트
    
    # 개별 이미지 점수 저장
    individual_scores = []  # 각 이미지의 개별 점수 리스트
    
    image_hashes = []
    
    # 각 이미지 분석
    for img in images:
        scores = analyze_image_quality(img, is_single_image=is_single_image)
        
        score_count = len(scores) # 단일 분석 시 3, 배치 분석 시 4
        
        if score_count == 3: # 단일 분석 (중복도 제외)
            total = (scores["해상도"] + scores["선명도"] + (1 - scores["노이즈"])) / 3
            dup_score = "N/A"
        else: # 배치 분석 (중복도 포함)
            total = (scores["해상도"] + scores["선명도"] + (1 - scores["노이즈"]) + (1 - scores["중복도"])) / 4
            dup_score = scores["중복도"]
        
        all_scores["해상도"].append(scores["해상도"])
        all_scores["선명도"].append(scores["선명도"])
        all_scores["노이즈"].append(scores["노이즈"])
        
        if not is_single_image:
             # 중복도 항목은 배치 분석일 때만 scores에 있으므로 저장
            all_scores["중복도"].append(scores["중복도"])
            
        all_scores["종합점수"].append(total)
        
        # 개별 점수 저장
        individual_scores.append({
            "해상도": round(scores["해상도"], 3),
            "선명도": round(scores["선명도"], 3),
            "노이즈": round(scores["노이즈"], 3),
            "중복도": dup_score if isinstance(dup_score, str) else round(dup_score, 3),
            "종합점수": round(total, 3),
        })
        
        # 실제 해상도 저장 (width x height)
        actual_resolutions.append((img.width, img.height))
        
        # 중복도 계산을 위한 해시 저장
        if not is_single_image:
            image_hashes.append(imagehash.average_hash(img))
    
        
    # 종합 점수 재계산: 개별 평균을 기반으로 계산
    avg_resolution = np.mean(all_scores["해상도"])
    avg_sharpness  = np.mean(all_scores["선명도"])
    avg_noise      = np.mean(all_scores["노이즈"])
    
    if not is_single_image and len(image_hashes) > 1:
        # 배치 분석: 중복도 계산 및 4개 지표 기반 최종 종합 점수 계산
        avg_dup = calculate_duplication_score(image_hashes)
        avg_total = np.mean(all_scores["종합점수"])
        report_avg_dup = round(avg_dup, 3) 
    else:
        # 단일 분석: 중복도 N/A 처리 및 3개 지표 기반 최종 종합 점수 계산
        avg_total = np.mean(all_scores["종합점수"])
        report_avg_dup = "N/A" 
    
    # 해상도 통계 계산
    widths = [r[0] for r in actual_resolutions]
    heights = [r[1] for r in actual_resolutions]
    total_pixels = [w * h for w, h in actual_resolutions]
    
    # 통계 계산
    result = {
        "총 이미지 수": len(images),
        "원본 데이터셋 크기": original_count if original_count > len(images) else len(images),
        "샘플링 여부": "예" if original_count > len(images) else "아니오",
        "평균 해상도": round(avg_resolution, 3),
        "평균 선명도": round(avg_sharpness, 3),
        "평균 노이즈": round(avg_noise, 3),
        "평균 중복도": report_avg_dup,
        "평균 종합 점수": round(avg_total, 3),
        "최소 종합 점수": round(np.min(all_scores["종합점수"]), 3),
        "최대 종합 점수": round(np.max(all_scores["종합점수"]), 3),
        "표준편차": round(np.std(all_scores["종합점수"]), 3) if len(all_scores["종합점수"]) > 1 else 0.0,
        
        # 실제 해상도 정보 추가
        "해상도 분포": {
            "최소": f"{min(widths)}x{min(heights)}",
            "최대": f"{max(widths)}x{max(heights)}",
            "평균": f"{int(np.mean(widths))}x{int(np.mean(heights))}",
            "중앙값": f"{int(np.median(widths))}x{int(np.median(heights))}",
            "평균 픽셀 수": f"{int(np.mean(total_pixels)):,}",
        },
        "해상도 목록": [f"{w}x{h}" for w, h in actual_resolutions],  # 선택된 이미지들의 실제 해상도
        "개별 점수": individual_scores,  # 각 이미지의 개별 점수 리스트
    }
    
    return result

def analyze_dataset_texts(texts: List[str], max_samples: int = 100) -> Dict:
    """
    여러 텍스트의 품질을 배치로 분석합니다.
    
    Args:
        texts: 텍스트 문자열 리스트
        max_samples: 최대 분석할 텍스트 개수 (성능 고려)
        
    Returns:
        dict: 전체 데이터셋의 품질 통계
    """
    if len(texts) == 0:
        return {
            "총 텍스트 수": 0,
            "평균 정확성": 0.0,
            "평균 중복도": 0.0,
            "평균 완전성": 0.0,
            "평균 종합 점수": 0.0,
        }
    
    # 샘플링 (너무 많으면 일부만)
    if len(texts) > max_samples:
        import random
        texts = random.sample(texts, max_samples)
    
    all_scores = {
        "정확성": [],
        "중복도": [],
        "완전성": [],
        "종합점수": []
    }
    
    # 개별 텍스트 점수 저장
    individual_scores = []  # 각 텍스트의 개별 점수 리스트
    
    # 각 텍스트 분석
    for text in texts:
        if not text or len(text.strip()) == 0:
            continue
            
        scores = analyze_text_quality(text)
        total = calc_total_score(scores)
        
        accuracy = scores["정확성(오탈자비율)"]
        duplication = scores["중복도(유사도역비율)"]
        completeness = scores["완전성(문장충실도)"]
        
        all_scores["정확성"].append(accuracy)
        all_scores["중복도"].append(duplication)
        all_scores["완전성"].append(completeness)
        all_scores["종합점수"].append(total)
        
        # 개별 점수 저장
        individual_scores.append({
            "정확성": round(accuracy, 3),
            "중복도": round(duplication, 3),
            "완전성": round(completeness, 3),
            "종합점수": round(total, 3),
        })
    
    if len(all_scores["종합점수"]) == 0:
        return {
            "총 텍스트 수": 0,
            "평균 정확성": 0.0,
            "평균 중복도": 0.0,
            "평균 완전성": 0.0,
            "평균 종합 점수": 0.0,
        }
    
    # 통계 계산
    result = {
        "총 텍스트 수": len(all_scores["종합점수"]),
        "평균 정확성": round(np.mean(all_scores["정확성"]), 3),
        "평균 중복도": round(np.mean(all_scores["중복도"]), 3),
        "평균 완전성": round(np.mean(all_scores["완전성"]), 3),
        "평균 종합 점수": round(np.mean(all_scores["종합점수"]), 3),
        "최소 종합 점수": round(np.min(all_scores["종합점수"]), 3),
        "최대 종합 점수": round(np.max(all_scores["종합점수"]), 3),
        "표준편차": round(np.std(all_scores["종합점수"]), 3),
        "개별 점수": individual_scores,  # 각 텍스트의 개별 점수 리스트
    }
    
    return result

def load_cifar10(num_samples: int = 100):
    """
    CIFAR-10 데이터셋을 로드합니다.
    
    Args:
        num_samples: 로드할 샘플 개수
        
    Returns:
        List[PIL.Image]: 이미지 리스트
    """
    try:
        from torchvision import datasets
        from torchvision import transforms
        
        # CIFAR-10 데이터셋 로드
        transform = transforms.Compose([
            transforms.ToPILImage()
        ])
        
        dataset = datasets.CIFAR10(
            root='./data', 
            train=True, 
            download=True, 
            transform=None
        )
        
        images = []
        for i in range(min(num_samples, len(dataset))):
            img, _ = dataset[i]
            if isinstance(img, Image.Image):
                images.append(img)
            else:
                # numpy array나 tensor인 경우 변환
                img_pil = Image.fromarray(np.array(img))
                images.append(img_pil)
        
        return images
    
    except ImportError:
        raise ImportError("torchvision이 설치되어 있지 않습니다. pip install torchvision 실행하세요.")
    except Exception as e:
        raise Exception(f"CIFAR-10 로드 실패: {e}")

def load_tid2013(num_samples: int = 100, custom_path: str = None):
    """
    TID2013 데이터셋을 로드합니다.
    
    Args:
        num_samples: 로드할 샘플 개수
        custom_path: 커스텀 경로 지정 (선택사항)
        
    Returns:
        List[PIL.Image]: 이미지 리스트
    """
    import os
    import glob
    
    # TID2013은 직접 다운로드가 어려우므로 로컬 경로에서 로드
    # 또는 커스텀 경로 사용
    
    # 가능한 경로들
    if custom_path:
        possible_paths = [custom_path]
    else:
        # 프로젝트 루트 기준으로 경로 생성
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_paths = [
            os.path.join(project_root, "data", "TID2013"),
            os.path.join(project_root, "TID2013"),
            os.path.join(".", "data", "TID2013"),
            os.path.join(".", "TID2013"),
            os.path.join("/", "data", "TID2013"),
            os.path.expanduser("~/TID2013"),
            os.path.expanduser("~/data/TID2013"),
        ]
    
    images = []
    
    for base_path in possible_paths:
        if not os.path.exists(base_path):
            continue
            
        # TID2013 구조 확인
        # 1. reference_images 폴더 안의 이미지
        ref_path = os.path.join(base_path, "reference_images")
        if os.path.exists(ref_path):
            img_files = []
            img_files.extend(glob.glob(os.path.join(ref_path, "*.bmp")))
            img_files.extend(glob.glob(os.path.join(ref_path, "*.png")))
            img_files.extend(glob.glob(os.path.join(ref_path, "*.jpg")))
            img_files.extend(glob.glob(os.path.join(ref_path, "*.jpeg")))
            
            if img_files:
                for i, img_file in enumerate(sorted(img_files)[:num_samples]):
                    try:
                        img = Image.open(img_file)
                        images.append(img)
                    except Exception as e:
                        print(f"이미지 로드 실패: {img_file}, {e}")
                        continue
                
                if images:
                    break
        
        # 2. 직접 이미지 파일이 있는 경우
        img_files_direct = []
        img_files_direct.extend(glob.glob(os.path.join(base_path, "*.bmp")))
        img_files_direct.extend(glob.glob(os.path.join(base_path, "*.png")))
        img_files_direct.extend(glob.glob(os.path.join(base_path, "*.jpg")))
        img_files_direct.extend(glob.glob(os.path.join(base_path, "*.jpeg")))
        
        if img_files_direct:
            for i, img_file in enumerate(sorted(img_files_direct)[:num_samples]):
                try:
                    img = Image.open(img_file)
                    images.append(img)
                except Exception as e:
                    print(f"이미지 로드 실패: {img_file}, {e}")
                    continue
            
            if images:
                break
    
    if not images:
        error_msg = (
            "TID2013 데이터셋을 찾을 수 없습니다.\n\n"
            "📥 다운로드 방법:\n"
            "1. 공식 웹사이트: http://www.ponomarenko.info/tid2013.htm\n"
            "2. 다운로드 후 다음 경로 중 하나에 배치:\n"
            f"   - {os.path.join(os.getcwd(), 'data', 'TID2013', 'reference_images')}\n"
            f"   - {os.path.join(os.getcwd(), 'TID2013', 'reference_images')}\n\n"
            "💡 또는 '커스텀 폴더' 옵션을 사용하여 본인의 이미지 폴더를 지정하세요!"
        )
        raise FileNotFoundError(error_msg)
    
    return images

def get_available_splits(dataset_name: str) -> List[str]:
    """
    Hugging Face 데이터셋의 사용 가능한 split 목록을 가져옵니다.
    (데이터셋 다운로드 없이 메타데이터만 확인)
    
    Args:
        dataset_name: Hugging Face 데이터셋 이름
        
    Returns:
        List[str]: 사용 가능한 split 목록 (예: ['train', 'test', 'validation'])
    """
    # 먼저 HfApi로 시도 (다운로드 없이 빠름)
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        dataset_info = api.dataset_info(dataset_name)
        
        # splits 정보 추출
        if hasattr(dataset_info, 'splits') and dataset_info.splits:
            return list(dataset_info.splits.keys())
    except Exception:
        pass  # HfApi 실패 시 다음 방법 시도
    
    # HfApi에서 splits를 못 가져왔으면 datasets 라이브러리로 폴백
    try:
        from datasets import load_dataset_builder
        
        # trust_remote_code 없이 시도
        try:
            builder = load_dataset_builder(dataset_name)
        except Exception:
            # trust_remote_code가 필요한 경우
            builder = load_dataset_builder(dataset_name, trust_remote_code=True)
        
        # 방법 1: builder.info.splits 확인
        if hasattr(builder, 'info') and hasattr(builder.info, 'splits'):
            splits = builder.info.splits
            if splits:
                return list(splits.keys())
        
        # 방법 2: builder.config.data_files에서 split 추출 (Parquet 기반 데이터셋)
        if hasattr(builder, 'config') and hasattr(builder.config, 'data_files'):
            data_files = builder.config.data_files
            if data_files and isinstance(data_files, dict):
                splits = list(data_files.keys())
                if splits:
                    return splits
        
        # 방법 3: builder.configs에서 split 추출
        if hasattr(builder, 'configs') and builder.configs:
            # 첫 번째 config의 data_files 확인
            first_config = builder.configs[0]
            if hasattr(first_config, 'data_files') and first_config.data_files:
                if isinstance(first_config.data_files, dict):
                    splits = list(first_config.data_files.keys())
                    if splits:
                        return splits
    except Exception:
        pass
    
    # 모든 방법 실패 시 기본값 반환
    return ["train", "test", "validation", "val"]

def load_huggingface_dataset(dataset_name: str, num_samples: int = 100, split: str = "train", image_column: str = None, download_full: bool = False, download_percentage: int = None):
    """
    Hugging Face Datasets에서 이미지 데이터셋을 로드합니다.
    
    Args:
        dataset_name: Hugging Face 데이터셋 이름 (예: "beans", "food101", "dataset:config")
                     ':' 구분자로 config를 지정할 수 있습니다
        num_samples: 로드할 샘플 개수 (download_percentage가 None일 때 사용)
        split: 데이터셋 split (예: "train", "test", "train[:100]")
        image_column: 이미지 컬럼 이름 (None이면 자동 감지)
        download_full: True면 전체 다운로드, False면 일부만 (기본값: False)
        download_percentage: 다운로드할 데이터셋 비율 (1-100, None이면 num_samples 사용)
        
    Returns:
        List[PIL.Image]: 이미지 리스트
    """
    try:
        from datasets import load_dataset, get_dataset_config_names
        
        # 데이터셋 이름에서 config 추출 (dataset_name:config 형식 지원)
        config_name = None
        base_dataset_name = dataset_name
        if ':' in dataset_name:
            parts = dataset_name.split(':', 1)
            base_dataset_name = parts[0]
            config_name = parts[1]
        
        # 퍼센티지 기반 다운로드
        if download_percentage is not None:
            # 퍼센티지 형식으로 split 생성: train[:10%]
            actual_split = f"{split}[:{download_percentage}%]"
            num_samples_to_use = None  # 퍼센티지 사용 시 num_samples 무시
        # 샘플 개수 기반 다운로드
        elif not download_full:
            # split에 이미 슬라이싱이 있는지 확인
            if "[" not in split:
                # 슬라이싱 추가: train[:num_samples] 형식
                actual_split = f"{split}[:{num_samples}]"
            else:
                actual_split = split
            num_samples_to_use = num_samples
        # 전체 다운로드
        else:
            actual_split = split
            num_samples_to_use = num_samples
        
        # 데이터셋 로드 (config가 필요한 경우 자동 처리)
        def try_load_dataset(dataset_name_to_use, config_to_use=None):
            """데이터셋 로드를 시도하는 헬퍼 함수"""
            if download_full:
                # 전체 다운로드: split 그대로 사용 (슬라이싱 없음)
                try:
                    if config_to_use:
                        return load_dataset(dataset_name_to_use, name=config_to_use, split=split, trust_remote_code=True)
                    else:
                        return load_dataset(dataset_name_to_use, split=split, trust_remote_code=True)
                except Exception:
                    if config_to_use:
                        return load_dataset(dataset_name_to_use, name=config_to_use, split=split)
                    else:
                        return load_dataset(dataset_name_to_use, split=split)
            else:
                # 일부만 다운로드: streaming 모드 사용 (전체 다운로드 안 함)
                try:
                    # Streaming 모드로 시도 (전체 다운로드 안 함, 필요한 부분만)
                    if config_to_use:
                        return load_dataset(
                            dataset_name_to_use, 
                            name=config_to_use,
                            split=actual_split, 
                            trust_remote_code=True,
                            streaming=True
                        )
                    else:
                        return load_dataset(
                            dataset_name_to_use, 
                            split=actual_split, 
                            trust_remote_code=True,
                            streaming=True
                        )
                except Exception:
                    # streaming 실패 시 일반 모드로 재시도 (캐시된 데이터 사용)
                    try:
                        if config_to_use:
                            return load_dataset(
                                dataset_name_to_use, 
                                name=config_to_use,
                                split=actual_split, 
                                trust_remote_code=True,
                                streaming=False
                            )
                        else:
                            return load_dataset(
                                dataset_name_to_use, 
                                split=actual_split, 
                                trust_remote_code=True,
                                streaming=False
                            )
                    except Exception:
                        if config_to_use:
                            return load_dataset(
                                dataset_name_to_use, 
                                name=config_to_use,
                                split=actual_split, 
                                trust_remote_code=True
                            )
                        else:
                            return load_dataset(
                                dataset_name_to_use, 
                                split=actual_split, 
                                trust_remote_code=True
                            )
        
        # 데이터셋 로드 시도
        try:
            dataset = try_load_dataset(base_dataset_name, config_name)
        except Exception as e:
            error_msg = str(e)
            # Config 관련 에러인지 확인
            if "Config name is missing" in error_msg or "pick one among the available configs" in error_msg:
                # 사용 가능한 config 목록 가져오기
                try:
                    available_configs = get_dataset_config_names(base_dataset_name)
                    if available_configs and len(available_configs) > 0:
                        # 첫 번째 config 자동 사용
                        auto_config = available_configs[0]
                        print(f"⚠️ Config가 지정되지 않아 첫 번째 config '{auto_config}'를 자동으로 사용합니다.")
                        print(f"   사용 가능한 configs: {', '.join(available_configs)}")
                        print(f"   다른 config를 사용하려면 데이터셋 이름을 '{base_dataset_name}:{auto_config}' 형식으로 지정하세요.")
                        dataset = try_load_dataset(base_dataset_name, auto_config)
                    else:
                        raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}")
                except Exception as config_error:
                    raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}\nConfig 조회 실패: {config_error}")
            else:
                raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}")
        
        # 이미지 컬럼 자동 감지
        if image_column is None:
            # 일반적인 이미지 컬럼 이름들
            possible_columns = ['image', 'images', 'img', 'photo', 'picture', 'Image', 'ImagePath']
            image_column = None
            
            for col in possible_columns:
                if col in dataset.column_names:
                    image_column = col
                    break
            
            # 없으면 첫 번째 컬럼 확인
            if image_column is None:
                for col in dataset.column_names:
                    try:
                        sample = dataset[0][col]
                        if isinstance(sample, Image.Image) or hasattr(sample, 'mode'):
                            image_column = col
                            break
                    except Exception:
                        continue
        
        # 이미지 컬럼을 찾지 못한 경우
        if image_column is None:
            # 텍스트 데이터셋인지 확인
            text_indicators = ['text', 'sentence', 'premise', 'hypothesis', 'question', 'context', 'answer', 'review', 'content']
            has_text_columns = any(col.lower() in text_indicators for col in dataset.column_names)
            
            if has_text_columns:
                raise ValueError(
                    f"이미지 데이터셋이 아닌 것으로 보입니다. 텍스트 데이터셋인 것 같습니다.\n"
                    f"사용 가능한 컬럼: {dataset.column_names}\n\n"
                    f"💡 해결 방법:\n"
                    f"  1. 데이터 타입을 '텍스트'로 변경하거나\n"
                    f"  2. 이미지 데이터셋을 선택하세요."
                )
            else:
                raise ValueError(
                    f"이미지 컬럼을 찾을 수 없습니다.\n"
                    f"사용 가능한 컬럼: {dataset.column_names}\n\n"
                    f"💡 이 데이터셋은 이미지 데이터셋이 아닐 수 있습니다.\n"
                    f"   데이터 타입을 확인하거나 다른 데이터셋을 선택해보세요."
                )
        
        images = []
        # 사용할 샘플 개수 결정
        # Streaming 모드인 경우 len() 계산이 느리므로 제한 사용
        is_streaming = hasattr(dataset, '__iter__') and not hasattr(dataset, '__len__')
        
        if is_streaming:
            # Streaming 모드: 필요한 개수만 순회
            max_samples = num_samples_to_use if num_samples_to_use is not None else 100
            for i, item in enumerate(dataset):
                if i >= max_samples:
                    break
                try:
                    img = item[image_column]
                    
                    # PIL Image로 변환
                    if isinstance(img, Image.Image):
                        images.append(img)
                    elif hasattr(img, 'convert'):
                        images.append(img)
                    else:
                        import numpy as np
                        if isinstance(img, np.ndarray):
                            img_pil = Image.fromarray(img)
                            images.append(img_pil)
                        else:
                            print(f"지원하지 않는 이미지 형식: {type(img)}")
                            continue
                except Exception as e:
                    print(f"이미지 {i} 로드 실패: {e}")
                    continue
        else:
            # 일반 모드: len() 사용 가능
            max_samples = num_samples_to_use if num_samples_to_use is not None else len(dataset)
            for i in range(min(max_samples, len(dataset))):
                try:
                    img = dataset[i][image_column]
                    
                    # PIL Image로 변환
                    if isinstance(img, Image.Image):
                        images.append(img)
                    elif hasattr(img, 'convert'):  # Image 객체인데 타입 체크가 안 되는 경우
                        images.append(img)
                    else:
                        # numpy array나 다른 형식인 경우
                        import numpy as np
                        if isinstance(img, np.ndarray):
                            img_pil = Image.fromarray(img)
                            images.append(img_pil)
                        else:
                            print(f"지원하지 않는 이미지 형식: {type(img)}")
                            continue
                except Exception as e:
                    print(f"이미지 {i} 로드 실패: {e}")
                    continue
        
        return images
    
    except ImportError:
        raise ImportError("datasets 라이브러리가 설치되어 있지 않습니다. pip install datasets 실행하세요.")
    except Exception as e:
        raise Exception(f"Hugging Face 데이터셋 로드 실패 ({dataset_name}): {e}")

def load_huggingface_text_dataset(dataset_name: str, num_samples: int = 100, split: str = "train", text_column: str = None, download_percentage: int = None, download_full: bool = False):
    """
    Hugging Face Datasets에서 텍스트 데이터셋을 로드합니다.
    
    Args:
        dataset_name: Hugging Face 데이터셋 이름 (예: "imdb", "yelp_review_full", "nyu-mll/glue:sst2")
                     ':' 구분자로 config를 지정할 수 있습니다 (예: "nyu-mll/glue:sst2")
        num_samples: 로드할 샘플 개수 (download_percentage가 None일 때 사용)
        split: 데이터셋 split (예: "train", "test")
        text_column: 텍스트 컬럼 이름 (None이면 자동 감지)
        download_percentage: 다운로드할 데이터셋 비율 (1-100, None이면 num_samples 사용)
        download_full: True면 전체 다운로드
        
    Returns:
        List[str]: 텍스트 리스트
    """
    # get_available_splits 함수는 이미 위에 정의되어 있음
    try:
        from datasets import load_dataset, get_dataset_config_names
        
        # 데이터셋 이름에서 config 추출 (dataset_name:config 형식 지원)
        config_name = None
        base_dataset_name = dataset_name
        if ':' in dataset_name:
            parts = dataset_name.split(':', 1)
            base_dataset_name = parts[0]
            config_name = parts[1]
        
        # 퍼센티지 기반 다운로드
        if download_percentage is not None:
            actual_split = f"{split}[:{download_percentage}%]"
            num_samples_to_use = None
        elif not download_full:
            if "[" not in split:
                actual_split = f"{split}[:{num_samples}]"
            else:
                actual_split = split
            num_samples_to_use = num_samples
        else:
            actual_split = split
            num_samples_to_use = None
        
        # 데이터셋 로드 (config가 필요한 경우 자동 처리)
        def try_load_dataset(dataset_name_to_use, config_to_use=None, split_to_use=None):
            """데이터셋 로드를 시도하는 헬퍼 함수"""
            if split_to_use is None:
                split_to_use = split if download_full else actual_split
            
            if download_full:
                # 전체 다운로드
                try:
                    if config_to_use:
                        return load_dataset(dataset_name_to_use, name=config_to_use, split=split_to_use, trust_remote_code=True)
                    else:
                        return load_dataset(dataset_name_to_use, split=split_to_use, trust_remote_code=True)
                except Exception:
                    if config_to_use:
                        return load_dataset(dataset_name_to_use, name=config_to_use, split=split_to_use)
                    else:
                        return load_dataset(dataset_name_to_use, split=split_to_use)
            else:
                # 일부만 다운로드: streaming 모드 사용
                try:
                    if config_to_use:
                        return load_dataset(
                            dataset_name_to_use, 
                            name=config_to_use,
                            split=split_to_use, 
                            trust_remote_code=True,
                            streaming=True
                        )
                    else:
                        return load_dataset(
                            dataset_name_to_use, 
                            split=split_to_use, 
                            trust_remote_code=True,
                            streaming=True
                        )
                except Exception:
                    # streaming 실패 시 일반 모드
                    if config_to_use:
                        return load_dataset(
                            dataset_name_to_use, 
                            name=config_to_use,
                            split=split_to_use, 
                            trust_remote_code=True
                        )
                    else:
                        return load_dataset(
                            dataset_name_to_use, 
                            split=split_to_use, 
                            trust_remote_code=True
                        )
        
        # 데이터셋 로드 시도 (재시도 로직 포함)
        dataset = None
        current_config = config_name
        current_split = split
        current_actual_split = actual_split
        max_retries = 3
        retry_count = 0
        
        while dataset is None and retry_count < max_retries:
            try:
                split_to_use = current_split if download_full else current_actual_split
                dataset = try_load_dataset(base_dataset_name, current_config, split_to_use)
            except Exception as e:
                error_msg = str(e)
                retry_count += 1
                
                # Config 관련 에러인지 확인
                if "Config name is missing" in error_msg or "pick one among the available configs" in error_msg:
                    # 사용 가능한 config 목록 가져오기
                    try:
                        from datasets import load_dataset_builder
                        available_configs = get_dataset_config_names(base_dataset_name)
                        
                        if available_configs and len(available_configs) > 0:
                            # train split이 있는 config를 우선 찾기
                            preferred_config = None
                            for config in available_configs:
                                try:
                                    builder = load_dataset_builder(base_dataset_name, config_name=config)
                                    if hasattr(builder, 'info') and hasattr(builder.info, 'splits'):
                                        splits = builder.info.splits
                                        if splits and 'train' in splits:
                                            preferred_config = config
                                            break
                                except Exception:
                                    continue
                            
                            # train split이 있는 config가 없으면 첫 번째 config 사용
                            auto_config = preferred_config if preferred_config else available_configs[0]
                            current_config = auto_config
                            
                            print(f"⚠️ Config가 지정되지 않아 config '{auto_config}'를 자동으로 사용합니다.")
                            print(f"   사용 가능한 configs: {', '.join(available_configs)}")
                            print(f"   다른 config를 사용하려면 데이터셋 이름을 '{base_dataset_name}:{auto_config}' 형식으로 지정하세요.")
                            
                            # 선택된 config에 사용 가능한 split 확인 및 자동 조정
                            try:
                                builder = load_dataset_builder(base_dataset_name, config_name=auto_config)
                                if hasattr(builder, 'info') and hasattr(builder.info, 'splits'):
                                    available_splits = list(builder.info.splits.keys())
                                    if current_split not in available_splits:
                                        # train -> test -> validation 순서로 우선순위
                                        for preferred_split in ['train', 'test', 'validation', 'val']:
                                            if preferred_split in available_splits:
                                                current_split = preferred_split
                                                # actual_split도 업데이트
                                                if "[" not in current_split:
                                                    current_actual_split = f"{current_split}[:{num_samples}]"
                                                else:
                                                    current_actual_split = current_split
                                                print(f"⚠️ 요청한 split이 없어 '{current_split}' split을 사용합니다.")
                                                print(f"   사용 가능한 splits: {', '.join(available_splits)}")
                                                break
                            except Exception:
                                pass  # split 확인 실패해도 계속 진행
                            
                            # 재시도
                            retry_count -= 1  # 재시도 카운트 조정 (이번 시도는 재시도로 간주하지 않음)
                            continue
                        else:
                            raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}")
                    except Exception as config_error:
                        raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}\nConfig 조회 실패: {config_error}")
                
                # Split 관련 에러인지 확인
                elif "Unknown split" in error_msg or "Should be one of" in error_msg:
                    # 사용 가능한 split 찾기
                    try:
                        from datasets import load_dataset_builder
                        builder = load_dataset_builder(base_dataset_name, config_name=current_config) if current_config else load_dataset_builder(base_dataset_name)
                        
                        if hasattr(builder, 'info') and hasattr(builder.info, 'splits'):
                            available_splits = list(builder.info.splits.keys())
                            # train -> test -> validation 순서로 우선순위
                            for preferred_split in ['train', 'test', 'validation', 'val']:
                                if preferred_split in available_splits:
                                    current_split = preferred_split
                                    # actual_split도 업데이트
                                    if "[" not in current_split:
                                        current_actual_split = f"{current_split}[:{num_samples}]"
                                    else:
                                        current_actual_split = current_split
                                    print(f"⚠️ 요청한 split이 없어 '{current_split}' split을 사용합니다.")
                                    print(f"   사용 가능한 splits: {', '.join(available_splits)}")
                                    break
                            else:
                                current_split = available_splits[0] if available_splits else "test"
                                if "[" not in current_split:
                                    current_actual_split = f"{current_split}[:{num_samples}]"
                                else:
                                    current_actual_split = current_split
                                print(f"⚠️ split '{current_split}'을 사용합니다.")
                                print(f"   사용 가능한 splits: {', '.join(available_splits)}")
                            
                            # 재시도
                            retry_count -= 1  # 재시도 카운트 조정 (이번 시도는 재시도로 간주하지 않음)
                            continue
                        else:
                            raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}")
                    except Exception as split_error:
                        raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}\nSplit 조회 실패: {split_error}")
                else:
                    if retry_count >= max_retries:
                        raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}")
                    else:
                        raise Exception(f"데이터셋 로드 실패: {base_dataset_name}\n에러: {e}")
        
        if dataset is None:
            raise Exception(f"데이터셋 로드 실패: {base_dataset_name} (최대 재시도 횟수 초과)")
        
        # 텍스트 컬럼 자동 감지
        if text_column is None:
            possible_columns = ['text', 'Text', 'review', 'content', 'sentence', 'document', 'abstract', 'body']
            text_column = None
            
            for col in possible_columns:
                if col in dataset.column_names:
                    text_column = col
                    break
            
            # 없으면 첫 번째 문자열 컬럼 찾기
            if text_column is None:
                for col in dataset.column_names:
                    if col not in ['label', 'labels', 'id', 'idx']:
                        try:
                            sample = dataset[0][col]
                            if isinstance(sample, str):
                                text_column = col
                                break
                        except:
                            continue
        
        if text_column is None:
            raise ValueError(f"텍스트 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {dataset.column_names}")
        
        texts = []
        # Streaming 모드인 경우 처리
        is_streaming = hasattr(dataset, '__iter__') and not hasattr(dataset, '__len__')
        
        if is_streaming:
            # Streaming 모드: 필요한 개수만 순회
            max_samples = num_samples_to_use if num_samples_to_use is not None else 100
            for i, item in enumerate(dataset):
                if i >= max_samples:
                    break
                try:
                    text = item[text_column]
                    if isinstance(text, str) and len(text.strip()) > 0:
                        texts.append(text)
                except Exception as e:
                    print(f"텍스트 {i} 로드 실패: {e}")
                    continue
        else:
            # 일반 모드: len() 사용 가능
            max_samples = num_samples_to_use if num_samples_to_use is not None else len(dataset)
            for i in range(min(max_samples, len(dataset))):
                try:
                    text = dataset[i][text_column]
                    if isinstance(text, str) and len(text.strip()) > 0:
                        texts.append(text)
                except Exception as e:
                    print(f"텍스트 {i} 로드 실패: {e}")
                    continue
        
        return texts
    
    except ImportError:
        raise ImportError("datasets 라이브러리가 설치되어 있지 않습니다. pip install datasets 실행하세요.")
    except Exception as e:
        raise Exception(f"Hugging Face 텍스트 데이터셋 로드 실패 ({dataset_name}): {e}")

def load_custom_dataset(folder_path: str, num_samples: int = 100):
    """
    로컬 폴더에서 이미지를 로드합니다.
    
    Args:
        folder_path: 이미지가 있는 폴더 경로
        num_samples: 최대 로드할 이미지 개수
        
    Returns:
        List[PIL.Image]: 이미지 리스트
    """
    import os
    import glob
    
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")
    
    # 지원하는 이미지 확장자
    extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"]
    
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        image_files.extend(glob.glob(os.path.join(folder_path, ext.upper())))
    
    if not image_files:
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {folder_path}")
    
    images = []
    for img_file in image_files[:num_samples]:
        try:
            img = Image.open(img_file)
            images.append(img)
        except Exception as e:
            print(f"이미지 로드 실패: {img_file}, {e}")
            continue
    
    return images

