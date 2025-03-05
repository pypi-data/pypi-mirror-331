# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Literal, overload

import pandas as pd

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.evaluation_result import EvaluationResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluate import EvaluationResult


@overload
def evaluate_metrics(
    configuration: GenAIConfiguration,
    data: pd.DataFrame,
    metrics: list[GenAIMetric] = [],
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "object",
    **kwargs,
) -> EvaluationResult: ...


@overload
def evaluate_metrics(
    configuration: GenAIConfiguration,
    data: pd.DataFrame | dict,
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "dict",
    **kwargs,
) -> dict: ...


@overload
def evaluate_metrics(
    configuration: GenAIConfiguration,
    data: pd.DataFrame | dict,
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "dataframe",
    **kwargs,
) -> pd.DataFrame: ...


@overload
def evaluate_metrics(
    configuration: AgenticAIConfiguration,
    data: dict,
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "dict",
    **kwargs,
) -> pd.DataFrame: ...


def evaluate_metrics(
    configuration: GenAIConfiguration | AgenticAIConfiguration,
    data: pd.DataFrame | dict,
    metrics: list[GenAIMetric] = [],
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "object",
    **kwargs,
):
    from .impl.evaluate_metrics_impl import _evaluate_metrics

    return _evaluate_metrics(configuration=configuration,
                             data=data,
                             metrics=metrics,
                             credentials=credentials,
                             output_format=output_format,
                             **kwargs)
