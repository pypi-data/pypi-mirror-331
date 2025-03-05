# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from ibm_watsonx_gov.config import ModelRiskConfiguration
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.evaluate import ModelRiskResult


def evaluate_model_risk(
        configuration: ModelRiskConfiguration,
        credentials: Credentials | None = None,
) -> ModelRiskResult:
    from .impl.evaluate_model_risk_impl import _evaluate_model_risk

    return _evaluate_model_risk(
        configuration,
        credentials,
    )
