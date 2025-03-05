# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Literal

import pandas as pd
from pydantic import Field

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric, MetricThreshold
from ibm_watsonx_gov.providers import UnitxtProvider

FAITHFULNESS = "faithfulness"


class FaithfulnessResult(RecordMetricResult):
    name: str = FAITHFULNESS
    faithfulness_attributions: list[dict] = None


unitxt_methods = [
    "token_k_precision",
    "sentence_bert_mini_lm",
]


class FaithfulnessMetric(GenAIMetric):
    """Defines the interface for computing the Faithfulness metric.

    The following methods are supported:
    1. token_k_precision
    2. sentence_bert_mini_lm (default)

    ```python
    metric = FaithfulnessMetric()
    ```

    ```python
    threshold  = MetricThreshold(type="lower_limit", value=0.5)
    method = "token_k_precision"
    metric = FaithfulnessMetric(method=method, threshold=threshold)
    ```
    """
    name: Annotated[str, Field(default=FAITHFULNESS)]
    tasks: Annotated[list[TaskType], Field(
        default=[TaskType.RAG])]
    thresholds: Annotated[list[MetricThreshold], Field(default=[MetricThreshold(
        type="lower_limit", value=0.8)])]
    method: Annotated[
        Literal["token_k_precision", "sentence_bert_mini_lm"],
        Field(description=f"The method used to compute the metric. One of \"token_k_precision\","
              " \"sentence_bert_mini_lm\".",
              default="sentence_bert_mini_lm")]

    def evaluate(self, data: pd.DataFrame | dict,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs) -> AggregateMetricResult:
        if self.method not in unitxt_methods:
            raise ValueError(
                f"The provided method '{self.method}' for computing '{self.name}' metric is not supported.")

        provider = UnitxtProvider(configuration=configuration,
                                  metric_name=self.name,
                                  metric_method=self.method,
                                  metric_prefix="metrics.rag",
                                  **kwargs)
        aggregated_metric_result = provider.evaluate(data=data)

        return aggregated_metric_result
