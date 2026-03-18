"""
DeepEvalInterface - DeepEval SDK wrapper with enhanced functionality.

Provides:
- Test case creation (LLMTestCase, ConversationalTestCase)
- Metric execution with retry logic
- Batch evaluation orchestration
- Dataset loading and creation
- Synthetic data generation
- Result analysis and formatting
- Configuration management
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from deepeval import evaluate, assert_test
from deepeval.test_case import LLMTestCase, ConversationalTestCase
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.synthesizer import Synthesizer
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ToolCorrectnessMetric,
    TaskCompletionMetric,
    KnowledgeRetentionMetric,
    RoleAdherenceMetric,
    BiasMetric,
    ToxicityMetric,
    GEval,
    HallucinationMetric,
    SummarizationMetric,
)


class DeepEvalInterface:
    """DeepEval SDK wrapper with logging, retry logic, and enhanced evaluation mechanisms."""

    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_RESULTS_DIR = "eval_results"

    def __init__(self, config: dict, logger: logging.Logger):
        """
        Initialize DeepEvalInterface.

        Args:
            config: Configuration dictionary with thresholds, retry settings, and optional overrides
            logger: Logger instance for logging operations
        """
        self.config = config
        self.logger = logger
        self.max_retries = int(config.get("max_retries", self.DEFAULT_MAX_RETRIES))
        self.retry_delay = float(config.get("retry_delay", self.DEFAULT_RETRY_DELAY))
        self.results_dir = config.get("results_dir", self.DEFAULT_RESULTS_DIR)
        self.thresholds = config.get("thresholds", {})

        os.makedirs(self.results_dir, exist_ok=True)

    # ==================== TEST CASE CREATION ====================

    def create_test_case(
        self,
        input: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        context: Optional[List[str]] = None,
        retrieval_context: Optional[List[str]] = None,
        tools_called: Optional[List[dict]] = None,
        expected_tools: Optional[List[str]] = None,
        token_cost: Optional[float] = None,
        completion_time: Optional[float] = None,
    ) -> LLMTestCase:
        """
        Create LLMTestCase with all 9 parameters.

        Args:
            input: User input / prompt
            actual_output: LLM response
            expected_output: Expected / golden response
            context: Ground truth context list
            retrieval_context: Retrieved context list from RAG pipeline
            tools_called: List of tool calls made by agent
            expected_tools: List of expected tool names
            token_cost: Token cost of the LLM call
            completion_time: Time taken to generate response

        Returns:
            LLMTestCase instance
        """
        try:
            test_case = LLMTestCase(
                input=input,
                actual_output=actual_output,
                expected_output=expected_output,
                context=context,
                retrieval_context=retrieval_context,
                tools_called=tools_called,
                expected_tools=expected_tools,
                token_cost=token_cost,
                completion_time=completion_time,
            )
            self.logger.info(f"Created LLMTestCase for input: {input[:80]}...")
            return test_case
        except Exception as e:
            self.logger.error(f"Failed to create LLMTestCase: {repr(e)}")
            raise

    def create_conversation_test_case(
        self,
        turns: List[LLMTestCase],
        chatbot_role: Optional[str] = None,
    ) -> ConversationalTestCase:
        """
        Create ConversationalTestCase from a list of turns.

        Args:
            turns: List of LLMTestCase instances representing conversation turns
            chatbot_role: Description of chatbot's intended role

        Returns:
            ConversationalTestCase instance
        """
        try:
            test_case = ConversationalTestCase(
                turns=turns,
                chatbot_role=chatbot_role,
            )
            self.logger.info(f"Created ConversationalTestCase with {len(turns)} turns")
            return test_case
        except Exception as e:
            self.logger.error(f"Failed to create ConversationalTestCase: {repr(e)}")
            raise

    def create_test_cases_from_dataset(
        self,
        dataset: List[dict],
        pipeline_fn: Callable[[str], str],
    ) -> List[LLMTestCase]:
        """
        Batch-create test cases by running a pipeline function over golden data.

        Args:
            dataset: List of golden dicts with input, expected_output, retrieval_context, context
            pipeline_fn: Callable that takes input string, returns actual_output string

        Returns:
            List of LLMTestCase instances
        """
        test_cases = []
        for i, golden in enumerate(dataset):
            try:
                actual_output = pipeline_fn(golden["input"])
                test_case = self.create_test_case(
                    input=golden["input"],
                    actual_output=actual_output,
                    expected_output=golden.get("expected_output"),
                    context=golden.get("context"),
                    retrieval_context=golden.get("retrieval_context"),
                    tools_called=golden.get("tools_called"),
                    expected_tools=golden.get("expected_tools"),
                )
                test_cases.append(test_case)
            except Exception as e:
                self.logger.error(f"Failed to create test case {i}: {repr(e)}")
                raise
        self.logger.info(f"Created {len(test_cases)} test cases from dataset")
        return test_cases

    # ==================== METRIC CREATION ====================

    def create_metric(
        self,
        metric_name: str,
        threshold: Optional[float] = None,
        **kwargs,
    ):
        """
        Create a DeepEval metric instance by name.

        Args:
            metric_name: Name of the metric class (e.g., "FaithfulnessMetric")
            threshold: Override threshold (uses config default if not provided)
            **kwargs: Additional keyword arguments for the metric constructor

        Returns:
            Metric instance

        Raises:
            ValueError: If metric_name is not recognized
        """
        metric_map = {
            "AnswerRelevancyMetric": AnswerRelevancyMetric,
            "FaithfulnessMetric": FaithfulnessMetric,
            "ContextualRelevancyMetric": ContextualRelevancyMetric,
            "ContextualPrecisionMetric": ContextualPrecisionMetric,
            "ContextualRecallMetric": ContextualRecallMetric,
            "ToolCorrectnessMetric": ToolCorrectnessMetric,
            "TaskCompletionMetric": TaskCompletionMetric,
            "KnowledgeRetentionMetric": KnowledgeRetentionMetric,
            "RoleAdherenceMetric": RoleAdherenceMetric,
            "BiasMetric": BiasMetric,
            "ToxicityMetric": ToxicityMetric,
            "HallucinationMetric": HallucinationMetric,
            "SummarizationMetric": SummarizationMetric,
        }

        if metric_name not in metric_map:
            self.logger.error(f"Unknown metric: {metric_name}")
            raise ValueError(f"Unknown metric: {metric_name}. Available: {list(metric_map.keys())}")

        resolved_threshold = threshold or self.thresholds.get(metric_name)
        metric_kwargs = {}
        if resolved_threshold is not None:
            metric_kwargs["threshold"] = resolved_threshold
        metric_kwargs.update(kwargs)

        try:
            metric = metric_map[metric_name](**metric_kwargs)
            self.logger.debug(f"Created metric: {metric_name} (threshold={resolved_threshold})")
            return metric
        except Exception as e:
            self.logger.error(f"Failed to create metric {metric_name}: {repr(e)}")
            raise

    def create_custom_metric(
        self,
        name: str,
        criteria: str,
        threshold: float = 0.6,
        evaluation_params: Optional[List] = None,
    ) -> GEval:
        """
        Create a custom GEval metric with natural language criteria.

        Args:
            name: Human-readable name for the metric
            criteria: Natural language evaluation criteria
            threshold: Pass/fail threshold
            evaluation_params: Optional list of LLMTestCaseParams to evaluate

        Returns:
            GEval metric instance
        """
        try:
            kwargs = {
                "name": name,
                "criteria": criteria,
                "threshold": threshold,
            }
            if evaluation_params:
                kwargs["evaluation_params"] = evaluation_params

            metric = GEval(**kwargs)
            self.logger.info(f"Created custom metric: {name}")
            return metric
        except Exception as e:
            self.logger.error(f"Failed to create custom metric '{name}': {repr(e)}")
            raise

    # ==================== METRIC EXECUTION ====================

    def measure_metric(self, metric, test_case) -> float:
        """
        Run a single metric against a test case with retry logic.

        Args:
            metric: DeepEval metric instance
            test_case: LLMTestCase or ConversationalTestCase

        Returns:
            Metric score as float, or None if all retries failed
        """
        metric_name = metric.__class__.__name__
        self.logger.debug(f"Measuring {metric_name}...")

        for attempt in range(self.max_retries):
            try:
                metric.measure(test_case)
                self.logger.info(
                    f"Metric {metric_name}: score={metric.score:.4f} "
                    f"(threshold={getattr(metric, 'threshold', 'N/A')})"
                )
                return metric.score
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    self.logger.warning(
                        f"Metric {metric_name} attempt {attempt + 1} failed: {repr(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"Metric {metric_name} failed after {self.max_retries} attempts: {repr(e)}"
                    )
                    return None

    def measure_metrics(
        self,
        metrics: list,
        test_case,
    ) -> Dict[str, dict]:
        """
        Run multiple metrics against a single test case.

        Args:
            metrics: List of DeepEval metric instances
            test_case: LLMTestCase or ConversationalTestCase

        Returns:
            Dict mapping metric name to {score, threshold, passed, reason}
        """
        results = {}
        for metric in metrics:
            metric_name = metric.__class__.__name__
            score = self.measure_metric(metric, test_case)
            threshold = getattr(metric, "threshold", None)
            results[metric_name] = {
                "score": score,
                "threshold": threshold,
                "passed": score is not None and threshold is not None and score >= threshold,
                "reason": getattr(metric, "reason", None),
            }
        self.logger.info(f"Measured {len(metrics)} metrics: {len([r for r in results.values() if r['passed']])} passed")
        return results

    # ==================== EVALUATION ORCHESTRATION ====================

    def run_evaluation(
        self,
        test_cases: List[LLMTestCase],
        metrics: list,
    ) -> list:
        """
        Run batch evaluation across test cases and metrics with retry logic.

        Args:
            test_cases: List of LLMTestCase instances
            metrics: List of metric instances to evaluate

        Returns:
            List of dicts, one per test case, with metric results
        """
        self.logger.info(
            f"Starting batch evaluation: {len(test_cases)} cases × {len(metrics)} metrics"
        )
        results = []
        for i, test_case in enumerate(test_cases):
            self.logger.debug(f"Evaluating test case {i + 1}/{len(test_cases)}")
            case_results = self.measure_metrics(metrics, test_case)
            results.append({"test_case": test_case, "metrics": case_results})
        self.logger.info(f"Batch evaluation complete: {len(results)} cases evaluated")
        return results

    def assert_test(self, test_case: LLMTestCase, metrics: list) -> None:
        """
        Assert single test case against metrics (pytest-compatible).

        Runs each metric with retry logic, then calls deepeval.assert_test
        which raises AssertionError on failure.

        Args:
            test_case: LLMTestCase to evaluate
            metrics: List of metric instances

        Raises:
            AssertionError: If any metric fails its threshold
        """
        self.logger.info(f"Asserting test case with {len(metrics)} metrics...")
        for metric in metrics:
            self.measure_metric(metric, test_case)
        try:
            assert_test(test_case, metrics)
            self.logger.info("assert_test PASSED")
        except AssertionError as e:
            self.logger.error(f"assert_test FAILED: {repr(e)}")
            self._save_failure_report(test_case, metrics, str(e))
            raise

    def evaluate_batch(
        self,
        test_cases: List[LLMTestCase],
        metrics: list,
    ) -> Any:
        """
        Run deepeval.evaluate() for batch evaluation with built-in reporting.

        This uses DeepEval's native evaluate() function which provides
        richer output and integrates with Confident AI dashboard.

        Args:
            test_cases: List of LLMTestCase instances
            metrics: List of metric instances

        Returns:
            DeepEval evaluation result object
        """
        self.logger.info(
            f"Running deepeval.evaluate(): {len(test_cases)} cases × {len(metrics)} metrics"
        )
        try:
            result = evaluate(test_cases, metrics)
            self.logger.info("deepeval.evaluate() complete")
            return result
        except Exception as e:
            self.logger.error(f"deepeval.evaluate() failed: {repr(e)}")
            raise

    # ==================== DATASET MANAGEMENT ====================

    def load_dataset(self, path: str) -> EvaluationDataset:
        """
        Load golden dataset from JSON file.

        Expected format: list of dicts with keys matching LLMTestCase params
        (input, expected_output, context, retrieval_context, etc.)

        Args:
            path: Path to JSON file

        Returns:
            EvaluationDataset instance

        Raises:
            FileNotFoundError: If path does not exist
            json.JSONDecodeError: If file is not valid JSON
        """
        self.logger.info(f"Loading dataset from: {path}")

        try:
            with open(path, "r") as f:
                data = json.load(f)

            goldens = []
            for entry in data:
                goldens.append(
                    Golden(
                        input=entry["input"],
                        expected_output=entry.get("expected_output"),
                        context=entry.get("context"),
                        retrieval_context=entry.get("retrieval_context"),
                    )
                )

            dataset = EvaluationDataset(goldens=goldens)
            self.logger.info(f"Loaded dataset: {len(goldens)} goldens from {path}")
            return dataset
        except FileNotFoundError:
            self.logger.error(f"Dataset file not found: {path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in dataset file {path}: {repr(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load dataset from {path}: {repr(e)}")
            raise

    def load_dataset_as_dicts(self, path: str) -> List[dict]:
        """
        Load golden dataset as raw dicts (for parametrize/fixture use).

        Args:
            path: Path to JSON file

        Returns:
            List of golden dicts
        """
        self.logger.info(f"Loading dataset as dicts from: {path}")

        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.logger.info(f"Loaded {len(data)} entries from {path}")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load dataset from {path}: {repr(e)}")
            raise

    def create_dataset(self, goldens: List[Golden]) -> EvaluationDataset:
        """
        Create EvaluationDataset from list of Golden objects.

        Args:
            goldens: List of Golden instances

        Returns:
            EvaluationDataset instance
        """
        try:
            dataset = EvaluationDataset(goldens=goldens)
            self.logger.info(f"Created dataset with {len(goldens)} goldens")
            return dataset
        except Exception as e:
            self.logger.error(f"Failed to create dataset: {repr(e)}")
            raise

    def create_golden(
        self,
        input: str,
        expected_output: Optional[str] = None,
        context: Optional[List[str]] = None,
        retrieval_context: Optional[List[str]] = None,
    ) -> Golden:
        """
        Create a single Golden instance.

        Args:
            input: Input prompt
            expected_output: Expected response
            context: Ground truth context
            retrieval_context: Retrieved context

        Returns:
            Golden instance
        """
        try:
            golden = Golden(
                input=input,
                expected_output=expected_output,
                context=context,
                retrieval_context=retrieval_context,
            )
            self.logger.debug(f"Created Golden for input: {input[:60]}...")
            return golden
        except Exception as e:
            self.logger.error(f"Failed to create Golden: {repr(e)}")
            raise

    # ==================== SYNTHETIC DATA GENERATION ====================

    def generate_synthetic_dataset(
        self,
        documents: List[str],
        max_goldens_per_document: int = 25,
    ) -> EvaluationDataset:
        """
        Generate synthetic golden dataset from source documents.

        Uses DeepEval's Synthesizer to create test data from documents.

        Args:
            documents: List of document strings
            max_goldens_per_document: Max goldens to generate per document

        Returns:
            EvaluationDataset with synthetic goldens
        """
        self.logger.info(
            f"Generating synthetic dataset from {len(documents)} documents "
            f"(max {max_goldens_per_document} per doc)"
        )

        try:
            synthesizer = Synthesizer()
            dataset = synthesizer.generate_goldens_from_docs(
                documents=documents,
                max_goldens_per_document=max_goldens_per_document,
            )
            self.logger.info(f"Generated synthetic dataset with {len(dataset.goldens)} goldens")
            return dataset
        except Exception as e:
            self.logger.error(f"Synthetic generation failed: {repr(e)}")
            raise

    def generate_goldens_from_contexts(
        self,
        contexts: List[List[str]],
        max_goldens_per_context: int = 2,
    ) -> EvaluationDataset:
        """
        Generate synthetic goldens from context lists.

        Args:
            contexts: List of context string lists
            max_goldens_per_context: Max goldens per context

        Returns:
            EvaluationDataset with synthetic goldens
        """
        self.logger.info(f"Generating goldens from {len(contexts)} context sets")

        try:
            synthesizer = Synthesizer()
            dataset = synthesizer.generate_goldens(
                contexts=contexts,
                max_goldens_per_context=max_goldens_per_context,
            )
            self.logger.info(f"Generated {len(dataset.goldens)} goldens from contexts")
            return dataset
        except Exception as e:
            self.logger.error(f"Context-based generation failed: {repr(e)}")
            raise

    # ==================== RESULT ANALYSIS ====================

    def get_metric_score(self, metric) -> Optional[float]:
        """
        Get score from an already-measured metric.

        Args:
            metric: Metric instance that has been measured

        Returns:
            Score as float, or None if not yet measured
        """
        score = getattr(metric, "score", None)
        self.logger.debug(f"{metric.__class__.__name__} score: {score}")
        return score

    def get_metric_reason(self, metric) -> Optional[str]:
        """
        Get reason/explanation from an already-measured metric.

        Args:
            metric: Metric instance that has been measured

        Returns:
            Reason string, or None if not available
        """
        reason = getattr(metric, "reason", None)
        self.logger.debug(f"{metric.__class__.__name__} reason: {reason}")
        return reason

    def is_metric_passing(self, metric) -> bool:
        """
        Check if a measured metric passes its threshold.

        Args:
            metric: Metric instance that has been measured

        Returns:
            True if score >= threshold
        """
        score = getattr(metric, "score", None)
        threshold = getattr(metric, "threshold", None)
        if score is None or threshold is None:
            return False
        return score >= threshold

    def format_results(self, evaluation_results: list) -> str:
        """
        Format evaluation results as a human-readable report.

        Args:
            evaluation_results: Output from run_evaluation()

        Returns:
            Formatted string report
        """
        lines = ["=" * 60, "EVALUATION RESULTS", "=" * 60]

        for i, result in enumerate(evaluation_results):
            test_case = result["test_case"]
            lines.append(f"\nTest Case {i + 1}: {test_case.input[:60]}...")
            lines.append("-" * 40)
            for metric_name, data in result["metrics"].items():
                status = "PASS" if data["passed"] else "FAIL"
                score_str = f"{data['score']:.4f}" if data["score"] is not None else "N/A"
                thresh_str = f"{data['threshold']:.4f}" if data["threshold"] is not None else "N/A"
                lines.append(f"  [{status}] {metric_name}: {score_str} (threshold: {thresh_str})")
                if data.get("reason"):
                    lines.append(f"         Reason: {data['reason'][:100]}")

        lines.append("\n" + "=" * 60)
        total = sum(len(r["metrics"]) for r in evaluation_results)
        passed = sum(
            1 for r in evaluation_results
            for m in r["metrics"].values()
            if m["passed"]
        )
        lines.append(f"Total: {passed}/{total} metrics passed")
        lines.append("=" * 60)

        report = "\n".join(lines)
        self.logger.info(f"Formatted results: {passed}/{total} passed")
        return report

    def summarize_results(self, evaluation_results: list) -> dict:
        """
        Summarize evaluation results as a structured dict.

        Args:
            evaluation_results: Output from run_evaluation()

        Returns:
            Dict with total, passed, failed, pass_rate, and per-metric breakdown
        """
        total = 0
        passed = 0
        per_metric = {}

        for result in evaluation_results:
            for metric_name, data in result["metrics"].items():
                total += 1
                if data["passed"]:
                    passed += 1
                if metric_name not in per_metric:
                    per_metric[metric_name] = {"total": 0, "passed": 0, "scores": []}
                per_metric[metric_name]["total"] += 1
                if data["passed"]:
                    per_metric[metric_name]["passed"] += 1
                if data["score"] is not None:
                    per_metric[metric_name]["scores"].append(data["score"])

        for metric_name in per_metric:
            scores = per_metric[metric_name]["scores"]
            per_metric[metric_name]["avg_score"] = (
                sum(scores) / len(scores) if scores else 0.0
            )

        summary = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "per_metric": per_metric,
        }
        self.logger.info(f"Summary: {passed}/{total} passed ({summary['pass_rate']:.1%})")
        return summary

    # ==================== RESULT PERSISTENCE ====================

    def save_results(self, results: list, filename: str) -> str:
        """
        Save evaluation results to JSON file.

        Args:
            results: Output from run_evaluation()
            filename: Output filename (without extension)

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.results_dir, f"{filename}_{timestamp}.json")

        try:
            serializable = []
            for result in results:
                entry = {
                    "input": result["test_case"].input,
                    "actual_output": result["test_case"].actual_output,
                    "metrics": result["metrics"],
                }
                serializable.append(entry)

            with open(filepath, "w") as f:
                json.dump(serializable, f, indent=2, default=str)

            self.logger.info(f"Results saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save results to {filepath}: {repr(e)}")
            raise

    def _save_failure_report(
        self,
        test_case: LLMTestCase,
        metrics: list,
        error_msg: str,
    ) -> Optional[str]:
        """
        Internal method to save failure report on assert_test failure.

        Args:
            test_case: The failing test case
            metrics: Metrics that were evaluated
            error_msg: Error message from the assertion

        Returns:
            Path to saved report or None if save fails
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.results_dir, f"failure_{timestamp}.json")
            report = {
                "timestamp": timestamp,
                "input": test_case.input,
                "actual_output": test_case.actual_output,
                "expected_output": test_case.expected_output,
                "error": error_msg,
                "metrics": {
                    m.__class__.__name__: {
                        "score": getattr(m, "score", None),
                        "threshold": getattr(m, "threshold", None),
                        "reason": getattr(m, "reason", None),
                    }
                    for m in metrics
                },
            }
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Failure report saved: {filepath}")
            return filepath
        except Exception:
            return None

    # ==================== CONFIGURATION ====================

    def get_threshold(self, metric_name: str) -> Optional[float]:
        """
        Get configured threshold for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Threshold value or None if not configured
        """
        return self.thresholds.get(metric_name)

    def update_threshold(self, metric_name: str, threshold: float) -> None:
        """
        Update threshold for a metric at runtime.

        Args:
            metric_name: Name of the metric
            threshold: New threshold value
        """
        self.thresholds[metric_name] = threshold
        self.logger.info(f"Updated threshold for {metric_name}: {threshold}")

    def get_config(self) -> dict:
        """
        Get current configuration.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()
