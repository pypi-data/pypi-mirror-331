from enum import Enum


class UploadFileType(Enum):
    """
    上传文件类型
    """

    # 构造函数添加访问类型属性
    def __init__(self, value, access_type):
        self._value_ = value
        self.access_type = access_type

    # 服务logo，公共访问
    SERVICE_ICON = ("service_icon", "public")
    # 服务ROS模板，私有访问
    ROS_TEMPLATE = ("ros_template", "private")
    # OOS模板，私有访问
    OOS_TEMPLATE = ("oos_template", "private")
    # 架构图，私有访问
    ARCHITECTURE_DIAGRAM = ("architecture_diagram", "private")
