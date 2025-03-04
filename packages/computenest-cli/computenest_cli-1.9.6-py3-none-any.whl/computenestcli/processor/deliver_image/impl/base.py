import os
import yaml

from computenestcli.common.str_util import StrUtil
from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.common.delivery_type import DeliveryType
from computenestcli.base_log import get_user_logger
from computenestcli.base_log import get_developer_logger
from typing import Dict

developer_logger = get_developer_logger()
user_logger = get_user_logger(BUILD_SERVICE)

class DeliverImageProcessor:
    @staticmethod
    def save_image_mapping(file_path, image_urls, docker_host_path):
        user_logger.info(f"save image mapping start.")
        # 原镜像与上传后镜像的映射关系
        image_mapping_dict = {
            "image-mapping": []
        }
        for image_url in image_urls:
            split_image_url = StrUtil.format_image_url(image_url)
            new_image_url = f"{docker_host_path}/{split_image_url}"
            image_mapping_dict["image-mapping"].append({
                image_url: new_image_url
            })

        user_logger.info(f"build image mapping success.")
        try:
            # 获取 file_path 所在的目录并确保目录存在
            directory = os.path.dirname(file_path)
            # 将 output_dict 写入 image-mapping.yaml
            mapping_file_path = os.path.join(directory, 'image-mapping.yaml')
            with open(mapping_file_path, 'w', encoding='utf-8') as file:
                yaml.dump(image_mapping_dict, file, allow_unicode=True, default_flow_style=False, sort_keys=False)
            user_logger.info(f"Image mapping file successfully saved to {mapping_file_path}")
        except Exception as e:
            user_logger.error(f"An error occurred: {e}")
            raise

