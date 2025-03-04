# -*- coding: utf-8 -*-
from Tea.exceptions import TeaException
from alibabacloud_computenestsupplier20210521 import models as compute_nest_supplier_20210521_models

from computenestcli.service.base import Service
from computenestcli.common.util import Util
from computenestcli.common import constant
from computenestcli.common.decorator import retry_on_exception
from computenestcli.base_log import get_developer_logger

developer_logger = get_developer_logger()

ARTIFACT_VERSION_NOT_FOUND = 'EntityNotExist.ArtifactVersion'

class ArtifactService(Service):

    @classmethod
    def create_artifact(cls, context, artifact_config, artifact_id=None):
        artifact_type = artifact_config.get(constant.ARTIFACT_TYPE)
        artifact_build_type = artifact_config.get(constant.ARTIFACT_BUILD_TYPE)
        version_name = Util.add_timestamp_to_version_name(artifact_config.get(constant.VERSION_NAME))
        supported_regions = artifact_config.get(constant.SUPPORT_REGION_IDS, []) or []
        artifact_property_config = artifact_config.get(constant.ARTIFACT_PROPERTY)
        artifact_build_property_config = artifact_config.get(constant.ARTIFACT_BUILD_PROPERTY)
        artifact_property = None
        artifact_build_property = None

        # config.yaml中传入artifact_property，则直接赋值。
        # 没传入artifact_property但传入artifact_build_property，则给artifact_property赋默认值。
        if artifact_property_config:
            artifact_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactProperty(
                region_id=artifact_property_config.get(constant.REGION_ID),
                image_id=artifact_property_config.get(constant.IMAGE_ID),
                commodity_code=artifact_property_config.get(constant.COMMODITY_CODE),
                commodity_version=artifact_property_config.get(constant.COMMODITY_VERSION),
                url=artifact_property_config.get(constant.URL),
                repo_name=artifact_property_config.get(constant.REPO_NAME),
                repo_id=artifact_property_config.get(constant.REPO_ID),
                tag=artifact_property_config.get(constant.TAG),
                repo_type=artifact_property_config.get(constant.REPO_TYPE)
            )
        elif artifact_build_property_config:
            if artifact_type == constant.ECS_IMAGE:
                artifact_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactProperty(
                    region_id=artifact_build_property_config.get(constant.REGION_ID)
                )
            elif artifact_type == constant.ACR_IMAGE or artifact_type == constant.HELM_CHART:
                artifact_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactProperty(
                    repo_type=artifact_build_property_config.get(constant.REPO_TYPE, 'Private')
                )

        # config.yaml中传入artifact_build_property，则直接赋值。
        if artifact_build_property_config:
            code_repo_data = artifact_build_property_config.get(constant.CODE_REPO)
            code_repo = None
            if code_repo_data:
                code_repo = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactBuildPropertyCodeRepo(
                    platform=code_repo_data.get(constant.PLATFORM),
                    owner=code_repo_data.get(constant.OWNER),
                    repo_name=code_repo_data.get(constant.REPO_NAME),
                    branch=code_repo_data.get(constant.BRANCH)
                )
            build_args_data = artifact_build_property_config.get(constant.BUILD_ARGS)
            build_args = []
            if build_args_data:
                for arg in build_args_data:
                    build_arg = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactBuildPropertyBuildArgs(
                        argument_name=arg.get(constant.DOCKER_BUILD_ARGUMENT_NAME),
                        argument_value=arg.get(constant.DOCKER_BUILD_ARGUMENT_VALUE)
                    )
                    build_args.append(build_arg)
            artifact_build_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactBuildProperty(
                region_id=artifact_build_property_config.get(constant.REGION_ID),
                source_image_id=artifact_build_property_config.get(constant.SOURCE_IMAGE_ID),
                command_type=artifact_build_property_config.get(constant.COMMAND_TYPE),
                command_content=artifact_build_property_config.get(constant.COMMAND_CONTENT),
                code_repo=code_repo,
                build_args=build_args,
                dockerfile_path=artifact_build_property_config.get(constant.DOCKER_FILE_PATH),
                source_container_image=artifact_build_property_config.get(constant.SOURCE_CONTAINER_IMAGE),

            )
        create_artifact_request = compute_nest_supplier_20210521_models.CreateArtifactRequest(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            artifact_build_type=artifact_build_type,
            name=artifact_config.get(constant.ARTIFACT_NAME),
            version_name=version_name,
            description=artifact_config.get(constant.DESCRIPTION),
            artifact_property=artifact_property,
            artifact_build_property=artifact_build_property,
            support_region_ids=supported_regions
        )
        client = cls._get_computenest_client(context)
        response = client.create_artifact(create_artifact_request)
        return response

    @classmethod
    @retry_on_exception(max_retries=10, delay=2, backoff=2, exceptions=(TeaException,))
    def release_artifact(cls, context, artifact_id):
        release_service_request = compute_nest_supplier_20210521_models.ReleaseArtifactRequest(artifact_id)
        client = cls._get_computenest_client(context)
        response = client.release_artifact(release_service_request)
        return response

    @classmethod
    def update_artifact(cls, context, artifact_data, artifact_id):
        artifact_type = artifact_data.get(constant.ARTIFACT_TYPE)
        version_name = Util.add_timestamp_to_version_name(artifact_data.get(constant.VERSION_NAME))
        supported_regions = artifact_data.get(constant.SUPPORT_REGION_IDS)
        artifact_property_data = artifact_data.get(constant.ARTIFACT_PROPERTY)
        artifact_build_property_data = artifact_data.get(constant.ARTIFACT_BUILD_PROPERTY)
        artifact_property = None
        artifact_build_property = None

        # config.yaml中传入artifact_property，则直接赋值。
        # 没传入artifact_property但传入artifact_build_property，则给artifact_property赋默认值。
        if artifact_property_data:
            artifact_property = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactProperty(
                region_id=artifact_property_data.get(constant.REGION_ID),
                image_id=artifact_property_data.get(constant.IMAGE_ID),
                commodity_code=artifact_property_data.get(constant.COMMODITY_CODE),
                commodity_version=artifact_property_data.get(constant.COMMODITY_VERSION),
                url=artifact_property_data.get(constant.URL),
                repo_name=artifact_property_data.get(constant.REPO_NAME),
                repo_id=artifact_property_data.get(constant.REPO_ID),
                tag=artifact_property_data.get(constant.TAG),
                repo_type=artifact_property_data.get(constant.REPO_TYPE)
            )
        elif artifact_build_property_data:
            if artifact_type == constant.ECS_IMAGE:
                artifact_property = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactProperty(
                    region_id=artifact_build_property_data.get(constant.REGION_ID)
                )
            elif artifact_type == constant.ACR_IMAGE or artifact_type == constant.HELM_CHART:
                artifact_property = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactProperty(
                    repo_type=artifact_build_property_data.get(constant.REPO_TYPE, 'Private')
                )

        # config.yaml中传入artifact_build_property，则直接赋值。
        if artifact_build_property_data:
            code_repo_data = artifact_build_property_data.get(constant.CODE_REPO)
            code_repo = None
            if code_repo_data:
                code_repo = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactBuildPropertyCodeRepo(
                    platform=code_repo_data.get(constant.PLATFORM),
                    owner=code_repo_data.get(constant.OWNER),
                    repo_name=code_repo_data.get(constant.REPO_NAME),
                    branch=code_repo_data.get(constant.BRANCH)
                )
            build_args_data = artifact_build_property_data.get(constant.BUILD_ARGS)
            build_args = []
            if build_args_data:
                for arg in build_args_data:
                    build_arg = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactBuildPropertyBuildArgs(
                        argument_name=arg.get(constant.DOCKER_BUILD_ARGUMENT_NAME),
                        argument_value=arg.get(constant.DOCKER_BUILD_ARGUMENT_VALUE)
                    )
                    build_args.append(build_arg)
            artifact_build_property = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactBuildProperty(
                region_id=artifact_build_property_data.get(constant.REGION_ID),
                source_image_id=artifact_build_property_data.get(constant.SOURCE_IMAGE_ID),
                command_type=artifact_build_property_data.get(constant.COMMAND_TYPE),
                command_content=artifact_build_property_data.get(constant.COMMAND_CONTENT),
                code_repo=code_repo,
                build_args=build_args,
                dockerfile_path=artifact_build_property_data.get(constant.DOCKER_FILE_PATH),
                source_container_image=artifact_build_property_data.get(constant.SOURCE_CONTAINER_IMAGE),

            )
        update_artifact_request = compute_nest_supplier_20210521_models.UpdateArtifactRequest(
            artifact_id=artifact_id,
            version_name=version_name,
            description=artifact_data.get(constant.DESCRIPTION),
            artifact_property=artifact_property,
            artifact_build_property=artifact_build_property,
            support_region_ids=supported_regions
        )
        client = cls._get_computenest_client(context)
        response = client.update_artifact(update_artifact_request)
        return response

    @classmethod
    def delete_artifact(cls, context, artifact_id, artifact_version):
        delete_artifact_request = compute_nest_supplier_20210521_models.DeleteArtifactRequest(artifact_id,
                                                                                              artifact_version)
        client = cls._get_computenest_client(context)
        response = client.delete_artifact(delete_artifact_request)
        return response

    @classmethod
    def list_artifact(cls, context, artifact_name):
        filter_first = compute_nest_supplier_20210521_models.ListArtifactsRequestFilter(
            name=constant.NAME,
            values=[artifact_name]
        )
        list_artifact_request = compute_nest_supplier_20210521_models.ListArtifactsRequest(
            filter=[
                filter_first
            ]
        )
        client = cls._get_computenest_client(context)
        response = client.list_artifacts(list_artifact_request)
        return response

    @classmethod
    @retry_on_exception()
    def list_acr_image_repositories(cls, context, artifact_type, repo_name):
        developer_logger.info(
            "list_acr_image_repositories artifact_type: %s repo_name: %s" % (artifact_type, repo_name))
        list_acr_image_repositories_request = compute_nest_supplier_20210521_models.ListAcrImageRepositoriesRequest(
            artifact_type=artifact_type,
            repo_name=repo_name
        )
        client = cls._get_computenest_client(context)
        response = client.list_acr_image_repositories(list_acr_image_repositories_request)
        developer_logger.info("list_acr_image_repositories response: %s" % response)
        # 如果body不为空，且repositories数组为空的话就抛出异常
        if response.body and not response.body.repositories:
            raise Exception("No repositories found")
        return response

    @classmethod
    @retry_on_exception()
    def list_acr_image_tags(cls, context, repo_id, artifact_type):
        list_acr_image_tags_request = compute_nest_supplier_20210521_models.ListAcrImageTagsRequest(
            repo_id=repo_id,
            artifact_type=artifact_type
        )
        client = cls._get_computenest_client(context)
        response = client.list_acr_image_tags(list_acr_image_tags_request)
        developer_logger.info("list_acr_image_tags response: %s" % response)
        if response.body and not response.body.images:
            raise Exception("No tags found")
        return response

    @classmethod
    def get_artifact(cls, context, artifact_name, artifact_version='', artifact_id=''):
        get_artifact_request = compute_nest_supplier_20210521_models.GetArtifactRequest(
            artifact_version=artifact_version,
            artifact_name=artifact_name,
            artifact_id=artifact_id,
        )
        client = cls._get_computenest_client(context)
        response = client.get_artifact(get_artifact_request)
        return response

    @classmethod
    def list_versions(cls, context, artifact_id):
        list_artifact_versions_request = compute_nest_supplier_20210521_models.ListArtifactVersionsRequest(artifact_id)
        client = cls._get_computenest_client(context)
        response = client.list_artifact_versions(list_artifact_versions_request)
        return response

    @classmethod
    def has_draft_version(cls, context, artifact_name):
        try:
            response = cls.get_artifact(context, artifact_name, 'draft')
            return True
        except TeaException as e:
            if e.code == ARTIFACT_VERSION_NOT_FOUND:
                return False
            else:
                developer_logger.error(f"Unexpected error while checking draft version for artifact {artifact_name}: {e}")
                raise
        except Exception as e:
            developer_logger.error(f"Failed to check draft version for artifact {artifact_name}: {e}")
            raise

