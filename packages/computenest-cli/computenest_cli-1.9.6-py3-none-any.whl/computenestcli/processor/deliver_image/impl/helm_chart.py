import os

from computenestcli.common import project_setup_constant
from computenestcli.base_log import get_developer_logger
from computenestcli.base_log import get_user_logger
from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.processor.deliver_image.impl.base import DeliverImageProcessor
from computenestcli.common.util import Util

developer_logger = get_developer_logger()
user_logger = get_user_logger(BUILD_SERVICE)

class DeliverImageHelmChartProcessor(DeliverImageProcessor):
    def extract_docker_images_from_template(self, file_path):
        user_logger.info("helm chart get docker images start.")
        # 尝试安装helm
        DeliverImageHelmChartProcessor.install_helm()
        # 运行 `helm template` 命令并返回其输出。
        dir_path = os.path.dirname(file_path)
        cmd = [
            f'helm template -f {file_path} {dir_path}'
        ]
        helm_output, helm_error = Util.run_cli_command(cmd, dir_path)
        # 获取 helm 中依赖的容器镜像
        helm_image_urls = set()
        for line in helm_output.decode().splitlines():
            if 'image:' in line:
                image_url = line.split('image:', 1)[1].strip().strip('"').strip("'")
                if not image_url or project_setup_constant.ALI_DOCKER_REPO_HOST_SUFFIX in image_url:
                    continue
                helm_image_urls.add(image_url)
        user_logger.info(
            f"Helm chart get docker images success, docker images:{helm_image_urls}")
        return helm_image_urls

    @staticmethod
    def install_helm():
        user_logger.info("helm chart install start.")
        if DeliverImageHelmChartProcessor.is_helm_installed():
            user_logger.info("Skipping installation as Helm is already installed.")
            return
        # 运行安装 helm 的命令
        cmd = 'curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash'
        user_logger.info(f"Executing Helm installation command: {cmd}")
        stdout, stderr = Util.run_cli_command(cmd, cwd=None)
        user_logger.debug(f"Helm installation output: {stdout.decode()}")
        user_logger.info("Helm chart installed successfully.")

    @staticmethod
    def is_helm_installed():
        try:
            stdout, stderr = Util.run_cli_command('helm version --short', cwd=None)
            user_logger.info(f"Helm is already installed: {stdout.decode()}")
            return True
        except ValueError:
            return False

