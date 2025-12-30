"""
Agent Pipeline
Orchestrates multiple agents for report processing
"""

import time
from typing import Dict, Any, List
from dataclasses import dataclass, field

from .base import BaseAgent, AgentResult
from .classifier import ClassifierAgent
from .validator import ValidatorAgent
from .summarizer import SummarizerAgent


@dataclass
class PipelineResult:
    """Result from pipeline processing"""
    success: bool
    results: Dict[str, AgentResult] = field(default_factory=dict)
    total_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)

    @property
    def classification(self) -> Dict[str, Any]:
        """Get classification result data"""
        if 'classifier' in self.results:
            return self.results['classifier'].data
        return {}

    @property
    def validation(self) -> Dict[str, Any]:
        """Get validation result data"""
        if 'validator' in self.results:
            return self.results['validator'].data
        return {}

    @property
    def summary(self) -> Dict[str, Any]:
        """Get summary result data"""
        if 'summarizer' in self.results:
            return self.results['summarizer'].data
        return {}


class AgentPipeline:
    """
    Pipeline for processing reports through multiple agents.
    Orchestrates classifier, validator, and summarizer agents.
    """

    def __init__(self):
        self.classifier = ClassifierAgent()
        self.validator = ValidatorAgent()
        self.summarizer = SummarizerAgent()

    def process_report(self, report_data: Dict[str, Any]) -> PipelineResult:
        """
        Process report through all agents.

        Args:
            report_data: Dict with 5W+1H fields

        Returns:
            PipelineResult with all agent results
        """
        start_time = time.time()
        results = {}
        errors = []

        # Step 1: Validate
        validation_result = self.validator.process(report_data)
        results['validator'] = validation_result

        if not validation_result.success:
            errors.append(f"Validation failed: {validation_result.error}")

        # Step 2: Classify (even if validation has warnings)
        if validation_result.data.get('is_valid', False) or validation_result.success:
            classification_result = self.classifier.process(report_data)
            results['classifier'] = classification_result

            if not classification_result.success:
                errors.append(f"Classification failed: {classification_result.error}")
            else:
                # Add classification to report data for summarizer
                report_data['category'] = classification_result.data.get('category')
                report_data['severity'] = classification_result.data.get('severity')

        # Step 3: Summarize
        summary_result = self.summarizer.process(report_data)
        results['summarizer'] = summary_result

        if not summary_result.success:
            errors.append(f"Summarization failed: {summary_result.error}")

        total_time = (time.time() - start_time) * 1000

        return PipelineResult(
            success=len(errors) == 0,
            results=results,
            total_time_ms=total_time,
            errors=errors
        )

    def quick_classify(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Quick classification without full pipeline.

        Args:
            report_data: Dict with at least 'what' field

        Returns:
            Classification data dict
        """
        result = self.classifier.process(report_data)
        return result.data if result.success else {}

    def validate_only(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validation only without other processing.

        Args:
            report_data: Dict with 5W+1H fields

        Returns:
            Validation data dict
        """
        result = self.validator.process(report_data)
        return result.data if result.success else {'is_valid': False, 'errors': [result.error]}

    def get_processing_stats(self, pipeline_result: PipelineResult) -> Dict[str, Any]:
        """Get processing statistics from pipeline result"""
        stats = {
            'total_time_ms': pipeline_result.total_time_ms,
            'agent_times': {},
            'success': pipeline_result.success
        }

        for agent_name, result in pipeline_result.results.items():
            stats['agent_times'][agent_name] = result.processing_time_ms

        return stats


# Singleton instance for easy access
_pipeline_instance = None


def get_pipeline() -> AgentPipeline:
    """Get singleton pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = AgentPipeline()
    return _pipeline_instance
