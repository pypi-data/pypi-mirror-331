# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from functools import partial
from time import time
from typing import Annotated, Any, Callable, Optional, Set

import pandas as pd
from pydantic import BaseModel, Field, PrivateAttr
from wrapt import decorator

from ibm_watsonx_gov.config import AgenticAIConfiguration
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.enums import EvaluatorFields
from ibm_watsonx_gov.entities.evaluation_result import ToolMetricResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluate.evaluate_metrics import evaluate_metrics
from ibm_watsonx_gov.metrics import (AnswerSimilarityMetric,
                                     ContextRelevanceMetric,
                                     FaithfulnessMetric)
from ibm_watsonx_gov.utils.python_utils import (add_if_unique,
                                                get_argument_value)


class AgenticEvaluation(BaseModel):

    credentials: Annotated[Optional[Credentials], Field(
        name="watsonx.governance Credentials", default=None)]
    experiment_id: Annotated[Optional[str], Field(name="Experiment ID",
                                                  description="An id for the experiment.",
                                                  default="1", examples=[
                                                      "experiment_1", "experiment_2"])]
    configuration: Annotated[Optional[AgenticAIConfiguration],
                             Field(name="Configuration object", default=None)]
    __metric_results: Annotated[list[ToolMetricResult],
                                PrivateAttr(default=[])]
    """__metric_results holds the results of all the evaluations done for a particular evaluation instance."""
    __execution_counts: Annotated[dict[str, dict[str, int]],
                                  PrivateAttr(default={})]
    """__execution_counts holds the execution count for a particular tool, for a given record_id."""
    __tools_being_run: Annotated[dict[str, Set[str]],
                                 PrivateAttr(default={})]
    """__tools_being_run holds the name of the current tools being run for a given record_id. Multiple decorators can be applied on a single tool using chaining. We don't want to hold multiple copies of same tool here."""

    def __validate(self, *, func: Callable, metrics: list[GenAIMetric], valid_metric_types: tuple[Any]):
        if not metrics:
            raise ValueError(
                "The 'metrics' argument can not be empty.")

        invalid_metrics = [metric.name for metric in metrics if not isinstance(
            metric, valid_metric_types)]
        if len(invalid_metrics):
            raise ValueError(
                f"The evaluator '{func.__name__}' is not applicable for "
                f"computing the metrics: {', '.join(invalid_metrics)}")

    def __compute_helper(self, *, func: Callable,
                         args: tuple,
                         kwargs: dict[str, Any],
                         configuration: AgenticAIConfiguration,
                         metrics: list[GenAIMetric],
                         metric_inputs: list[EvaluatorFields],
                         metric_outputs: list[EvaluatorFields],
                         metric_references: list[EvaluatorFields] = []) -> dict:
        """
        Helper method for computing metrics.

        Does the following:
            1. Computes tool latency metric, and appends the result to the :py:attr:`AgenticEvaluation.metric_results` attribute.
            2. Calls the original tool. 
            3. Computes the list of metrics given, and appends the result to the :py:attr:`AgenticEvaluation.metric_results` attribute.
            4. Returns the result of the original tool without any changes.

        Args:
            func (Callable): The tool on which the metric is to be computed
            args (tuple): The tuple of positional arguments passed to the tool
            kwargs (dict[str, Any]): The dictionary of keyword arguments passed to the tool
            configuration (AgenticAIConfiguration): The tool specific configuration
            metrics (list[GenAIMetric]): The list of metrics to compute.
            metric_inputs (list[EvaluatorFields]): The list of inputs for the metric.
            metric_outputs (list[EvaluatorFields]): The list of outputs for the metric.
            metric_references (list[EvaluatorFields], optional): The optional list of references for the metric. Defaults to [].

        Raises:
            ValueError: If the record id field is missing from the tool inputs.

        Returns:
            dict: The result of the wrapped tool.
        """

        get_arg_value = partial(
            get_argument_value, func=func, args=args, kwargs=kwargs)

        defaults = metric_inputs + metric_outputs + metric_references
        _configuration = AgenticAIConfiguration.create_configuration(app_config=self.configuration,
                                                                     method_config=configuration,
                                                                     defaults=defaults)
        _data = {}
        for field in metric_inputs + metric_references:
            _field = getattr(_configuration, field.value)
            if not (isinstance(_field, list)):
                _field = [_field]
            _data.update(dict(map(lambda f: (
                f, get_arg_value(param_name=f)), _field)))

        # Add record id to the data
        _field = getattr(_configuration, EvaluatorFields.RECORD_ID_FIELD.value,
                         EvaluatorFields.get_default_fields_mapping()[EvaluatorFields.RECORD_ID_FIELD])
        _record_id_value = get_arg_value(param_name=_field)
        if _record_id_value is None:
            raise ValueError(
                f"The {_field} is required for evaluation. Please add it while invoking the application.")
        _data[_field] = _record_id_value

        if _record_id_value not in self.__tools_being_run:
            self.__tools_being_run[_record_id_value] = set()
        if _record_id_value not in self.__execution_counts:
            self.__execution_counts[_record_id_value] = dict()

        if func.__name__ not in self.__tools_being_run[_record_id_value]:
            self.__tools_being_run[_record_id_value].add(func.__name__)
            self.__execution_counts[_record_id_value][func.__name__] = self.__execution_counts[_record_id_value].get(
                func.__name__, 0) + 1

        start_time = time()
        original_result = func(*args, **kwargs)
        latency = time() - start_time

        tool_mr = {
            "tool_name": func.__name__,
            "execution_count": self.__execution_counts[_record_id_value].get(func.__name__),
            "name": "tool_latency (s)",
            "method": "",
            "provider": "",
            "record_id": _record_id_value,
            "value": latency
        }

        add_if_unique(ToolMetricResult(**tool_mr), self.__metric_results,
                      ["tool_name", "execution_count", "name", "record_id"])

        if func.__name__ in self.__tools_being_run[_record_id_value]:
            self.__tools_being_run[_record_id_value].remove(func.__name__)

        for field in metric_outputs:
            _field = getattr(_configuration, field.value)
            if not (isinstance(_field, list)):
                _field = [_field]
            _data.update(dict(map(lambda f: (
                f, original_result.get(f)), _field)))

        metric_result = evaluate_metrics(configuration=_configuration, data=_data,
                                         metrics=metrics, credentials=self.credentials,
                                         output_format="dict")

        for mr in metric_result:
            tool_result = {
                "tool_name": func.__name__,
                "execution_count": self.__execution_counts[_record_id_value].get(func.__name__),
                **mr
            }
            tmr = ToolMetricResult(**tool_result)
            self.__metric_results.append(tmr)

        return original_result

    def evaluate_context_relevance(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       ContextRelevanceMetric()
                                   ]
                                   ) -> dict:
        """
        An evaluation decorator for computing context relevance metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ContextRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ContextRelevanceMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                ```python
                evaluator = AgenticEvaluation()
                @evaluator.evaluate_context_relevance
                def agentic_tool(*args, *kwargs):
                    pass
                ```

            2. Usage with different thresholds and methods
                ```python
                metric_1 = ContextRelevanceMetric(method="sentence_bert_bge", threshold=MetricThreshold(type="lower_limit", value=0.5))
                metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                evaluator = AgenticEvaluation()
                @evaluator.evaluate_context_relevance(metrics=[metric_1, metric_2])
                def agentic_tool(*args, *kwargs):
                    pass
                ```
        """
        if func is None:
            return partial(self.evaluate_context_relevance, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ContextRelevanceMetric,))

                metric_inputs = [EvaluatorFields.QUESTION_FIELD]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating context relevance metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_answer_similarity(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       AnswerSimilarityMetric()
                                   ]
                                   ) -> dict:
        """
        An evaluation decorator for computing answer similarity metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerSimilarityMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AnswerSimilarityMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                ```python
                evaluator = AgenticEvaluation()
                @evaluator.evaluate_answer_similarity
                def agentic_tool(*args, *kwargs):
                    pass
                ```

            2. Usage with different thresholds and methods
                ```python
                metric_1 = AnswerSimilarityMetric(method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                metric_2 = AnswerSimilarityMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                evaluator = AgenticEvaluation()
                @evaluator.evaluate_answer_similarity(metrics=[metric_1, metric_2])
                def agentic_tool(*args, *kwargs):
                    pass
                ```
        """

        if func is None:
            return partial(self.evaluate_answer_similarity, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(AnswerSimilarityMetric,))

                metric_inputs = [
                    EvaluatorFields.QUESTION_FIELD,
                    EvaluatorFields.CONTEXT_FIELDS
                ]
                metric_references = [EvaluatorFields.REFERENCE_FIELDS]
                metric_outputs = [EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs,
                                                        metric_references=metric_references)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating answer similarity metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_faithfulness(self,
                              func: Optional[Callable] = None,
                              *,
                              configuration: Optional[AgenticAIConfiguration] = None,
                              metrics: list[GenAIMetric] = [
                                  FaithfulnessMetric()
                              ]
                              ) -> dict:
        """
        An evaluation decorator for computing faithfulness metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.FaithfulnessMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ FaithfulnessMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                ```python
                evaluator = AgenticEvaluation()
                @evaluator.evaluate_faithfulness
                def agentic_tool(*args, *kwargs):
                    pass
                ```

            2. Usage with different thresholds and methods
                ```python
                metric_1 = FaithfulnessMetric(method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                metric_2 = FaithfulnessMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                evaluator = AgenticEvaluation()
                @evaluator.evaluate_faithfulness(metrics=[metric_1, metric_2])
                def agentic_tool(*args, *kwargs):
                    pass
                ```
        """

        if func is None:
            return partial(self.evaluate_faithfulness, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(FaithfulnessMetric,))

                metric_inputs = [
                    EvaluatorFields.QUESTION_FIELD,
                    EvaluatorFields.CONTEXT_FIELDS
                ]
                metric_outputs = [EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating faithfulness metric on {func.__name__},") from ex

        return wrapper(func)

    def get_metric_results(self) -> list[ToolMetricResult]:
        """
        Get the tool metrics results as a list

        Returns:
            list[ToolMetricResult]: The list of metric results
        """
        return sorted(self.__metric_results)

    def get_metrics_df(self, input_data: Optional[pd.DataFrame] = None,
                       record_id_field: str = "record_id") -> pd.DataFrame:
        """
        Get metrics dataframe.

        If the input dataframe is provided, it will be merged with the metrics dataframe.

        Args:
            input_data (Optional[pd.DataFrame], optional): Input data to merge with metrics dataframe.. Defaults to None.
            record_id_field (str, optional): Field to use for merging input data and metrics dataframe.. Defaults to "record_id".

        Returns:
            pd.DataFrame: Metrics dataframe.
        """

        results = sorted(self.__metric_results)

        def converter(m): return m.model_dump(
            exclude={"provider"}, exclude_none=True)

        metrics_df = pd.DataFrame(list(map(converter, results)))
        if input_data is None:
            return metrics_df

        return input_data.merge(metrics_df, on=record_id_field)
