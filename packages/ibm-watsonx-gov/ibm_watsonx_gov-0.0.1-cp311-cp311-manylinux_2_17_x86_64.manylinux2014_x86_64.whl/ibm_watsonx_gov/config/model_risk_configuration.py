# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from pydantic import BaseModel, PositiveInt

from ibm_watsonx_gov.entities.credentials import WxGovConsoleCredentials
from ibm_watsonx_gov.entities.foundation_model import FoundationModel


class WxGovConsoleConfiguration(BaseModel):
    model_id: str
    credentials: WxGovConsoleCredentials


class ModelRiskConfiguration(BaseModel):
    model_details: FoundationModel
    risk_dimensions: list[str] | None = None
    max_sample_size: PositiveInt | None = None
    wx_gc_configuration: WxGovConsoleConfiguration | None = None
    pdf_report_output_path: str | None = None
