from pathlib import Path

from computenestcli.common.logging_constant import SETUP_PROJECT
from computenestcli.processor.jinja2 import Jinja2Processor
from computenestcli.common import project_setup_constant
from computenestcli.common.artifact_source_type import ArtifactSourceType

from computenestcli.base_log import get_developer_logger, log_monitor
from computenestcli.base_log import get_user_logger

from computenestcli.service.project_setup.docker_compose_setup_handler import DockerComposeSetupHandler
from computenestcli.service.project_setup.dockerfile_setup_handler import DockerfileSetupHandler
from computenestcli.service.project_setup.helm_setup_handler import HelmSetupHandler
from computenestcli.service.project_setup.source_code_setup_handler import SourceCodeSetupHandler
from computenestcli.service.project_setup.buildpacks_setup_handler import BuildpacksSetupHandler

developer_logger = get_developer_logger()
user_logger = get_user_logger(SETUP_PROJECT)


class ProjectSetup:
    def __init__(self, output_base_path, parameters):
        self.output_base_path = Path(output_base_path).absolute()
        self.parameters = parameters
        self.processor = Jinja2Processor()
        self.handler = self._select_handler()

    def _select_handler(self):
        artifact_source_type = self.parameters.get(project_setup_constant.ARTIFACT_SOURCE_TYPE_KEY)
        handler_args = (self.output_base_path, self.parameters)

        if artifact_source_type == ArtifactSourceType.DOCKER_COMPOSE.value:
            return DockerComposeSetupHandler(*handler_args)
        elif artifact_source_type == ArtifactSourceType.DOCKERFILE.value:
            return DockerfileSetupHandler(*handler_args)
        elif artifact_source_type == ArtifactSourceType.SOURCE_CODE.value:
            return SourceCodeSetupHandler(*handler_args)
        elif artifact_source_type == ArtifactSourceType.HELM_CHART.value:
            return HelmSetupHandler(*handler_args)
        elif artifact_source_type == ArtifactSourceType.BUILDPACKS.value:
            return BuildpacksSetupHandler(*handler_args)
        else:
            raise Exception("Unsupported Artifact Source Type.")

    def setup_project(self):
        self.validate_parameters()
        self.save_computenest_parameters()
        self.generate_templates()
        self.copy_resources()

    @log_monitor("SetupProject", "ValidateParameters")
    def validate_parameters(self):
        self.handler.validate_parameters()

    @log_monitor("SetupProject", "SaveComputeNestParameters")
    def save_computenest_parameters(self):
        self.handler.save_computenest_parameters()

    @log_monitor("SetupProject", "GenerateTemplates")
    def generate_templates(self):
        self.handler.generate_templates()

    @log_monitor("SetupProject", "CopyResources")
    def copy_resources(self):
        self.handler.copy_resources()
        self.handler.generate_architecture()
