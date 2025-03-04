import os

from dockerfile_parse import DockerfileParser

from computenestcli.common import project_setup_constant, constant
from computenestcli.common.constant import DOCKER_BUILD_ARGUMENT_NAME, DOCKER_BUILD_ARGUMENT_VALUE
from computenestcli.common.project_setup_constant import COMMON_LOG_FILTER
from computenestcli.service.project_setup.setup_handler import SetupHandler


class DockerfileSetupHandler(SetupHandler):

    def validate_parameters(self):
        dockerfile_path = self.parameters.get(project_setup_constant.DOCKERFILE_PATH_KEY)
        if not dockerfile_path:
            raise Exception("Dockerfile path is empty.")
        dockerfile_path = dockerfile_path.strip()
        if not os.path.exists(dockerfile_path):
            raise Exception(f"Dockerfile path:{dockerfile_path} does not exist.")

    def generate_templates(self):
        self.select_package()
        self._replace_variables()
        self.generate_specified_templates(project_setup_constant.INPUT_DOCKERFILE_ROS_TEMPLATE_NAME,
                                          project_setup_constant.INPUT_ECS_IMAGE_CONFIG_NAME)

    def _generate_ecs_image_builder_command(self):
        total_commands = []

        # 通过dockerfile构建镜像命令
        build_docker_image_command = self._generate_build_image_command()
        total_commands.append(build_docker_image_command)

        return '\n'.join(total_commands)

    def _generate_build_image_command(self):
        command_list = []

        docker_image_name = self.parameters.get(project_setup_constant.REPO_NAME_KEY)
        if docker_image_name is None:
            raise ValueError("repo name can't be null!")
        docker_image_name = docker_image_name.lower()
        self.parameters[project_setup_constant.DOCKER_IMAGE_NAME_KEY] = docker_image_name
        dockerfile_path = self.parameters.get(project_setup_constant.DOCKERFILE_PATH_KEY)
        build_args = self.parameters.get(constant.DOCKER_BUILD_ARGS)
        build_args_str = self._get_docker_build_args(build_args)
        build_docker_image_command = f'docker build {build_args_str} ' \
                                     f'-f {os.path.relpath(dockerfile_path, os.getcwd())}' \
                                     f' -t {docker_image_name} . ' + COMMON_LOG_FILTER

        command_list.append(build_docker_image_command)
        command_content = '\n'.join(command_list)
        return command_content

    def _replace_variables(self):
        security_ports, service_ports = self._extract_ports_from_dockerfile()
        self.parameters[project_setup_constant.SERVICE_PORTS_KEY] = service_ports
        self.parameters[project_setup_constant.SECURITY_GROUP_PORTS_KEY] = security_ports
        custom_parameters = self.parameters.get(project_setup_constant.CUSTOM_PARAMETERS_KEY)
        docker_run_env_parameters = self._build_docker_run_parameters(custom_parameters)
        if docker_run_env_parameters and len(docker_run_env_parameters) > 0:
            self.parameters[project_setup_constant.DOCKER_RUN_ENV_ARGS] = docker_run_env_parameters
        self.parameters[project_setup_constant.ECS_IMAGE_BUILDER_COMMAND_CONTENT_KEY] = \
            self._generate_ecs_image_builder_command()

    def _get_dockerfile_content(self) -> str:
        """
        获取 Dockerfile 的内容。

        返回:
            str: Dockerfile 的内容。

        异常:
            FileNotFoundError: 如果找不到 Dockerfile。
        """
        docker_file_path = self.parameters.get(project_setup_constant.DOCKERFILE_PATH_KEY)
        if not docker_file_path:
            raise ValueError("未找到有效的 Dockerfile 路径。")
        if not os.path.isabs(docker_file_path):
            docker_file_path = os.path.abspath(docker_file_path)

        try:
            with open(docker_file_path) as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到 Dockerfile：{docker_file_path}")

    def _extract_ports_from_dockerfile(self):
        """
        从 Dockerfile 中提取暴露的端口信息（包括端口号和协议）。
        返回:
            list: 包含元组的列表，每个元组包含端口和协议（例如，('8080', 'tcp')）。
            如果没有暴露的端口，默认添加 ('8080', 'tcp')。
        """
        # 获取 Dockerfile 内容
        content = self._get_dockerfile_content()

        # 使用 DockerfileParser
        parser = DockerfileParser()
        parser.content = content

        ports_to_open = []  # 初始化返回的端口和协议列表
        service_ports = []  # 初始化仅端口的列表

        # 获取环境变量
        env_vars = parser.envs

        # 遍历指令并寻找 EXPOSE
        for line in content.splitlines():
            if line.lower().startswith('expose'):
                _, *ports = line.split()
                for port in ports:
                    # 处理环境变量的两种形式
                    if port.startswith('${') and port.endswith('}'):
                        var_name = port[2:-1]  # 去掉 ${ 和 }
                    elif port.startswith('$'):
                        var_name = port[1:]  # 去掉 $
                    else:
                        var_name = None

                    if var_name:
                        # 尝试从 env_vars 中获取值
                        port_num = env_vars.get(var_name)
                        if port_num is None:
                            continue  # 如果未找到值，则跳过
                        protocol = 'tcp'  # 默认协议
                    else:
                        # 处理常规端口和协议
                        port_parts = port.split('/')
                        port_num = port_parts[0]
                        protocol = port_parts[1] if len(port_parts) > 1 else 'tcp'  # 默认协议为 TCP

                    ports_to_open.append((port_num, protocol))  # 添加元组形式的端口和协议
                    service_ports.append(port_num)

        # 如果没有暴露任何端口，默认返回空的 ports_to_open 和 service_ports
        if not ports_to_open:
            ports_to_open.append(('8080', 'tcp'))
            service_ports.append('8080')

        return ports_to_open, service_ports

    def _build_docker_run_parameters(self, custom_parameters: list):
        """
        构建docker run的自定义参数
        入参：
        "CustomParameters": [
                {
                    "Name": "InstanceSize",
                    "Type": "String",
                    "Label": "ECS Instance Size",
                    "Description": "The size of the EC2 instance",
                    "Default": "t2.micro",
                    "AllowedValues": ["t2.micro", "t2.small", "t2.medium"]
                }
            ]
        返回:
            -e InstanceSize=${InstanceSize}
        """
        if not custom_parameters:
            return None
        run_parameters = []
        for param in custom_parameters:
            name = param.get("Name")
            if name:
                run_parameters.append(f"-e {name}=${{{name}}}")  # 拼接环境变量格式

            # 返回拼接的参数字符串
        return ' '.join(run_parameters)

    def _get_docker_build_args(self, build_args: []):
        # 准备构建参数
        build_arg_commands = []
        if build_args:
            for arg in build_args:
                build_value = arg.get(DOCKER_BUILD_ARGUMENT_VALUE)
                name = arg.get(DOCKER_BUILD_ARGUMENT_NAME)
                if name and build_value:  # 确保 name 和 value 都不为空
                    build_arg_commands.append(f"--build-arg {name}={build_value}")

        build_args_str = " ".join(build_arg_commands) if build_arg_commands else ""
        return build_args_str
