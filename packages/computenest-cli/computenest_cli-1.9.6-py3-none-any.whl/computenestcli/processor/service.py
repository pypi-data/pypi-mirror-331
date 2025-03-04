import os
import json
from pathlib import Path
from computenestcli.common.locale import Locale
from ruamel.yaml import YAML
from Tea.exceptions import TeaException

from computenestcli.common.docker_compose_helper import DockerComposeHelper
from computenestcli.common.file_util import FileUtil
from computenestcli.common.terraform_util import TerraformUtil
from computenestcli.common.logging_constant import SPLIT_LINE, BUILD_SERVICE
from computenestcli.common.service_processor_helper import ServiceProcessorHelper
from computenestcli.common.upload_file_type import UploadFileType
from computenestcli.service.supplier import SupplierService
from computenestcli.common import constant, project_setup_constant
from computenestcli.common.export_type import ExportType
from computenestcli.common.util import Util
from computenestcli.processor.artifact import ArtifactProcessor
from computenestcli.service.file import FileService
from computenestcli.service.credentials import CredentialsService
from computenestcli.common.service_type import ServiceType
from computenestcli.base_log import get_developer_logger
from computenestcli.base_log import get_user_logger

developer_logger = get_developer_logger()
user_logger = get_user_logger(BUILD_SERVICE)
FILE = 'file'
DRAFT = 'draft'
SERVICE_NOT_FOUND = 'EntityNotExist.Service'
CUSTOM_OPERATIONS = 'CustomOperations'
ACTIONS = 'Actions'
TEMPLATE_URL = 'TemplateUrl'
SHARE_TYPE = 'ShareType'
APPROVAL_TYPE = 'ApprovalType'
ALWAYS_LATEST = 'AlwaysLatest'
SECURITY_GROUPS = 'SecurityGroups'
HIDDEN_PARAMETER_KEYS = 'HiddenParameterKeys'
PREDEFINED_PARAMETERS = 'PredefinedParameters'
NETWORK_METADATA = 'NetworkMetadata'
DEPLOY_TIME_OUT = 'DeployTimeout'
UPDATE_INFO = 'UpdateInfo'
METADATA = 'Metadata'
PARAMETER_GROUPS = 'ParameterGroups'
PARAMETER_CONFIGS = "ParameterConfigs"
DEFAULT_VALUE = 'DefaultValue'


class ServiceProcessor:

    def __init__(self, context):
        self.context = context
        self.config_dir = None

    def _get_service(self, service_id, service_version):
        service = SupplierService.get_service(self.context, service_id, service_version)
        if service.body.service_id is None:
            raise TeaException({
                'code': SERVICE_NOT_FOUND,
                'message': 'Service does not exist'
            })
        return service

    def _replace_artifact_data(self, artifact_relations_config, actifact_config):
        for artifact_info in artifact_relations_config.values():
            artifact_id_placeholder = artifact_info.get(constant.ARTIFACT_ID)
            artifact_id_match = Util.regular_expression(artifact_id_placeholder)
            # 将占位符${Artifact.Artifact_x.ArtifactId}解析并输出dict
            artifact_id = actifact_config.get(artifact_id_match[1]).get(artifact_id_match[2])
            # [0][1][2]为刚才解析出得占位符的分解，即Artifact，Artifact_x，ArtifactId
            artifact_info[constant.ARTIFACT_ID] = artifact_id
            artifact_info[constant.ARTIFACT_VERSION] = "draft"

    def _replace_file_path_with_url(self, file_uri, upload_file_type=None):
        # 如果是http路径那么直接返回即可
        if file_uri.startswith("http"):
            return file_uri

        # 如果是相对路径
        if not file_uri.startswith("/"):
            # 判断self.config_dir和file_uri是否有重复路径
            if not file_uri.startswith(self.config_dir):
                file_uri = os.path.join(self.config_dir, file_uri)
        file_name = os.path.basename(file_uri)
        upload_credentials = CredentialsService.get_upload_credentials(self.context, file_name,
                                                                       upload_file_type.access_type)
        file_url = FileService.put_file(upload_credentials, file_uri, FILE)
        return file_url

    def _replace_parameters(self, content, parameters):
        new_content = content
        if isinstance(content, dict):
            new_content = {}
            for key, value in content.items():
                new_key = self._replace_parameters(key, parameters)
                new_value = self._replace_parameters(value, parameters)
                new_content[new_key] = new_value
        elif isinstance(content, list):
            new_content = []
            for value in content:
                new_value = self._replace_parameters(value, parameters)
                new_content.append(new_value)
        elif isinstance(content, str):
            parameter_match = Util.regular_expression(content)
            if parameter_match and len(parameter_match) == 1 and parameter_match[0] in parameters:
                new_content = parameters.get(parameter_match[0])
            else:
                new_content = content
        elif isinstance(content, bool):
            new_content = content
        return new_content

    def _delete_field(self, data, field):
        if isinstance(data, dict):
            for key in list(data.keys()):
                if key == field:
                    del data[key]
                else:
                    self._delete_field(data[key], field)
        elif isinstance(data, list):
            for item in data:
                self._delete_field(item, field)

    # 判断是需要创建服务还是更新服务。返回True表示创建服务，返回False表示更新服务
    def _should_create_service(self, service_id, service_name):
        if service_id:
            # 如果有service_id传入，那么更新服务
            try:
                SupplierService.get_service(self.context, service_id, DRAFT)
                return False
            except TeaException as e:
                if e.code == "EntityNotExist.Service":
                    return True
        elif service_name:
            # 没有draft版本，就走创建逻辑,有draft版本，默认为更新
            service_list = SupplierService.list_service(self.context, service_name, [DRAFT])
            if len(service_list.body.services) == 0:
                # 兼容原逻辑。如果没有传入service_id,也没找到对应名称的服务，那么创建服务
                return True
            else:
                # 如果有传入service_name，但是找到了对应名称的服务，那么更新服务
                return False
        else:
            raise Exception('Neither service_id nor service_name is provided.')

    @Util.measure_time
    def import_command(self, data_config, file_path, update_artifact, service_info, service_id, service_name='',
                       version_name='', icon='', desc='', parameters={}):
        if parameters:
            data_config = self._replace_parameters(data_config, parameters)

        service_config = data_config[constant.SERVICE]
        self.config_dir = os.path.dirname(file_path)

        ServiceProcessorHelper.pre_process_service_info(service_config, service_info, service_name, version_name, icon,
                                                        desc)
        # 读取默认环境变量文件内容，补充入参数管理default里
        operation_metadata = data_config.get(constant.SERVICE).get(constant.OPERATION_METADATA, {})
        if operation_metadata and PARAMETER_CONFIGS in operation_metadata:
            parameter_config = operation_metadata.get(PARAMETER_CONFIGS, [])[0]
            if isinstance(parameter_config, dict):
                for group in parameter_config[METADATA][PARAMETER_GROUPS]:
                    relative_path = group.get(constant.DEFAULT_ENV_FILE_PATH)
                    # 将相对路径替换成绝对路径
                    env_file_path = os.path.join(os.path.dirname(self.config_dir), os.path.abspath(relative_path))
                    env_content = DockerComposeHelper.get_env_content(env_file_path)
                    group[DEFAULT_VALUE] = env_content

        if constant.DEPLOY_METADATA in service_config:
            deploy_metadata_config = service_config[constant.DEPLOY_METADATA]
            if data_config.get(constant.ARTIFACT):
                artifact_processor = ArtifactProcessor(self.context)
                data_artifact = artifact_processor.process(data_config, file_path, update_artifact, version_name)
                # 遍历部署物关联映射，进行部署物替换
                support_artifact_relation_types = [constant.ARTIFACT_RELATION, constant.FILE_ARTIFACT_RELATION,
                                                   constant.ACR_IMAGE_ARTIFACT_RELATION,
                                                   constant.HELM_CHART_ARTIFACT_RELATION]
                for relation_type, artifact_relations_config in \
                        deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA, {}).items():
                    if relation_type in support_artifact_relation_types:
                        self._replace_artifact_data(artifact_relations_config, data_artifact)
        # 获取服务id
        if not service_id:
            # service_name 优先取传入的service_name，其次取service_info中的，最后取config.yaml中的
            if not service_name:
                service_info_list = service_config.get(constant.SERVICE_INFO)
                if service_info_list and len(service_info_list) > 0:
                    service_name = service_info_list[0].get(constant.NAME)
            if service_name:
                service_list = SupplierService.list_service(self.context, service_name, None)
                if service_list.body.services:
                    service_id = service_list.body.services[0].service_id
        if service_config.get(constant.OPERATION_METADATA):
            # 判断CUSTOM_OPERATIONS是否存在
            if CUSTOM_OPERATIONS in service_config[constant.OPERATION_METADATA]:
                for operation_template in service_config[constant.OPERATION_METADATA][CUSTOM_OPERATIONS][ACTIONS]:
                    # 将相对路径替换成绝对路径
                    operation_template_path = os.path.join(self.config_dir,
                                                           operation_template.get(TEMPLATE_URL))
                    operation_template[TEMPLATE_URL] = self._replace_file_path_with_url(operation_template_path,
                                                                                        UploadFileType.OOS_TEMPLATE)
        if self._should_create_service(service_id, service_name):
            # 将服务logo的本地路径替换成Url
            self._replace_service_info(service_config, None, icon)
            # 将模版文件的本地路径替换成url
            if deploy_metadata_config.get(constant.TEMPLATE_CONFIGS):
                self._update_deploy_type_and_trans_terraform_template(service_config, deploy_metadata_config.get(constant.TEMPLATE_CONFIGS))
                for template in deploy_metadata_config.get(constant.TEMPLATE_CONFIGS):
                    # 将相对路径替换成绝对路径
                    self._replace_config_file_to_url(template, constant.URL, UploadFileType.ROS_TEMPLATE)
                    self._replace_config_file_to_url(template, constant.ARCHITECTURE_DIAGRAM_URL,
                                                     UploadFileType.ARCHITECTURE_DIAGRAM)
            # 将SupplierDeployMetadata的路径做替换
            if constant.SUPPLIER_DEPLOY_METADATA in deploy_metadata_config and \
                    constant.SUPPLIER_TEMPLATE_CONFIGS in deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA):
                supplier_deploy_metadata = deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA)
                # terraform类型的模板转换成ros模板
                self._update_deploy_type_and_trans_terraform_template(service_config, supplier_deploy_metadata.get(constant.SUPPLIER_TEMPLATE_CONFIGS))
                for supplier_template in supplier_deploy_metadata.get(constant.SUPPLIER_TEMPLATE_CONFIGS):
                    self._replace_config_file_to_url(supplier_template, constant.URL, UploadFileType.ROS_TEMPLATE)
            SupplierService.create_service(self.context, service_config, service_id, service_name)
        else:
            draft_service = self._get_service(service_id, DRAFT)
            self._replace_service_info(service_config, draft_service.body.service_infos, icon)
            service_deploy_metadata = json.loads(draft_service.body.deploy_metadata)

            # TemplateConfigs服务模版列表配置存在
            if constant.TEMPLATE_CONFIGS in deploy_metadata_config:
                service_template_list = service_deploy_metadata.get(constant.TEMPLATE_CONFIGS, [])
                config_template_list = deploy_metadata_config.get(constant.TEMPLATE_CONFIGS)
                # 更新服务也需要转换terraform
                self._update_deploy_type_and_trans_terraform_template(service_config, config_template_list)

                self._compare_and_replace_template_file(service_template_list, config_template_list,
                                                        constant.URL)
                self._compare_and_replace_template_file(service_template_list, config_template_list,
                                                        constant.ARCHITECTURE_DIAGRAM_URL)

            # SupplierDeployMetadata配置存在且有模版列表配置
            if constant.SUPPLIER_DEPLOY_METADATA in deploy_metadata_config and \
                    constant.SUPPLIER_TEMPLATE_CONFIGS in deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA):
                supplier_deploy_metadata = deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA)
                config_supplier_template_list = supplier_deploy_metadata.get(constant.SUPPLIER_TEMPLATE_CONFIGS)
                # 已存在的服务的supplier_template_configs
                service_supplier_template_list = service_deploy_metadata.get(constant.SUPPLIER_DEPLOY_METADATA, {}) \
                    .get(constant.SUPPLIER_TEMPLATE_CONFIGS, [])
                # 更新服务的时候也需要转换terraform
                self._update_deploy_type_and_trans_terraform_template(service_config, config_supplier_template_list)
                self._compare_and_replace_template_file(service_supplier_template_list, config_supplier_template_list,
                                                        constant.URL)

            SupplierService.update_service(self.context, service_config, service_id, service_name)

    # 根据serviceConfig，判断是否是terraform部署方式，若是，则进行转换
    def _update_deploy_type_and_trans_terraform_template(self, service_config, config_template_list):
        if not service_config.get(constant.DEPLOY_TYPE):
            terraform_path = TerraformUtil.exist_terraform_structure(self.config_dir)
            if isinstance(terraform_path, str):
                service_config[constant.DEPLOY_TYPE] = constant.TERRAFORM_DEPLOY_TYPE
                for template in config_template_list:
                    TerraformUtil.trans_terraform_to_ros(terraform_path, template, constant.URL)

    def _replace_service_info(self, service_config, service_infos_existed=None, icon=None):
        def update_service_info_attribute(service_info, service_infos_existed, attribute):
            if not service_info.get(attribute):
                locale = service_info.get(constant.LOCALE)
                service_info_existed = ServiceProcessorHelper.get_service_info_by_locale(service_infos_existed,
                                                                                         locale)

                if service_info_existed:
                    service_info[attribute] = service_info_existed.get(attribute)

        service_infos = service_config.get(constant.SERVICE_INFO)
        for service_info in service_infos:
            icon_uri = service_info.get(constant.IMAGE)
            if icon_uri:
                service_info[constant.IMAGE] = self._replace_file_path_with_url(icon_uri, UploadFileType.SERVICE_ICON)
            if service_infos_existed:
                # 1. 如果直接传入某个参数，则采用该参数值(在pre_process_service_info已处理)
                # 2. 如果没有传入某个参数，则从config.yaml中的service_info中获取(在pre_process_service_info已处理)
                # 3. 如果config.yaml中没有传入service_info，则直接采用原服务的icon、service_name与desc
                for attribute in [constant.IMAGE, constant.NAME, constant.SHORT_DESCRIPTION]:
                    update_service_info_attribute(service_info, service_infos_existed, attribute)

    """
    对比服务原有模版配置，字段对应值相同则不进行文件上传操作，直接使用原有链接
    service_template_list: 原有服务模版列表
    config_template_list: 配置服务模版列表
    work_dir: 执行路径, 结合url_key对应路径算出
    url_key: 文件配置key
    """

    def _compare_and_replace_template_file(self, service_template_list, config_template_list, url_key):
        name_url_mapping = {template[constant.NAME]: template.get(url_key) for template in
                            service_template_list}
        # 检查模版文件是否重复，重复则不再上传，直接使用原有Url
        for template in config_template_list:
            service_template_value = name_url_mapping.get(template[constant.NAME])
            if service_template_value:
                if not template.get(url_key):
                    template[url_key] = service_template_value
                    continue
                # 将相对路径替换成绝对路径
                template_path = os.path.join(self.config_dir, template.get(url_key))
                template[url_key] = self._check_and_get_url(service_template_value, template_path)
            else:
                self._replace_config_file_to_url(template, url_key, UploadFileType.ROS_TEMPLATE)

    """
    对比已有链接和文件内容是否相同，相同则返回链接，不相同则返回文件上传生成链接
    """

    def _check_and_get_url(self, existed_url, file_path):
        is_same_content = FileService.check_file_repeat(existed_url, file_path)
        if is_same_content:
            return existed_url.split('?')[0] if '?' in existed_url else existed_url

        return self._replace_file_path_with_url(file_path, UploadFileType.ROS_TEMPLATE)

    """
    将配置字典中的文件路径替换为oss url
    config_dict：配置字典
    path_key: 文件相对路径key
    """

    def _replace_config_file_to_url(self, config_dict, path_key, upload_file_type=None):
        if config_dict.get(path_key):
            url_path = os.path.join(self.config_dir, config_dict.get(path_key))
            config_dict[path_key] = self._replace_file_path_with_url(url_path, upload_file_type)


    def export_command(self, service_id, version_name, export_type, output_base_dir, export_project_name,
                       export_file_name):
        if not output_base_dir:
            output_base_dir = os.getcwd()
        output_base_dir = os.path.abspath(output_base_dir)
        if ExportType.CONFIG_ONLY.name == export_type:
            user_logger.info("export_type is CONFIG_ONLY")
            if not export_file_name:
                export_file_name = constant.DEFAULT_EXPORT_FILE_NAME
            self._export_config(service_id, version_name, output_base_dir, export_file_name)
        elif ExportType.FULL_SERVICE.name in export_type:
            user_logger.info("export_type is FULL_SERVICE")
            self._export_service(service_id, version_name, output_base_dir, export_project_name)
        else:
            raise Exception("export_type is not supported!")

    def _get_service_detail(self, service_id, service_version):
        get_service_response = SupplierService.get_service(self.context, service_id, service_version)
        service_body = get_service_response.body
        deploy_metadata = json.loads(service_body.deploy_metadata)
        operation_metadata = json.loads(service_body.operation_metadata)
        approval_type = service_body.approval_type
        share_type = service_body.share_type
        service_type = service_body.service_type
        deploy_type = service_body.deploy_type
        # self._delete_field(deploy_metadata, NETWORK_METADATA)
        # self._delete_field(deploy_metadata, DEPLOY_TIME_OUT)
        self._delete_field(deploy_metadata, ALWAYS_LATEST)
        if ServiceType.MANAGED.value == service_type:
            self._delete_field(deploy_metadata, constant.TEMPLATE_CONFIGS)
        else:
            for config in deploy_metadata[constant.TEMPLATE_CONFIGS]:
                self._delete_field(config, SECURITY_GROUPS)
                # self._delete_field(config, HIDDEN_PARAMETER_KEYS)
                # self._delete_field(config, PREDEFINED_PARAMETERS)
                self._delete_field(config, UPDATE_INFO)

        service_info_list = [service_info.to_map() for service_info in service_body.service_infos]
        parameters = {
            constant.DEPLOY_TYPE: deploy_type,
            constant.DEPLOY_METADATA: deploy_metadata,
            constant.OPERATION_METADATA: operation_metadata,
            constant.SERVICE_TYPE: service_type,
            constant.SERVICE_INFO: service_info_list,
            constant.SHARE_TYPE: share_type,
            constant.APPROVAL_TYPE: approval_type
        }

        service = {
            constant.SERVICE: parameters
        }
        return service, deploy_metadata

    def _export_config(self, service_id, service_version, output_path, export_file_name):
        config_yaml = self._get_service_config(service_id, service_version)
        self._dump_config(config_yaml, output_path, export_file_name)

    def _get_service_config(self, service_id, service_version):
        service_config, deploy_metadata = self._get_service_detail(service_id, service_version)
        supplier_deploy_metadata = deploy_metadata.get(constant.SUPPLIER_DEPLOY_METADATA)

        if supplier_deploy_metadata:
            service_config.setdefault(constant.ARTIFACT, {})
            artifact = ArtifactProcessor(self.context)

            relation_types = [
                constant.ARTIFACT_RELATION,
                constant.HELM_CHART_ARTIFACT_RELATION,
                constant.FILE_ARTIFACT_RELATION,
                constant.ACR_IMAGE_ARTIFACT_RELATION
            ]

            i = 1
            for artifact_relation_type in supplier_deploy_metadata:
                if artifact_relation_type in relation_types:
                    for image_key in supplier_deploy_metadata.get(artifact_relation_type, {}):
                        artifact_key = f"{constant.ARTIFACT}_{i}"
                        i += 1
                        artifact_info = supplier_deploy_metadata[artifact_relation_type].get(image_key, {})
                        artifact_id = artifact_info.get(constant.ARTIFACT_ID)
                        artifact_version = artifact_info.get(constant.ARTIFACT_VERSION)

                        if artifact_id and artifact_version:
                            artifact_key_detail = artifact.get_artifact_detail(artifact_id, artifact_version)
                            service_config[constant.ARTIFACT][artifact_key] = artifact_key_detail

        return service_config

    def _export_service(self, service_id, version_name, output_base_dir, export_project_name):
        """
        导出整个服务，包括如下
        ├── resources                   - 服务资源文件
        │   ├── icons
        │   │   └── logo.png            - 服务logo
        │   ├── architecture
        │   │   └── architecture.jpg    - 架构图
        │   └── artifact_resources      - 部署物相关资源文件
        │       └── file                - 文件部署物目录
        │           └── artifact.zip
        ├── ros_templates               - 服务ROS模板，可以有多个
        │   └── template.yaml           - 示例ROS模板
        ├── config.yaml                 - 服务配置文件
        """
        service_config = self._get_service_config(service_id, version_name)
        if not output_base_dir:
            output_base_dir = os.getcwd()
        if export_project_name:
            output_base_dir = os.path.join(output_base_dir, export_project_name)

        os.makedirs(output_base_dir, exist_ok=True)
        self._replace_ros_template(service_config, output_base_dir)
        self._replace_service_logo(service_config, output_base_dir)
        self._replace_artifact(service_config, output_base_dir)
        self._replace_to_placeholder(service_config)
        # self._generate_preset_parameters(service_config, output_base_dir)
        self._dump_config(service_config, output_base_dir)
        user_logger.info("===========================")
        user_logger.info("Successfully export the service!")
        user_logger.info(f"The service id: {service_id}")
        user_logger.info(f"The service version: {version_name}")
        user_logger.info(f"The output path: {output_base_dir}\n")
        user_logger.info("===========================")

    @staticmethod
    def _replace_to_placeholder(service_config):
        # 替换ArtifactId与ArtifactVersion
        supplier_deploy_metadata = service_config.get(constant.SERVICE, {}).get(constant.DEPLOY_METADATA, {}).get(
            constant.SUPPLIER_DEPLOY_METADATA, {})

        artifact_num = 1
        for relation_type in supplier_deploy_metadata:
            if relation_type in (
                    constant.ARTIFACT_RELATION,
                    constant.HELM_CHART_ARTIFACT_RELATION,
                    constant.FILE_ARTIFACT_RELATION,
                    constant.ACR_IMAGE_ARTIFACT_RELATION
            ):
                relation_data = supplier_deploy_metadata.get(relation_type, {})
                for artifact_relation_key in relation_data:
                    artifact_object = relation_data.get(artifact_relation_key, {})
                    if constant.ARTIFACT_ID in artifact_object and constant.ARTIFACT_VERSION in artifact_object:
                        artifact_object[constant.ARTIFACT_ID] = f"${{Artifact.Artifact_{artifact_num}.ArtifactId}}"
                        artifact_object[
                            constant.ARTIFACT_VERSION] = f"${{Artifact.Artifact_{artifact_num}.ArtifactVersion}}"
                        artifact_num += 1

        # 托管版暂不支持
        # service_config._replace_managed_parameters_to_placeholder(service_config)

        user_logger.info("Replace artifact and managed parameters to placeholder")

    @staticmethod
    def _replace_managed_parameters_to_placeholder(service_config):
        supplier_deploy_metadata = service_config.get(constant.SERVICE, {}).get(constant.DEPLOY_METADATA, {}).get(
            constant.SUPPLIER_DEPLOY_METADATA, {})
        # 替换托管版的参数，包括RoleName、ParameterMappings中的内容。目前仅支持替换RegionId，VpcId等网络参数
        service_type = service_config.get(constant.SERVICE, {}).get(constant.SERVICE_TYPE)
        if service_type == ServiceType.MANAGED.value:
            supplier_deploy_metadata[constant.ROLE_NAME] = "${RoleName}"
            supplier_template_configs = supplier_deploy_metadata.get(constant.SUPPLIER_TEMPLATE_CONFIGS, [])
            for supplier_template_config in supplier_template_configs:
                if constant.PARAMETER_MAPPINGS in supplier_template_config:
                    parameter_mappings = supplier_template_config.get(constant.PARAMETER_MAPPINGS)
                    for parameter_mapping in parameter_mappings:
                        parameter_key = parameter_mapping[constant.PARAMETER_KEY]
                        if constant.REGION_ID == parameter_key:
                            parameter_value_mapping = parameter_mapping[constant.PARAMETER_VALUE_MAPPING]
                            # 获取region_name并替换为${RegionId}
                            region_name = next(iter(parameter_value_mapping))
                            parameter_value_mapping["${RegionId}"] = parameter_value_mapping.pop(region_name)

                            # 替换内部参数
                            parameters = parameter_value_mapping["${RegionId}"]["Parameters"]
                            parameters["VpcId"] = "${VpcId}"
                            parameters["ZoneId"] = "${ZoneId}"
                            parameters["VSwitchId"] = "${VSwitchId}"

    @staticmethod
    def _generate_preset_parameters(service_config, output_base_dir):
        service_type = service_config.get(constant.SERVICE, {}).get(constant.SERVICE_TYPE)
        if service_type == ServiceType.MANAGED.value:
            FileUtil.copy_from_package(project_setup_constant.INPUT_ROOT_PATH,
                                       project_setup_constant.INPUT_PRESET_PARAMETERS_NAME, Path(output_base_dir))
        user_logger.info("Generate preset parameters")

    @staticmethod
    def _dump_config(service_config, output_base_dir, export_file_name='config.yaml'):
        os.makedirs(output_base_dir, exist_ok=True)
        file_path = os.path.join(output_base_dir, export_file_name)
        yaml = YAML(typ='rt')
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.width = 180
        with open(file_path, "w") as file:
            yaml.dump(service_config, file)
        user_logger.info("===========================")
        user_logger.info(f"Successfully export the {export_file_name}!")
        user_logger.info(f"The file path: {file_path}")
        user_logger.info("===========================")

    @staticmethod
    def _replace_ros_template(service_config, project_base_dir):
        user_logger.info("Replace ROS template")
        template_base_dir = os.path.join(project_base_dir, 'ros_templates')
        os.makedirs(template_base_dir, exist_ok=True)

        service = service_config.get(constant.SERVICE)
        service_type = service.get(constant.SERVICE_TYPE)

        if service_type == ServiceType.PRIVATE.value:
            template_configs = service.get(constant.DEPLOY_METADATA, {}).get(constant.TEMPLATE_CONFIGS, [])
        elif service_type == ServiceType.MANAGED.value:
            template_configs = service.get(constant.DEPLOY_METADATA, {}).get(constant.SUPPLIER_DEPLOY_METADATA, {}).get(
                constant.SUPPLIER_TEMPLATE_CONFIGS, [])
        else:
            raise ValueError(f"Service type: {service_type} is not supported!")

        for i, template_config in enumerate(template_configs, start=1):
            template_name = template_config.get(constant.NAME)
            template_url = template_config.get(constant.URL)
            if template_url:
                developer_logger.info(f"Template name: {template_name}, Template URL: {template_url}")
                local_filename = f'template{i}.yaml'
                template_config[constant.URL] = os.path.join('ros_templates', local_filename)
                FileService.download_file(template_url, local_filename=local_filename,
                                          output_base_dir=template_base_dir)
            else:
                user_logger.info(f"Warning: Template URL for {template_name} is missing.")

    @staticmethod
    def _replace_service_logo(service_config, project_base_dir):
        user_logger.info("Replace service logo")
        service_logo_dir = os.path.join(project_base_dir, 'resources', 'icons')
        os.makedirs(service_logo_dir, exist_ok=True)

        service = service_config.get(constant.SERVICE)
        service_info_list = service.get(constant.SERVICE_INFO, {})
        for service_info in service_info_list:
            image_url = service_info.get(constant.IMAGE)
            locale = service_info.get(constant.LOCALE)
            if not locale:
                locale = Locale.ZH_CN.value
            if image_url:
                service_info[constant.IMAGE] = os.path.join('resources', 'icons', f'service_logo_{locale}.png')
                FileService.download_file(image_url, local_filename='service_logo.png',
                                          output_base_dir=service_logo_dir)
            else:
                user_logger.info("Warning: Service logo URL is missing.")

    @staticmethod
    def _replace_artifact(service_config, output_base_dir):
        user_logger.info("Replace artifact")
        artifact_base_dir = os.path.join(output_base_dir, 'resources', 'artifact_resources', 'file')
        os.makedirs(artifact_base_dir, exist_ok=True)

        artifacts = service_config.get(constant.ARTIFACT, {})
        for key, value in artifacts.items():
            url = value.get('ArtifactProperty', {}).get('Url')
            if url:
                developer_logger.info(f"{key}: {url}")
                filename = FileService.download_file(url, output_base_dir=artifact_base_dir)
                developer_logger.info(f"fileName: {filename}")
                value['ArtifactProperty']['Url'] = os.path.join('resources', 'artifact_resources', 'file', filename)
            else:
                user_logger.info(f"Warning: URL for artifact {key} is missing.")