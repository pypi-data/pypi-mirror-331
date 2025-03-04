"""REST API entities for monitoring."""

import dataclasses
from typing import Literal, Optional

from dataclasses_json import config, dataclass_json

from . import entities

_FIELD_IS_UPDATABLE = "FIELD_IS_UPDATABLE"


@dataclass_json
@dataclasses.dataclass
class AssessmentConfig:
    name: Optional[str] = None


@dataclass_json
@dataclasses.dataclass
class NamedGuidelineEntry:
    key: Optional[str] = None
    guidelines: Optional[list[str]] = None


@dataclass_json
@dataclasses.dataclass
class NamedGuidelines:
    entries: Optional[list[NamedGuidelineEntry]]


def ExcludeIfNone(value):
    return value is None


@dataclass_json
@dataclasses.dataclass
class EvaluationConfig:
    metrics: Optional[list[AssessmentConfig]] = None
    no_metrics: Optional[bool] = None
    named_guidelines: Optional[NamedGuidelines] = dataclasses.field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )


@dataclass_json
@dataclasses.dataclass
class SamplingConfig:
    sampling_rate: Optional[float] = None


@dataclass_json
@dataclasses.dataclass
class PeriodicSchedule:
    frequency_interval: Optional[int] = None
    frequency_unit: Optional[str] = None


@dataclass_json
@dataclasses.dataclass
class ScheduleConfig:
    periodic_schedule: Optional[PeriodicSchedule] = None
    pause_status: Optional[Literal["UNPAUSED", "PAUSED"]] = None


@dataclass_json
@dataclasses.dataclass
class Monitor:
    experiment_id: Optional[str] = dataclasses.field(
        default=None,
        metadata={**config(exclude=ExcludeIfNone), _FIELD_IS_UPDATABLE: False},
    )
    workspace_path: Optional[str] = dataclasses.field(
        default=None,
        metadata={**config(exclude=ExcludeIfNone), _FIELD_IS_UPDATABLE: False},
    )
    evaluation_config: Optional[EvaluationConfig] = dataclasses.field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    sampling: Optional[SamplingConfig] = dataclasses.field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    schedule: Optional[ScheduleConfig] = dataclasses.field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    is_agent_external: Optional[bool] = dataclasses.field(
        default=None,
        metadata={**config(exclude=ExcludeIfNone), _FIELD_IS_UPDATABLE: False},
    )
    evaluated_traces_table: Optional[str] = dataclasses.field(
        default=None,
        metadata={**config(exclude=ExcludeIfNone), _FIELD_IS_UPDATABLE: False},
    )

    def get_update_mask(self) -> str:
        """Get the update mask for the fields that have changed."""
        return ",".join(
            field.name
            for field in dataclasses.fields(self)
            if getattr(self, field.name) is not None
            and field.metadata.get(_FIELD_IS_UPDATABLE, True)
        )


@dataclass_json
@dataclasses.dataclass
class MonitorInfo:
    monitor: Optional[Monitor] = None
    endpoint_name: Optional[str] = None

    @property
    def is_external(self) -> bool:
        """Returns True if the monitor is external."""
        return self.monitor and self.monitor.is_agent_external

    def _get_monitoring_config(self) -> entities.MonitoringConfig:
        """Extract common monitoring configuration logic."""
        monitor = self.monitor or Monitor()
        sampling_config = monitor.sampling or SamplingConfig()
        evaluation_config = monitor.evaluation_config or EvaluationConfig()
        assessment_configs = evaluation_config.metrics or []

        # Get periodic config
        periodic_config = None
        if monitor.schedule and monitor.schedule.periodic_schedule:
            periodic_schedule = monitor.schedule.periodic_schedule
            if (
                periodic_schedule.frequency_interval
                and periodic_schedule.frequency_unit
            ):
                periodic_config = entities.PeriodicMonitoringConfig(
                    interval=periodic_schedule.frequency_interval,
                    unit=periodic_schedule.frequency_unit,
                )

        # Convert named guidelines
        global_guidelines = None
        if (
            monitor.evaluation_config
            and monitor.evaluation_config.named_guidelines
            and monitor.evaluation_config.named_guidelines.entries
        ):
            global_guidelines = {
                entry.key: entry.guidelines
                for entry in monitor.evaluation_config.named_guidelines.entries
                if entry.key and entry.guidelines
            }

        return entities.MonitoringConfig(
            sample=sampling_config.sampling_rate,
            metrics=[metric.name for metric in assessment_configs],
            periodic=periodic_config,
            paused=(
                monitor.schedule.pause_status == entities.SchedulePauseStatus.PAUSED
            ),
            global_guidelines=global_guidelines,
        )

    def to_monitor(self) -> entities.Monitor:
        """Converts the REST API response to a Python Monitor object."""
        monitor = self.monitor or Monitor()
        assert not monitor.is_agent_external, "Monitor is external"

        return entities.Monitor(
            endpoint_name=self.endpoint_name,
            evaluated_traces_table=monitor.evaluated_traces_table,
            experiment_id=monitor.experiment_id,
            workspace_path=monitor.workspace_path,
            monitoring_config=self._get_monitoring_config(),
        )

    def to_external_monitor(self) -> entities.ExternalMonitor:
        """Converts the REST API response to an External Monitor object."""
        monitor = self.monitor or Monitor()
        assert monitor.is_agent_external, "Monitor is internal"

        return entities.ExternalMonitor(
            ingestion_endpoint_name=self.endpoint_name,
            monitoring_table=monitor.evaluated_traces_table,
            experiment_id=monitor.experiment_id,
            monitoring_config=self._get_monitoring_config(),
        )


@dataclass_json
@dataclasses.dataclass
class JobCompletionEvent:
    success: Optional[bool] = None
    error_message: Optional[str] = None


@dataclass_json
@dataclasses.dataclass
class MonitoringEvent:
    job_start: Optional[dict] = None
    job_completion: Optional[JobCompletionEvent] = None


@dataclass_json
@dataclasses.dataclass
class MonitoringMetric:
    num_traces_evaluated: Optional[int] = None
