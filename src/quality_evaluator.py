"""
라벨링 기반 품질 평가 모듈
제공된 기준표에 따른 품질 지표 계산 (mAP, IOU, F1, Kappa, ROUGE, BLEU, CER 등)
"""
import numpy as np
from typing import List, Dict, Optional, Union
from collections import Counter

# 선택적 의존성 (없으면 경고만 출력)
try:
    from sklearn.metrics import cohen_kappa_score, f1_score, accuracy_score
    from sklearn.metrics import classification_report
    _sklearn_available = True
except ImportError:
    _sklearn_available = False
    print("⚠️ scikit-learn이 설치되지 않았습니다. 일부 기능이 제한됩니다.")

try:
    from rouge_score import rouge_scorer
    _rouge_available = True
except ImportError:
    _rouge_available = False
    print("⚠️ rouge-score가 설치되지 않았습니다. ROUGE 점수를 계산할 수 없습니다.")

try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    _bleu_available = True
except ImportError:
    _bleu_available = False
    print("⚠️ nltk가 설치되지 않았습니다. BLEU 점수를 계산할 수 없습니다.")

try:
    import jiwer
    _cer_available = True
except ImportError:
    _cer_available = False
    print("⚠️ jiwer가 설치되지 않았습니다. CER 점수를 계산할 수 없습니다.")


# 품질 임계값 설정 (기본값)
DEFAULT_THRESHOLDS = {
    "semantic_accuracy": {
        "f1_score": {"threshold": 0.9, "metric": "F1-Score"},
        "iou": {"threshold": 0.7, "metric": "IOU"},
        "map": {"threshold": 0.7, "metric": "mAP"}
    },
    "consistency": {
        "kappa": {"threshold": 0.8, "metric": "Cohen's Kappa"},
        "irr": {"threshold": 0.8, "metric": "IRR"}
    },
    "completeness": {
        "missing_rate": {"threshold": 0.0, "metric": "MissingRate"},
        "null_rate": {"threshold": 0.05, "metric": "NullRate"}
    },
    "validity": {
        "f1_model": {"threshold": 0.8, "metric": "F1-Score"},
        "rouge": {"threshold": 0.5, "metric": "ROUGE-1"},
        "bleu": {"threshold": 0.5, "metric": "BLEU"},
        "cer": {"threshold": 0.1, "metric": "CER"}
    },
    "diversity": {
        "category_variance": {"threshold": 0.1, "metric": "Variance"},
        "entropy": {"threshold": 0.0, "metric": "Entropy"}
    },
    "safety": {
        "toxicity_rate": {"threshold": 0.0, "metric": "ToxicityRate"}
    }
}


def evaluate_semantic_accuracy(
    predictions: List[Union[str, int]],
    ground_truth: List[Union[str, int]],
    task_type: str = "classification"
) -> Dict:
    """
    의미 정확성 평가: mAP, IOU, F1-Score
    
    Args:
        predictions: 예측 라벨 리스트
        ground_truth: 실제 라벨 리스트
        task_type: 작업 타입 ("classification", "detection", "segmentation")
        
    Returns:
        dict: 정확성 지표 딕셔너리
    """
    if not _sklearn_available:
        return {
            "f1_score": None,
            "accuracy": None,
            "iou": None,
            "map": None,
            "error": "scikit-learn이 설치되지 않았습니다."
        }
    
    if len(predictions) != len(ground_truth):
        return {
            "error": f"예측과 실제 라벨의 개수가 일치하지 않습니다. (예측: {len(predictions)}, 실제: {len(ground_truth)})"
        }
    
    results = {}
    
    # F1-Score 및 Accuracy 계산
    if task_type == "classification":
        # 분류 작업
        try:
            f1 = f1_score(ground_truth, predictions, average='weighted')
            accuracy = accuracy_score(ground_truth, predictions)
            results["f1_score"] = round(float(f1), 3)
            results["accuracy"] = round(float(accuracy), 3)
        except Exception as e:
            results["f1_score"] = None
            results["accuracy"] = None
            results["error"] = str(e)
    
    # IOU 계산 (객체 탐지/세그멘테이션용)
    if task_type in ["detection", "segmentation"]:
        iou = calculate_iou(predictions, ground_truth)
        results["iou"] = round(float(iou), 3) if iou is not None else None
    
    # mAP 계산 (객체 탐지용)
    if task_type == "detection":
        map_score = calculate_map(predictions, ground_truth)
        results["map"] = round(float(map_score), 3) if map_score is not None else None
    
    return results


def calculate_iou(predictions: List, ground_truth: List) -> Optional[float]:
    """
    IOU (Intersection over Union) 계산
    간단한 버전: 바운딩 박스가 아닌 경우 클래스 일치율로 계산
    """
    if len(predictions) != len(ground_truth):
        return None
    
    matches = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    total = len(predictions)
    
    if total == 0:
        return None
    
    return matches / total


def calculate_map(predictions: List, ground_truth: List) -> Optional[float]:
    """
    mAP (mean Average Precision) 계산
    간단한 버전: 평균 정밀도로 근사
    """
    if not _sklearn_available:
        return None
    
    try:
        from sklearn.metrics import average_precision_score
        
        # 이진 분류로 변환 (간단한 버전)
        unique_labels = sorted(set(ground_truth))
        if len(unique_labels) == 2:
            # 이진 분류
            y_true_binary = [1 if label == unique_labels[1] else 0 for label in ground_truth]
            y_pred_binary = [1 if label == unique_labels[1] else 0 for label in predictions]
            ap = average_precision_score(y_true_binary, y_pred_binary)
            return float(ap)
        else:
            # 다중 분류: 각 클래스별 AP의 평균
            aps = []
            for label in unique_labels:
                y_true_binary = [1 if l == label else 0 for l in ground_truth]
                y_pred_binary = [1 if l == label else 0 for l in predictions]
                try:
                    ap = average_precision_score(y_true_binary, y_pred_binary)
                    aps.append(ap)
                except:
                    pass
            return float(np.mean(aps)) if aps else None
    except Exception:
        return None


def evaluate_consistency(
    labels_by_raters: List[List[Union[str, int]]],
    rater_names: Optional[List[str]] = None
) -> Dict:
    """
    일관성 평가: Cohen's Kappa, IRR
    
    Args:
        labels_by_raters: 평가자별 라벨 리스트 [[rater1_labels], [rater2_labels], ...]
        rater_names: 평가자 이름 리스트 (선택적)
        
    Returns:
        dict: 일관성 지표 딕셔너리
    """
    if not _sklearn_available:
        return {
            "kappa": None,
            "irr": None,
            "error": "scikit-learn이 설치되지 않았습니다."
        }
    
    if len(labels_by_raters) < 2:
        return {
            "error": "일관성 평가를 위해서는 최소 2명의 평가자가 필요합니다."
        }
    
    # 모든 평가자의 라벨 개수가 동일한지 확인
    num_items = len(labels_by_raters[0])
    if not all(len(labels) == num_items for labels in labels_by_raters):
        return {
            "error": "모든 평가자의 라벨 개수가 일치해야 합니다."
        }
    
    results = {}
    
    # Cohen's Kappa 계산 (평가자 쌍별)
    kappas = []
    for i in range(len(labels_by_raters)):
        for j in range(i + 1, len(labels_by_raters)):
            try:
                kappa = cohen_kappa_score(labels_by_raters[i], labels_by_raters[j])
                kappas.append(kappa)
            except Exception as e:
                pass
    
    if kappas:
        results["kappa"] = round(float(np.mean(kappas)), 3)
        results["kappa_pairs"] = len(kappas)
    else:
        results["kappa"] = None
    
    # IRR (Inter-Rater Reliability) - 간단한 버전: 일치율
    agreements = []
    for i in range(len(labels_by_raters)):
        for j in range(i + 1, len(labels_by_raters)):
            matches = sum(1 for a, b in zip(labels_by_raters[i], labels_by_raters[j]) if a == b)
            agreement = matches / num_items if num_items > 0 else 0
            agreements.append(agreement)
    
    if agreements:
        results["irr"] = round(float(np.mean(agreements)), 3)
    else:
        results["irr"] = None
    
    return results


def evaluate_completeness(
    dataset: List[Dict],
    required_fields: List[str],
    optional_fields: List[str] = None
) -> Dict:
    """
    완전성 평가: MissingRate, NullRate
    
    Args:
        dataset: 데이터셋 리스트 (각 항목은 딕셔너리)
        required_fields: 필수 필드 리스트
        optional_fields: 비필수 필드 리스트
        
    Returns:
        dict: 완전성 지표 딕셔너리
    """
    if not dataset:
        return {
            "missing_rate": 1.0,
            "null_rate": 1.0,
            "error": "데이터셋이 비어있습니다."
        }
    
    total_items = len(dataset)
    missing_count = 0
    null_count = 0
    total_optional_fields = 0
    
    for item in dataset:
        # 필수 필드 누락 검사
        for field in required_fields:
            if field not in item or item[field] is None or item[field] == "":
                missing_count += 1
                break  # 한 항목당 한 번만 카운트
        
        # 비필수 필드 결측치 검사
        if optional_fields:
            for field in optional_fields:
                if field in item:
                    total_optional_fields += 1
                    if item[field] is None or item[field] == "":
                        null_count += 1
    
    missing_rate = missing_count / total_items if total_items > 0 else 1.0
    null_rate = null_count / total_optional_fields if total_optional_fields > 0 else 0.0
    
    return {
        "missing_rate": round(float(missing_rate), 3),
        "null_rate": round(float(null_rate), 3),
        "missing_count": missing_count,
        "null_count": null_count,
        "total_items": total_items
    }


def evaluate_validity(
    model_predictions: List[str],
    ground_truth: List[str],
    task_type: str = "generation"
) -> Dict:
    """
    유효성 평가: F1, ROUGE, BLEU, CER
    
    Args:
        model_predictions: 모델 예측 결과 리스트
        ground_truth: 실제 정답 리스트
        task_type: 작업 타입 ("generation", "classification", "qa")
        
    Returns:
        dict: 유효성 지표 딕셔너리
    """
    if len(model_predictions) != len(ground_truth):
        return {
            "error": f"예측과 실제 정답의 개수가 일치하지 않습니다. (예측: {len(model_predictions)}, 실제: {len(ground_truth)})"
        }
    
    results = {}
    
    # F1-Score (분류 작업용)
    if task_type == "classification" and _sklearn_available:
        try:
            f1 = f1_score(ground_truth, model_predictions, average='weighted')
            results["f1_model"] = round(float(f1), 3)
        except:
            results["f1_model"] = None
    
    # ROUGE 점수 (생성 작업용)
    if task_type in ["generation", "qa"] and _rouge_available:
        rouge_scores = calculate_rouge(model_predictions, ground_truth)
        results.update(rouge_scores)
    
    # BLEU 점수 (생성 작업용)
    if task_type in ["generation", "qa"] and _bleu_available:
        bleu_scores = calculate_bleu(model_predictions, ground_truth)
        results.update(bleu_scores)
    
    # CER (Character Error Rate) - 생성 작업용
    if task_type in ["generation", "qa"] and _cer_available:
        cer_scores = calculate_cer(model_predictions, ground_truth)
        results.update(cer_scores)
    
    return results


def calculate_rouge(predictions: List[str], ground_truth: List[str]) -> Dict:
    """ROUGE 점수 계산"""
    if not _rouge_available:
        return {"rouge_1": None, "rouge_2": None, "rouge_l": None}
    
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge_1_scores = []
        rouge_2_scores = []
        rouge_l_scores = []
        
        for pred, ref in zip(predictions, ground_truth):
            scores = scorer.score(ref, pred)
            rouge_1_scores.append(scores['rouge1'].fmeasure)
            rouge_2_scores.append(scores['rouge2'].fmeasure)
            rouge_l_scores.append(scores['rougeL'].fmeasure)
        
        return {
            "rouge_1": round(float(np.mean(rouge_1_scores)), 3),
            "rouge_2": round(float(np.mean(rouge_2_scores)), 3),
            "rouge_l": round(float(np.mean(rouge_l_scores)), 3)
        }
    except Exception as e:
        return {"rouge_1": None, "rouge_2": None, "rouge_l": None, "error": str(e)}


def calculate_bleu(predictions: List[str], ground_truth: List[str]) -> Dict:
    """BLEU 점수 계산"""
    if not _bleu_available:
        return {"bleu": None}
    
    try:
        smooth = SmoothingFunction().method1
        bleu_scores = []
        
        for pred, ref in zip(predictions, ground_truth):
            try:
                ref_tokens = word_tokenize(ref.lower())
                pred_tokens = word_tokenize(pred.lower())
                bleu = sentence_bleu([ref_tokens], pred_tokens, smoothing_function=smooth)
                bleu_scores.append(bleu)
            except:
                pass
        
        return {
            "bleu": round(float(np.mean(bleu_scores)), 3) if bleu_scores else None
        }
    except Exception as e:
        return {"bleu": None, "error": str(e)}


def calculate_cer(predictions: List[str], ground_truth: List[str]) -> Dict:
    """CER (Character Error Rate) 계산"""
    if not _cer_available:
        return {"cer": None}
    
    try:
        cer_scores = []
        for pred, ref in zip(predictions, ground_truth):
            try:
                cer = jiwer.cer(ref, pred)
                cer_scores.append(cer)
            except:
                pass
        
        return {
            "cer": round(float(np.mean(cer_scores)), 3) if cer_scores else None
        }
    except Exception as e:
        return {"cer": None, "error": str(e)}


def evaluate_diversity(labels: List[Union[str, int]]) -> Dict:
    """
    다양성 평가: CategoryVariance, Entropy
    
    Args:
        labels: 라벨 리스트
        
    Returns:
        dict: 다양성 지표 딕셔너리
    """
    if not labels:
        return {
            "category_variance": None,
            "entropy": None,
            "error": "라벨이 없습니다."
        }
    
    label_counts = Counter(labels)
    total = len(labels)
    num_categories = len(label_counts)
    
    # Category Variance 계산 (분포의 분산)
    proportions = [count / total for count in label_counts.values()]
    variance = np.var(proportions)
    
    # Entropy 계산
    entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in proportions)
    max_entropy = np.log2(num_categories) if num_categories > 0 else 0
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    return {
        "category_variance": round(float(variance), 3),
        "entropy": round(float(entropy), 3),
        "normalized_entropy": round(float(normalized_entropy), 3),
        "num_categories": num_categories,
        "total_items": total
    }


def evaluate_safety(data: List[str], toxic_keywords: Optional[List[str]] = None) -> Dict:
    """
    안전성 평가: 유해 표현 검출
    
    Args:
        data: 텍스트 데이터 리스트
        toxic_keywords: 유해 키워드 리스트 (없으면 기본 목록 사용)
        
    Returns:
        dict: 안전성 지표 딕셔너리
    """
    if toxic_keywords is None:
        # 기본 유해 키워드 목록 (간단한 버전)
        toxic_keywords = [
            "개새끼", "병신", "미친", "쓰레기", "죽어", "시발", "좆",
            "fuck", "shit", "damn", "bitch", "asshole"
        ]
    
    toxic_count = 0
    total_items = len(data)
    
    for text in data:
        text_lower = text.lower()
        for keyword in toxic_keywords:
            if keyword.lower() in text_lower:
                toxic_count += 1
                break  # 한 항목당 한 번만 카운트
    
    toxicity_rate = toxic_count / total_items if total_items > 0 else 0.0
    
    return {
        "toxicity_rate": round(float(toxicity_rate), 3),
        "toxic_count": toxic_count,
        "total_items": total_items
    }


def evaluate_quality_with_thresholds(
    quality_results: Dict,
    thresholds: Optional[Dict] = None
) -> Dict:
    """
    임계값 기반 품질 평가
    
    Args:
        quality_results: 품질 지표 결과 딕셔너리
        thresholds: 임계값 딕셔너리 (없으면 기본값 사용)
        
    Returns:
        dict: 평가 결과 (값, 임계값, PASS/FAIL 상태 포함)
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
    
    evaluated_results = {}
    
    for category, metrics in quality_results.items():
        evaluated_results[category] = {}
        category_thresholds = thresholds.get(category, {})
        
        for metric_name, value in metrics.items():
            if value is None:
                evaluated_results[category][metric_name] = {
                    "value": None,
                    "threshold": None,
                    "status": "N/A",
                    "error": "계산 불가"
                }
                continue
            
            # 임계값 찾기
            threshold_config = category_thresholds.get(metric_name, {})
            threshold = threshold_config.get("threshold", 0.0)
            metric_display = threshold_config.get("metric", metric_name)
            
            # PASS/FAIL 판정
            # 일부 지표는 낮을수록 좋음 (CER, MissingRate, NullRate, ToxicityRate)
            if metric_name in ["cer", "missing_rate", "null_rate", "toxicity_rate"]:
                status = "PASS ✅" if value <= threshold else "FAIL ❌"
            else:
                status = "PASS ✅" if value >= threshold else "FAIL ❌"
            
            evaluated_results[category][metric_name] = {
                "value": value,
                "threshold": threshold,
                "status": status,
                "metric_display": metric_display
            }
    
    return evaluated_results

