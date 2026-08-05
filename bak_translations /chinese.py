POST_PROCESS_ERROR = "无法加载后处理代码"
CANNOT_BACKTEST_WHILE_TRAINING = "在训练的时候不能跑模型模拟"
CANNOT_FIND_CLASS_NAME_SHOULD_TRAIN_SCRATCH = (
    "无法找到缺陷种类，可能是由于新添加了缺陷种类。请从零训练。"
)
WIDTH_HEIGHT_DEFINED_ERROR = "长、宽 要么 都定义，要么都不定义"

TRAINING_IN_LOCAL_MODE = "本机"
TRAINING_IN_REMOTE_MODE = "多GPU机"
TRAINING_IN_PROGRESS = "正在训练"
TRAIN_SCHEDULED = "已经加入训练序列，前面还有%d个神经网路"
TRAIN_FROM_SCRATCH = "从头训练"
TRAIN_INCREMENTAL = "进阶训练"
TRAIN_LABEL_SCORING = "标签评分 "
TRAIN_CONSTRUCTING_NETWORK = "训练中：创建神经网络"
TRAIN_SETUP = "训练中：初始化"
TRAIN_TRAINING = "训练中：开始训练"
TRAIN_VALIDATING = "训练中：验证模型"
TRAIN_DONE = "训练完成。"
TRAIN_DONE_TIME_MTIME = "训练完成。总计用时 %d 分钟。上次训练完成时间: %s"
TRAIN_DONE_TIME_MTIME_ONE_MINUTE = "训练完成。总计用时 1 分钟。上次训练完成时间: %s"
TRAIN_FAILED = "训练失败"
TRAIN_FAILURE_NETWORK_NOT_ENOUGH_TRAINING_IMAGES = "训练网络至少需要2张训练图片"
TRAIN_FAILURE_FEATURE_WITHOUT_TRAINING_LABELS = (
    "训练特征至少需要1张包含该特征的训练图片"
)
TRAIN_CANCELLED = "训练已取消"
TRAIN_INCREMENTAL_CLASS_CHANGED_ERROR = (
    "新的标签种类和之前训练模型用的标签种类不一致，需要从头训练"
)
TRAIN_INCREMENTAL_PREPROCESS_CHANGED_ERROR = "预处理配置改变，需要从头训练"
TRAIN_INCREMENTAL_PREPROCESS_CONFIG_LOAD_ERROR = "无法读取预处理配置，需要从头训练"
TRAIN_INCREMENTAL_PREPROCESS_FEATURE_ID_MISMATCH_ERROR = (
    "预处理配置中的特征ID不匹配。必须从头开始训练"
)
TRAIN_ERROR_BASE_MESSAGE = (
    "内部服务器错误： 训练期间发生意外错误。请联系 UnitX 团队并提供日志文件。错误详情 -"
)
TRAIN_UPLOADING_DATA = "上传数据中"
TRAIN_DOWNLOAD_FAILED_DATA = "训练后端下载数据失败"

NETWORK_CONFIG_FOR_MODEL_VERSION_NOT_FOUND = "未找到此ID对应的模型: "
NETWORK_CONFIG_NAME_ALREADY_EXISTS = "同样名字的模型已经存在"
NETWORK_MERGE_IMAGE_SIZE_ERROR = "当前模型的裁剪尺寸大于被合并图片的尺寸，这将会导致训练失败，请调节裁剪尺寸后重新进行标签合并。"

VALIDATION_MISSING = "训练一次模型可以看到验证结果"
VALIDATION_EXPORT_HEADER_ASSET_ID = "ID"
VALIDATION_EXPORT_HEADER_FILE_NAME = "文件名"
VALIDATION_EXPORT_HEADER_LABELS = "标签"
VALIDATION_EXPORT_HEADER_PREDICTIONS = "模型预测"
VALIDATION_ITERATION_DONE_TIME_REMAIN = "正在进行验证：第%d/%d次迭代完成。剩余%d分钟。"
VALIDATION_ITERATION_DONE_TIME_REMAIN_ONE_MINUTE = (
    "正在进行验证：第%d/%d次迭代完成。剩余1分钟。"
)

INFER_IMAGE_DIMENSION_SMALLER_THAN_CROP_END = "在模型 {} 中，照片尺寸 {} 小于预处理的终止裁剪尺寸 {}，请用尺寸一致的照片，并确保照片尺寸大于预处理的终止尺寸。"

INFER_INSUFFICIENT_GPU_MEMORY_ERROR = (
    "GPU内存不足，无法进行模型推理，请等待训练完成或关闭其他占用GPU的程序后重试。"
)

OVERLAY_INFER_INFO_DEFECT = "缺陷"
OVERLAY_INFER_INFO_POINT = "点"
OVERLAY_INFER_INFO_LINE = "线"
OVERLAY_INFER_INFO_CIRCLE = "圆"

PRODUCTION_NETWORK_SIMULATOR_NO_JSON_FOR_PART = "缺少JSON文件。"
PRODUCTION_NETWORK_SIMULATOR_IMAGE_PATH_EMPTY = "缺少照片。"
PRODUCTION_THRESHOLD_SIMULATOR_JSON_ERROR = "无法读取JSON文件。"
PRODUCTION_NETWORK_SIMULATOR_FAIL_MESSAGE = "个物料模拟失败:"
PRODUCTION_ORIGINAL_IMAGE = "原始照片: "
PRODUCTION_REINFERED_IMAGE = "模拟判定: "

REMOTES_UPDATE_FAILED = "制作离线安装包的时候发生了错误。"

TRAIN_MODEL_BACKEND_ERROR = "训练服务报错"

DATABASE_FAILURE = "数据库操作失败"

MODEL_VERSION_NOT_FOUND = "未找到ID为%d的模型版本"
MODEL_VERSION_NOT_SELECTED = "没有选择模型版本"
MODEL_VERSION_NOT_TRAINED = "模型没有训练"
MODEL_VERSION_WITHOUT_BASE_MODEL_VERSION_ID = "在型号版本%d中未发现基本型号版本ID"
MODEL_VERSION_ERROR = "这个模型版本没有训练成功"
MODEL_VERSION_INCREMENTAL_ERROR = (
    "这个模型版本没有训练成功，请用一个不同的模型版本进阶。"
)
NETWORK_CONFIG_NOT_FOUND = "未找到ID为%d的模型"

UPDATE_TASK_STATUS_FAIL = "更新任务状态失败。"
DELETED = "[已删除]"
BACKTEST_MISSING_RAW_IMAGE = "一些照片已经被删除。无法模型模拟。"
BACKTEST_MISSING_IMAGE_PATH = "跑机软件没有存原图"

ANALYTICS_TESTSEND_AUTH_ERROR = "授权失败."
ANALYTICS_TESTSEND_RECEIVER_ERROR = "收件人信息错误."
ANALYTICS_TESTSEND_EMAILFORMAT_ERROR = "收件人邮件地址错误."
ANALYTICS_TESTSEND_NETWORK_ERROR = "网络连接失败."
ANALYTICS_TESTSEND_UNKNOWN_ERROR = "未知错误."

LARGE_IMAGE_CONFIG_PARSING_ERROR = "large_image_config.json有错误"
LARGE_IMAGE_CONFIG_SPLIT_OVERLAP_PERCENT_TOO_LARGE_ERROR = (
    "image_split_overlap_percent必须小于1"
)

DIFF_REPORT_DATA_MISSING_FILE = "缺少文件"
DIFF_REPORT_INVALID_CONFIG = "无法读取配置文件"
DIFF_REPORT_MISSING_VERSION = "缺少版本"


IMPORT_NETWORK_ERROR_CORTEX_VERSION_NOT_SPECIFIED = (
    "未指定 Cortex 版本！请检查生产目录。"
)
IMPORT_NETWORK_ERROR_MODEL_VERSION_NOT_SPECIFIED = (
    "未指定模型版本。请确保最新的 Cortex 正在运行并重新导出模型。"
)
IMPORT_NETWORK_ERROR_INVALID_IMPORTED_VERSION = (
    "模型版本比当前 Cortex 版本更新。请升级 Cortex 以导入此模型。"
)
IMPORT_NETWORK_ERROR_PICKLING_ERROR = "导入错误，请检查文件是否错误或损坏。"
IMPORT_NETWORK_ERROR_GENERIC_ERROR = "反序列化错误："
NETWORK_CONFIG_CLONE_ERROR = "复制模型失败，请重试。注意：空模型无法复制。如果您尝试复制空模型，请创建一个新模型。"
UNKNOWN_NETWORK_ERROR = "未知的模型{network}, 请检查配置文件中的'sequences'参数或者重新训练名为{network}的模型"
EMPTY_NETWORK_ERROR = "Capture '{capture_name}' 没有配置网络名, 请检查配置文件中的'cc_network_mapping'参数"

FEATURE_LIST_TOO_MANY = "功能列表最多只能包含 {maximum_network_cnt} 个功能"

# Translation for threshold tuning charts
THRESHOLD_TUNING_CHARTS_TITLE_FOR_DEFECT = "按{}的缺陷分布"
THRESHOLD_TUNING_CHARTS_TITLE_FOR_PART = "按{}的物料分布"
THRESHOLD_TUNING_CHARTS_Y_LABEL_FOR_DEFECT = "缺陷的数量"
THRESHOLD_TUNING_CHARTS_Y_LABEL_FOR_PART = "物料的数量"
THRESHOLD_TUNING_CHARTS_X_LABEL_FOR_CRITERIA = "判定条件:"
THRESHOLD_TUNING_CHARTS_X_LABEL_FOR_MODIFIER = "聚合维度:"
THRESHOLD_MEASURE_TYPE_AREA = "面积"
THRESHOLD_MEASURE_TYPE_MIN_RECTANGLE_LENGTH = "最小矩形长度"
THRESHOLD_MEASURE_TYPE_MIN_RECTANGLE_WIDTH = "最小矩形宽度"
THRESHOLD_MEASURE_TYPE_HORIZONTAL_WIDTH = "水平宽度"
THRESHOLD_MEASURE_TYPE_VERTICAL_HEIGHT = "竖直高度"
THRESHOLD_MEASURE_CENTER_X_COOR = "缺陷中心点X坐标"
THRESHOLD_MEASURE_CENTER_Y_COOR = "缺陷中心点Y坐标"
THRESHOLD_MEASURE_TYPE_COUNT = "总数量"
THRESHOLD_MEASURE_TYPE_TOTAL_AREA = "总面积"
THRESHOLD_CHARTS_DISCLAIMER_TEXT = "* 如果数据范围较大，接近阈值的条形图颜色可能不精确，仅供参考。请查看图例摘要中的物料决策数据以验证阈值更新。"

IMAGE_USED_BY_GENAI_ERROR = "图片被genai使用，不能删除所有标签。"
LABEL_EVALUATION_PREFIX = "标签评估："
TRAIN_TASK_ID_NOT_FOUND = "未能找到训练运行的任务ID。"


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

# 2.5D OptiX Capture Config Validation Messages
VALIDATE_25D_OPTIX_LESS_CC_ERROR = "序列中至少需要4个捕获配置"
VALIDATE_25D_OPTIX_EXPOSURE_ERROR = "所有捕获配置必须具有相同的曝光时间"
VALIDATE_25D_OPTIX_UNIQUE_PATTERN_ERROR = "每个捕获配置必须具有唯一的通道模式"
VALIDATE_25D_OPTIX_QUADRANT_ERROR = "所有象限必须至少有一个激活通道"
VALIDATE_25D_OPTIX_INVALID_JSON_ERROR = "模式格式无效，必须是有效的JSON数组"
VALIDATE_25D_OPTIX_INVALID_PATTERN_ERROR = "模式必须是环形列表"
VALIDATE_25D_OPTIX_INVALID_RING_ERROR = "每个环必须是通道列表"
VALIDATE_25D_OPTIX_INVALID_VALUE_ERROR = "环{ring_number}只能包含0和1"
VALIDATE_25D_OPTIX_RING_LENGTH_ERROR = (
    "环{ring_number}必须包含{expected_length}个通道，实际包含{actual_length}个"
)
VALIDATE_25D_OPTIX_INVALID_FORMAT_ERROR = (
    "Optix格式无效。环长度为{actual_lengths}。请检查Optix版本配置。"
)
VALIDATE_25D_OPTIX_LARGE_FOV_INNER_CHANNEL_ERROR = "顶部面板灯不允许使用在2.5D中"
VALIDATE_25D_OPTIX_LFOV_NO_TARGET_RINGS_ERROR = (
    "未找到LFOV 2.5D的目标环。至少需要有一个环（环2或环3）完全连接。"
)
VALIDATE_25D_OPTIX_LFOV_QUADRANT_COVERAGE_ERROR = (
    "{ring_name}的象限覆盖不满足要求。2.5D成像需要覆盖所有象限。"
)
VALIDATE_25D_OPTIX_LFOV_NON_TARGET_RINGS_ACTIVE_ERROR = (
    "模式{pattern_index}在{ring_name}中有激活通道，但{ring_name}不是LFOV 2.5D成像的目标环。"
    "只有目标环{target_rings}应该具有激活通道。"
)
VALIDATE_25D_OPTIX_LFOV_INVALID_PATTERN_LENGTH_ERROR = (
    "LFOV 2.5D的模式数组长度无效。期望4或8个模式，但找到{actual_length}个。"
    "LFOV 2.5D成像需要恰好4或8个捕获配置以确保正确的照明序列。"
)
VALIDATE_25D_OPTIX_LFOV_BRIGHTNESS_INCONSISTENT_ERROR = (
    "环{ring_number}的亮度值在捕获配置中不一致。"
    "发现的值：{unique_values}。所有捕获配置必须对环{ring_number}具有相同的亮度。"
)
VALIDATE_25D_OPTIX_LFOV_SINGLE_MODE_MULTIPLE_SECTIONS_ERROR = (
    "环{ring_number}中的模式{pattern_index}同时激活了多个部分。"
    "单模式条形灯设置只允许一次激活一个部分。"
)
VALIDATE_25D_OPTIX_LFOV_DUAL_MODE_NON_ADJACENT_SECTIONS_ERROR = (
    "环{ring_number}中的模式{pattern_index}激活了非相邻的部分。"
    "双模式条形灯设置只允许同时激活两个相邻的部分。"
)
VALIDATE_25D_OPTIX_LFOV_DUAL_MODE_TOO_MANY_SECTIONS_ERROR = (
    "环{ring_number}中的模式{pattern_index}激活了超过两个部分。"
    "双模式条形灯设置只允许同时激活两个相邻的部分。"
)
