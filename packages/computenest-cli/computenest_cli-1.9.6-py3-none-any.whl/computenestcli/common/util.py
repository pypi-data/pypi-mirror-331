import re
import select
import time
import yaml
import base64
import datetime
import subprocess
from computenestcli.base_log import get_developer_logger
developer_logger = get_developer_logger()

class Util:
    def __init__(self):
        pass

    @staticmethod
    def regular_expression(data):
        match = re.match(r'\$\{([\w\.]+)\}', data)
        if match:
            parts = match.group(1).split('.')
            return parts
        else:
            return None

    @staticmethod
    def add_timestamp_to_version_name(data=''):
        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%Y%m%d%H%M%S")
        if data:
            new_version_name = str(data) + "_" + time_str
        else:
            new_version_name = time_str
        return new_version_name

    @staticmethod
    def add_timestamp_to_artifact_name(artifact_type, name):
        timestamp = int(time.time() * 1000)
        # 取时间戳的末尾6位
        truncated_timestamp = timestamp % 1000000
        # 拼接并返回结果
        return f"{artifact_type}{truncated_timestamp}_{name}"

    @staticmethod
    def lowercase_first_letter(data):
        if isinstance(data, dict):
            return {k[0].lower() + k[1:]: v for k, v in data.items()}
        elif isinstance(data, str):
            return data[0].lower() + data[1:]
        else:
            return data

    @staticmethod
    def run_cli_command(command, cwd):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        output, error = process.communicate()
        return_code = process.returncode
        if return_code != 0:
            developer_logger.error(output.decode())
            developer_logger.error(error.decode())
            raise ValueError(f"Shell command:{command} exec failed")
        return output, error

    @staticmethod
    def run_command_with_real_time_logging(command, cwd):
        developer_logger.info(f"Executing command: {command}")

        process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            text=True,
            bufsize=1  # 使用行缓冲
        )

        stdout_lines = []
        stderr_lines = []
        line_count = 0
        max_lines = 80  # 每次读取 80 行

        while True:
            reads = [process.stdout, process.stderr]
            ready_to_read, _, _ = select.select(reads, [], [])

            for stream in ready_to_read:
                for line in stream:
                    line = line.strip()
                    if line:
                        if stream is process.stderr:
                            stderr_lines.append(line)
                        elif stream is process.stdout:
                            if 'Error' in line:
                                stderr_lines.append(line)
                                continue
                            stdout_lines.append(line)

                    line_count += 1
                    if line_count >= max_lines:
                        if stdout_lines:
                            combined_stdout = ' | '.join(stdout_lines)
                            developer_logger.info(f"commandStdout: {combined_stdout}")
                            stdout_lines = []

                        if stderr_lines:
                            combined_stderr = ' | '.join(stderr_lines)
                            developer_logger.error(f"commandStderr: {combined_stderr}")
                            stderr_lines = []

                        line_count = 0

            if process.poll() is not None:
                break

        # 打印剩余的行
        if stdout_lines:
            combined_stdout = ' | '.join(stdout_lines)
            developer_logger.info(f"commandStdout: {combined_stdout}")

        if stderr_lines:
            combined_stderr = ' | '.join(stderr_lines)
            developer_logger.error(f"commandStderr: {combined_stderr}")

        process.stdout.close()
        process.stderr.close()

        return_code = process.wait()
        if return_code != 0:
            raise ValueError(f"Command '{command}' failed with return code {return_code}")

    @staticmethod
    def measure_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            return result

        return wrapper

    @staticmethod
    def get_current_time():
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return current_time

    @staticmethod
    def encode_base64(input_string):
        # 将字符串转换为字节
        byte_data = input_string.encode('utf-8')
        # 进行Base64编码
        base64_encoded_data = base64.b64encode(byte_data)
        # 将编码后的字节数据转换回字符串
        return base64_encoded_data.decode('utf-8')

    @staticmethod
    def decode_base64(encoded_data):
        decoded_bytes = base64.b64decode(encoded_data)
        decoded_text = decoded_bytes.decode("utf-8")
        return decoded_text

    @staticmethod
    def write_yaml_to_file(data, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, allow_unicode=True)
