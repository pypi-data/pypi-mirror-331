# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import pandas as pd
from pydantic import BaseModel
from typing import List



class RiskMetric(BaseModel):
    name: str
    value: float | str | List[float]


class Benchmark(BaseModel):
    name: str
    metrics: list[RiskMetric]

    def get_metric_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.model_dump()["metrics"])


class Risk(BaseModel):
    name: str
    benchmarks: list[Benchmark]


class ModelRiskResult(BaseModel):
    risks: list[Risk]
    output_file_path: str | None = None
