# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Optional

from pydantic import Field
from typing_extensions import Self

from ibm_watsonx_gov.entities.base_classes import BaseConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields, TaskType


class AgenticAIConfiguration(BaseConfiguration):
    """
    Configuration interface for Agentic AI tools and applications.
    """

    task_type: Annotated[Optional[TaskType], Field(title="Task Type",
                                                   description="The generative task type.",
                                                   default=None,
                                                   examples=[TaskType.RAG])]
    input_fields: Annotated[Optional[list[str]], Field(title="Input Fields",
                                                       description="The list of model input fields in the data.",
                                                       default=[],
                                                       examples=[["question", "context1", "context2"]])]
    question_field: Annotated[Optional[str], Field(title="Question Field",
                                                   description="The question field in the input fields.",
                                                   default=None,
                                                   examples=["question"])]
    context_fields: Annotated[Optional[list[str]], Field(title="Context Fields",
                                                         description="The list of context fields in the input fields.",
                                                         default=[],
                                                         examples=[["context1", "context2"]])]
    output_fields: Annotated[Optional[list[str]], Field(title="Output Fields",
                                                        description="The list of model output fields in the data.",
                                                        default=[],
                                                        examples=[["output"]])]
    reference_fields: Annotated[Optional[list[str]], Field(title="Reference Fields",
                                                           description="The list of reference fields in the data.",
                                                           default=[],
                                                           examples=[["reference"]])]
    record_id_field: Annotated[Optional[str], Field(title="Record ID Field",
                                                    description="The record id field denoting a unique record.",
                                                    default=None,
                                                    examples=["record_id"])]
    record_timestamp_field: Annotated[Optional[str], Field(title="Record Timestamp Field",
                                                           description="The record timestamp field denoting a timestamp for this record in UTC string.",
                                                           default=None,
                                                           examples=["record_timestamp"])]

    @classmethod
    def create_configuration(cls, *, app_config: Optional[Self],
                             method_config: Optional[Self],
                             defaults: list[EvaluatorFields],
                             add_record_fields: bool = True) -> Self:
        """
        Creates a configuration object based on the provided parameters.

        Args:
            app_config (Optional[Self]): The application configuration.
            method_config (Optional[Self]): The method configuration.
            defaults (list[EvaluatorFields]): The default fields to include in the configuration.
            add_record_fields (bool, optional): Whether to add record fields to the configuration. Defaults to True.

        Returns:
            Self: The created configuration object.
        """

        if method_config is not None:
            return method_config

        if app_config is not None:
            return app_config

        config = {field.value: EvaluatorFields.get_default_fields_mapping()[
            field] for field in defaults}

        if not add_record_fields:
            return cls(**config)

        system_fields = [EvaluatorFields.RECORD_ID_FIELD,
                         EvaluatorFields.RECORD_TIMESTAMP_FIELD]
        for field in system_fields:
            if field not in defaults:
                config[field.value] = EvaluatorFields.get_default_fields_mapping()[
                    field]
        return cls(**config)
