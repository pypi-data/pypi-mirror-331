import os
import re
import time
import yaml

from computenestcli.common.logging_constant import BUILD_SERVICE
from computenestcli.common.util import Util, developer_logger

from computenestcli.common import constant
from computenestcli.base_log import get_user_logger

user_logger = get_user_logger(BUILD_SERVICE)

exclude_files = ['schema.yaml', 'template.yaml']

class TerraformUtil:
    def __init__(self):
        pass

    @staticmethod
    def exist_terraform_structure(file_path):
        for root, dirs, files in os.walk(file_path):
            if root.count(os.sep) == file_path.count(os.sep) + 1:
                infrastructure_dir = os.path.join(root, constant.TERRAFORM_STRUCTURE)
                if os.path.isdir(infrastructure_dir):
                    terraform_infrastructure_parent_dir = os.path.dirname(infrastructure_dir)
                    for filename in os.listdir(infrastructure_dir):
                        if filename.endswith(".tf"):
                            return terraform_infrastructure_parent_dir
        return None

    """
    通过rostran cli 将terraform模板转换为ros模板，并进行相应替换
    """

    @staticmethod
    def trans_terraform_to_ros(terraform_path, config_dict, path_key):
        target_path = f"{terraform_path}/template.yaml"
        command = f"rostran transform  {terraform_path} -S terraform --force --compatible --extra-files '*' --target-path {target_path}"

        schema_path = f"{terraform_path}/schema.yaml"
        try:
            output, error = Util.run_cli_command(command, cwd=None)

            last_modify_time = None
            for attempt in range(10):
                if os.path.exists(target_path):
                    # 文件存在，检查修改时间
                    current_modify_time = os.path.getmtime(target_path)
                    if last_modify_time is None or current_modify_time != last_modify_time:
                        last_modify_time = current_modify_time;
                    else:
                        break
                else:
                    time.sleep(2)
            else:
                # 如果 for 循环没有正常通过 break 退出，则抛出 Timeout 异常
                raise Exception(f"转换Terraform模板超时")

            # 去除yaml文件中的infrastructure的前缀
            with open(target_path, 'r') as stream:
                template_data = yaml.safe_load(stream)
            # 读取 parameters YAML 文件
            with open(schema_path, 'r', ) as param_file:
                parameters_data = yaml.safe_load(param_file)

            if 'Workspace' in template_data:
                workspace = template_data['Workspace']
                # 创建一个新的字典用来保存修改后的模板
                updated_workspace = {}

                for key, value in workspace.items():
                    # 根据要求修改键名
                    if key.startswith('infrastructure/') and key.endswith('.tf'):
                        new_key = re.sub(r'^infrastructure/', '', key)
                        updated_workspace[new_key] = value
                    elif key in exclude_files:
                        continue
                    else:
                        updated_workspace[key] = value  # 其他键保持不变

                template_data['Workspace'] = updated_workspace
            # 添加Parameters.yaml
            for key, value in parameters_data.items():
                template_data[key] = value

            with open(target_path, 'w', encoding='utf-8') as file:
                yaml.dump(template_data, file, allow_unicode=True)

            # 设置Ros模板路径
            config_dict[path_key] = target_path

            developer_logger.info(output.decode())
            developer_logger.info(error.decode())
        except Exception as e:
            developer_logger.error(f"Error occurred when trans terraform to ros: {e}")
            raise e
