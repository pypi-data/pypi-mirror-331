import os
import re

from computenestcli.service.project_setup.setup_handler import SetupHandler, ORIGINAL_REPO_PATH, WORKSPACE_PATH
from computenestcli.common import project_setup_constant


class SourceCodeSetupHandler(SetupHandler):

    def validate_parameters(self):
        source_code_path = self.parameters.get(project_setup_constant.SOURCE_CODE_PATH_KEY)
        if not source_code_path:
            raise Exception("Source code path is empty.")
        self.parameters[project_setup_constant.SOURCE_CODE_PATH_KEY] = source_code_path.strip()
        if not os.path.exists(source_code_path):
            raise Exception(f"Source code path:{source_code_path} does not exist.")

    def generate_templates(self):
        self.select_package()
        self._replace_variables()
        self.generate_specified_templates(project_setup_constant.INPUT_SOURCE_CODE_ROS_TEMPLATE_NAME,
                                          project_setup_constant.INPUT_ECS_IMAGE_CONFIG_NAME)

    def _replace_variables(self):
        self._replace_run_command()
        self.parameters[project_setup_constant.ECS_IMAGE_BUILDER_COMMAND_CONTENT_KEY] = \
            self._generate_ecs_image_builder_command()

    def _replace_run_command(self):
        def replace_variable(match):
            var_name = match.group(1)
            if var_name not in names:
                return f'${{!{var_name}}}'
            return match.group(0)

        pattern = r'\$\{([^}]+)\}'
        custom_parameters = self.parameters.get(project_setup_constant.CUSTOM_PARAMETERS_KEY)
        if not custom_parameters:
            return

        names = [item['Name'] for item in custom_parameters]
        run_command = self.parameters.get(project_setup_constant.RUN_COMMAND_KEY)
        if not run_command:
            return
        run_command = re.sub(pattern, replace_variable, run_command)
        self.parameters[project_setup_constant.RUN_COMMAND_KEY] = run_command

    def _generate_ecs_image_builder_command(self):
        commands = [f"mkdir -p {WORKSPACE_PATH}"]
        # 生成cp 命令，将用户指定的运行命令根目录移动到指定目录

        root_path = self.parameters.get(project_setup_constant.SOURCE_CODE_PATH_KEY)
        commands.append(f"cp -r {ORIGINAL_REPO_PATH}/{root_path}/* {WORKSPACE_PATH}/")
        return '\n'.join(commands)
