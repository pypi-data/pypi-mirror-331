import os
import time
import json

from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.service.image import ImageService
from computenestcli.common.util import Util
from computenestcli.common import constant
from computenestcli.service.credentials import CredentialsService
from computenestcli.base_log import get_user_logger, log_monitor
from computenestcli.base_log import get_developer_logger

developer_logger = get_developer_logger()
user_logger = get_user_logger(BUILD_SERVICE)

IMAGEID = 'imageId'
RUNNING = 'Running'
WAITING = 'Waiting'
QUEUED = 'Queued'
FAILED = 'Failed'
SUCCESS = 'Success'
RESPONSE = 'Response'
INVOCATIONS = 'Invocations'
INVOCATION = 'Invocation'
INVOKEINSTANCES = 'InvokeInstances'
INVOKEINSTANCE = 'InvokeInstance'
INVOCATIONRESULTS = 'InvocationResults'
INVOCATIONRESULT = 'InvocationResult'
OUTPUT = 'Output'
ACS_ECS_RUNCOMMAND = 'ACS::ECS::RunCommand'
MAX_RETRIES = 3
MAX_WAIT_TIME_SECOND = 1


class ImageProcessor:

    def __init__(self, context):
        self.context = context

    def get_execution_logs(self, execution_id):
        response = ImageService.list_task_executions(self.context, execution_id).body.task_executions
        for task_execution in response:
            if task_execution.task_action == ACS_ECS_RUNCOMMAND and (
                    task_execution.status == FAILED or task_execution.status == SUCCESS):
                child_execution_id = task_execution.task_execution_id
                execution_logs = json.loads(
                    ImageService.list_execution_logs(self.context, child_execution_id).body.execution_logs[2].message)
                if task_execution.status == FAILED:
                    execution_log = \
                    execution_logs[RESPONSE][INVOCATIONS][INVOCATION][0][INVOKEINSTANCES][INVOKEINSTANCE][0][OUTPUT]
                elif task_execution.status == SUCCESS:
                    execution_log = execution_logs[RESPONSE][INVOCATION][INVOCATIONRESULTS][INVOCATIONRESULT][0][OUTPUT]
                message = Util.decode_base64(execution_log)
            elif task_execution.status == FAILED:
                message = task_execution.status_message
        return message

    @log_monitor("BuildService", "BuildArtifacts", "EcsImageBuild")
    def process_image(self, image_data):
        retry_times = 0
        execution_id = ImageService.start_update_image_execution(self.context, image_data)
        user_logger.info(
                         f"The task： {execution_id} to create an image has started executing. "
                         )
        while True:
            image_data = ImageService.list_execution(self.context, execution_id)
            execution = image_data.body.executions[0]
            status = execution.status
            if status == RUNNING or status == WAITING or status == QUEUED:
                current_tasks = execution.current_tasks
                if current_tasks is None or len(current_tasks) == 0:
                    if retry_times < MAX_RETRIES:
                        retry_times += 1
                        time.sleep(MAX_WAIT_TIME_SECOND)
                        continue
                    if retry_times >= MAX_RETRIES:
                        raise Exception("Build image failed, error message: ", execution.status_message)
                current_task = current_tasks[0].task_name
                user_logger.info(f'Executing...The current task is :{current_task}')
            elif status == FAILED:
                raise Exception("Execution failed, Error message: ", execution.status_message)
                # try:
                #     execution_log = self.get_execution_logs(execution_id)
                #     dlogger.info("The detailed execution exception: \n", execution_log)
                # except Exception as e:
                #     dlogger.info('get execution exception failed', e)
            elif status == SUCCESS:
                image_data = ImageService.list_execution(self.context, execution_id)
                outputs = json.loads(image_data.body.executions[0].outputs)
                image_id = outputs[IMAGEID]
                current_time = Util.get_current_time()
                try:
                    execution_log = self.get_execution_logs(execution_id)
                    # dlogger.info("The detailed execution exception: \n", execution_log)
                except Exception as e:
                    user_logger.error('get execution exception failed', e)
                log_message = (
                    f"Successfully created a new image {image_id}! "
                )

                # 打印合并后的日志
                user_logger.info(log_message)
                break
            time.sleep(100)

        return image_id

    def process_acr_image(self, acr_image_name, acr_image_tag, repo_path, docker_repo_url, build_type, build_args: [],
                          dockerfile_path: ""):
        response = CredentialsService.get_artifact_repository_credentials(self.context, constant.ACR_IMAGE)
        username = response.body.credentials.username
        password = response.body.credentials.password
        repository_name = response.body.available_resources[0].repository_name
        docker_host_path = os.path.dirname(response.body.available_resources[0].path)
        # 准备构建参数
        build_arg_commands = []
        if build_args:
            for arg in build_args:
                build_value = arg.get(constant.DOCKER_BUILD_ARGUMENT_VALUE)
                name = arg.get(constant.DOCKER_BUILD_ARGUMENT_NAME)
                if name and build_value:  # 确保 name 和 value 都不为空
                    build_arg_commands.append(f"--build-arg {name}={build_value}")

        build_args_str = " ".join(build_arg_commands) if build_arg_commands else ""
        if build_type == constant.DOCKER_REPO_TYPE:
            commands = [
                f"docker pull {docker_repo_url}",
                f"docker login {repository_name} --username={username} --password={password}",
                f"docker tag {docker_repo_url} {docker_host_path}/{acr_image_name}:{acr_image_tag}",
                f"docker push {docker_host_path}/{acr_image_name}:{acr_image_tag}"
            ]
        elif build_type == constant.DOCKER_FILE_TYPE:
            developer_logger.info(f"repo_path: {repo_path}")
            commands = [
                f"sudo docker build {build_args_str} -t {acr_image_name}:{acr_image_tag} -f {dockerfile_path} {repo_path}",
                f"sudo docker login {repository_name} --username={username} --password={password}",
                f"sudo docker tag {acr_image_name}:{acr_image_tag} {docker_host_path}/{acr_image_name}:{acr_image_tag}",
                f"sudo docker push {docker_host_path}/{acr_image_name}:{acr_image_tag}"
            ]
        else:
            raise ValueError(f"acr_image build_type {build_type} is not supported")

        try:
            for command in commands:
                Util.run_command_with_real_time_logging(command, repo_path)
        except Exception as e:
            user_logger.error(f"Error occurred: {e}")
            raise e

    @log_monitor("BuildService", "BuildArtifacts", "HelmPackageBuild")
    def process_helm_chart(self, file_path, helm_chart_repo_name, helm_chart_tag, helm_chart_url, build_type):
        response = CredentialsService.get_artifact_repository_credentials(self.context, constant.HELM_CHART)
        username = response.body.credentials.username
        password = response.body.credentials.password
        repository_name = response.body.available_resources[0].repository_name
        chart_path = os.path.dirname(response.body.available_resources[0].path)
        if build_type == constant.HELM_REPO_TYPE:
            local_repo_name = helm_chart_url.split("/")[2]
            commands = [
                f"helm repo add {local_repo_name} {helm_chart_url}",
                f"helm pull {local_repo_name}/{helm_chart_repo_name} --version {helm_chart_tag}",
                f"helm registry login -u {username} {repository_name} -p {password}",
                f"helm push {helm_chart_repo_name}-{helm_chart_tag}.tgz oci://{chart_path}"
            ]
        elif build_type == constant.HELM_PACKAGE_TYPE:
            file_name = file_path.split("/")[-1]
            file_path = os.path.dirname(file_path)
            commands = [
                f"helm registry login -u {username} {repository_name} -p {password}",
                f"helm push {file_name} oci://{chart_path}"
            ]
        else:
            raise ValueError(f"helm_chart build_type {build_type} is not supported")

        merged_command = " && ".join(commands)
        try:
            output, error = Util.run_cli_command(merged_command, file_path)
            user_logger.info(output.decode())
            user_logger.info(error.decode())
        except Exception as e:
            user_logger.error(f"Error occurred: {e}")
            raise e
