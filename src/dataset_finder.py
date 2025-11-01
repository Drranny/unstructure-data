"""
Hugging Face 데이터셋 검색 및 목록 조회 모듈
"""
from typing import List, Dict, Optional

def search_huggingface_datasets(
    query: str = "", 
    task: str = None,
    max_results: int = 50
) -> List[Dict]:
    """
    Hugging Face Hub에서 데이터셋을 검색합니다.
    
    Args:
        query: 검색어 (예: "image classification", "sentiment")
        task: 작업 타입 (예: "image-classification", "text-classification")
        max_results: 최대 결과 수
        
    Returns:
        List[Dict]: 데이터셋 정보 리스트
    """
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        
        # 검색 파라미터 설정
        search_params = {
            "search": query,
            "limit": max_results,
        }
        
        if task:
            search_params["task"] = task
        
        # 데이터셋 검색
        datasets = api.list_datasets(**search_params)
        
        results = []
        for dataset in datasets:
            results.append({
                "id": dataset.id,
                "author": dataset.author,
                "downloads": getattr(dataset, 'downloads', 0),
                "likes": getattr(dataset, 'likes', 0),
            })
        
        return results
    
    except ImportError:
        raise ImportError("huggingface_hub가 설치되어 있지 않습니다. pip install huggingface_hub 실행하세요.")
    except Exception as e:
        raise Exception(f"데이터셋 검색 실패: {e}")

def get_popular_datasets(task: str = None, max_results: int = 30) -> List[Dict]:
    """
    인기 있는 데이터셋 목록을 가져옵니다.
    
    Args:
        task: 작업 타입 필터 (예: "image-classification", "text-classification")
        max_results: 최대 결과 수
        
    Returns:
        List[Dict]: 인기 데이터셋 목록
    """
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        
        # 인기 데이터셋 검색 (다운로드 수 기준)
        datasets = api.list_datasets(
            sort="downloads",
            direction=-1,
            limit=max_results,
            task=task if task else None
        )
        
        results = []
        for dataset in datasets:
            results.append({
                "id": dataset.id,
                "author": dataset.author,
                "downloads": getattr(dataset, 'downloads', 0),
                "likes": getattr(dataset, 'likes', 0),
            })
        
        return results
    
    except ImportError:
        raise ImportError("huggingface_hub가 설치되어 있지 않습니다.")
    except Exception as e:
        # 실패 시 미리 정의된 목록 반환
        return get_predefined_datasets(task)

def get_predefined_datasets(task: str = None) -> List[Dict]:
    """
    미리 정의된 인기 데이터셋 목록을 반환합니다.
    
    Args:
        task: 작업 타입 필터
        
    Returns:
        List[Dict]: 데이터셋 목록
    """
    # 이미지 데이터셋
    image_datasets = [
        {"id": "beans", "author": "beans", "downloads": 50000, "likes": 100, "task": "image-classification"},
        {"id": "food101", "author": "food101", "downloads": 200000, "likes": 500, "task": "image-classification"},
        {"id": "cifar10", "author": "cifar10", "downloads": 300000, "likes": 800, "task": "image-classification"},
        {"id": "cifar100", "author": "cifar100", "downloads": 150000, "likes": 400, "task": "image-classification"},
        {"id": "mnist", "author": "mnist", "downloads": 500000, "likes": 1200, "task": "image-classification"},
        {"id": "fashion_mnist", "author": "fashion_mnist", "downloads": 200000, "likes": 600, "task": "image-classification"},
        {"id": "cats_vs_dogs", "author": "cats_vs_dogs", "downloads": 100000, "likes": 300, "task": "image-classification"},
        {"id": "stanford_dogs", "author": "stanford_dogs", "downloads": 80000, "likes": 250, "task": "image-classification"},
        {"id": "caltech101", "author": "caltech101", "downloads": 60000, "likes": 200, "task": "image-classification"},
        {"id": "imagenet-1k", "author": "imagenet1k", "downloads": 1000000, "likes": 2000, "task": "image-classification"},
    ]
    
    # 텍스트 데이터셋
    text_datasets = [
        {"id": "imdb", "author": "imdb", "downloads": 400000, "likes": 1000, "task": "text-classification"},
        {"id": "yelp_review_full", "author": "yelp_review_full", "downloads": 300000, "likes": 800, "task": "text-classification"},
        {"id": "yelp_review_polarity", "author": "yelp_review_polarity", "downloads": 250000, "likes": 600, "task": "text-classification"},
        {"id": "ag_news", "author": "ag_news", "downloads": 200000, "likes": 500, "task": "text-classification"},
        {"id": "amazon_polarity", "author": "amazon_polarity", "downloads": 350000, "likes": 900, "task": "text-classification"},
        {"id": "amazon_reviews_multi", "author": "amazon_reviews_multi", "downloads": 180000, "likes": 450, "task": "text-classification"},
        {"id": "sst2", "author": "sst2", "downloads": 500000, "likes": 1200, "task": "text-classification"},
        {"id": "squad", "author": "squad", "downloads": 600000, "likes": 1500, "task": "question-answering"},
        {"id": "glue", "author": "glue", "downloads": 800000, "likes": 2000, "task": "text-classification"},
        {"id": "xnli", "author": "xnli", "downloads": 150000, "likes": 400, "task": "natural-language-inference"},
    ]
    
    if task == "image-classification" or task is None:
        return image_datasets
    elif task == "text-classification":
        return text_datasets
    else:
        return image_datasets + text_datasets

