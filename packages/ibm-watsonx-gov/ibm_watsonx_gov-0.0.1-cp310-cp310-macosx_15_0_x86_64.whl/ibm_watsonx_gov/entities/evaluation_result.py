# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from typing import Annotated, Any

import pandas as pd
from pydantic import BaseModel, Field

from ibm_watsonx_gov.entities.base_classes import BaseMetricResult


class RecordMetricResult(BaseMetricResult):
    record_id: str
    record_timestamp: str | None = None


class ToolMetricResult(RecordMetricResult):
    tool_name: Annotated[str, Field(
        title="Tool Name", description="Name of the tool for which this result is computed.")]
    execution_count: Annotated[int, Field(
        title="Execution count", description="The execution count for this tool name.", gt=0, default=1)]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            return False

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) == \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) < \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) > \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) <= \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) >= \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)


class AggregateMetricResult(BaseMetricResult):
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    total_records: int
    record_level_metrics: list[RecordMetricResult] = []


class EvaluationResult(BaseModel):
    metrics_result: list[AggregateMetricResult]

    def to_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the evaluation result to a dataframe

        Args:
            data (pd.DataFrame): the input dataframe

        Returns:
            pd.DataFrame: new dataframe of the input and the evaluated metrics
        """
        values_dict: dict[str, list[float | str | bool]] = {}
        for result in self.metrics_result:
            values_dict[f"{result.name}.{result.method}"] = [
                record_metric.value for record_metric in result.record_level_metrics]

        return pd.concat([data, pd.DataFrame.from_dict(values_dict)], axis=1)

    def to_record_metrics_dict(self) -> list[dict]:
        result = []
        for aggregate_metric_result in self.metrics_result:
            for record_level_metric_result in aggregate_metric_result.record_level_metrics:
                result.append(record_level_metric_result.model_dump())
        return result
