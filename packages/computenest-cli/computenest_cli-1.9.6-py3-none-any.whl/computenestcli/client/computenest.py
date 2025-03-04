# -*- coding: utf-8 -*-
from alibabacloud_computenestsupplier20210521.client import Client as ComputeNestSupplier20210521Client
from computenestcli.client.base import BaseClient
from computenestcli.common.constant import AP_SOUTHEAST_1
from alibabacloud_tea_openapi.models import GlobalParameters


class ComputeNestClient(BaseClient):

    def __init__(self, context):
        super().__init__(context.region_id,
                         context.credentials.access_key_id,
                         context.credentials.access_key_secret,
                         context.credentials.security_token,
                         context.extra_parameters)

    def create_client_compute_nest(self):
        if self.region_id == AP_SOUTHEAST_1:
            self.config.endpoint = f'computenestsupplier.ap-southeast-1.aliyuncs.com'
        else:
            self.config.endpoint = f'computenestsupplier.cn-hangzhou.aliyuncs.com'

        if self.extra_parameters is not None:
            # 安全治理：事件内容完整性/请求来源IP未记录治理方案，必须要有Ip
            source_ip = self.extra_parameters.get('SourceIp')
            secure_transport = self.extra_parameters.get('SecureTransport')
            queries = {}
            if source_ip:
                queries['SourceIp'] = source_ip
            if secure_transport:
                queries['SecureTransport'] = secure_transport

            if queries:
                global_params = GlobalParameters(queries=queries)
                self.config.global_parameters = global_params
        return ComputeNestSupplier20210521Client(self.config)