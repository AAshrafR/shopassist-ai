"""
MLflow experiment tracking for ShopAssist AI.
Tracks RAG pipeline configuration parameters, retrieval metrics, and run artifacts.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, Optional
import mlflow

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "mlflow.db"


class MLflowTracker:
    def __init__(self, experiment_name: str = "shopassist-rag-eval"):
        self.experiment_name = experiment_name
        mlflow.set_tracking_uri(f"sqlite:///{DB_PATH.resolve()}")
        mlflow.set_experiment(experiment_name)

    def log_evaluation_run(
        self,
        run_name: str,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        artifacts: Optional[Dict[str, str]] = None
    ):
        """Logs an evaluation run with hyperparams, metrics, and text artifacts."""
        with mlflow.start_run(run_name=run_name) as run:
            # Log params
            for k, v in params.items():
                mlflow.log_param(k, str(v))

            # Log metrics
            for k, v in metrics.items():
                mlflow.log_metric(k, float(v))

            # Log artifacts
            if artifacts:
                for filename, content in artifacts.items():
                    temp_path = BASE_DIR / "data" / "processed" / filename
                    temp_path.write_text(content, encoding="utf-8")
                    mlflow.log_artifact(str(temp_path))

            print(f"Logged run '{run_name}' to MLflow (ID: {run.info.run_id})")
            return run.info.run_id
