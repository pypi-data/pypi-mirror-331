import re


class StrUtil:
    def __init__(self):
        pass

    # 将输入参数改为计算巢部署物允许的格式
    @staticmethod
    def sanitize_name(name):
        # 只允许字母、数字、下划线、和中划线
        pattern = r'[^\w-]+'
        # 替换不符合的字符为下划线
        sanitized_name = re.sub(pattern, '_', name)
        return sanitized_name

    # 将字符串首字符lower
    @staticmethod
    def lower_first_char(name):
        if not name:
            return name
        return name[0].lower() + name[1:]

    @staticmethod
    def capitalize_keys(data):
        """
        递归地对字典的所有键进行首字符大写。

        :param data: 输入的数据结构，可以是列表、字典、字符串等
        :return: 更新后的数据结构
        """
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                # 将键的首字符大写
                new_key = key[0].upper() + key[1:] if isinstance(key, str) else key
                # 递归处理值
                new_dict[new_key] = StrUtil.capitalize_keys(value)
            return new_dict
        elif isinstance(data, list):
            return [StrUtil.capitalize_keys(element) for element in data]
        else:
            return data

    @staticmethod
    def format_image_url(image_url):
        image_split = image_url.split("/")
        image_split_len = len(image_split)
        if image_split_len >= 2:
            # image为<registry>/<namespace>/<image_name>:<tag>类型 或 <namespace>/<image_name>:<tag>类型
            namespace = image_split[-2]
            last_name = image_split[-1]
            last_name_split = last_name.split(":")
            # image_name保留namespace，便于做区分
            image_name = "{}/{}".format(namespace, last_name_split[0])
            image_tag = last_name_split[1] if len(last_name_split) == 2 else 'latest'
        else:
            # image为<image_name>:<tag>类型
            last_name_split = image_split[0].split(":")
            image_name = last_name_split[0]
            image_tag = last_name_split[1] if len(last_name_split) == 2 else 'latest'

        split_image_url = f"{image_name}:{image_tag}"
        return split_image_url
