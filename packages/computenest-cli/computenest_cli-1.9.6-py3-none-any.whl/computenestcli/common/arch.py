from enum import Enum


class Arch(Enum):
    """
    架构类型
    """
    ECS_SINGLE = 'EcsSingle'
    ECS_CLUSTER = 'EcsCluster'
    CS_CLUSTER = 'CsCluster'
