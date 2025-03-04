import yaml

from computenestcli.common import project_setup_constant
from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.base_log import get_user_logger
from computenestcli.base_log import get_developer_logger
from computenestcli.processor.deliver_image.impl.base import DeliverImageProcessor

developer_logger = get_developer_logger()
user_logger = get_user_logger(BUILD_SERVICE)

class DeliverImageDockerComposeProcessor(DeliverImageProcessor):
    def extract_docker_images_from_template(self, file_path):
        user_logger.info("docker compose get docker images start.")
        # 解析docker-compose.yaml，找到其中的开源镜像
        with open(file_path, 'r') as stream:
            docker_compose_dict = yaml.load(stream, Loader=yaml.FullLoader)
        docker_image_urls = set()
        # 遍历 services 找到所有的 image_url
        services = docker_compose_dict.get('services', {})
        try:
            for service, config in services.items():
                image_url = config.get('image')
                if not image_url or project_setup_constant.ALI_DOCKER_REPO_HOST_SUFFIX in image_url \
                        or config.get('secrets') or config.get("build"):
                    continue
                docker_image_urls.add(image_url)
        except Exception as e:
            user_logger.error(f"docker compose get docker images failed: {e}")
            raise
        user_logger.info(
            f"Docker compose get docker images success, docker images:{docker_image_urls}")
        return docker_image_urls

