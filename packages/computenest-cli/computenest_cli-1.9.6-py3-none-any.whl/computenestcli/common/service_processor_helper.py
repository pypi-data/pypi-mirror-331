from computenestcli.common import constant
from computenestcli.common.locale import Locale
from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.common.str_util import StrUtil
from computenestcli.base_log import get_user_logger

user_logger = get_user_logger(BUILD_SERVICE)

class ServiceProcessorHelper:
    def __init__(self):
        pass

    # 1. 如果参数传入service_name，则将参数的值覆盖到service_config的service_info的中文名称
    # 2. 如果参数传入service_info，则将参数的值覆盖到service_config
    # 3. 如果原service_config中的service_info没有采用list，则改为list格式
    @staticmethod
    def pre_process_service_info(service_config, service_info_list, service_name, version_name, icon,
                                 desc):
        # 如果同时传入service_name和service_info，抛出异常
        if service_name and service_info_list:
            raise Exception('service_name and service_info cannot be both provided.')

        # 兼容逻辑：处理config中仅输入单service_info的情况，转换为List
        if isinstance(service_config.get(constant.SERVICE_INFO), dict):
            service_config[constant.SERVICE_INFO] = [service_config.get(constant.SERVICE_INFO)]

        service_config[constant.VERSION_NAME] = version_name
        # 兼容逻辑：如果参数传入service_info，则将参数的值覆盖到service_config
        if service_info_list:
            if not isinstance(service_info_list, list):
                raise Exception('service_info should be a list.')
            # service_info_list中的Key首字符转为大写
            service_info_list = StrUtil.capitalize_keys(service_info_list)
            service_config[constant.SERVICE_INFO] = service_info_list
        else:
            # 传入service_name的情况，将service_name等构建为一个service_info，默认locale为zh-CN
            if constant.SERVICE_INFO not in service_config or len(service_config.get(constant.SERVICE_INFO)) == 0:
                service_config[constant.SERVICE_INFO] = [{
                    constant.NAME: service_name,
                    constant.SHORT_DESCRIPTION: desc,
                    constant.IMAGE: icon,
                    constant.LOCALE: Locale.ZH_CN.value
                }]
            elif len(service_config.get(constant.SERVICE_INFO)) == 1:
                locale = service_config.get(constant.SERVICE_INFO)[0].get(constant.LOCALE)
                if not locale:
                    service_config[constant.SERVICE_INFO][0][constant.LOCALE] = Locale.ZH_CN.value
                if service_name:
                    service_config[constant.SERVICE_INFO][0][constant.NAME] = service_name
                if desc:
                    service_config[constant.SERVICE_INFO][0][constant.SHORT_DESCRIPTION] = desc
                if icon:
                    service_config[constant.SERVICE_INFO][0][constant.IMAGE] = icon
            elif len(service_config.get(constant.SERVICE_INFO)) == 2:
                for service_info in service_config.get(constant.SERVICE_INFO):
                    locale = service_info.get(constant.LOCALE)
                    # 默认只改中文的
                    if locale == Locale.ZH_CN.value:
                        if service_name:
                            service_info[constant.NAME] = service_name
                        if desc:
                            service_info[constant.SHORT_DESCRIPTION] = desc
                        if icon:
                            service_info[constant.IMAGE] = icon
            else:
                raise Exception('service_info should be a list with length <= 2.')

    @staticmethod
    def get_service_info_by_locale(service_info_list, locale):
        if not locale:
            locale = Locale.ZH_CN.value
        for service_info in service_info_list:
            if not isinstance(service_info, dict):
                if service_info.locale == locale:
                    # service_info object转换为dict
                    service_info = service_info.to_map()
                    return service_info
            elif service_info.get(constant.LOCALE) == locale:
                return service_info