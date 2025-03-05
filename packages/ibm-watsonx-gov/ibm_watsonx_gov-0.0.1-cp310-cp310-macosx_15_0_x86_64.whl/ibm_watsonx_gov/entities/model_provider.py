# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from pydantic import BaseModel, Field

from ibm_watsonx_gov.entities.credentials import WxAICredentials
from ibm_watsonx_gov.entities.enums import ModelProviderType


class ModelProvider(BaseModel):
    type_: ModelProviderType = Field(alias="type")


class WxAIModelProvider(ModelProvider):
    type_: ModelProviderType = Field(
        default=ModelProviderType.IBM_WATSONX_AI,
        alias="type"
    )
    credentials: WxAICredentials | None = None


class CustomModelProvider(ModelProvider):
    type_: ModelProviderType = Field(
        default=ModelProviderType.CUSTOM,
        alias="type",
    )
