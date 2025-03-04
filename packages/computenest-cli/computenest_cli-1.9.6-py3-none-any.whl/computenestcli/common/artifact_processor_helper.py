import os

from computenestcli.common.delivery_type import DeliveryType
from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.common.str_util import StrUtil
from computenestcli.common.util import Util
from computenestcli.base_log import get_user_logger

user_logger = get_user_logger(BUILD_SERVICE)

class ArtifactProcessorHelper:
    def __init__(self):
        pass

    """
    方法功能：
    1. 校验file_path是否存在，file_path可为yaml文件路径或目录路径。
    2. 如果file_path存在且为目录路径，如./wordpress。
       如果delivery_type为DockerCompose，那么自动替换为./wordpress/docker-compose.yaml。
       如果delivery_type为HelmChart，那么自动替换为./wordpress/values.yaml。
    """
    @staticmethod
    def validate_and_replace_file_path(delivery_type, file_path='.'):
        if not os.path.exists(file_path):
            user_logger.error(f"Error: No such file or directory: {file_path}.")
            raise ValueError(f"Error: No such file or directory: {file_path}.")
        # 换成绝对路径
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        # 检查文件路径是否包含 ".yaml" 或 ".yml"
        if file_path.endswith(('.yaml', '.yml')):
            return file_path
        else:
            if delivery_type == DeliveryType.DOCKER_COMPOSE.value:
                file_path = os.path.join(file_path, "docker-compose.yaml")
                # 检测文件是否存在
                if not os.path.exists(file_path):
                    user_logger.error(f"Error: No such file or directory: {file_path}.")
                    raise ValueError(f"Error: No such file or directory: {file_path}.")
                return file_path
            elif delivery_type == DeliveryType.HELM_CHART.value:
                file_path = os.path.join(file_path, "values.yaml")
                # 检测文件是否存在
                if not os.path.exists(file_path):
                    user_logger.error(f"Error: No such file or directory: {file_path}.")
                    raise ValueError(f"Error: No such file or directory: {file_path}.")
                return file_path
            else:
                raise ValueError(f"Error: Invalid delivery_type '{delivery_type}'. "
                                 f"Expected 'DockerCompose' or 'HelmChart'.")

    """
    方法功能：
    输入容器镜像url和地域ID，生成ArtifactBuildType为ContainerImage的config配置。
    该配置可用于将容器镜像上传到对应地域下的计算巢容器镜像仓库。
    """
    @staticmethod
    def generate_config_for_container_image(image_urls, region_id):
        data_config = {
            "Artifact": {}
        }
        for image_url in image_urls:
            split_image_url = StrUtil.format_image_url(image_url).split(':')
            repo_name = split_image_url[0]
            tag = split_image_url[1]
            artifact_key = repo_name.replace('/', '-')
            artifact_name = Util.add_timestamp_to_artifact_name("Acr", artifact_key)
            artifact_config = {
                "ArtifactType": "AcrImage",
                "ArtifactBuildType": "ContainerImage",
                "ArtifactName": artifact_name,
                "Description": artifact_name,
                "ArtifactProperty": {
                    "RepoName": repo_name,
                    "Tag": tag,
                    "RepoType": "Public"
                },
                "ArtifactBuildProperty": {
                    "RegionId": region_id,
                    "SourceContainerImage": image_url
                }
            }
            data_config.get("Artifact").update({artifact_key: artifact_config})
        return data_config