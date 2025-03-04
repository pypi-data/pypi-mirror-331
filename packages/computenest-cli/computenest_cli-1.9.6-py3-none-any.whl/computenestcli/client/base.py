# -*- coding: utf-8 -*-
from alibabacloud_tea_openapi import models as open_api_models


class BaseClient:
    def __init__(self, region_id, access_key_id, access_key_secret, security_token=None, extra_parameters=None, global_parameters=None):
        self.region_id = region_id
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.security_token = security_token
        self.extra_parameters = extra_parameters
        self.config = open_api_models.Config(access_key_id=access_key_id, access_key_secret=access_key_secret,
                                             security_token=security_token, global_parameters=global_parameters)
