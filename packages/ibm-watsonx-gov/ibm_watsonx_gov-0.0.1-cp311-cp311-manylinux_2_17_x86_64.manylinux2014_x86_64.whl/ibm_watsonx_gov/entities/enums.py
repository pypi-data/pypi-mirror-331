# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from enum import Enum


class EvaluationProvider(Enum):
    """Supported evaluation providers for metrics computation"""
    UNITXT = "unitxt"
    WATSONX_GOV = "watsonx_governance"

    @staticmethod
    def values():
        """Get all values of the enum"""
        return [e.value for e in EvaluationProvider]


class TaskType(Enum):
    """Supported task types for generative AI models"""
    QA = "question_answering"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    GENERATION = "generation"
    EXTRACTION = "extraction"
    RAG = "retrieval_augmented_generation"

    @staticmethod
    def values():
        return [e.value for e in TaskType]


class InputDataType(Enum):
    """Supported input data types"""
    STRUCTURED = "structured"
    TEXT = "unstructured_text"
    IMAGE = "unstructured_image"
    MULTIMODAL = "multimodal"


class ProblemType(Enum):
    """Supported problem types for predictive AI models"""
    BINARY = "binary"
    MULTICLASS = "multiclass"
    REGRESSION = "regression"


class UnitxtColumnNames(Enum):
    """Column names used in the Unitxt library"""
    QUESTION = "question"
    ANSWER = "answer"
    CONTEXTS = "contexts"
    GROUND_TRUTHS = "ground_truths"


class EvaluationStage(Enum):
    """Supported evaluation stages"""
    DEVELOPMENT = "development"
    PRE_PRODUCTION = "pre_production"
    PRODUCTION = "production"


class ModelProviderType(Enum):
    """Supported model provider types for Generative AI"""
    IBM_WATSONX_AI = "ibm_watsonx.ai"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"


class Region(Enum):
    """Supported IBM Cloud regions"""
    DALLAS = "us-south"
    FRANKFURT = "eu-de"
    SYDNEY = "au-syd"
    TORONTO = "ca-tor"


class EvaluatorFields(Enum):
    """Fields used in the evaluator"""
    INPUT_FIELDS = "input_fields"
    OUTPUT_FIELDS = "output_fields"
    REFERENCE_FIELDS = "reference_fields"
    QUESTION_FIELD = "question_field"
    CONTEXT_FIELDS = "context_fields"
    RECORD_ID_FIELD = "record_id_field"
    RECORD_TIMESTAMP_FIELD = "record_timestamp_field"

    @staticmethod
    def get_default_fields_mapping() -> dict["EvaluatorFields", str | list[str]]:
        """Get the default fields mapping for the evaluator"""
        return {
            EvaluatorFields.INPUT_FIELDS: ["input_text"],
            EvaluatorFields.OUTPUT_FIELDS: ["generated_text"],
            EvaluatorFields.REFERENCE_FIELDS: ["ground_truth"],
            EvaluatorFields.QUESTION_FIELD: "input_text",
            EvaluatorFields.CONTEXT_FIELDS: ["context"],
            EvaluatorFields.RECORD_ID_FIELD: "record_id",
            EvaluatorFields.RECORD_TIMESTAMP_FIELD: "record_timestamp"
        }
