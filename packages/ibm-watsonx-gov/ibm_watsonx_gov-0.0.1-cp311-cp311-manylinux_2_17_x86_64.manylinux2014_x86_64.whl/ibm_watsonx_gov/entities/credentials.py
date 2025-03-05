# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
from typing import Annotated

from pydantic import BaseModel, Field


class Credentials(BaseModel):
    api_key: Annotated[str, Field(title="Api Key",
                                  description="The user api key.")]
    url: Annotated[str, Field(title="watsonx.governance url",
                              description="The watsonx.governance url. By default the url for dallas region is used.",
                              default="https://api.aiopenscale.cloud.ibm.com")]
    service_instance_id:  Annotated[str | None, Field(title="Service instance id",
                                                      description="The watsonx.governance service instance id.",
                                                      default=None)]
    username: Annotated[str | None, Field(title="User name",
                                          description="The user name.",
                                          default=None)]
    version: Annotated[str | None, Field(title="Version",
                                         description="The watsonx.governance version.",
                                         default=None)]
    disable_ssl: Annotated[bool, Field(title="Disable ssl",
                                       description="The flag to disable ssl.",
                                       default=False)]

    @classmethod
    def create_from_env(cls):
        return Credentials(
            api_key=os.getenv("WXG_API_KEY"),
            url=os.getenv("WXG_URL", "https://api.aiopenscale.cloud.ibm.com"),
            service_instance_id=os.getenv("WXG_SERVICE_INSTANCE_ID"),
            username=os.getenv("WXG_USERNAME"),
            version=os.getenv("WXG_VERSION", None),
            disable_ssl=os.getenv("WXG_DISABLE_SSL", False)
        )


class WxAICredentials(BaseModel):
    url: Annotated[str, Field(
        title="watsonx.ai url",
        description="The url for watsonx ai service",
        default="https://us-south.ml.cloud.ibm.com",
        examples=[
            "https://us-south.ml.cloud.ibm.com",
            "https://eu-de.ml.cloud.ibm.com",
            "https://eu-gb.ml.cloud.ibm.com",
            "https://jp-tok.ml.cloud.ibm.com",
            "https://au-syd.ml.cloud.ibm.com",
        ]
    )]
    api_key: str
    version: str | None = None
    username: str | None = None

    @classmethod
    def create_from_env():
        return WxAICredentials(
            url=os.getenv("WXAI_URL"),
            api_key=os.getenv("WXAI_API_KEY"),
            version=os.getenv("WXAI_VERSION"),
            username=os.getenv("WXAI_USERNAME"),
        )


class WxGovConsoleCredentials(BaseModel):
    url: str
    username: str
    password: str
    api_key: str | None = None

    @classmethod
    def create_from_env():
        return WxGovConsoleCredentials(
            url=os.getenv("WXGC_URL"),
            username=os.getenv("WXGC_USERNAME"),
            password=os.getenv("WXGC_PASSWORD"),
            api_key=os.getenv("WXGC_API_KEY"),
        )
