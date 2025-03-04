# -*- coding: utf-8 -*-
import json
import sys

import yaml
import click
import os
import stat
from computenestcli.common import constant
from computenestcli.common.logging_constant import SETUP_PROJECT, BUILD_SERVICE
from computenestcli.exception.global_exception_handler import GlobalExceptionHandler
from computenestcli.processor.artifact import ArtifactProcessor
from computenestcli.processor.service import ServiceProcessor
from computenestcli.processor.check import CheckProcessor
from computenestcli.processor.jinja2 import Jinja2Processor
from computenestcli.service.project_setup.project_setup import ProjectSetup
from computenestcli.common.context import Context
from computenestcli.common.credentials import Credentials
from computenestcli.service.project_initializer import ProjectInitializer
from computenestcli.base_log import get_user_logger

if sys.version_info >= (3, 10):
    from importlib import resources
else:
    import importlib_resources as resources

user_logger = get_user_logger(SETUP_PROJECT)

COMPUTENEST_CREDENTIALS_FILE_PATH = os.path.expanduser(constant.COMPUTENEST_CREDENTIALS_PATH)
ALIYUN_CLI_CREDENTIALS_FILE_PATH = os.path.expanduser(constant.ALIYUN_CLI_CREDENTIALS_PATH)
CONFIG_FILE_NAME = 'config.yaml'
DEFAULT_COMPUTENEST_PARAMETERS_PATH = '.computenest/.computenest_parameters.yaml'
COMPUTENEST_DIR = '.computenest'

DEFAULT_SERVICE_CONFIG = {
    'Service': {
        'RegionId': 'cn-hangzhou',
        'DeployMetadata': {
            'TemplateConfigs': [
                {
                    'Name': '模版1',
                    'Url': 'templates/template.yaml'
                }
            ]
        },
        'ServiceType': 'private',
        'ServiceInfo': {
            'Locale': 'zh-CN',
            'ShortDescription': 'A sample service.',
            'Image': 'https://service-info-public.oss-cn-hangzhou.aliyuncs.com/1853370294850618/service-image/bfd30cc4-e959-4093-b5cb-77a05058b911.png',
        }
    }
}


@click.group()
@click.version_option(package_name='computenest-cli')
def main():
    pass


# 使用该命令可以创建或者更新一个服务,需要在项目的根目录下执行
@click.command(
    name='import',
    help='Import a service configuration. '
         'If the service does not exist, it will be created, otherwise it will be updated. '
         'Execute this command in the project root directory that includes the .computenest directory.'
)
@click.option('--region_id',
              required=False,
              default='cn-hangzhou',
              help='The ID of the region where the service will be deployed. '
                   'For example, "cn-hangzhou" for Hangzhou region or "ap-southeast-1" for Singapore region.'
                   'If not specified, the region_id will be cn-hangzhou.')
@click.option('--update_artifact',
              default=False,
              help='Specify whether the artifact needs to be updated. '
                   'Set to "True" to update the existing artifact, or "False" to keep the existing one.')
@click.option('--service_info',
              required=False,
              help='A JSON string that describes a list of service information. '
                   'Each entry should have "Locale", "ShortDescription", "Image", and "Name".')
@click.option('--service_id',
              default=None,
              help='The unique identifier for the service. '
                   'If specified, this will be used to identify the service being imported, '
                   'and if service name is specified, '
                   'this command will update the service name to the specified service name.'
                   'If not specified, the service name will be used to identify the service. ')
@click.option('--service_name',
              default=None,
              help='The name of the service being imported. '
                   'This name will be used to identify the service.')
@click.option('--version_name',
              default=None,
              help='An optional description for the version of the service. '
                   'This can help differentiate between different deployments of the same service.')
@click.option('--icon',
              default=None,
              help='URL to the icon image for the service. '
                   'This URL should point to a publicly accessible image location (e.g., OSS URL).')
@click.option('--desc',
              default=None,
              help='A brief description of the service. '
                   'This information can help users understand the purpose of the service.')
@click.option('--file_path',
              required=False,
              help='The file path to the configuration file for the service. '
                   'This YAML file should contain all necessary settings for the service.'
                   'If not specified, the configuration file will use the .computenest/config.yaml of the current directory.')
@click.option('--access_key_id',
              required=False,
              help='The Access Key ID for authentication. '
                   'This should be provided by the service provider to authorize access.')
@click.option('--access_key_secret',
              required=False,
              help='The Access Key Secret for authentication. '
                   'This is used alongside the Access Key ID to validate the user’s credentials.')
@click.option('--security_token',
              default=None,
              help='An optional security token for additional authentication. '
                   'This is typically used for temporary security credentials.')
@click.option('--parameters',
              required=False,
              default='{}',
              help='A JSON string representing parameters to be passed to the service configuration. '
                   'This allows for dynamic settings when deploying the service.')
@click.option('--parameter_path',
              required=False,
              default='',
              help='The file path to a parameter file. If specified, this will override the parameters '
                   'provided in the --parameters option. This file should be in JSON or YAML format.')
@click.option('--extra_parameters',
              required=False,
              default='{}',
              help='Extra System parameters, such as source ip.')
def import_command(region_id, update_artifact, service_info, service_id, service_name, version_name, icon, desc,
                   file_path, access_key_id, access_key_secret, security_token, parameters, parameter_path,
                   extra_parameters):
    user_logger = get_user_logger(BUILD_SERVICE)
    credentials = get_credentials(access_key_id, access_key_secret, security_token)

    if service_info:
        service_info = json.loads(service_info)
    if parameter_path:
        with open(parameter_path, 'r') as stream:
            parameter_json = yaml.load(stream, Loader=yaml.FullLoader)
    else:
        parameter_json = json.loads(parameters)
    if not file_path:
        current_dir = os.path.basename(os.getcwd())
        if current_dir == COMPUTENEST_DIR:
            # 当前目录为.computenest
            user_logger.info('The file path is not specified, using config.yaml in the current directory.')
            file_path = os.path.join(os.getcwd(), CONFIG_FILE_NAME)
        else:
            # 如果当前目录不是 .computenest，则使用默认路径
            user_logger.info('The file path is not specified, using the default path: .computenest/config.yaml')
            file_path = os.path.join(os.getcwd(), COMPUTENEST_DIR, CONFIG_FILE_NAME)
    # 如果没有config.yaml，使用默认的配置
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        config = DEFAULT_SERVICE_CONFIG
    else:
        with open(file_path, 'r') as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)
    if region_id is None:
        region_id = config[constant.SERVICE][constant.REGION_ID]
    elif region_id not in (constant.CN_HANGZHOU, constant.AP_SOUTHEAST_1):
        click.echo('The region_id is not supported, only cn-hangzhou and ap-southeast-1 are supported.')
        return

    extra_parameters_json = None
    try:
        extra_parameters_json = json.loads(extra_parameters)
    except json.JSONDecodeError:
        user_logger.warning('The extra_parameters is not a valid JSON string.')
    context = Context(region_id, credentials, extra_parameters_json)
    service = ServiceProcessor(context)
    check = CheckProcessor(config, file_path, service_name, service_id)
    check.processor()
    service.import_command(data_config=config, file_path=file_path, update_artifact=update_artifact,
                           service_info=service_info, service_id=service_id, service_name=service_name,
                           version_name=version_name, icon=icon, desc=desc, parameters=parameter_json)


@click.command(name='export')
@click.option('--region_id',
              required=False,
              default='cn-hangzhou',
              help='The ID of the region where the service will be deployed. '
                   'For example, "cn-hangzhou" for Hangzhou region or "ap-southeast-1" for Singapore region.'
                   'If not specified, the region_id will be cn-hangzhou.')
@click.option('--service_id',
              required=True,
              help='The unique identifier for the service to be exported. '
                   'This ID is required to specify which service configuration you wish to export.')
@click.option('--version_name',
              required=False,
              help='An optional name for the version of the service being exported. '
                   'This can help differentiate versions of configurations being managed.')
@click.option('--export_type',
              default='FULL_SERVICE',
              help='Type of export to be performed. '
                   'Valid options include "CONFIG_ONLY" to export only the configuration files, '
                   'or "FULL_SERVICE" to export the entire service including all related components and configurations.')
@click.option('--output_dir',
              required=False,
              help='The directory where the exported files will be saved. '
                   'Make sure this path is writable and that you have permission to write to it.'
                   'If not specified, the exported files will be saved in the .computenest directory of the current working directory.')
@click.option('--export_project_name',
              required=False,
              help='Optional name for the exported project. '
                   'If specified, this name can be used to identify the project in the output directory.')
@click.option('--export_file_name',
              required=False,
              default='config.yaml',
              help='The name of the exported configuration file. '
                   'By default, this will be "config.yaml". You can specify a different name if required.')
@click.option('--access_key_id',
              required=False,
              help='The Access Key ID for authentication with the service provider. '
                   'This is necessary for API authentication and should be kept secure.')
@click.option('--access_key_secret',
              required=False,
              help='The Access Key Secret associated with the Access Key ID. '
                   'This value is crucial for securely verifying the user’s identity and must not be shared.')
@click.option('--security_token',
              default=None,
              help='An optional security token for additional authentication. '
                   'This is typically used with temporary security credentials'
                   ' to enhance security during the export process.')
def export_command(region_id, service_id, version_name, export_type, output_dir, export_project_name,
                   export_file_name, access_key_id, access_key_secret, security_token):
    context = Context(region_id, get_credentials(access_key_id, access_key_secret, security_token))
    service = ServiceProcessor(context)
    if not output_dir:
        output_dir = COMPUTENEST_DIR
    service.export_command(service_id, version_name, export_type, output_dir, export_project_name, export_file_name)


@click.command(name='generate')
@click.option('--type',
              required=False,
              default='project',
              help='Type of generation, including the whole project or a single file.')
@click.option('--file_path',
              required=False,
              help='File path for the specific file to generate.')
@click.option('--parameters',
              required=False,
              help='Parameters for the generation process in JSON format. Default is an empty JSON object.')
@click.option('--output_path',
              required=False,
              default=COMPUTENEST_DIR,
              help='The directory where the generated files will be saved. '
                   'Ensure you have permission to write to this path.'
                   'If not specified, the generated files will be saved in the .computenest directory'
                   ' of the current working directory.')
@click.option('--parameter_path',
              required=False,
              help='Path to a parameter file. This option overrides the parameters provided in the parameters option.'
                   'If parameters_path and parameters not specified, the parameters will be read from '
                   'the .computenest/.computenest_parameters.yaml file in the current directory.')
@click.option('--overwrite', '-y', is_flag=True, help='Confirm overwrite of output file without prompt.')
def generate_command(file_path, type, parameters, output_path, parameter_path, overwrite):
    jinja2 = Jinja2Processor()
    if parameter_path is None and parameters is None:
        parameter_path = DEFAULT_COMPUTENEST_PARAMETERS_PATH
    if parameter_path:
        # 判断如果不存在则直接打出错误日志
        if not os.path.exists(parameter_path):
            user_logger.error(f'The parameters_path {parameter_path} does not exist.')
        with open(parameter_path, 'r') as stream:
            parameter_json = yaml.load(stream, Loader=yaml.FullLoader)
    else:
        parameter_json = json.loads(parameters)
    # 如果文件已经存在，向用户提示是否想要继续
    if os.path.exists(output_path) and not overwrite:
        click.confirm(f'The file {output_path} already exists. Do you want to overwrite it?', abort=True)
    if file_path:
        jinja2.process(file_path, parameter_json, output_path)
        return
    if type == 'project':
        if not output_path:
            output_path = COMPUTENEST_DIR
        project_setup_service = ProjectSetup(output_path, parameter_json)
        project_setup_service.setup_project()


@click.command(name='login')
@click.option('--access_key_id',
              required=True,
              help='The Access Key ID for authentication with the service provider. '
                   'This is required for authentication and identifies the user account. '
                   'If credentials have already been configured using aliyun-cli, '
                   'those credentials will be utilized automatically.')
@click.option('--access_key_secret',
              required=True,
              help='The Access Key Secret associated with the Access Key ID. '
                   'It is used to securely verify the user’s identity and must be kept confidential. '
                   'If credentials have already been configured using aliyun-cli, '
                   'those credentials will be utilized automatically.')
@click.option('--security_token',
              default=None,
              help='An optional security token used for temporary credentials. '
                   'Provide this token if using temporary security credentials. '
                   'If credentials have already been configured using aliyun-cli, '
                   'those credentials will be utilized automatically.')
def login_command(access_key_id, access_key_secret, security_token):
    os.makedirs(os.path.dirname(COMPUTENEST_CREDENTIALS_FILE_PATH), exist_ok=True)
    credentials = {
        'access_key_id': access_key_id,
        'access_key_secret': access_key_secret,
        'security_token': security_token
    }
    if os.path.exists(COMPUTENEST_CREDENTIALS_FILE_PATH):
        os.remove(COMPUTENEST_CREDENTIALS_FILE_PATH)
    with open(COMPUTENEST_CREDENTIALS_FILE_PATH, 'w') as f:
        yaml.dump(credentials, f)
    os.chmod(COMPUTENEST_CREDENTIALS_FILE_PATH, stat.S_IRUSR)
    click.echo('Credentials saved successfully.')


@click.command(name='init-project')
@click.option('--project_name',
              required=True,
              help='The name of the project to be initialized. '
                   'This name will be used to create the project directory, '
                   'supported projects can be listed by running "computenest-cli list-projects".')
@click.option('--output_path',
              required=False,
              default='.',
              help='The path where the project files and directory will be created. '
                   'Specify a valid directory path (e.g., /path/to/your/project) to determine where the project will be set up. '
                   'If no path is provided, the project will be created in the current working directory (denoted by ".").')
def init_project_command(project_name, output_path):
    project_name = project_name.strip()
    supported_projects = load_supported_projects('')

    project = next((proj for proj in supported_projects if proj['name'] == project_name), None)
    if project is None:
        click.echo(f'Project {project_name} is not supported.'
                   f'You can list supported projects by running "computenest-cli list-projects".')
        return 1

    project_initializer = ProjectInitializer(project_name, output_path)
    project_initializer.download_project()


@click.command(name='list-projects')
@click.option('--service_type',
              required=False,
              help='The type of services to filter the listed projects. '
                   'Valid options include "private", indicating that the services are deployed on user-owned resources, '
                   'and "managed", indicating that the services are hosted on resources provided by the service provider. '
                   'If no type is specified, all projects will be listed regardless of service type. '
                   'Use this option to narrow down the results to specific service types that fit your deployment needs.')
def list_projects_command(service_type):
    supported_projects = load_supported_projects(service_type)
    click.echo('Supported Projects:')
    headers = ["Name", "Service Type", "Description", "GitHub URL"]
    table = [headers]
    row_format = "{:<40} {:<10} {:<40} {:<60}"
    separator = '-' * (len(row_format.format(*headers)) + 2)

    for project in supported_projects:
        row = [project['name'], project['service_type'], project['description'], project['github_url']]
        table.append(row)

    click.echo(separator)
    click.echo(row_format.format(*headers))
    click.echo(separator)

    for row in table[1:]:
        click.echo(row_format.format(*row))
    click.echo(separator)

@click.command(
    name='deliver-artifact',
    help='Deliver images in the yaml file. '
         'Automatically detect container images referenced in docker-compose.yaml or Helm charts and replace them with managed artifacts.'
)
@click.option('--region_id',
              required=False,
              default='cn-hangzhou',
              help='The ID of the region where the service will be deployed. '
                   'For example, "cn-hangzhou" for Hangzhou region or "ap-southeast-1" for Singapore region.'
                   'If not specified, the region_id will be cn-hangzhou.')
@click.option('--delivery_type',
              required=False,
              default='DockerCompose',
              help='Project types for image delivery.'
                   'Options: DockerCompose or HelmChart'
                   '"DockerCompose" for projects using docker-compose.yaml or "HelmChart" for projects utilizing helm charts.')
@click.option('--file_path',
              required=False,
              default='.',
              help='Specify either the working directory or a project configuration file. '
                   'You can provide a directory as the working directory or supply the path to a specific file, '
                   'such as docker-compose.yaml or values.yaml. ')
@click.option('--access_key_id',
              required=False,
              help='The Access Key ID for authentication. '
                   'This should be provided by the service provider to authorize access.')
@click.option('--access_key_secret',
              required=False,
              help='The Access Key Secret for authentication. '
                   'This is used alongside the Access Key ID to validate the user’s credentials.')
@click.option('--security_token',
              default=None,
              help='An optional security token used for temporary credentials. '
                   'If you are using a temporary security credential, provide this token to authenticate your access. '
                   'This is typically provided by the service provider during the authentication process.')
def deliver_command(region_id, delivery_type, file_path, access_key_id, access_key_secret, security_token):
    context = Context(region_id, get_credentials(access_key_id, access_key_secret, security_token))
    artifact = ArtifactProcessor(context)
    artifact.deliver_command(region_id, delivery_type, file_path)


# 优先从COMPUTENEST_CREDENTIALS_FILE_PATH中获取
# 如果没有，则从ALIYUN_CLI_CREDENTIALS_FILE_PATH中加载
# 阿里云命令行参考：https://help.aliyun.com/zh/cli/configure-credentials
def load_credentials_from_file():
    if os.path.exists(COMPUTENEST_CREDENTIALS_FILE_PATH):
        with open(COMPUTENEST_CREDENTIALS_FILE_PATH, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    elif os.path.exists(ALIYUN_CLI_CREDENTIALS_FILE_PATH):
        with open(ALIYUN_CLI_CREDENTIALS_FILE_PATH, 'r') as f:
            credentials = json.load(f)
            if credentials:
                if 'current' in credentials and 'profiles' in credentials:
                    current_profile_name = credentials['current']
                    for profile in credentials['profiles']:
                        if profile['name'] == current_profile_name:
                            return {
                                'access_key_id': profile.get('access_key_id', ''),
                                'access_key_secret': profile.get('access_key_secret', ''),
                                'security_token': profile.get('security_token', '')
                            }
    return None


def get_credentials(access_key_id=None, access_key_secret=None, security_token=None):
    # 检查传入的凭证参数是否存在
    if access_key_id and access_key_secret:
        return Credentials(access_key_id, access_key_secret, security_token)

    # 如果没有提供凭证，则从文件中加载
    credentials = load_credentials_from_file()
    if credentials:
        access_key_id = access_key_id or credentials.get(constant.ACCESS_KEY_ID)
        access_key_secret = access_key_secret or credentials.get(constant.ACCESS_KEY_SECRET)
        security_token = security_token or credentials.get(constant.SECURITY_TOKEN)

    if not access_key_id or not access_key_secret:
        raise click.ClickException('Access Key ID and Access Key Secret must be provided or set via the login command.')

    return Credentials(access_key_id, access_key_secret, security_token)


def load_supported_projects(service_type):
    with resources.open_text(constant.SUPPORTED_PROJECTS_RESOURCE_DIR, constant.SUPPORTED_PROJECTS_NAME) as f:
        supported_projects = yaml.load(f, Loader=yaml.FullLoader).get('projects', [])
    if service_type == 'private':
        return [proj for proj in supported_projects if proj['service_type'] == 'private']
    elif service_type == 'managed':
        return [proj for proj in supported_projects if proj['service_type'] == 'managed']
    else:
        return supported_projects


main.add_command(import_command)
main.add_command(export_command)
main.add_command(generate_command)
main.add_command(login_command)
main.add_command(init_project_command)
main.add_command(list_projects_command)
main.add_command(deliver_command)

if __name__ == '__main__':
    global_exception_handler = GlobalExceptionHandler()
    sys.excepthook = global_exception_handler.exception_handler
    main()
