"""
Hugging Face 데이터셋 검색 및 목록 조회 모듈
"""
from typing import List, Dict, Optional
import time

def search_huggingface_datasets(
    query: str = "", 
    task: str = None,
    max_results: int = 50,
    fallback_on_error: bool = True
) -> List[Dict]:
    """
    Hugging Face Hub에서 데이터셋을 검색합니다.
    
    Args:
        query: 검색어 (예: "image classification", "sentiment")
        task: 작업 타입 (예: "image-classification", "text-classification")
        max_results: 최대 결과 수
        fallback_on_error: API 실패 시 미리 정의된 목록으로 폴백할지 여부
        
    Returns:
        List[Dict]: 데이터셋 정보 리스트
    """
    # 빈 검색어 처리
    if not query or not query.strip():
        if fallback_on_error:
            return get_predefined_datasets(task)
        return []
    
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        query_clean = query.strip()
        
        # 정확한 데이터셋 ID 형식 확인 (사용자/데이터셋명)
        is_exact_id = "/" in query_clean and len(query_clean.split("/")) == 2
        
        # 정확한 데이터셋 ID로 직접 조회 시도 (task 필터 무시)
        if is_exact_id:
            try:
                dataset_info = api.dataset_info(query_clean)
                result = {
                    "id": dataset_info.id,
                    "author": dataset_info.author if hasattr(dataset_info, 'author') else query_clean.split("/")[0],
                    "downloads": getattr(dataset_info, 'downloads', 0),
                    "likes": getattr(dataset_info, 'likes', 0),
                }
                # 정확한 ID 입력 시 task 필터 무시하고 반환
                return [result]
            except Exception as direct_error:
                # 직접 조회 실패 시 일반 검색으로 진행
                pass
        
        # 검색 전략: task 필터 없이 먼저 검색 시도 (더 넓은 결과)
        # 정확한 매칭이 중요하므로 먼저 task 필터 없이 시도
        search_strategies = [
            {"search": query_clean, "limit": max_results},  # task 필터 없이
        ]
        
        # task 필터가 있는 경우에도 시도 (2번째 우선순위)
        if task:
            search_strategies.append({
                "search": query_clean,
                "limit": max_results,
                "task": task
            })
        
        # 여러 전략 시도
        for search_params in search_strategies:
            try:
                datasets = api.list_datasets(**search_params)
                results = []
                for dataset in datasets:
                    # 검색어가 데이터셋 ID에 포함되어 있는지 확인
                    if query_clean.lower() in dataset.id.lower():
                        results.append({
                            "id": dataset.id,
                            "author": dataset.author,
                            "downloads": getattr(dataset, 'downloads', 0),
                            "likes": getattr(dataset, 'likes', 0),
                        })
                
                if results:
                    return results
            except Exception:
                continue
        
        # 위 전략이 실패하면 재시도 로직 사용
        # task 필터 없이 먼저 검색 시도 (모든 데이터셋 검색 가능)
        search_params = {
            "search": query_clean,
            "limit": max_results,
        }
        
        # 재시도 로직 (최대 3번)
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # task 필터 없이 검색 (모든 데이터셋 검색 가능)
                datasets = api.list_datasets(**search_params)
                
                results = []
                for dataset in datasets:
                    # 검색어가 데이터셋 ID나 설명에 포함되어 있는지 확인
                    dataset_id_lower = dataset.id.lower()
                    if query_clean.lower() in dataset_id_lower:
                        results.append({
                            "id": dataset.id,
                            "author": dataset.author,
                            "downloads": getattr(dataset, 'downloads', 0),
                            "likes": getattr(dataset, 'likes', 0),
                        })
                
                # 결과가 있으면 반환
                if results:
                    return results
                
                # 결과가 없을 때: task 필터를 추가해서 재시도 (task가 지정된 경우만)
                if not results and task and attempt == 0:
                    try:
                        search_params_with_task = {
                            "search": query_clean,
                            "limit": max_results,
                            "task": task
                        }
                        datasets_with_task = api.list_datasets(**search_params_with_task)
                        for dataset in datasets_with_task:
                            if query_clean.lower() in dataset.id.lower():
                                results.append({
                                    "id": dataset.id,
                                    "author": dataset.author,
                                    "downloads": getattr(dataset, 'downloads', 0),
                                    "likes": getattr(dataset, 'likes', 0),
                                })
                        if results:
                            return results
                    except Exception:
                        pass
                
                # 결과가 없고 마지막 시도면 폴백 또는 빈 결과 반환
                if attempt == max_retries - 1:
                    if fallback_on_error:
                        # 검색어가 미리 정의된 데이터셋과 일치하는지 확인
                        predefined = get_predefined_datasets(task)
                        filtered = [
                            d for d in predefined 
                            if query_clean.lower() in d["id"].lower() or query_clean.lower() in str(d.get("author", "")).lower()
                        ]
                        return filtered if filtered else []
                    return []
                
                # 재시도 전 대기
                time.sleep(retry_delay * (attempt + 1))
                
            except Exception as retry_error:
                if attempt == max_retries - 1:
                    # 마지막 시도 실패 시 폴백 또는 예외 발생
                    if fallback_on_error:
                        predefined = get_predefined_datasets(task)
                        filtered = [
                            d for d in predefined 
                            if query_clean.lower() in d["id"].lower() or query_clean.lower() in str(d.get("author", "")).lower()
                        ]
                        return filtered if filtered else []
                    raise Exception(f"데이터셋 검색 실패 (재시도 {max_retries}회 후): {retry_error}")
                time.sleep(retry_delay * (attempt + 1))
        
        return []
    
    except ImportError:
        if fallback_on_error:
            return get_predefined_datasets(task)
        raise ImportError("huggingface_hub가 설치되어 있지 않습니다. pip install huggingface_hub 실행하세요.")
    except Exception as e:
        if fallback_on_error:
            # API 실패 시 검색어가 포함된 미리 정의된 데이터셋 필터링하여 반환
            predefined = get_predefined_datasets(task)
            filtered = [
                d for d in predefined 
                if query.lower() in d["id"].lower() or query.lower() in str(d.get("author", "")).lower()
            ]
            return filtered if filtered else []
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
        
        # 재시도 로직 (최대 2번)
        max_retries = 2
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
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
                
                # 결과가 있으면 반환
                if results:
                    return results
                
                # 결과가 없고 마지막 시도면 폴백
                if attempt == max_retries - 1:
                    return get_predefined_datasets(task)
                
                # 재시도 전 대기
                time.sleep(retry_delay * (attempt + 1))
                
            except Exception as retry_error:
                if attempt == max_retries - 1:
                    # 마지막 시도 실패 시 폴백
                    return get_predefined_datasets(task)
                time.sleep(retry_delay * (attempt + 1))
        
        return get_predefined_datasets(task)
    
    except ImportError:
        return get_predefined_datasets(task)
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
        # 추가 유명 이미지 데이터셋
        {"id": "oxford-iiit-pet", "author": "oxford-iiit-pet", "downloads": 70000, "likes": 180, "task": "image-classification"},
        {"id": "oxford_flowers102", "author": "oxford_flowers102", "downloads": 60000, "likes": 150, "task": "image-classification"},
        {"id": "stanford-cars", "author": "stanford-cars", "downloads": 80000, "likes": 200, "task": "image-classification"},
        {"id": "stl10", "author": "stl10", "downloads": 90000, "likes": 220, "task": "image-classification"},
        {"id": "svhn", "author": "svhn", "downloads": 120000, "likes": 300, "task": "image-classification"},
        {"id": "celeba", "author": "celeba", "downloads": 150000, "likes": 400, "task": "image-classification"},
        {"id": "places365", "author": "places365", "downloads": 180000, "likes": 450, "task": "image-classification"},
        {"id": "sun397", "author": "sun397", "downloads": 100000, "likes": 250, "task": "image-classification"},
        {"id": "inat2021", "author": "inat2021", "downloads": 200000, "likes": 500, "task": "image-classification"},
        {"id": "coco", "author": "coco", "downloads": 800000, "likes": 2000, "task": "object-detection"},
        {"id": "openimages", "author": "openimages", "downloads": 600000, "likes": 1500, "task": "object-detection"},
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
        # 추가 유명 텍스트 데이터셋
        {"id": "nyu-mll/glue", "author": "nyu-mll", "downloads": 800000, "likes": 2000, "task": "text-classification"},
        {"id": "super_glue", "author": "super_glue", "downloads": 400000, "likes": 1000, "task": "text-classification"},
        {"id": "squad_v2", "author": "squad_v2", "downloads": 500000, "likes": 1200, "task": "question-answering"},
        {"id": "wikitext", "author": "wikitext", "downloads": 300000, "likes": 800, "task": "language-modeling"},
        {"id": "wikitext-2", "author": "wikitext-2", "downloads": 250000, "likes": 600, "task": "language-modeling"},
        {"id": "wikitext-103", "author": "wikitext-103", "downloads": 200000, "likes": 500, "task": "language-modeling"},
        {"id": "bookcorpus", "author": "bookcorpus", "downloads": 400000, "likes": 1000, "task": "language-modeling"},
        {"id": "common_crawl", "author": "common_crawl", "downloads": 500000, "likes": 1200, "task": "language-modeling"},
        {"id": "openwebtext", "author": "openwebtext", "downloads": 350000, "likes": 900, "task": "language-modeling"},
        {"id": "rotten_tomatoes", "author": "rotten_tomatoes", "downloads": 150000, "likes": 400, "task": "text-classification"},
        {"id": "reuters", "author": "reuters", "downloads": 180000, "likes": 450, "task": "text-classification"},
        {"id": "20newsgroups", "author": "20newsgroups", "downloads": 200000, "likes": 500, "task": "text-classification"},
        {"id": "tweet_eval", "author": "tweet_eval", "downloads": 250000, "likes": 600, "task": "text-classification"},
        {"id": "emotion", "author": "emotion", "downloads": 300000, "likes": 700, "task": "text-classification"},
        {"id": "sentiment140", "author": "sentiment140", "downloads": 280000, "likes": 650, "task": "text-classification"},
        {"id": "multi_nli", "author": "multi_nli", "downloads": 400000, "likes": 900, "task": "natural-language-inference"},
        {"id": "snli", "author": "snli", "downloads": 350000, "likes": 800, "task": "natural-language-inference"},
        {"id": "quora", "author": "quora", "downloads": 300000, "likes": 700, "task": "text-classification"},
        {"id": "dbpedia_14", "author": "dbpedia_14", "downloads": 200000, "likes": 500, "task": "text-classification"},
        {"id": "yahoo_answers_topics", "author": "yahoo_answers_topics", "downloads": 150000, "likes": 400, "task": "text-classification"},
    ]
    
    if task == "image-classification" or task is None:
        return image_datasets
    elif task == "text-classification":
        return text_datasets
    else:
        return image_datasets + text_datasets

