TRAIN_SCHEDULED = "已经加入训练序列，前面还有%d个神经网路"
# Translation for import and export project
IMPORT_PROJECT_ERROR_CORTEX_VERSION_NOT_SPECIFIED = (
    "当前Cortex版本未指定！请检查生产目录。"
)
IMPORT_PROJECT_ERROR_MODEL_VERSION_NOT_SPECIFIED = "导c文件中未指定Cortex版本。请确保最新版本的Cortex正在运行，并重新导出项目后再导入。"
IMPORT_PROJECT_ERROR_INVALID_IMPORTED_VERSION = "导入的项目Cortex版本 {} 必须与当前Cortex版本 {} 的主版本和次版本一致，仅允许补丁版本不同。例如，版本 5.3.1 与 5.3.0 兼容，但与 5.2.1 不兼容。请升级 Cortex 以导入此项目。"
IMPORT_PROJECT_ERROR_PICKLING_ERROR = "导入项目错误：请检查导入文件是否已损坏或损坏。"
IMPORT_PROJECT_ERROR_GENERIC_ERROR = "反序列化错误："

UPLOAD_FAILED_OSS_MODEL_PATH_NONE = "OSS 模型路径为空，因为上传失败。"
TRAIN_AUTO_PICKING_BATCH_SIZE = "训练中：自动优化循环参数"
TRAIN_EPOCH_DONE_TIME_REMAIN = "训练中: 已完成循环 %d/%d。剩余 %d 分钟"
TRAIN_EPOCH_DONE_TIME_REMAIN_ONE_MINUTE = "训练中: 已完成循环 %d/%d。剩余 1 分钟"
TRAIN_STARTING = "开始训练..."
TRAIN_CREATE_TRAIN_BACKGROUND_DATASET = (
    "创建用于优化准确性的训练数据集： 已完成%d个特征（共%d个）"
)
TRAIN_CREATE_TRAIN_DATASET = "创建训练数据集： 已完成%d个特征（共%d个）"
TRAIN_CREATE_VALIDATION_DATASET = "创建验证数据集： 已完成%d个特征（共%d个）"
TRAIN_OOM_ERROR_RESTART = "GPU 内存不够，请减小缩放尺寸，再次加入训练。"

REPLICATE_TRAIN_TRAINING_OOM_ERROR = (
    "GPU 内存不足，无法进行复制训练。请减少 GPU 内存使用并验证是否选择了正确的 GPU。"
)
REPLICATE_TRAIN_VALIDATION_OOM_ERROR = (
    "GPU 内存不足，无法进行复制验证。请减少 GPU 内存使用并验证是否选择了正确的 GPU。"
)

AUTO_LABEL_OUT_OF_MEMORY = "显存不足，无法使用自动标注模型，请确保GPU没有被其他进程占用，且图像尺寸不超过24MP。"