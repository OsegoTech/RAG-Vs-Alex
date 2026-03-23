import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self, metrics_file: str = "metrics.json"):
        self.metrics_file = os.path.join(os.path.dirname(__file__), '..', metrics_file)
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> List[Dict[str, Any]]:
        """Load metrics from file."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metrics: {e}")
                return []
        return []

    def _save_metrics(self):
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

    def record_query(self, query: str, response_time: float, num_sources: int,
                    num_documents: int, num_errors: int, success: bool):
        """Record a query's metrics."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_time": response_time,
            "num_sources": num_sources,
            "num_documents": num_documents,
            "num_errors": num_errors,
            "success": success
        }

        self.metrics.append(metric)
        self._save_metrics()
        logger.info(f"Recorded metrics for query: {query[:50]}...")

    def get_metrics(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get metrics filtered by date range."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)  # Default to last 7 days
        if end_date is None:
            end_date = datetime.now()

        filtered_metrics = []
        for metric in self.metrics:
            metric_time = datetime.fromisoformat(metric["timestamp"])
            if start_date <= metric_time <= end_date:
                filtered_metrics.append(metric)

        return filtered_metrics

    def get_summary_stats(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Calculate summary statistics."""
        metrics = self.get_metrics(start_date, end_date)

        if not metrics:
            return {
                "total_queries": 0,
                "successful_queries": 0,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "avg_documents_retrieved": 0.0,
                "total_errors": 0
            }

        total_queries = len(metrics)
        successful_queries = sum(1 for m in metrics if m["success"])
        total_response_time = sum(m["response_time"] for m in metrics)
        total_documents = sum(m["num_documents"] for m in metrics)
        total_errors = sum(m["num_errors"] for m in metrics)

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "error_rate": (total_queries - successful_queries) / total_queries if total_queries > 0 else 0.0,
            "avg_response_time": total_response_time / total_queries,
            "avg_documents_retrieved": total_documents / total_queries,
            "total_errors": total_errors
        }