import sys

import yaml
from click import ClickException
import traceback
from computenestcli.base_log import get_developer_logger, get_logger
from computenestcli.common.logging_type import LoggingType
from computenestcli.exception.cli_common_exception import CliCommonException

developer_logger = get_developer_logger()
root = get_logger(LoggingType.ROOT.value)


class GlobalExceptionHandler:
    def __init__(self):
        pass

    def exception_handler(self, exctype, value, exp_traceback):
        traceback_info = ''.join(traceback.format_tb(exp_traceback))
        if issubclass(exctype, ZeroDivisionError):
            self.handle_zero_division_error(value, traceback_info)
        elif issubclass(exctype, FileNotFoundError):
            self.handle_file_not_found_error(value, traceback_info)
        elif issubclass(exctype, yaml.YAMLError):
            self.handle_yaml_error(value, traceback_info)
        elif issubclass(exctype, KeyError):
            self.handle_key_error(value, traceback_info)
        elif issubclass(exctype, CliCommonException):
            self.handle_cli_common_exception(value, traceback_info)
        elif issubclass(exctype, ClickException):
            self.handle_click_exception(value, traceback_info)
        else:
            self.handle_generic_error(exctype, value, traceback_info)

    def handle_click_exception(self, value, traceback_info):
        root.error(f"{value}")
        developer_logger.error(f"{value}, traceback={traceback_info}")

    def handle_cli_common_exception(self, value, traceback_info):
        root.error(f"{value}")
        if value.original_exception:
            original_traceback_info = ''.join(traceback.format_exception(type(value.original_exception),
                                                                         value.original_exception,
                                                                         value.original_exception.__traceback__))
            developer_logger.error(f"Original exception traceback:\n{original_traceback_info}")
        developer_logger.error(f"{value}, traceback={traceback_info}", exc_info=1)


    def handle_zero_division_error(self, value, traceback_info):
        root.error(f"Zero Division Error {value}")
        developer_logger.error(f"Zero Division Error: {value}, traceback={traceback_info}", exc_info=1)

    def handle_file_not_found_error(self, value, traceback_info):
        root.error(f"File Not Found Error: {value}")
        developer_logger.info("really!")
        developer_logger.error(f"File Not Found Error: {value}, traceback={traceback_info}", exc_info=1)

    def handle_yaml_error(self, value, traceback_info):
        root.error(f"YAML Parsing Error: {value}")
        developer_logger.error(f"YAML Parsing Error {value}, traceback={traceback_info}", exc_info=1)

    def handle_key_error(self, value, traceback_info):
        root.error(f"Dict Key Error: {value}")
        developer_logger.error(f"Dict Key Error {value}, traceback={traceback_info}", exc_info=1)

    def handle_generic_error(self, exctype, value, traceback_info):
        root.error(f"Inner Exception: {value}")
        developer_logger.error(f"Inner Exception {value}, traceback={traceback_info}", exc_info=1)


# 设置全局异常处理钩子
exception_handler = GlobalExceptionHandler()
sys.excepthook = exception_handler.exception_handler
