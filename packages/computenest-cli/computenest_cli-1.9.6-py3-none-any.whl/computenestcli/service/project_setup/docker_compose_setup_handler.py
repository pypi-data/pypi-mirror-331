import os
import yaml

from computenestcli.common import project_setup_constant
from computenestcli.common.docker_compose_helper import DockerComposeHelper
from computenestcli.common.file_util import FileUtil
from computenestcli.common.project_setup_constant import COMMON_LOG_FILTER
from computenestcli.service.project_setup.setup_handler import SetupHandler, ORIGINAL_REPO_PATH, WORKSPACE_PATH


class DockerComposeSetupHandler(SetupHandler):

    def __init__(self, output_base_path, parameters):
        super().__init__(output_base_path, parameters)

    def validate_parameters(self):
        docker_compose_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY)
        if not docker_compose_path:
            raise Exception("Docker compose path is empty.")
        docker_compose_path = docker_compose_path.strip()
        if not os.path.exists(docker_compose_path):
            raise Exception(f"Docker compose path:{docker_compose_path} does not exist.")
        docker_compose_env_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_ENV_PATH_KEY)
        if not docker_compose_env_path:
            docker_compose_env_path = os.path.join(os.path.dirname(docker_compose_path), '.env')
        docker_compose_env_path = docker_compose_env_path.strip()
        if not os.path.exists(docker_compose_env_path):
            self.user_logger.warning(f"Docker compose env path:{docker_compose_env_path} does not exist.")

    def generate_templates(self):
        self.select_package()
        self._replace_variables()
        self.generate_specified_templates(project_setup_constant.INPUT_DOCKER_COMPOSE_ROS_TEMPLATE_NAME,
                                          project_setup_constant.INPUT_ECS_IMAGE_CONFIG_NAME)

    def _generate_ecs_image_builder_command(self):
        total_commands = []

        # 生成复制所需文件命令
        copy_repo_files_command = self._generate_copy_repo_files_command()
        total_commands.append(copy_repo_files_command)

        # 生成 .env 文件处理命令
        env_process_commands = self._generate_env_process_command()
        total_commands.extend(env_process_commands)

        # 生成替换docker-compose.yaml中pull_policy的sed命令
        docker_compose_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY)
        docker_compose_sed_command = DockerComposeHelper.generate_docker_compose_sed_command(docker_compose_path)
        total_commands.append(docker_compose_sed_command)

        # 生成构建和拉取镜像命令
        image_artifact_command = self._generate_build_and_pull_image_command()
        total_commands.append(image_artifact_command)

        # 返回所有命令
        return '\n'.join(total_commands) + '\n'

    def _generate_build_and_pull_image_command(self):
        docker_compose_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY)
        override_file_paths = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_OVERRIDE_PATHS_KEY)

        command_list = []

        # 构建 docker-compose 命令
        docker_compose_files = [f"-f {docker_compose_path}"]

        # 如果有 override 文件，添加到命令中
        if override_file_paths:
            for override_file in override_file_paths:
                docker_compose_files.append(f"-f {override_file}")
        docker_compose_files_combined = ' '.join(docker_compose_files)

        # 分别构建 pull 和 build 命令
        docker_compose_build_command = f"docker compose {docker_compose_files_combined} build "
        # 可能会拉取失败，但是可能只依赖build出的镜像，所以不影响构建
        docker_compose_pull_command = f"docker compose {docker_compose_files_combined} pull" + COMMON_LOG_FILTER + "|| true"

        command_list.append(docker_compose_build_command)
        command_list.append(docker_compose_pull_command)

        command_content = '\n'.join(command_list)

        return command_content

    # 分析docker-compose，生成命令：复制所需的目录和文件到指定目录
    def _generate_copy_repo_files_command(self):
        reserved_files_and_dirs = self._get_reserved_files_and_dirs()

        commands = [f"mkdir -p {WORKSPACE_PATH}"]
        created_directories = set()
        created_directories.add(WORKSPACE_PATH)

        for path in reserved_files_and_dirs:
            relpath = os.path.relpath(path)
            origin_item_abspath = os.path.join(ORIGINAL_REPO_PATH, relpath)
            destination_path = os.path.join(WORKSPACE_PATH, os.path.dirname(relpath))
            if destination_path.endswith(os.sep):
                destination_path = destination_path[:-1]

            if destination_path not in created_directories:
                commands.append(f"mkdir -p \"{destination_path}\"")
                created_directories.add(destination_path)
            command = (
                f"if [ -e \"{origin_item_abspath}\" ]; then "
                f"cp -r \"{origin_item_abspath}\" \"{destination_path}/\"; "
                "fi"
            )
            commands.append(command)

        # 返回由换行符隔开的命令字符串
        return '\n'.join(commands)

    # 生成处理.env文件的命令
    def _generate_env_process_command(self):
        # 当用户指定了某个环境变量文件后，将其作为默认环境变量文件
        env_process_commands = [f'cd {WORKSPACE_PATH}']
        specified_env_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_ENV_PATH_KEY)
        if specified_env_path:
            # 目标 .env 文件的路径
            dir_name = os.path.dirname(specified_env_path)
            if not dir_name:
                dir_name = '.'

            target_env_path = f'{dir_name}/.env'

            # 检查仓库中是否已经存在 .env 文件
            if not os.path.exists(target_env_path):
                if os.path.exists(specified_env_path):
                    # 如果 .env 文件不存在，复制用户提供的文件到 .env
                    command = f"cp {specified_env_path} {target_env_path}"
                    env_process_commands.append(command)
            elif os.path.basename(specified_env_path) != os.path.basename(target_env_path):
                # 如果存在，将用户提供文件的内容追加到现有的 .env 文件中
                command = f"cat {specified_env_path} >> {target_env_path}"
                env_process_commands.append(command)

        return env_process_commands

    def _replace_variables(self):
        pre_start_command = self.parameters.get(project_setup_constant.PRE_START_COMMAND_KEY, '')
        docker_compose_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY)

        docker_compose_path = f'{project_setup_constant.DOCKER_COMPOSE_DIR}{os.path.relpath(docker_compose_path, os.getcwd())}'
        docker_compose_env_path = f'{os.path.dirname(docker_compose_path)}/.env'
        self.parameters[project_setup_constant.ENV_PATH] = docker_compose_env_path

        self.parameters[project_setup_constant.PRE_START_COMMAND_KEY] = pre_start_command

        # 如果是docker compose
        # 1. 提取出端口，修改对应的Parameters
        # 2. 提取出替换参数，生成替换命令
        service_ports_and_security_group_ports = DockerComposeHelper.parse_docker_compose_ports(
            self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY),
            self.parameters.get(project_setup_constant.DOCKER_COMPOSE_ENV_PATH_KEY)
        )
        security_group_ports = service_ports_and_security_group_ports.get(
            project_setup_constant.SECURITY_GROUP_PORTS_KEY, [])
        self.parameters[project_setup_constant.SECURITY_GROUP_PORTS_KEY] = security_group_ports
        service_ports = service_ports_and_security_group_ports.get(project_setup_constant.SERVICE_PORTS_KEY, {})
        self.parameters[project_setup_constant.SERVICE_PORTS_KEY] = service_ports
        self.parameters[
            project_setup_constant.ECS_IMAGE_BUILDER_COMMAND_CONTENT_KEY] = self._generate_ecs_image_builder_command()

        # 检查是否需要 GPU
        if self._check_gpu_requirement():
            self.parameters[project_setup_constant.IMAGE_ID_KEY] = project_setup_constant.GPU_ECS_SOURCE_IMAGE_ID
            self.parameters[project_setup_constant.NeedGPU_KEY] = True


    # 获取到需要保留的目录与文件
    def _get_reserved_files_and_dirs(self):
        # 获取 Docker Compose 文件路径和目标目录
        docker_compose_path = os.path.abspath(self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY))
        docker_compose_dir = os.path.dirname(docker_compose_path)

        # 初始化待复制集合
        files_to_copy = set()
        dirs_to_copy = set()

        # 添加 Docker Compose 文件到待复制集合
        files_to_copy.add(docker_compose_path)

        # 读取 Docker Compose YAML 文件
        try:
            with open(docker_compose_path, 'r') as stream:
                compose_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            self.developer_logger.error(f"Error parsing YAML file: {exc}", exc_info=1)
            return

        # 检测 env_file 文件以及 Dockerfile 和构建上下文
        # 获取所有相关路径
        specified_env_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_ENV_PATH_KEY)
        if specified_env_path:
            specified_env_path = os.path.abspath(specified_env_path)
            files_to_copy.add(specified_env_path)
        services = compose_data.get('services', {})
        for service in services.values():
            service_env_files = service.get('env_file', [])
            service_env_files = [service_env_files] if isinstance(service_env_files, str) else service_env_files

            for env_file in service_env_files:
                if isinstance(env_file, dict):
                    env_file = env_file.get('path', '')
                env_abs_path = os.path.abspath(os.path.join(docker_compose_dir, env_file))
                # 如果docker-compose中指定的env_file不存在，就不用添加到待复制集合了
                if os.path.exists(env_abs_path):
                    files_to_copy.add(env_abs_path)

            # 处理Dockerfile
            build_config = service.get('build', {})
            if build_config:
                if isinstance(build_config, str):
                    build_context_abs_path = os.path.abspath(build_config)
                    dockerfile_path = os.path.join(build_context_abs_path, 'Dockerfile')
                else:
                    # 获取build context相对于docker-compose.yaml的路径
                    build_context_rel_path = build_config.get('context', '.')
                    build_context_abs_path = os.path.abspath(os.path.join(docker_compose_dir, build_context_rel_path))
                    dockerfile_path = os.path.normpath(os.path.join(build_context_abs_path, build_config.get('dockerfile', 'Dockerfile')))
                # 确保目录和 Dockerfile 存在
                dockerfile_path = os.path.abspath(dockerfile_path)
                if os.path.exists(dockerfile_path):
                    dirs_to_copy.add(build_context_abs_path)
                    files_to_copy.add(dockerfile_path)

            # 检查卷挂载资源
            for volume in service.get('volumes', []):
                self.developer_logger.info(f"Processing volume: {volume}")

                if isinstance(volume, dict):
                    source = volume.get('source', '')
                    target = volume.get('target', '')
                    volume_type = volume.get('type', 'volume')

                    if volume_type == 'bind':
                        host_path = source
                    else:
                        self.developer_logger.info(
                            f"Volume named '{source}' of type '{volume_type}' not directly mapped to host unless bind.")
                        continue
                else:
                    # 考虑匿名卷的情况
                    if ':' not in volume:
                        continue

                    parts = volume.split(':')
                    host_path = parts[0]

                    # 考虑绑定挂载中需要宿主机目录或文件的情况
                    if host_path.startswith('/'):
                        continue

                host_abs_path = os.path.abspath(os.path.join(docker_compose_dir, host_path))

                if os.path.exists(host_abs_path):
                    if os.path.isfile(host_abs_path):
                        files_to_copy.add(host_abs_path)
                        self.developer_logger.info(f"Added file to copy: {host_abs_path}")
                    else:
                        dirs_to_copy.add(host_abs_path)
                        self.developer_logger.info(f"Added directory to copy: {host_abs_path}")
                else:
                    self.developer_logger.warning(
                        f"Volume host path '{host_abs_path}' does not exist. Will be created.")
                    # os.makedirs(host_abs_path, exist_ok=True)
                    dirs_to_copy.add(host_abs_path)
        filtered_dirs_to_copy = FileUtil.remove_subdirectories(dirs_to_copy)

        # 去除在保留目录中的文件
        files_to_copy -= {file_path for file_path in files_to_copy
                          if any(file_path.startswith(dir_path + os.sep) for dir_path in filtered_dirs_to_copy)}

        # 返回最终保留的目录与文件集合
        return filtered_dirs_to_copy.union(files_to_copy)

    def _check_gpu_requirement(self):
        """
        检查 docker-compose 文件中是否需要 GPU
        :return: 如果需要 GPU 返回 True，否则返回 False
        """
        docker_compose_path = os.path.abspath(self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY))
        try:
            with open(docker_compose_path, 'r') as stream:
                compose_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            self.developer_logger.error(f"Error parsing YAML file: {exc}", exc_info=1)
            return False

        services = compose_data.get('services', {})
        for service in services.values():
            deploy = service.get('deploy', {})
            resources = deploy.get('resources', {})
            reservations = resources.get('reservations', {})
            devices = reservations.get('devices', [])

            for device in devices:
                if device.get('driver') == 'nvidia' or 'gpu' in device.get('capabilities', []):
                    return True

        return False
