"""
Model evaluation metrics endpoint.
Serves pre-computed evaluation results for the dashboard.
"""
import os
import json
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["evaluation"])

EVAL_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "evaluation_results",
    "evaluation_summary.json"
)


@router.get("/models/comparison")
def get_model_comparison():
    """Return evaluation metrics for all platform models."""
    if not os.path.exists(EVAL_FILE):
        return {
            "available": False,
            "message": "Run evaluate_models.py to generate metrics",
            "data": {}
        }

    with open(EVAL_FILE, "r") as f:
        data = json.load(f)

    return {
        "available": True,
        "data": data,
    }
