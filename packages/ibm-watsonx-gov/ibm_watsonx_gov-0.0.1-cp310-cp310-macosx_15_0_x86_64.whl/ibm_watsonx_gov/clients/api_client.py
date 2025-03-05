
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from ibm_cloud_sdk_core.authenticators import (CloudPakForDataAuthenticator,
                                               IAMAuthenticator)
from ibm_watson_openscale import APIClient as WOSClient

from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.utils.url_mapping import WOS_URL_MAPPING


class APIClient():

    def __init__(self, credentials: Credentials) -> WOSClient:
        if credentials.version:
            authenticator = CloudPakForDataAuthenticator(url=credentials.url,
                                                         username=credentials.username,
                                                         apikey=credentials.api_key,
                                                         disable_ssl_verification=credentials.disable_ssl
                                                         )
        else:
            url_map = WOS_URL_MAPPING.get(credentials.url)
            if not url_map:
                raise ValueError(
                    f"Invalid url {credentials.url}. Please provide openscale service url.")

            authenticator = IAMAuthenticator(apikey=credentials.api_key,
                                             url=url_map.iam_url,
                                             disable_ssl_verification=credentials.disable_ssl)

        self.wos_client = WOSClient(
            authenticator=authenticator,
            service_url=credentials.url,
            service_instance_id=credentials.service_instance_id,
        )
