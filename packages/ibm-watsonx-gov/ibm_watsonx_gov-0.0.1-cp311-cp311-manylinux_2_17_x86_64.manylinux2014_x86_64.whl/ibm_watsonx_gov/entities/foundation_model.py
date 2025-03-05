# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Callable

from pydantic import BaseModel, Field

from ibm_watsonx_gov.entities.model_provider import (CustomModelProvider,
                                                     ModelProvider,
                                                     WxAIModelProvider)


class FoundationModel(BaseModel):
    model_name: str | None = None
    provider: ModelProvider


class WxAIFoundationModel(FoundationModel):
    model_id: str
    project_id: str | None = None
    space_id: str | None = None
    provider: ModelProvider = Field(default_factory=WxAIModelProvider)


class CustomFoundationModel(FoundationModel):
    scoring_fn: Callable
    provider: ModelProvider = Field(default_factory=CustomModelProvider)
