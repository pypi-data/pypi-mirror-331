import time
import json
import os
import re
from concurrent.futures.thread import ThreadPoolExecutor

from Tea.exceptions import TeaException

from computenestcli.common.artifact_processor_helper import ArtifactProcessorHelper
from computenestcli.common.decorator import retry_on_exception
from computenestcli.processor.deliver_image.deliver_image_manager import DeliverImageManager
from computenestcli.common.logging_constant import LOGGING_CLOSURE_NAME, BUILD_SERVICE
from computenestcli.exception.cli_common_exception import CliCommonException
from computenestcli.service.artifact import ArtifactService
from computenestcli.service.artifact import ARTIFACT_VERSION_NOT_FOUND
from computenestcli.service.file import FileService
from computenestcli.service.credentials import CredentialsService
from computenestcli.common.util import Util
from computenestcli.processor.image import ImageProcessor
from computenestcli.common import constant
from computenestcli.common.context import Context
from computenestcli.base_log import get_user_logger, log_monitor

user_logger = get_user_logger(BUILD_SERVICE)
TRUE = 'True'
FALSE = 'False'
UPDATE_ARTIFACT = 'UpdateArtifact'
CREATED = 'Created'
CREATE_FAILED = 'CreateFailed'
AVAILABLE = 'Available'
DELIVERING = 'Delivering'
DATA = 'data'
RESULT = 'result'
IMAGE_BUILDER = 'ImageBuilder'
ACR_IMAGE_BUILDER = 'AcrImageBuilder'
HELM_CHART_BUILDER = 'HelmChartBuilder'
ARTIFACT = 'artifact'
DRAFT = 'draft'
REGION_ID = 'regionId'
COMMAND_CONTENT = 'CommandContent'
ENTITY_ALREADY_EXIST_DRAFT_ARTIFACT = 'EntityAlreadyExist.DraftArtifact'
ARTIFACT_STATUS_NOT_SUPPORT_OPERATION = 'OperationDenied'


class ArtifactProcessor:

    def __init__(self, context):
        self.context = context
        self.user_logger = get_user_logger(BUILD_SERVICE)

    def _get_file_artifact_url(self, artifact_name):
        get_artifact_data = json.loads(ArtifactService.get_artifact(self.context, artifact_name).body.artifact_property)
        url = get_artifact_data.get(constant.URL)
        return url

    def _create_image_from_image_builder(self, config, artifact_config):
        image_builder_config = config.get(IMAGE_BUILDER)
        id_image = artifact_config.get(constant.ARTIFACT_PROPERTY).get(constant.IMAGE_ID)
        id_image_match = Util.regular_expression(id_image)
        data_image_oos = image_builder_config.get(id_image_match[1])
        region_id = data_image_oos[constant.REGION_ID]
        command_content = data_image_oos[COMMAND_CONTENT]
        # 识别命令语句中的占位符
        pattern = r'\$\{Artifact\.(.*?)\.ArtifactProperty\.Url\}'
        matches = re.findall(pattern, command_content)
        if matches:
            artifact_key = matches[0].strip()
            artifact_name = config[constant.ARTIFACT].get(artifact_key, {}).get(constant.ARTIFACT_NAME)
            url = self._get_file_artifact_url(artifact_name)
            parts = url.split("/")
            # 截取文件部署物下载链接的后半部分
            artifact_url = parts[-2] + "/" + parts[-1]
            placeholder = f'${{Artifact.{artifact_key}.ArtifactProperty.Url}}'
            # 替换真正的url
            command_content = command_content.replace(placeholder, artifact_url)
            data_image_oos[COMMAND_CONTENT] = command_content
        data_image_oos = Util.lowercase_first_letter(data_image_oos)
        region_id_image = data_image_oos[REGION_ID]
        image_context = Context(region_id_image, self.context.credentials)
        image_processor = ImageProcessor(image_context)
        return region_id, image_processor.process_image(data_image_oos)

    '''
    根据acrImageBuilder构造容器镜像部署物
    service_config为整个服务的配置，对应的acrImageBuilder结构如下：
    AcrImageBuilder:
      AcrImage_VcControllerManager:
        BuilderType: DockerRepo
        DockerRepoUrl: 'volcanosh/vc-controller-manager:v1.9.0'
        # DockerFilePath: 'resources/artifact_resources/acr_image/Dockerfile'
        RepoName: volcanosh/vc-controller-manager
        Tag: v1.9.0
        
    artifact_config对应的是单个部署物的配置，只包含value部分，对应的结构如下：
    Artifact_AcrImage_VcControllerManager:
      ArtifactType: AcrImage
      ArtifactName: VcControllerManager
      Description: VcControllerManager AcrImage部署物
      ArtifactProperty:
        RepoName: ${AcrImageBuilder.AcrImage_VcControllerManager.RepoName}
        Tag: ${AcrImageBuilder.AcrImage_VcControllerManager.Tag}
    '''

    def _create_acrimage_from_acrimage_builder(self, service_config, artifact_config, file_path_config):
        try:
            artifact_type = artifact_config.get(constant.ARTIFACT_TYPE)
            image_processor = ImageProcessor(self.context)
            acr_image_builder_dict = service_config.get(ACR_IMAGE_BUILDER)
            repo_name_var = artifact_config.get(constant.ARTIFACT_PROPERTY).get(constant.REPO_NAME)
            acr_image_builder_key = Util.regular_expression(repo_name_var)[1]
            acr_image_builder = acr_image_builder_dict.get(acr_image_builder_key)
            file_path = os.path.dirname(file_path_config)
            acr_image_name = acr_image_builder[constant.REPO_NAME]
            acr_image_tag = acr_image_builder[constant.TAG]
            build_type = acr_image_builder.get(constant.BUILD_TYPE)
            build_args = acr_image_builder.get(constant.DOCKER_BUILD_ARGS)
            if build_type == constant.DOCKER_REPO_TYPE:
                docker_repo_url = acr_image_builder[constant.DOCKER_REPO_URL]
                image_processor.process_acr_image(acr_image_name, acr_image_tag, file_path, docker_repo_url, build_type,
                                                  build_args, dockerfile_path=None)
                repo_id = self._get_repo_id(artifact_type, acr_image_name)
            elif acr_image_builder.get(constant.DOCKER_FILE_PATH):
                dockerfile_path = acr_image_builder[constant.DOCKER_FILE_PATH]
                file_path = os.path.abspath(file_path)
                file_path = os.path.dirname(file_path)
                image_processor.process_acr_image(acr_image_name, acr_image_tag, file_path,
                                                  None, constant.DOCKER_FILE_TYPE, build_args, dockerfile_path)
                repo_id = self._get_repo_id(artifact_type, acr_image_name)
            else:
                # 对应的容器镜像已上传到计算巢，校验是否存在
                repo_id = self._get_exist_acr_image_repo_id(artifact_type, acr_image_name, acr_image_tag)
        except FileNotFoundError as e:
            # 使用 logger.exception() 记录错误信息
            user_logger.error("An error occurred while trying to open the file.")
            raise
        return acr_image_name, repo_id, acr_image_tag

    def _get_repo_id(self, artifact_type, acr_image_name):
        response_body = ArtifactService.list_acr_image_repositories(self.context, artifact_type, acr_image_name).body
        if response_body and response_body.repositories:
            for repository in response_body.repositories:
                if repository.repo_name == acr_image_name:
                    return repository.repo_id
        raise Exception(f"No Repo found,repo_name: {acr_image_name}")

    def _create_helmchart_from_helmchart_builder(self, service_config, artifact_config, file_path_config):
        artifact_type = artifact_config.get(constant.ARTIFACT_TYPE)
        image_processor = ImageProcessor(self.context)
        helm_chart_data = service_config.get(HELM_CHART_BUILDER)
        helm_chart_var = artifact_config.get(constant.ARTIFACT_PROPERTY).get(constant.REPO_NAME)
        helm_chart_match = Util.regular_expression(helm_chart_var)
        helm_chart_builder = helm_chart_data.get(helm_chart_match[1])
        file_path = os.path.dirname(file_path_config)
        helm_chart_repo_name = helm_chart_builder[constant.REPO_NAME]
        helm_chart_tag = helm_chart_builder[constant.TAG]
        build_type = helm_chart_builder.get(constant.BUILD_TYPE)
        if build_type == constant.HELM_REPO_TYPE:
            helm_repo_url = helm_chart_builder[constant.HELM_REPO_URL]
            image_processor.process_helm_chart(file_path, helm_chart_repo_name, helm_chart_tag,
                                               helm_repo_url, build_type)
            helm_chart_repo_id = self._get_repo_id(artifact_type, helm_chart_repo_name)
        elif helm_chart_builder.get(constant.HELM_CHART_PATH):
            helm_chart_file_path = os.path.join(os.path.dirname(file_path_config),
                                                helm_chart_builder[constant.HELM_CHART_PATH])
            image_processor.process_helm_chart(helm_chart_file_path, helm_chart_repo_name, helm_chart_tag,
                                               None, constant.HELM_PACKAGE_TYPE)
            helm_chart_repo_id = self._get_repo_id(artifact_type, helm_chart_repo_name)
        # 若不存在认为线上仓库已存在相关容器镜像
        else:
            helm_chart_repo_id = self._get_exist_acr_image_repo_id(artifact_type, helm_chart_repo_name, helm_chart_tag)

        return helm_chart_repo_name, helm_chart_repo_id, helm_chart_tag

    def _get_exist_acr_image_repo_id(self, artifact_type, repo_name, tag):
        repo_id = self._get_repo_id(artifact_type, repo_name)
        # 查到repo_id后检索所有已存在的tag，检查提供的tag是否存在
        tags = ArtifactService.list_acr_image_tags(self.context, repo_id, artifact_type).body.images
        tag_values = [item.tag for item in tags]
        if tag not in tag_values:
            raise ValueError(
                f"Invalid or non-existent {artifact_type} version provided. repo_name:{repo_name}, tag:{tag}.")
        return repo_id

    def _replace_artifact_file_path_with_url(self, file_path):
        artifact_credentials = CredentialsService.get_artifact_repository_credentials(self.context, constant.FILE)
        file_artifact_url = FileService.put_file(artifact_credentials, file_path, ARTIFACT)
        return file_artifact_url

    def _release_artifact(self, artifact_id, artifact_name):
        ArtifactService.release_artifact(self.context, artifact_id)
        while True:
            # 定时检测部署物发布状态
            try:
                data_response = ArtifactService.get_artifact(self.context, artifact_name, 'draft')
                artifact_status = data_response.body.status
                # if artifact_status == DELIVERING:
            except TeaException as e:
                if e.code == ARTIFACT_VERSION_NOT_FOUND:
                    # user_logger.info('The release is complete')
                    break
                else:
                    raise
            time.sleep(25)

    def _check_draft_artifact_created(self, artifact_id):
        while True:
            try:
                data_response = ArtifactService.list_versions(self.context, artifact_id)
                draft_artifact_created = False
                for artifact in data_response.body.artifacts:
                    if artifact.artifact_version == DRAFT and artifact.status == CREATED:
                        draft_artifact_created = True
                        break
                    elif artifact.artifact_version == DRAFT and artifact.status == CREATE_FAILED:
                        user_logger.error(f"The artifact {artifact_id} is failed to create.\n")
                        raise CliCommonException(artifact.status_detail)
                if draft_artifact_created:
                    break
            except TeaException:
                raise
            except CliCommonException:
                raise
            time.sleep(25)

    def get_artifact_detail(self, artifact_id, artifact_version):
        response = ArtifactService.get_artifact(self.context, '', artifact_version, artifact_id)
        artifact_type = response.body.artifact_type
        artifact_name = response.body.name
        description = response.body.description
        support_region_ids = response.body.support_region_ids
        artifact_property = json.loads(response.body.artifact_property)
        parameters = {
            constant.ARTIFACT_TYPE: artifact_type,
            constant.ARTIFACT_NAME: artifact_name,
            constant.DESCRIPTION: description,
            constant.ARTIFACT_PROPERTY: artifact_property,
            constant.SUPPORT_REGION_IDS: support_region_ids
        }
        return parameters

    @log_monitor("BuildService", "BuildArtifacts", periodic_logging=True, periodic_logging_interval=60,
                 dynamic_logging=True)
    def process(self, data_config, file_path_config, update_artifact=False, version_name='', **kwargs):
        artifact_dict = data_config.get(constant.ARTIFACT)
        pending_artifacts = list(artifact_dict.values())
        completed_artifacts = []
        dynamic_logging_message = kwargs.get(LOGGING_CLOSURE_NAME)

        def task_done_callback(future):
            artifact_name = future.result()
            # 查找在pending中的artifact并移除
            for artifact in pending_artifacts:
                if artifact[constant.ARTIFACT_NAME] == artifact_name:
                    pending_artifacts.remove(artifact)
                    break
            # 将artifact放入已完成列表
            completed_artifacts.append(artifact_name)
            completed_count = len(completed_artifacts)
            total_count = completed_count + len(pending_artifacts)
            message = (
                f"Artifacts build progress: {completed_count}/{total_count}"
            )
            dynamic_logging_message(message)

        with ThreadPoolExecutor(max_workers=10, thread_name_prefix="process_image") as executor:
            future_list = []
            for artifact_config in artifact_dict.values():
                if constant.ARTIFACT_NAME not in artifact_config:
                    continue
                future = executor.submit(self._process_single_artifact, data_config, file_path_config,
                                         artifact_config, version_name, update_artifact)
                future.add_done_callback(task_done_callback)
                future_list.append(future)
            [future.result() for future in future_list]
        return artifact_dict

    def _process_single_artifact(self, data_config, file_path_config, artifact_config, version_name, update_artifact):
        artifact_type = artifact_config.get(constant.ARTIFACT_TYPE)
        artifact_name = artifact_config.get(constant.ARTIFACT_NAME)
        if version_name:
            artifact_config[constant.VERSION_NAME] = version_name
        artifact_config[UPDATE_ARTIFACT] = update_artifact
        artifact_data_list = ArtifactService.list_artifact(self.context, artifact_name)
        if len(artifact_data_list.body.artifacts) == 0:
            if artifact_type == constant.FILE:
                # 将相对路径替换成绝对路径
                file_path = os.path.join(os.path.dirname(file_path_config),
                                         artifact_config.get(constant.ARTIFACT_PROPERTY).get(constant.URL))
                # 将文件部署物的本地路径替换成Url
                artifact_config[constant.ARTIFACT_PROPERTY][
                    constant.URL] = self._replace_artifact_file_path_with_url(file_path)
            elif artifact_type == constant.ECS_IMAGE:
                if IMAGE_BUILDER in data_config:
                    # 利用oos模版创建镜像
                    region_id, image_id = self._create_image_from_image_builder(data_config, artifact_config)
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.REGION_ID] = region_id
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.IMAGE_ID] = image_id
            elif artifact_type == constant.ACR_IMAGE:
                if ACR_IMAGE_BUILDER in data_config:
                    acr_image_name, repo_id, acr_image_tag = self._create_acrimage_from_acrimage_builder(
                        data_config, artifact_config, file_path_config)
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_NAME] = acr_image_name
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.TAG] = acr_image_tag
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_ID] = repo_id
            elif artifact_type == constant.HELM_CHART:
                helm_chart_name, helm_chart_id, helm_chart_tag = self._create_helmchart_from_helmchart_builder(
                    data_config, artifact_config, file_path_config)
                artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_NAME] = helm_chart_name
                artifact_config[constant.ARTIFACT_PROPERTY][constant.TAG] = helm_chart_tag
                artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_ID] = helm_chart_id
            create_artifact_response = ArtifactService.create_artifact(self.context, artifact_config)
            managed_build = artifact_config.get(constant.ARTIFACT_BUILD_PROPERTY) is not None
            artifact_id = create_artifact_response.body.artifact_id
            if managed_build:
                self.user_logger.info(f"Start managed build artifact: {artifact_id}", extra={"service_name": "aab"})
            self._check_draft_artifact_created(artifact_id)
            user_logger.info(
                f"Successfully created a new artifact: {artifact_id}\n"
            )
        # 只有update_artifact为false且已经有draft版本才跳过创建artifact
        elif not artifact_config.get(UPDATE_ARTIFACT) and ArtifactService.has_draft_version(self.context, artifact_name):
            artifact_id = artifact_data_list.body.artifacts[0].artifact_id
            self.user_logger.info(
                f"No need to update the artifact: {artifact_id}"
            )
        else:
            if artifact_type == constant.FILE:
                file_url_existed = self._get_file_artifact_url(artifact_name)
                # 将相对路径替换成绝对路径
                file_path = os.path.join(os.path.dirname(file_path_config),
                                         artifact_config.get(constant.ARTIFACT_PROPERTY).get(constant.URL))
                result_artifact = FileService.check_file_repeat(file_url_existed, file_path)
                # 检查文件部署物是否重复，重复则不再上传，使用现有Url
                if result_artifact:
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.URL] = file_url_existed.split('?')[0]
                else:
                    artifact_config[constant.ARTIFACT_PROPERTY][
                        constant.URL] = self._replace_artifact_file_path_with_url(file_path)
            elif artifact_type == constant.ECS_IMAGE:
                if IMAGE_BUILDER in data_config:
                    # 利用oos模版创建镜像
                    region_id, image_id = self._create_image_from_image_builder(data_config, artifact_config)
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.REGION_ID] = region_id
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.IMAGE_ID] = image_id
            elif artifact_type == constant.ACR_IMAGE:
                if ACR_IMAGE_BUILDER in data_config:
                    acr_image_name, repo_id, acr_image_tag = self._create_acrimage_from_acrimage_builder(
                        data_config, artifact_config, file_path_config)
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_NAME] = acr_image_name
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.TAG] = acr_image_tag
                    artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_ID] = repo_id
            elif artifact_type == constant.HELM_CHART:
                helm_chart_name, helm_chart_id, helm_chart_tag = self._create_helmchart_from_helmchart_builder(
                    data_config, artifact_config, file_path_config)
                artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_NAME] = helm_chart_name
                artifact_config[constant.ARTIFACT_PROPERTY][constant.TAG] = helm_chart_tag
                artifact_config[constant.ARTIFACT_PROPERTY][constant.REPO_ID] = helm_chart_id
            artifact_id = artifact_data_list.body.artifacts[0].artifact_id
            managed_build = artifact_config.get(constant.ARTIFACT_BUILD_PROPERTY) is not None
            if managed_build:
                self.user_logger.info(f"Start updating the managed build artifact: {artifact_id}")
            self._create_or_update_artifact(artifact_config, artifact_id)
            self._check_draft_artifact_created(artifact_id)
            self.user_logger.info(
                f"Successfully updated the artifact:{artifact_id}"
            )
        artifact_config[constant.ARTIFACT_ID] = artifact_id
        return artifact_name

    @retry_on_exception(max_retries=10, delay=2, backoff=2, exceptions=(TeaException,))
    def _create_or_update_artifact(self, artifact_data, artifact_id):
        try:
            ArtifactService.create_artifact(self.context, artifact_data, artifact_id)
        except TeaException as e:
            if e.code == ENTITY_ALREADY_EXIST_DRAFT_ARTIFACT:
                try:
                    ArtifactService.update_artifact(self.context, artifact_data, artifact_id)
                except TeaException as e:
                    if e.code == ARTIFACT_STATUS_NOT_SUPPORT_OPERATION:
                        raise
            else:
                raise

    def deliver_command(self, region_id, delivery_type, file_path):
        file_path = ArtifactProcessorHelper.validate_and_replace_file_path(delivery_type, file_path)
        user_logger.info(f"file_path: {file_path}")
        # 得到需要上传的容器镜像
        deliver_image_processor = DeliverImageManager(delivery_type)
        docker_image_urls = deliver_image_processor.extract_docker_images_from_template(file_path)
        # 将容器镜像上传到计算巢容器镜像仓库
        artifact_processor = ArtifactProcessor(self.context)

        # 将 set 转换为 list
        docker_image_urls = list(docker_image_urls)
        # 一次最多批量上传10个镜像
        batch_size = 10
        total_images = len(docker_image_urls)
        for i in range(0, total_images, batch_size):
            batch_end = min(i + batch_size, total_images)
            batch = docker_image_urls[i:batch_end]
            artifact_config = ArtifactProcessorHelper.generate_config_for_container_image(batch, region_id)
            try:
                artifact_processor.process(artifact_config, None)
            except Exception as e:
                user_logger.error(f"Failed to process batch {i // batch_size + 1}: {e}")
                raise

        # 获取计算巢容器镜像仓库路径
        response = CredentialsService.get_artifact_repository_credentials(self.context, constant.ACR_IMAGE)
        docker_host_path = os.path.dirname(response.body.available_resources[0].path)

        # 如果镜像全部上传成功，将原镜像和托管构建镜像的映射文件保存到image-mapping.yaml
        deliver_image_processor.save_image_mapping(file_path, docker_image_urls, docker_host_path)
