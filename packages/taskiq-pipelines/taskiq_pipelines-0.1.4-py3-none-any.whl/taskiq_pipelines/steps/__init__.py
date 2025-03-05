"""Package with default pipeline steps."""

from logging import getLogger
from typing import Any, Dict

from taskiq_pipelines.abc import AbstractStep
from taskiq_pipelines.steps.filter import FilterStep
from taskiq_pipelines.steps.mapper import MapperStep
from taskiq_pipelines.steps.sequential import SequentialStep

logger = getLogger(__name__)


def parse_step(step_type: str, step_data: Dict[str, Any]) -> AbstractStep:
    step_cls = AbstractStep._known_steps.get(step_type)
    if step_cls is None:
        logger.warning(f"Unknown step type: {step_type}")
        raise ValueError("Unknown step type.")
    return step_cls(**step_data)


__all__ = [
    "FilterStep",
    "MapperStep",
    "SequentialStep",
]
