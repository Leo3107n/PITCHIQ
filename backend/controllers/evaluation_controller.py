"""
Evaluation Controller
Thin layer — delegates entirely to evaluation_service.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from backend.services.evaluation_service import (
    get_all_metrics,
    get_model_metrics,
    get_model_confusion_matrix,
)


def handle_all_metrics() -> dict:
    try:
        return get_all_metrics()
    except Exception as e:
        return {"error": str(e)}


def handle_model_metrics(model_name: str = "best") -> dict:
    try:
        return get_model_metrics(model_name)
    except (ValueError, FileNotFoundError) as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Evaluation failed: {e}"}


def handle_confusion_matrix(model_name: str = "best") -> dict:
    try:
        return get_model_confusion_matrix(model_name)
    except (ValueError, FileNotFoundError) as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Confusion matrix failed: {e}"}
