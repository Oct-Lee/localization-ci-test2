import logging


logger = logging.getLogger(__name__)


CAMERA_NOT_FOUND_ERROR = (
    "camera[{camera_id}] not Founded. "
    "Please check whether the "
    "'camera_id' parameter of the configration file is correct"
)


ERROR_MESSAGE = (
    "camera is not Founded"
)


WARNING_MESSAGE = (
    "The camera have disconnected"
)


MESSAGE = (
    "摄像头没有找到，请检查配置文件"
)


CHINESE_ERROR = (
    "无法打开摄像头设备，请检查摄像头是不是正常"
)


PORTUGUESE_MESSAGE = (
    "A camera nao foi encontrada"
)


PORTUGUESE_ERROR = (
    "A camera esta desconectada"
)


logger.error(
    "prod_ui qapp quited"
)


logger.info(
    "Stavrt NVIDIA CUDA pipeline"
)
