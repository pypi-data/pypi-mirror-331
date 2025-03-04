# -*- coding: utf-8 -*-
import oss2
import requests
import hashlib
import os

from computenestcli.base_log import get_developer_logger
from computenestcli.common import constant
from computenestcli.service.base import Service
from urllib.parse import unquote

FILE = 'file'

developer_logger = get_developer_logger()


class FileService(Service):

    @classmethod
    def put_file(cls, credentials, file_path, type):
        file_name = os.path.basename(file_path)
        if type == FILE:
            sts_access_key_id = credentials.body.data.access_key_id
            sts_access_key_secret = credentials.body.data.access_key_secret
            security_token = credentials.body.data.security_token
            bucket_name = credentials.body.data.bucket_name
            object_name = credentials.body.data.key
            region_id = credentials.body.data.region_id
        else:
            sts_access_key_id = credentials.body.credentials.access_key_id
            sts_access_key_secret = credentials.body.credentials.access_key_secret
            security_token = credentials.body.credentials.security_token
            bucket_name = credentials.body.available_resources[0].repository_name
            object_name = '{}/{}'.format(credentials.body.available_resources[0].path, file_name)
            region_id = credentials.body.available_resources[0].region_id
        try:
            endpoint = f'oss-{region_id}.aliyuncs.com'
            auth = oss2.StsAuth(sts_access_key_id, sts_access_key_secret, security_token)
            bucket = oss2.Bucket(auth, endpoint, bucket_name)
            with open(file_path, 'rb') as fileobj:
                bucket.put_object(object_name, fileobj)
        except oss2.exceptions.OssError as e:
            developer_logger.error(f"Failed to upload file: {e}")

        url = "https://{}.{}/{}".format(bucket_name, endpoint, object_name)
        return url

    @classmethod
    def get_object_to_file(cls, credentials, oss_path, output_path, type):
        path_split = oss_path.split('/')
        bucket_name = path_split[2:3]
        object_name = path_split[-1]
        if object_name.contains('?'):
            object_name = object_name.split('?')[0]
        if type == FILE:
            sts_access_key_id = credentials.body.data.access_key_id
            sts_access_key_secret = credentials.body.data.access_key_secret
            security_token = credentials.body.data.security_token
            region_id = credentials.body.data.region_id
        else:
            sts_access_key_id = credentials.body.credentials.access_key_id
            sts_access_key_secret = credentials.body.credentials.access_key_secret
            security_token = credentials.body.credentials.security_token
            region_id = credentials.body.available_resources[0].region_id
        endpoint = f'oss-{region_id}.aliyuncs.com'
        auth = oss2.StsAuth(sts_access_key_id, sts_access_key_secret, security_token)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        bucket.get_object_to_file(object_name, output_path)

    @classmethod
    def download_file(cls, url, local_filename=None, output_base_dir=None):
        """
        使用requests库下载文件到指定目录
        :param url: 文件的URL地址
        :param local_filename: 本地保存的文件名，默认为URL的最后一部分
        :param output_base_dir: 指定的下载目录，默认为当前工作目录
        :return: 本地文件的完整路径
        """
        if local_filename is None:
            # 从URL中提取文件名并进行解码，确保文件名正确无误
            local_filename = unquote(url.split('/')[-1])
            if '?' in local_filename:
                local_filename = local_filename.split('?')[0]

        # 确保下载目录存在，如果未指定则使用当前工作目录
        if not output_base_dir:
            output_base_dir = os.getcwd()
        os.makedirs(output_base_dir, exist_ok=True)
        file_path = os.path.join(output_base_dir, local_filename)

        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # 如果响应状态码不是200，将抛出异常
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # 使用分块传输，适用于大文件下载
                    f.write(chunk)
        return local_filename

    @classmethod
    def check_file_repeat(cls, url, local_file_path):
        # 获取远程文件内容
        response = requests.get(url)

        # 处理URL，去掉可能存在的参数部分
        base_url = url.split('?')[0] if '?' in url else url

        # 获取文件名和保存路径
        file_name = os.path.basename(base_url)  # 获取基础文件名
        temp_file_path = os.path.join(constant.TEMP_PATH, file_name)

        # 确保临时目录存在
        os.makedirs(constant.TEMP_PATH, exist_ok=True)

        # 将远程文件保存到临时路径
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(response.content)

        # 定义一个函数用于计算文件的 MD5 哈希值
        def calculate_md5(file_path):
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        # 计算临时文件和本地文件的 MD5
        remote_file_md5 = calculate_md5(temp_file_path)
        local_file_md5 = calculate_md5(local_file_path)

        # 删除临时文件并返回MD5比较结果
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return remote_file_md5 == local_file_md5
