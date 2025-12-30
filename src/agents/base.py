"""
Base Agent Class
Foundation for all AI agents in the system
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from agent processing"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    processing_time_ms: float = 0.0
    agent_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'processing_time_ms': self.processing_time_ms,
            'agent_name': self.agent_name,
            'timestamp': self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """
    Abstract base class for AI agents.
    All agents should inherit from this class.
    """

    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Process input data and return result.
        Must be implemented by subclasses.

        Args:
            input_data: Input data for processing

        Returns:
            AgentResult with processing results
        """
        pass

    def validate_input(self, input_data: Dict[str, Any], required_fields: list) -> Optional[str]:
        """
        Validate that required fields are present in input.

        Args:
            input_data: Input data to validate
            required_fields: List of required field names

        Returns:
            Error message if validation fails, None if valid
        """
        missing = [f for f in required_fields if not input_data.get(f)]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        return None

    def _create_result(
        self,
        success: bool,
        data: Dict[str, Any] = None,
        error: str = None,
        processing_time_ms: float = 0.0
    ) -> AgentResult:
        """Helper to create AgentResult"""
        return AgentResult(
            success=success,
            data=data or {},
            error=error,
            processing_time_ms=processing_time_ms,
            agent_name=self.name
        )

    def _log_processing(self, input_data: Dict, result: AgentResult):
        """Log processing for debugging"""
        if result.success:
            self.logger.info(
                f"Processing complete in {result.processing_time_ms:.2f}ms"
            )
        else:
            self.logger.error(f"Processing failed: {result.error}")
