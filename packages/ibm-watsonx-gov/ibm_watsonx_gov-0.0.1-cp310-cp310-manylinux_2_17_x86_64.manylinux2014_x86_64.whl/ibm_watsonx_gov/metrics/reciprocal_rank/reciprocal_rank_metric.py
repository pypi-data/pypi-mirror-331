# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from ibm_watsonx_gov.entities.enums import TaskType
from ibm_watsonx_gov.entities.evaluation_result import RecordMetricResult
from ibm_watsonx_gov.entities.metric import GenAIMetric, MetricThreshold
from ibm_watsonx_gov.entities.metric_groups import RetrievalQualityMetricGroup

RECIPROCAL_RANK = "reciprocal_rank"


class ReciprocalRankResult(RecordMetricResult):
    name: str = RECIPROCAL_RANK


class ReciprocalRankMetric(GenAIMetric):
    name: str = RECIPROCAL_RANK
    group: RetrievalQualityMetricGroup = RetrievalQualityMetricGroup()
    tasks: list[TaskType] = [TaskType.RAG]
    is_reference_free: bool = True
    thresholds: list[MetricThreshold] = [MetricThreshold(
        type="lower_limit", value=0.8)]
