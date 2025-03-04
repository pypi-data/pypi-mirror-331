from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.common.delivery_type import DeliveryType
from computenestcli.base_log import get_user_logger
from computenestcli.base_log import get_developer_logger
from computenestcli.processor.deliver_image.impl.base import DeliverImageProcessor
from computenestcli.processor.deliver_image.impl.docker_compose import DeliverImageDockerComposeProcessor
from computenestcli.processor.deliver_image.impl.helm_chart import DeliverImageHelmChartProcessor
from typing import Dict

developer_logger = get_developer_logger()
user_logger = get_user_logger(BUILD_SERVICE)

class DeliverImageManager:
    def __init__(self, delivery_type):
        self.delivery_type = delivery_type
        self.deliver_image_processor_map: Dict[DeliveryType, DeliverImageProcessor] = {}
        self.deliver_image_processor_map[DeliveryType.DOCKER_COMPOSE.value] = DeliverImageDockerComposeProcessor()
        self.deliver_image_processor_map[DeliveryType.HELM_CHART.value] = DeliverImageHelmChartProcessor()

    def get_deliver_image_processor(self, delivery_type):
        return self.deliver_image_processor_map.get(delivery_type)

    def extract_docker_images_from_template(self, file_path):
        try:
            processor = self.get_deliver_image_processor(self.delivery_type)
            if not processor:
                raise ValueError("No suitable processor found for the given delivery type.")
            return processor.extract_docker_images_from_template(file_path)
        except Exception as e:
            user_logger.error(f"Failed to extract docker images from template: {e}")
            raise

    def save_image_mapping(self, file_path, image_urls, docker_host_path):
        try:
            processor = self.get_deliver_image_processor(self.delivery_type)
            if not processor:
                raise ValueError("No suitable processor found for the given delivery type.")
            return processor.save_image_mapping(file_path, image_urls, docker_host_path)
        except Exception as e:
            user_logger.error(f"Failed to save image mapping: {e}")
            raise

