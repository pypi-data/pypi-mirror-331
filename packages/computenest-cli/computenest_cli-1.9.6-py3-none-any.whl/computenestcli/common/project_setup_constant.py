# # # # 生成的项目相对路径 # # # #
# icon资源目录
OUTPUT_ICON_DIR = "resources/icons/"
# 架构图目录
OUTPUT_ARCH_DIR = "resources/architecture/"
# 软件包目录
OUTPUT_PACKAGE_DIR = "resources/artifact_resources/file/"
# Dockerfile文件目录
OUTPUT_DOCKERFILE_DIR = "resources/artifact_resources/acr_image/"
# Docker compose文件目录
OUTPUT_DOCKER_COMPOSE_DIR = "resources/artifact_resources/docker_compose/"
# Helm Chart包目录
OUTPUT_HELM_CHART_DIR = "resources/artifact_resources/helm_chart/"
# ROS模板目录相对路径，暂时先不考虑多模板
OUTPUT_ROS_TEMPLATE_DIR = "ros_templates/"
# docs目录相对路径
OUTPUT_DOCS_DIR = "docs/"

# 默认服务icon
OUTPUT_SERVICE_ICON_NAME = "service_logo.png"
# 默认架构图
DEFAULT_ARCHITECTURE = "architecture.jpg"
# Dockerfile文件名称
OUTPUT_DOCKERFILE_NAME = "Dockerfile"
# ROS模板文件名称
OUTPUT_ROS_TEMPLATE_NAME = "template.yaml"
# config.yaml文件名称
OUTPUT_CONFIG_NAME = "config.yaml"
# 托管版预设参数文件名称
OUTPUT_PRESET_PARAMETERS_NAME = "preset_parameters.yaml"
# README.md文件名称
OUTPUT_README_NAME = "README-en.md"
# index.md
OUTPUT_INDEX_NAME = "index.md"

# # # # 生成项目所需模板与资源的路径信息 # # # #
# 包内资源目录，需要用.这种方式来指定路径
INPUT_ROOT_PATH = "computenestcli.resources.project_generation"
INPUT_ROS_TEMPLATE_ECS_SINGLE_PATH = "computenestcli.resources.project_generation.ros_templates.ecs_single"
INPUT_ROS_TEMPLATE_ECS_CLUSTER_PATH = "computenestcli.resources.project_generation.ros_templates.ecs_cluster"
INPUT_ROS_TEMPLATE_CS_CLUSTER_PATH = "computenestcli.resources.project_generation.ros_templates.cs_cluster"
INPUT_CONFIG_PATH = "computenestcli.resources.project_generation.configs"
INPUT_DOCS_ECS_SINGLE_PATH = "computenestcli.resources.project_generation.docs.ecs_single"
INPUT_DOCS_ECS_CLUSTER_PATH = "computenestcli.resources.project_generation.docs.ecs_cluster"
# icon资源目录名称
INPUT_ICON_DIR = "icons"
# 架构图目录名称
INPUT_ARCH_ECS_SINGLE_DIR = "ecs_single"
INPUT_ARCH_ECS_CLUSTER_DIR = "ecs_cluster"
INPUT_ARCH_PATH = "computenestcli.resources.project_generation.architecture"

# ECS镜像的情况，config.yaml模板名称
INPUT_ECS_IMAGE_CONFIG_NAME = "ecs_image_config.yaml.j2"
# Helm Chart config.yaml模板名称
INPUT_HELM_CHART_CONFIG_NAME = "helm_chart_config.yaml.j2"

# ros_template资源名称
INPUT_SOURCE_CODE_ROS_TEMPLATE_NAME = "source_code.yaml.j2"
INPUT_DOCKERFILE_ROS_TEMPLATE_NAME = "dockerfile.yaml.j2"
INPUT_BUILDPACKS_ROS_TEMPLATE_NAME = "buildpacks.yaml.j2"
INPUT_DOCKER_COMPOSE_ROS_TEMPLATE_NAME = "docker_compose.yaml.j2"
INPUT_HELM_CHART_ROS_TEMPLATE_NAME = "helm_chart.yaml.j2"

# 托管版预设参数模板名称
INPUT_PRESET_PARAMETERS_NAME = "preset_parameters.yaml"
# 传入参数转换为的文件名称
OUTPUT_PARAMETERS_FILE_NAME = ".computenest_parameters.yaml"
# README.md资源名称
INPUT_README_NAME = "README.md"
APP_NAME = "myapp"
# 生成的ros模板中DockerCompose文件目录
DOCKER_COMPOSE_DIR = "/root/application/"

# # # # 参数Key # # # #
# 软件形态
ARTIFACT_SOURCE_TYPE_KEY = "ArtifactSourceType"
# 架构
ARCHITECTURE_KEY = "Arch"
# 源代码路径
SOURCE_CODE_PATH_KEY = "SourceCodePath"
# 安装包路径
PACKAGE_PATH_KEY = "PackagePath"
# 安装包名称
PACKAGE_NAME_KEY = "PackageName"
# Dockerfile路径
DOCKERFILE_PATH_KEY = "DockerFilePath"
# Docker运行的环境变量参数
DOCKER_RUN_ENV_ARGS = "DockerRunEnvArgs"
# Docker Compose路径
DOCKER_COMPOSE_PATH_KEY = "DockerComposeYamlPath"
# override
DOCKER_COMPOSE_OVERRIDE_PATHS_KEY = "DockerComposeOverrideYamlPaths"
# Docker Compose Env 路径
DOCKER_COMPOSE_ENV_PATH_KEY = "DockerComposeEnvPath"
# Docker Compose YAML
DOCKER_COMPOSE_YAML = "DockerComposeYaml"
# 软件安装运行命令
RUN_COMMAND_KEY = "RunCommand"
# Helm Chart目录
HELM_CHART_PATH_KEY = "HelmChartPath"
# Helm Chart Values值
HELM_CHART_VALUES_KEY = "ChartValues"
# 自定义服务参数
CUSTOM_PARAMETERS_KEY = "CustomParameters"
# 服务端口号
SERVICE_PORTS_KEY = "ServicePorts"
# 安全组端口号
SECURITY_GROUP_PORTS_KEY = "SecurityGroupPorts"
# 服务类型
SERVICE_TYPE_KEY = "ServiceType"
# 服务地域
SERVICE_REGION_KEY = "ServiceRegion"
# 可部署地域
DEPLOY_REGION_KEY = "AllowedRegion"
# 架构
ARCH_KEY = "Architecture"
# Ec镜像ID
ECS_IMAGE_ID_KEY = "EcsImageId"
# 端口号，需要映射的容器与宿主机的端口号，例如：8080:8080
PORT_KEY = "Port"
# 仓库名称
REPO_NAME_KEY = "RepoName"
# 仓库全称 TODO:后续统一切换到RepoFullName，不使用RepoName
REPO_FULL_NAME_KEY = "RepoFullName"
# ServiceName
SERVICE_NAME = "ServiceName"
# PreStartCommand
PRE_START_COMMAND_KEY = "PreStartCommand"
# PostStartCommand
POST_START_COMMAND_KEY = "PostStartCommand"
# docker compose环境变量文件的绝对路径
ENV_PATH = "EnvPath"
# AcrImageArtifactParameters
ACR_IMAGE_ARTIFACT_PARAMETERS_KEY = "AcrImageArtifactParameters"
# FileArtifactParameters
FILE_ARTIFACT_PARAMETERS_KEY = "FileArtifactParameters"
# SourcePaths
SOURCE_PATHS_KEY = "SourcePaths"
# Target
TARGET_KEY = "Target"
# 用于ECS镜像构建的命令Key
ECS_IMAGE_BUILDER_COMMAND_CONTENT_KEY = "EcsImageBuilderCommandContent"
# 构建出的镜像的名称key
DOCKER_IMAGE_NAME_KEY = "DockerImageName"

# 阿里容器镜像仓库后缀
ALI_DOCKER_REPO_HOST_SUFFIX = "aliyuncs.com"
# 镜像ID
IMAGE_ID_KEY = "ImageId"
# 基础镜像的oos转译前缀
OOS_TRANSLATE_IMAGE_PREFIX = "resolve:oos:aliyun/services/"
# GPU镜像ID
GPU_ECS_SOURCE_IMAGE_ID = "aliyun/services/computenest/images/aliyun_3_2104_docker_26_gpu_cuda_12_4_60g"
NeedGPU_KEY = "NeedGPU"

#执行指令时日志过滤Filter
COMMON_LOG_FILTER = " 2>&1 | stdbuf -oL grep -viE 'Downloading|sha256|extracting|KiB|Downloaded' "
