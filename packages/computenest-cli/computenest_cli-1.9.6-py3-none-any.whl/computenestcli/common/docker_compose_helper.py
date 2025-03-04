import os
import re

import yaml
import shutil
from datetime import datetime
from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.base_log import get_developer_logger
from computenestcli.base_log import get_user_logger
from computenestcli.common.str_util import StrUtil
from computenestcli.common import project_setup_constant

developer_logger = get_developer_logger()
user_logger = get_user_logger(BUILD_SERVICE)


class DockerComposeHelper:
    def __init__(self):
        pass

    # 生成替换docker-compose.yaml中pull_policy的sed命令
    @staticmethod
    def generate_docker_compose_sed_command(docker_compose_path):
        # 替换always为if_not_present
        return f"sed -i 's/pull_policy: always/pull_policy: if_not_present/g' {docker_compose_path}"

    # 读取env文件内容
    @staticmethod
    def get_env_content(specified_env_file_path):
        env_content = ''
        env_abs_path = ''
        if specified_env_file_path:
            env_abs_path = os.path.abspath(specified_env_file_path)
        if env_abs_path and os.path.exists(env_abs_path):
            with open(env_abs_path, 'r') as file:
                env_content = file.read()
        return env_content

    # 生成替换.env中指定参数的值的sed命令与echo命令
    @staticmethod
    def generate_env_sed_commands(custom_parameters, docker_compose_path, specified_env_file_path):
        commands = []

        # 解析 docker-compose.yaml 获取 env_file 引用
        with open(docker_compose_path, 'r') as stream:
            try:
                compose_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                user_logger.info(f"Error parsing YAML file: {exc}")
                return []

        # 获取 docker-compose 中所有的 env_file 路径
        env_files = set()
        env_files.add(specified_env_file_path)
        docker_compose_dir = os.path.dirname(docker_compose_path)
        for service in compose_data.get('services', {}).values():
            service_env_files = service.get('env_file', [])
            service_env_files = [service_env_files] if isinstance(service_env_files, str) else service_env_files
            for env_file in service_env_files:
                if isinstance(env_file, dict):
                    env_file = env_file.get('path', '')
                env_files.add(os.path.join(docker_compose_dir, env_file))

        for env_file_path in env_files:
            # 检查目录是否存在，不存在则创建
            env_abs_path = os.path.abspath(env_file_path)
            env_content = ''
            if os.path.exists(env_abs_path):
                with open(env_abs_path, 'r') as file:
                    env_content = file.read()

            # DockerCompose 相关文件在 ROS 模板中的实际路径
            docker_compose_env_path = f'{project_setup_constant.DOCKER_COMPOSE_DIR}{os.path.relpath(env_file_path, os.getcwd())}'

            if env_file_path == specified_env_file_path:
                docker_compose_env_path = f'{os.path.dirname(docker_compose_env_path)}/.env'
            for param in custom_parameters:
                name = param.get("Name")
                if name:
                    variable_pattern = f"{name}="
                    # 如果变量存在则替换
                    if variable_pattern in env_content:
                        command = f"sed -i 's/{variable_pattern}[^\\n]*/{variable_pattern}${{{name}}}/' {docker_compose_env_path}"
                        commands.append(command)
                    elif env_file_path == specified_env_file_path:
                        # 如果变量不存在则添加到.env文件中
                        command = f"echo '{name}=${{{name}}}' >> {docker_compose_env_path}"
                        commands.append(command)

        return commands

    @staticmethod
    def resolve_env_variable(port_str, env_dict):
        # 正则表达式匹配不同的替换模式
        env_var_pattern = re.compile(r'\${([^:}]+)(?::-([^}]+))?}')  # 匹配 ${VAR} 或 ${VAR:-default}

        def replace_var(match):
            var_name = match.group(1)
            default = match.group(2) if match.group(2) is not None else None
            if var_name in env_dict:
                return env_dict[var_name]
            elif default is not None:
                return default
            else:
                raise Exception(f"Port not specified or specified in an invalid way: '{var_name}' is missing and no default value provided.")

        return env_var_pattern.sub(replace_var, port_str)

    @staticmethod
    def parse_docker_compose_ports(docker_compose_path, docker_compose_env_path):
        """
        解析 docker-compose 文件以提取端口信息。

        返回:
            dict: 包含两个字段的字典：
                - ServicePorts: 含有每个服务的端口信息，形式为服务名与其列表的端口-协议对。
                - SecurityGroupPorts: 去重后的所有主机级别端口的列表，用于安全组配置。

        异常:
            - FileNotFoundError: 如果 docker-compose 文件路径无效或找不到该文件。
            - ValueError: 如果端口格式无效。

        备注:
            - 默认为 TCP 协议，如果端口未指定协议。
            - 处理多种端口表示法，包括：
                * 单个端口（例如，"3000"）
                * 映射端口（例如，"8000:8080"）
                * 主机特定端口（例如，"127.0.0.1:8001:8001"）
                * 指定协议的端口（例如，"50000:50000/tcp"）
        示例返回结构:
        {
            "ServicePorts": {
                "webapp": [
                    ("8080", "tcp"),
                    ("443", "tcp")
                ]
            },
            "SecurityGroupPorts": [
                "8080",
                "443",
            ]
        }
        """
        if not os.path.isabs(docker_compose_path):
            docker_compose_path = os.path.abspath(docker_compose_path)

        with open(docker_compose_path, 'r') as file:
            compose_content = yaml.safe_load(file)

        env_dict = DockerComposeHelper.parse_docker_compose_env(docker_compose_env_path)
        service_ports_details = {}
        security_group_ports = set()

        services = compose_content.get('services', {})
        for service_name, service_data in services.items():
            service_ports_list = service_data.get('ports', [])
            service_item_ports = set()  # 使用集合来去重端口信息

            for port in service_ports_list:
                protocol = 'tcp'
                if isinstance(port, (str, int)):
                    port_str = str(port)

                    # 解析带有默认值的环境变量
                    port_str = DockerComposeHelper.resolve_env_variable(port_str, env_dict)

                    parts = port_str.split(':')
                    if len(parts) == 1:  # "3000"
                        host_port = container_port = parts[0]
                    elif len(parts) == 2:  # "8000:8000", "49100:22"
                        host_port, container_port = parts
                    elif len(parts) == 3:  # "127.0.0.1:8001:8001"
                        _, host_port, container_port = parts
                    else:
                        raise ValueError(f"Invalid port format: {port}")

                    if '/' in container_port:  # "50000:50000/tcp"
                        container_port, protocol = container_port.split('/')
                elif isinstance(port, dict):
                    host_port = str(port.get('published', port.get('target')))
                    protocol = port.get('protocol', 'tcp')
                else:
                    raise ValueError(f"Invalid port format: {port}")

                security_group_ports.add((host_port, protocol))  # 将端口添加到 SecurityGroupPorts

                if protocol == 'tcp':
                    service_item_ports.add((host_port, protocol))

            service_ports_details[service_name] = list(service_item_ports)  # 转回列表以便返回

        result = {
            project_setup_constant.SERVICE_PORTS_KEY: service_ports_details,
            project_setup_constant.SECURITY_GROUP_PORTS_KEY: list(security_group_ports)
        }

        return result

    # 读取docker compose环境变量文件，并将其中的键值对返回
    @staticmethod
    def parse_docker_compose_env(docker_compose_env_path):
        env_vars = {}
        if not docker_compose_env_path:
            return env_vars
        if not os.path.isabs(docker_compose_env_path):
            docker_compose_env_path = os.path.abspath(docker_compose_env_path)
        if os.path.exists(docker_compose_env_path):
            with open(docker_compose_env_path, 'r') as file:
                for line in file:
                    # 去除空白和换行
                    line = line.strip()
                    # 忽略注释行
                    if line.startswith('#') or not line:
                        continue
                    # 分割键值对
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            return env_vars
        return {}