from enum import Enum


class DeliveryType(Enum):
    """
    国外开源镜像需要上传到计算巢容器镜像仓库，让国内用户也能拉取镜像
    支持自动上传镜像的部署类型，包括：DockerCompose、HelmChart
    """
    DOCKER_COMPOSE = "DockerCompose"
    HELM_CHART = "HelmChart"
