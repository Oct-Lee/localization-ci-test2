import logging


logger = logging.getLogger(__name__)


CAMERA_NOT_FOUND_ERROR = (
    "camera[{camera_id}] not Founded. "
    "Please check whether the "
    "'camera_id' parameter ofthe configrations file is correct"
)


ERROR_MESSAGE = (
    "camera not Founded"
)


WARNING_MESSAGE = (
    "The camera have disconnected"
)


MESSAGE = (
    "摄像头没有找到，请检查配置文件"
)


CHINESE_ERROR = (
    "打开无法摄像头设备，请检查摄像头是不是正常"
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
    "Start NVIDIA CUDA pipeline"
)
POST_PROCESS_ERROR = "post processing has failed - please check script"
CANNOT_BACKTEST_WHILE_TRAINING = (
    "Network Simulation cannot run while training is in progress."
)
CANNOT_FIND_CLASS_NAME_SHOULD_TRAIN_SCRATCH = (
    "cannot find class name. likely added new defect class. "
    "should train from scratch."
)
WIDTH_HEIGHT_DEFINED_ERROR = "width and height must be both defined, or both undefined"

TRAINING_IN_LOCAL_MODE = "Local"
TRAINING_IN_REMOTE_MODE = "Multi-GPU"
TRAINING_IN_PROGRESS = "Training in progress"
TRAIN_SCHEDULED = "added to training queue: %d network(s) scheduled before this network"
TRAIN_FROM_SCRATCH = "Train From Scratch"
TRAIN_INCREMENTAL = "Incremental Train"
TRAIN_LABEL_SCORING = "Label Scoring"
TRAIN_CONSTRUCTING_NETWORK = "training in progress: constructing network"
TRAIN_SETUP = "training in progress: setting up"
TRAIN_TRAINING = "training in progress: started training"
TRAIN_VALIDATING = "training in progress: validating model"
TRAIN_DONE = "Training done."
TRAIN_DONE_TIME_MTIME = "Training done. %d minutes total. last trained time: %s"
TRAIN_DONE_TIME_MTIME_ONE_MINUTE = (
    "Training done. 1 minute total. last trained time: %s"
)
TRAIN_FAILED = "trained failed"
TRAIN_FAILURE_NETWORK_NOT_ENOUGH_TRAINING_IMAGES = (
    "Network requires at least 2 training images for training."
)
TRAIN_FAILURE_FEATURE_WITHOUT_TRAINING_LABELS = (
    "Feature requires at least 1 training image with feature present for training."
)
TRAIN_CANCELLED = "Model was cancelled during training"
TRAIN_INCREMENTAL_CLASS_CHANGED_ERROR = (
    "The new labels have different types from the existing model. "
    "Must train from scratch."
)
TRAIN_INCREMENTAL_PREPROCESS_CHANGED_ERROR = (
    "Preprocess config has changed. Must train from scratch."
)
TRAIN_INCREMENTAL_PREPROCESS_CONFIG_LOAD_ERROR = (
    "Cannot load Preprocess config. Must train from scratch."
)
TRAIN_INCREMENTAL_PREPROCESS_FEATURE_ID_MISMATCH_ERROR = (
    "Feature ID mismatch in preprocess config. Must train from scratch."
)
TRAIN_ERROR_BASE_MESSAGE = (
    "Internal Server Error: Unexpected error happened during training. "
    "Please contact UnitX team with the log file. Error Details -"
)
TRAIN_UPLOADING_DATA = "uploading data"
TRAIN_DOWNLOAD_FAILED_DATA = "Download model failed from training server"
TRAIN_DOWNLOAD_IMAGE_FAILED_DATA = "Failed to download image from OSS"
TRAIN_FAILED_MOVE_IMAGE = "Failed to move image"


NETWORK_CONFIG_FOR_MODEL_VERSION_NOT_FOUND = (
    "Network config not found for model version id: "
)
NETWORK_CONFIG_NAME_ALREADY_EXISTS = "Network with the same name already exists"
NETWORK_MERGE_IMAGE_SIZE_ERROR = "The current network's crop size is larger than the merged image size, which will result in training failure. Please adjust the crop size and remerge the labels."

VALIDATION_MISSING = "Please run training to get validation results."
VALIDATION_EXPORT_HEADER_ASSET_ID = "Asset Id"
VALIDATION_EXPORT_HEADER_FILE_NAME = "File Name"
VALIDATION_EXPORT_HEADER_LABELS = "Labels"
VALIDATION_EXPORT_HEADER_PREDICTIONS = "Predictions"
VALIDATION_ITERATION_DONE_TIME_REMAIN = (
    "validation in progress: iteration %d/%d done. %d minutes remaining"
)
VALIDATION_ITERATION_DONE_TIME_REMAIN_ONE_MINUTE = (
    "validation in progress: iteration %d/%d done. 1 minute remaining"
)

INFER_IMAGE_DIMENSION_SMALLER_THAN_CROP_END = (
    "For the network {}, the image dimension {} is smaller than the pre-process crop end {}. "
    "Please make sure all images are of the same size and match the pre-process specifications."
)

INFER_INSUFFICIENT_GPU_MEMORY_ERROR = "Not enough GPU memory to run inference. Please wait for training to finish or shut down other programs using GPU and try again."

OVERLAY_INFER_INFO_DEFECT = "Defect"
OVERLAY_INFER_INFO_POINT = "Points"
OVERLAY_INFER_INFO_LINE = "Lines"
OVERLAY_INFER_INFO_CIRCLE = "Circles"

PRODUCTION_NETWORK_SIMULATOR_NO_JSON_FOR_PART = "Missing JSON file."
PRODUCTION_NETWORK_SIMULATOR_IMAGE_PATH_EMPTY = "Cannot find image."
PRODUCTION_THRESHOLD_SIMULATOR_JSON_ERROR = "Cannot load JSON file."
PRODUCTION_NETWORK_SIMULATOR_FAIL_MESSAGE = "part(s) failed because of"
PRODUCTION_ORIGINAL_IMAGE = "Capture time: "
PRODUCTION_REINFERED_IMAGE = "Inference time: "

REMOTES_UPDATE_FAILED = "Something went wrong when packaging the installer."

TRAIN_MODEL_BACKEND_ERROR = "Training service reported an error"
DATABASE_FAILURE = "Database operation failure"

MODEL_VERSION_NOT_FOUND = "Model version with id %d not found"
MODEL_VERSION_NOT_SELECTED = "No model version selected"
MODEL_VERSION_NOT_TRAINED = "Train the model to see the inference result"
MODEL_VERSION_WITHOUT_BASE_MODEL_VERSION_ID = (
    "Base model version id not found in model version %d"
)
MODEL_VERSION_ERROR = "Broken model version selected"
MODEL_VERSION_INCREMENTAL_ERROR = (
    "The base model version is broken."
    "Please use a different model version for incremental train."
)
NETWORK_CONFIG_NOT_FOUND = "Network with id %d not found"

UPDATE_TASK_STATUS_FAIL = "Update Task Status Failed."
DELETED = "[DELETED]"
BACKTEST_MISSING_RAW_IMAGE = "Some images have been deleted. Cannot run simulation."
BACKTEST_MISSING_IMAGE_PATH = "Image was not saved during production."

ANALYTICS_TESTSEND_AUTH_ERROR = "Bad Authentication."
ANALYTICS_TESTSEND_RECEIVER_ERROR = "Invalid Receiver Format."
ANALYTICS_TESTSEND_EMAILFORMAT_ERROR = "Invalid Email Address Format."
ANALYTICS_TESTSEND_NETWORK_ERROR = "Network Connectivity Issue."
ANALYTICS_TESTSEND_UNKNOWN_ERROR = "Unexpected Issue."

LARGE_IMAGE_CONFIG_PARSING_ERROR = "Cannot parse large_image_config.json"
LARGE_IMAGE_CONFIG_SPLIT_OVERLAP_PERCENT_TOO_LARGE_ERROR = (
    "image_split_overlap_percent must be less than 1"
)

DIFF_REPORT_MISSING_FILE = "does not exist at"
DIFF_REPORT_INVALID_CONFIG = "Invalid Config due to"
DIFF_REPORT_MISSING_VERSION = "Version file not found"

IMPORT_NETWORK_ERROR_CORTEX_VERSION_NOT_SPECIFIED = (
    "Cortex version is not specified! Please check ProdX directory."
)
IMPORT_NETWORK_ERROR_MODEL_VERSION_NOT_SPECIFIED = "The model version is not specified. Please make sure the latest Cortex is running and export the model again."
IMPORT_NETWORK_ERROR_INVALID_IMPORTED_VERSION = "The model version is newer than the current version of Cortex. Please upgrade Cortex to import this model."
IMPORT_NETWORK_ERROR_PICKLING_ERROR = (
    "Error importing, please check if the file is wrong or damaged."
)
IMPORT_NETWORK_ERROR_GENERIC_ERROR = "Error deserializing: "
NETWORK_CONFIG_CLONE_ERROR = "Failed to clone the network. Please try again. Note: Empty networks cannot be cloned. Create a new network if you are attempting to clone an empty one."
UNKNOWN_NETWORK_ERROR = "Unknown network {network}, Please Check 'sequences' parameters in the configuration file or retain the model named {network}"
EMPTY_NETWORK_ERROR = "Capture '{capture_name}' dose not configure network, Please check the 'cc_network_mapping' params in the configure file"

FEATURE_LIST_TOO_MANY = (
    "Feature list must contain at most {maximum_network_cnt} features"
)

# Translation for threshold tuning charts
THRESHOLD_TUNING_CHARTS_TITLE_FOR_DEFECT = "Defect Distribution by {}"
THRESHOLD_TUNING_CHARTS_TITLE_FOR_PART = "Part Distribution by {}"
THRESHOLD_TUNING_CHARTS_Y_LABEL_FOR_DEFECT = "Number of Defects"
THRESHOLD_TUNING_CHARTS_Y_LABEL_FOR_PART = "Number of Parts"
THRESHOLD_TUNING_CHARTS_X_LABEL_FOR_CRITERIA = "Criteria:"
THRESHOLD_TUNING_CHARTS_X_LABEL_FOR_MODIFIER = "Modifier:"
THRESHOLD_MEASURE_TYPE_AREA = "Area"
THRESHOLD_MEASURE_TYPE_MIN_RECTANGLE_LENGTH = "MR Length"
THRESHOLD_MEASURE_TYPE_MIN_RECTANGLE_WIDTH = "MR Width"
THRESHOLD_MEASURE_TYPE_HORIZONTAL_WIDTH = "Horizontal Width"
THRESHOLD_MEASURE_TYPE_VERTICAL_HEIGHT = "Vertical Height"
THRESHOLD_MEASURE_CENTER_X_COOR = "Defect Ctr. Point X Coor."
THRESHOLD_MEASURE_CENTER_Y_COOR = "Defect Ctr. Point Y Coor."
THRESHOLD_MEASURE_TYPE_COUNT = "Count"
THRESHOLD_MEASURE_TYPE_TOTAL_AREA = "Total Area"
THRESHOLD_CHARTS_DISCLAIMER_TEXT = "* Large data ranges may cause bar colors near thresholds to be imprecise and is for reference only.\n Please check the legend summary to verify threshold updates."

IMAGE_USED_BY_GENAI_ERROR = "Images are used by genai and cannot remove all labels."
TRAIN_TASK_ID_NOT_FOUND = "Could not find task id for training run."
LABEL_EVALUATION_PREFIX = "Label Evaluation:"

# Translation for import and export project
IMPORT_PROJECT_ERROR_CORTEX_VERSION_NOT_SPECIFIED = (
    "The current Cortex version is not specified! Please check the ProdX directory."
)
IMPORT_PROJECT_ERROR_MODEL_VERSION_NOT_SPECIFIED = "The Cortex version is not specified in the import file. Please ensure the latest Cortex is running and export the project again to import."
IMPORT_PROJECT_ERROR_INVALID_IMPORTED_VERSION = "The imported project's Cortex version {} must match the current version of Cortex {} at the major and minor levels, allowing differences only in the patch level. For example, version 5.3.1 is compatible with 5.3.0 but not with 5.2.1. Please upgrade Cortex to import this project."
IMPORT_PROJECT_ERROR_PICKLING_ERROR = (
    "Error importing: please check if the file is corrupted or damaged."
)

UPLOAD_FAILED_OSS_MODEL_PATH_NONE = "The oss model path is None because upload failed."
TRAIN_AUTO_PICKING_BATCH_SIZE = "training in progress: auto picking batch size"
TRAIN_EPOCH_DONE_TIME_REMAIN = (
    "training in progress: iteration %d/%d done. %d minutes remaining"
)
TRAIN_EPOCH_DONE_TIME_REMAIN_ONE_MINUTE = (
    "training in progress: iteration %d/%d done. 1 minute remaining"
)
TRAIN_STARTING = "Starting training..."
TRAIN_CREATE_TRAIN_BACKGROUND_DATASET = (
    "Creating training dataset for accuracy optimization. %d out of %d features done."
)
TRAIN_CREATE_TRAIN_DATASET = "Creating training dataset: %d out of %d features done."
TRAIN_CREATE_VALIDATION_DATASET = (
    "Creating validation dataset: %d out of %d features done."
)
TRAIN_OOM_ERROR_RESTART = "GPU out of memory. Please reduce the training resize ratio and reschedule the training."
REPLICATE_TRAIN_TRAINING_OOM_ERROR = "GPU ran out of memory when attempting to replicate training. Please reduce GPU memory usage and verify correct GPU is selected."
REPLICATE_TRAIN_VALIDATION_OOM_ERROR = "GPU ran out of memory when attempting to replicate validation. Please reduce GPU memory usage and verify correct GPU is selected."

AUTO_LABEL_OUT_OF_MEMORY = "Auto Labeler ran out of memory. Please ensure GPU is not occupied by other processes, and images are no greater than 24MP."

# 2.5D OptiX Capture Config Validation Messages
VALIDATE_25D_OPTIX_LESS_CC_ERROR = "At least 4 CCs are required in the sequence"
VALIDATE_25D_OPTIX_EXPOSURE_ERROR = "All CCs must have the same exposure time"
VALIDATE_25D_OPTIX_UNIQUE_PATTERN_ERROR = "Each CC must have a unique channel pattern"
VALIDATE_25D_OPTIX_QUADRANT_ERROR = (
    "All quadrants must have at least one active channel"
)
VALIDATE_25D_OPTIX_INVALID_JSON_ERROR = (
    "Invalid pattern format, must be a valid JSON array"
)
VALIDATE_25D_OPTIX_INVALID_PATTERN_ERROR = "Pattern must be a list of rings"
VALIDATE_25D_OPTIX_INVALID_RING_ERROR = "Each ring must be a list of channels"
VALIDATE_25D_OPTIX_INVALID_VALUE_ERROR = (
    "Ring {ring_number} must contain only 0s and 1s"
)
VALIDATE_25D_OPTIX_RING_LENGTH_ERROR = "Ring {ring_number} must contain exactly {expected_length} channels, got {actual_length}"
VALIDATE_25D_OPTIX_INVALID_FORMAT_ERROR = "Invalid Optix format. Ring lengths are {actual_lengths}. Please check the Optix version configuration."
VALIDATE_25D_OPTIX_LARGE_FOV_INNER_CHANNEL_ERROR = (
    "Top panel cannot be turned on for Large FOV 2.5D"
)
VALIDATE_25D_OPTIX_LFOV_NO_TARGET_RINGS_ERROR = "No target rings found for LFOV 2.5D. At least one ring (ring 2 or ring 3) must be fully connected."
VALIDATE_25D_OPTIX_LFOV_QUADRANT_COVERAGE_ERROR = "Quadrant coverage not met for {ring_name}. All quadrants must be covered for 2.5D imaging."
VALIDATE_25D_OPTIX_LFOV_NON_TARGET_RINGS_ACTIVE_ERROR = (
    "Pattern {pattern_index} has active channels in {ring_name}, which is not a target ring for LFOV 2.5D imaging. "
    "Only target rings {target_rings} should have active channels."
)
VALIDATE_25D_OPTIX_LFOV_INVALID_PATTERN_LENGTH_ERROR = (
    "Invalid pattern array length for LFOV 2.5D. Expected 4 or 8 patterns, but found {actual_length}. "
    "LFOV 2.5D imaging requires exactly 4 or 8 capture configs for proper illumination sequence."
)

VALIDATE_25D_OPTIX_LFOV_BRIGHTNESS_INCONSISTENT_ERROR = (
    "Brightness values for Ring {ring_number} are inconsistent across capture configs. "
    "Found values: {unique_values}. All capture configs must have the same brightness for Ring {ring_number}."
)
VALIDATE_25D_OPTIX_LFOV_SINGLE_MODE_MULTIPLE_SECTIONS_ERROR = (
    "Pattern {pattern_index} in Ring {ring_number} has multiple sections active simultaneously. "
    "Single mode bar light setup allows only one section to be turned on at a time."
)
VALIDATE_25D_OPTIX_LFOV_DUAL_MODE_NON_ADJACENT_SECTIONS_ERROR = (
    "Pattern {pattern_index} in Ring {ring_number} has non-adjacent sections active. "
    "Dual mode bar light setup allows only adjacent two sections to be turned on simultaneously."
)
VALIDATE_25D_OPTIX_LFOV_DUAL_MODE_TOO_MANY_SECTIONS_ERROR = (
    "Pattern {pattern_index} in Ring {ring_number} has more than two sections active. "
    "Dual mode bar light setup allows only two adjacent sections to be turned on simultaneously."
)
# 2.5D OptiX Capture Config Validation Messages
VALIDATE_25D_OPTIX_LESS_CC_ERROR = "At least 4 CCs are required in the sequence"
VALIDATE_25D_OPTIX_EXPOSURE_ERROR = "All CCs must have the same exposure time"
VALIDATE_25D_OPTIX_UNIQUE_PATTERN_ERROR = "Each CC must have a unique channel pattern"
VALIDATE_25D_OPTIX_QUADRANT_ERROR = (
    "All quadrants must have at least one active channel"
)
VALIDATE_25D_OPTIX_INVALID_JSON_ERROR = (
    "Invalid pattern format, must be a valid JSON array"
)
VALIDATE_25D_OPTIX_INVALID_PATTERN_ERROR = "Pattern must be a list of rings"
VALIDATE_25D_OPTIX_INVALID_RING_ERROR = "Each ring must be a list of channels"
VALIDATE_25D_OPTIX_INVALID_VALUE_ERROR = (
    "Ring {ring_number} must contain only 0s and 1s"
)
VALIDATE_25D_OPTIX_RING_LENGTH_ERROR = "Ring {ring_number} must contain exactly {expected_length} channels, got {actual_length}"
VALIDATE_25D_OPTIX_INVALID_FORMAT_ERROR = "Invalid Optix format. Ring lengths are {actual_lengths}. Please check the Optix version configuration."
VALIDATE_25D_OPTIX_LARGE_FOV_INNER_CHANNEL_ERROR = (
    "Top panel cannot be turned on for Large FOV 2.5D"
)
VALIDATE_25D_OPTIX_LFOV_NO_TARGET_RINGS_ERROR = "No target rings found for LFOV 2.5D. At least one ring (ring 2 or ring 3) must be fully connected."
VALIDATE_25D_OPTIX_LFOV_QUADRANT_COVERAGE_ERROR = "Quadrant coverage not met for {ring_name}. All quadrants must be covered for 2.5D imaging."
VALIDATE_25D_OPTIX_LFOV_NON_TARGET_RINGS_ACTIVE_ERROR = (
    "Pattern {pattern_index} has active channels in {ring_name}, which is not a target ring for LFOV 2.5D imaging. "
    "Only target rings {target_rings} should have active channels."
)
VALIDATE_25D_OPTIX_LFOV_INVALID_PATTERN_LENGTH_ERROR = (
    "Invalid pattern array length for LFOV 2.5D. Expected 4 or 8 patterns, but found {actual_length}. "
    "LFOV 2.5D imaging requires exactly 4 or 8 capture configs for proper illumination sequence."
)

VALIDATE_25D_OPTIX_LFOV_BRIGHTNESS_INCONSISTENT_ERROR = (
    "Brightness values for Ring {ring_number} are inconsistent across capture configs. "
    "Found values: {unique_values}. All capture configs must have the same brightness for Ring {ring_number}."
)
VALIDATE_25D_OPTIX_LFOV_SINGLE_MODE_MULTIPLE_SECTIONS_ERROR = (
    "Pattern {pattern_index} in Ring {ring_number} has multiple sections active simultaneously. "
    "Single mode bar light setup allows only one section to be turned on at a time."
)
VALIDATE_25D_OPTIX_LFOV_DUAL_MODE_NON_ADJACENT_SECTIONS_ERROR = (
    "Pattern {pattern_index} in Ring {ring_number} has non-adjacent sections active. "
    "Dual mode bar light setup allows only adjacent two sections to be turned on simultaneously."
)
VALIDATE_25D_OPTIX_LFOV_DUAL_MODE_TOO_MANY_SECTIONS_ERROR = (
    "Pattern {pattern_index} in Ring {ring_number} has more than two sections active. "
    "Dual mode bar light setup allows only two adjacent sections to be turned on simultaneously."
)
DOCKER_CONTAINER_NOT_RUNNING = "Software dependency container error. Try restarting the software or IPC to recovery"

DOCKER_SERVICE_NOT_AVAILABLE = "Docker service is unavailable. Try restarting IPC"

DOCKER_STACK_OK = "Docker OK, Postgres container running"

DOCKER_POSTGRES_RECOVERED = "Postgres back up after docker restart"

CONFIG_FILE_PARSE_ERROR = "global.toml file corrupted"

CONFIG_DUPLICATE_KEYS = "global.toml file corrupted"

GLOBAL_TOML_OK = "global.toml present and valid: {path}"

SYMLINK_UNITX_DATA_INVALID = "unitx_data folder corrupted. Contact UnitX support"

GPU_DRIVER_NOT_AVAILABLE = "GPU driver unavailable. Refer to manual to install driver"

GPU_PCIE_DEVICE_NOT_FOUND = "GPU PCIe device not detected. Check GPU installation/power"


POSTGRES_CONNECTION_REFUSED = (
    "Postgres connection refused. Check container status or 5432 port occupancy"
)

POSTGRES_CONNECT_OTHER = "Database port 5432 is error. Check port status and retry"

POSTGRES_RESTART_FAILED = "Postgres container restart failed during preflight"

DATA_DISK_NOT_MOUNTED = "Data disk not mounted. Check disk mount status."

DATA_MOUNT_OK = "Data mount check OK: {detail}"

MISSING_AUTOSTART_FILE = (
    "Data disk mounted but autostart file missing. Check auto-mount configuration."
)

# env_disk_space (GB threshold from warn_percent)
DISK_READ_ERROR = "Cannot read disk usage: {err}"
DISK_LOW_FREE_SPACE = "Partition {mount} has {free_gb:.1f} GB remaining."
DISK_SPACE_SUFFICIENT = "About {free_gb:.1f} GB free on {mount}."

# monitor stack / env_grafana (gather_monitor_stack_issues; prod log uses get_english_strings)
MONITOR_DOCKER_LIST_OSE = "[docker] cannot list containers: {err}"
MONITOR_DOCKER_PS_FAIL = "[docker] docker ps failed rc={rc} {err}"
MONITOR_CONTAINER_NOT_RUNNING = "[container] not running: {name}"
MONITOR_PROM_UP_FAIL = "[Prometheus] up query failed: {err} (url={url})"
MONITOR_PROM_UP_EMPTY = "[Prometheus] query=up has no data points: {reason}"
MONITOR_PROM_JOBS_DOWN = "[Prometheus] job targets DOWN: {jobs}"
MONITOR_PROM_SCRAPE_FAIL = "[Prometheus] scrape_samples_scraped request failed: {err}"
MONITOR_PROM_SCRAPE_ZERO = "[Prometheus] total scraped samples is 0: {reason}"
MONITOR_PROM_TS_FAIL = "[Prometheus] timestamp/freshness check failed: {err}"
MONITOR_PROM_STALE = (
    "[Prometheus] {n} up series have stale timestamp (>5min), data may be old"
)
MONITOR_7414_NOT_RUNNING = "not running: {names}"

GRAFANA_NO_DATA = "Grafana monitoring system has no data. Contact technical support."

POSTGRES_CONTAINER_RESTARTING = "The Postgres container is restarting"

BACKUP_NOT_ENABLED = "Backup disabled. Enable backup if needed."
BACKUP_CONFIG_READ_ERROR = "Cannot read backup config file: {err}"

BACKUP_STALE_WARNING = "No backup for {days:.1f} days. Check backup status."
BACKUP_FRESHNESS_OK = (
    "Backup freshness OK: most recent successful backup {age_days:.1f} days ago"
)
BACKUP_CANNOT_DETERMINE = "Cannot determine backup freshness: {reason}"
BACKUP_NO_DEST_PATH = "destination_path not configured, skipping backup freshness check"
BACKUP_COLLECTION_FAILED = "Backup chain status query failed: {error}"
BACKUP_NO_TIMESTAMP = "Cannot parse backup timestamp from duplicity output"
BACKUP_LAST_FULL = "Full backup time: {time}"
BACKUP_LAST_INCREMENTAL = "Most recent incremental backup time: {time}"

# --- boot_popup_gui (GTK) ---
BOOT_POPUP_WINDOW_TITLE = "System Startup Check Failed"

BOOT_POPUP_HEADLINE = (
    "Errors detected during system check. Some functions may not work properly. Resolve immediately, "
    "or Prod will fail to start."
)

BOOT_POPUP_SECTION_ERROR = "Error"
BOOT_POPUP_SECTION_WARNING = "Warning"
BOOT_POPUP_EMPTY = "None"
BOOT_POPUP_BTN_OK = "OK"

BOOT_POPUP_AGENT_NO_RESPONSE = (
    "boot_check_agent not responding. Contact technical support."
)
BOOT_POPUP_AGENT_TIMEOUT = "Agent timeout (curl or subprocess)"
BOOT_POPUP_CONFIG_JSON_INVALID = (
    "boot_check_config.json invalid or unreadable. Contact technical support."
)
BOOT_POPUP_PARSE_FAILED = "Failed to parse agent JSON"
BOOT_POPUP_FETCH_BUDGET = (
    "Fetching boot-check results timed out ({n}s). The agent may still be busy"
)
# General Errors
ERROR_INVALID_REQUEST = "Invalid request"
ERROR_INTERNAL_SERVER = "Internal server error"
ERROR_NOT_FOUND = "Resource not found"
ERROR_UNAUTHORIZED = "Unauthorized access"
ERROR_FORBIDDEN = "Forbidden access"

ERROR_DATABASE_CONNECTION = "Database connection failed"
ERROR_DATABASE_QUERY = "Database query failed"

SUCCESS_OPERATION = "Operation successful"

# Recording Errors
ERROR_RECORDING_START_TIME_REQUIRED = "startTime is required"
ERROR_RECORDING_ALREADY_IN_PROGRESS = "Recording is already in progress"
ERROR_RECORDING_START_FAILED = "Failed to start recording: {}"
ERROR_RECORDING_END_TIME_REQUIRED = "endTime is required"
ERROR_RECORDING_NO_RECORDING_IN_PROGRESS = "No recording in progress"
ERROR_RECORDING_START_TIME_NOT_FOUND = "Recording start time not found"
ERROR_RECORDING_END_TIME_INVALID = "endTime must be later than startTime"
ERROR_RECORDING_STOP_FAILED = "Failed to stop recording: {}"

# Work Order Errors
ERROR_WORKORDER_LOG_CONFIG_INVALID = "logConfig must be an object"
ERROR_WORKORDER_MISSING_REQUIRED_FIELDS = (
    "Missing required fields: projectName, problemName, problemDescription"
)
ERROR_WORKORDER_PART_ID_REQUIRED = "logConfig.partId is required for material mode"
ERROR_WORKORDER_TIME_RANGE_REQUIRED = (
    "startTime and endTime are required for time range based work orders"
)
ERROR_WORKORDER_TIME_RANGE_INVALID = "startTime must be earlier than endTime"
ERROR_WORKORDER_CREATE_FAILED = "Failed to create work order: {}"
ERROR_WORKORDER_NOT_FOUND = "Work order {} not found"
ERROR_WORKORDER_DELETE_FAILED = "Failed to delete work order: {}"
ERROR_WORKORDER_PAUSE_RESUME_FAILED = "Failed to pause/resume work order: {}"
ERROR_WORKORDER_CANNOT_RESUME = "Cannot resume work order in status: {}"
ERROR_WORKORDER_CANNOT_PAUSE = "Cannot pause work order in status: {}"
ERROR_WORKORDER_LIST_FAILED = "Failed to get work order list: {}"
ERROR_WORKORDER_INVALID_START_DATE = "Invalid startDate format. Expected YYYY-MM-DD"
ERROR_WORKORDER_INVALID_END_DATE = "Invalid endDate format. Expected YYYY-MM-DD"
ERROR_WORKORDER_NO_ATTACHMENTS = "No attachments for work order"
ERROR_WORKORDER_VALIDATION_FAILED = "Work order validation failed"
ERROR_WORKORDER_RETRY_COLLECTION_INVALID_STATUS = (
    "Cannot retry collection for workorder in {} status"
)
ERROR_WORKORDER_PAUSE_UPLOAD_INVALID_STATUS = (
    "Cannot pause upload for work order {}. Current status: {}, expected: UPLOADING"
)
ERROR_WORKORDER_RESUME_COMPRESSION_INVALID_STATUS = "Cannot resume compression for workorder {}. Current status: {}, expected: COMPRESS_FAILED"
ERROR_WORKORDER_RESUME_INVALID_STATUS = "Cannot resume workorder {}. Current status: {}, expected: UPLOAD_PAUSED or UPLOAD_FAILED"
ERROR_WORKORDER_DELETE_INVALID_STATUS = "Cannot delete workorder {} in status: {}. Workorder must be paused, failed, or completed before deletion."
ERROR_WORKORDER_SIZE_EXCEEDS_LIMIT = (
    "Workorder size {:.2f}GB exceeds maximum allowed {}GB"
)
ERROR_WORKORDER_NO_PENDING_COMPRESSION_TASKS = (
    "No pending compression tasks found for workorder {}"
)
ERROR_WORKORDER_NO_COMPLETED_COMPRESSION_TASKS = (
    "Workorder {} has no completed compression tasks"
)
ERROR_WORKORDER_RETRY_UPLOAD_INVALID_STATUS = (
    "Cannot retry upload for work order {}. Current status: {}, expected: UPLOAD_FAILED"
)
ERROR_WORKORDER_NO_VALID_ATTACHMENT_FILES = (
    "No valid attachment files found for workorder {}"
)

# File Errors
ERROR_FILE_NOT_FOUND = "File not found: {}"
ERROR_FILE_EMPTY = "File is empty: {}"
ERROR_FILE_NO_VALID_PATHS = "No valid source paths found: {}"
ERROR_FILE_PATH_NOT_EXIST = "Path does not exist: {}"
ERROR_FILE_PROPERTIES_NOT_FOUND = "{} not existed"

# Authentication Errors
ERROR_AUTH_LOGIN_FAILED = "Login failed with status {}"
ERROR_AUTH_FAILED = "Authentication failed: {}"
ERROR_AUTH_NO_TOKEN = "No token in response"
ERROR_AUTH_FETCH_TOKEN_FAILED = "Failed to fetch token: {}"

# Cloud Storage Errors
ERROR_CLOUD_SOURCE_NOT_FOUND = "Source file not found: {}"
ERROR_CLOUD_SOURCE_NOT_FILE = "Source path is not a file: {}"
ERROR_CLOUD_INVALID_PROVIDER = "Invalid cloud provider: {}. Valid providers: {}"
ERROR_CLOUD_TASK_NOT_RUNNING = "Task {} is not running. Current status: {}"
ERROR_CLOUD_TASK_ALREADY_RUNNING = "Task {} already has a running Celery task: {}"
ERROR_CLOUD_TASK_NOT_PAUSED = "Task {} is not paused. Current status: {}"
ERROR_CLOUD_TASK_NO_UPLOAD_ID = (
    "Task {} has no upload_id, cannot resume. Might be single-part upload task."
)
ERROR_CLOUD_TASK_INCOMPLETE = (
    "Cannot delete file for incomplete task. Task ID: {}, Status: {}"
)
ERROR_CLOUD_MISSING_CONFIG_FIELDS = "Missing required fields in [ossService]: {}"
ERROR_CLOUD_PART_SIZE_EXCEEDS_MAX = (
    "Part size {} bytes exceeds maximum allowed {} bytes"
)
ERROR_CLOUD_INVALID_SERVICE_TYPE = "Invalid serviceType '{}' for {}. Expected: '{}'"
ERROR_CLOUD_CONFIG_FILE_NOT_FOUND = (
    "Config file not found: {}. Please check configuration."
)
ERROR_CLOUD_MISSING_OSS_SERVICE = "Missing [ossService] section in config file"
ERROR_CLOUD_PROVIDER_NOT_REGISTERED = (
    "Provider '{}' not registered. Available providers: {}"
)

# Compression Errors
ERROR_COMPRESSION_NO_VALID_PATHS = "No valid source paths found: {}"
ERROR_COMPRESSION_INVALID_LEVEL = "Invalid compression level: {}. Must be 1-22"
ERROR_COMPRESSION_TASK_NOT_PENDING = (
    "Task {} is not in PENDING status. Current status: {}"
)
ERROR_COMPRESSION_TASK_NOT_RUNNING = "Task {} is not running. Current status: {}"
ERROR_COMPRESSION_TASK_ALREADY_RUNNING = "Task {} already has a running Celery task: {}"
ERROR_COMPRESSION_TASK_NOT_PAUSED = "Task {} is not paused. Current status: {}"
ERROR_COMPRESSION_TASK_INCOMPLETE = (
    "Cannot delete file for incomplete task. Task ID: {}, Status: {}"
)
ERROR_COMPRESSION_INSUFFICIENT_DISK_SPACE = (
    "Insufficient disk space. Required {} bytes, available {} bytes"
)
ERROR_COMPRESSION_TOTAL_SIZE_ZERO = "Total size of source files is 0, source paths: {}"
ERROR_COMPRESSION_ABORTED_BY_USER = "User aborted the compression"

# Log Capture Errors
ERROR_LOG_MATERIAL_ID_NOT_FOUND = "partIdNotFound: part_id={}"
ERROR_LOG_UNITX_LOG_NOT_FOUND = "unitxLogNotFound"
ERROR_LOG_PART_ID_REQUIRED = "part_id is required for part_id mode"
ERROR_LOG_TIME_RANGE_INVALID = "Invalid time range"

# Cascader Options Errors
ERROR_CASCADER_GET_OPTIONS_FAILED = "Failed to get cascader options: {}"

# Cloud Upload Task Errors
ERROR_UPLOAD_TASK_NOT_FOUND = "Task not found"
ERROR_UPLOAD_NETWORK_UNREACHABLE = "Network error: Unable to connect to server"
ERROR_UPLOAD_NETWORK_TIMEOUT = "Network error: Connection timeout"
ERROR_UPLOAD_NETWORK_CONNECTION_FAILED = "Network error: Connection failed"
ERROR_UPLOAD_AUTH_INVALID_CREDENTIALS = (
    "Authentication error: Invalid credentials or access denied"
)
ERROR_UPLOAD_STORAGE_INSUFFICIENT_SPACE = "Storage error: Insufficient disk space"
ERROR_UPLOAD_FILE_NOT_FOUND = "File error: File not found"
ERROR_UPLOAD_OSS_BUCKET_NOT_EXIST = "OSS error: Bucket does not exist"
ERROR_UPLOAD_OSS_INVALID_BUCKET_NAME = "OSS error: Invalid bucket name"
ERROR_UPLOAD_SECURITY_SSL_CERTIFICATE = "Security error: SSL/Certificate issue"
ERROR_UPLOAD_NETWORK_DNS_RESOLUTION = "Network error: Cannot resolve server address"
ERROR_UPLOAD_GENERIC_ERROR = "Error: {}"
ERROR_UPLOAD_UNKNOWN_ERROR = "Unknown error occurred"

# Attachment Type Display Names
ATTACHMENT_TYPE_LOG = "Log Files"
ATTACHMENT_TYPE_TRAINING_DATA = "Training Data"
ATTACHMENT_TYPE_MODEL = "Model"
ATTACHMENT_TYPE_CONFIG = "Configuration"
ATTACHMENT_TYPE_POSTPROCESS = "Post-process Files"
ATTACHMENT_TYPE_LOCAL_FILE = "Local Files"

# Work Order Status Display Names
WORKORDER_STATUS_DRAFT = "Draft"
WORKORDER_STATUS_SUBMITTED = "Submitted"
WORKORDER_STATUS_COLLECTING = "Collecting"
WORKORDER_STATUS_COLLECTION_FAILED = "Collection Failed"
WORKORDER_STATUS_COMPRESSING = "Compressing"
WORKORDER_STATUS_COMPRESS_PAUSED = "Compress Paused"
WORKORDER_STATUS_COMPRESS_FAILED = "Compress Failed"
WORKORDER_STATUS_COMPRESSED = "Compressed"
WORKORDER_STATUS_UPLOADING = "Uploading"
WORKORDER_STATUS_UPLOAD_PAUSED = "Upload Paused"
WORKORDER_STATUS_UPLOAD_FAILED = "Upload Failed"
WORKORDER_STATUS_COMPLETED = "Completed"

# Attachment Validation Errors
ERROR_ATTACHMENT_NO_FILES_FOUND = "No files found in {} configured paths"
ERROR_ATTACHMENT_TOTAL_SIZE_ZERO = "{} total file size is 0 bytes"

# Success Messages
SUCCESS_RECORDING_STARTED = "Recording started"
SUCCESS_RECORDING_STOPPED = "Recording stopped"
SUCCESS_WORKORDER_CREATED = "Work order created successfully"
PRODUCTION_PY_IMAGING_CONFIG_NOT_AVAILABLE = (
    "imaging_config is not defined in /home/unitx/unitx_data/config/production.py"
)
PRODUCTION_PY_IMAGING_CONFIG_UNKOWN_SOURCE = (
    "/home/unitx/unitx_data/config/production.py imaging_config unknown source: {}"
)
PRODUCTION_PY_IMAGING_CONFIG_DUPLICATE_CC = "/home/unitx/unitx_data/config/production.py same capture config cannot be used for different cameras in the same part type"
PRODUCTION_PY_IMAGING_CONFIG_LIVE_MODE_ONLY_ALLOW_ONE_IMAGE = (
    "Live mode only supports 1 controller source with 1 capture config"
)
PRODUCTION_PY_PART_TYPE_NOT_UNIQUE = (
    "/home/unitx/unitx_data/config/production.py part_type must be unique"
)
PRODUCTION_PY_DUPLICATE_CAPTURE_CONFIG = (
    "/home/unitx/unitx_data/config/production.py cannot use duplicate capture config"
)
PRODUCTION_PY_DUPLICATE_CAMERA_ACROSS_PARTS = "/home/unitx/unitx_data/config/production.py cannot use the same camera across different part types"
PRODUCTION_PY_EMPTY_SEQUENCE_NAME_IN_COMPUTATIONAL_CONFIG = "/home/unitx/unitx_data/config/production.py computational image feature should define sequence_name"
PRODUCTION_PY_IMAGING_CONFIG_DUPLICATE_SEQUENCE_NAME = "/home/unitx/unitx_data/config/production.py can not use duplicate sequence name: {}"
PRODUCTION_PY_COMPUTATIONAL_CONFIG_UNKOWN_METHOD = (
    "/home/unitx/unitx_data/config/production.py unknown image computation method: {}"
)

CONTROLLER_ID_IS_MISSING = "{} not found, please check the hardware settings."
CONTROLLER_ID_IS_REPEAT = (
    "Duplicate {} has been set, please check the hardware settings."
)
CONTROLLER_CAPTURE_NAME_INVALID = "The capture names '{capture_names}' are configured incorrectly and are not exist in OptiX's db, please check the config in OptiX."
CONTROLLER_SEQUENCE_HARDWARE_INDEX_NOT_FOUND = "Hardware index for sequence [{}] of controller [{}] not found. Unable to start image validation. Please check the configuration."
CAMERA_SEQUENCE_NOT_FOUND = "Camera mode [{}] sequence [{}] details not found. Maybe not configured. If configured, please check the configuration."

PERMISSION_MODULE_OPTIX = "Flex Edge-OptiX"

PERMISSION_MODULE_COMX = "Flex Edge-ComX"

PERMISSION_MODULE_EDGE_OTHER = "FleX Edge - Other"

# Global config UI module cards (served via get_global_configs.modules)
GLOBAL_CONFIG_MODULE_GROUP_MASK_NAME = "Mask Drawing"
GLOBAL_CONFIG_MODULE_GROUP_MASK_DESCRIPTION = ""
GLOBAL_CONFIG_MODULE_GROUP_COMPRESSOR_NAME = "Image Compression"
GLOBAL_CONFIG_MODULE_GROUP_COMPRESSOR_DESCRIPTION = "All parameter settings only compress JPG images and will not affect images in other formats"
GLOBAL_CONFIG_MODULE_GROUP_IMAGE_NAME = "Image Save and Deletion"
GLOBAL_CONFIG_MODULE_GROUP_IMAGE_DESCRIPTION = (
    "Image deletion is triggered when either disk space or time condition is met"
)
GLOBAL_CONFIG_MODULE_GROUP_TIMEOUT_NAME = "System Timeout"
GLOBAL_CONFIG_MODULE_GROUP_TIMEOUT_DESCRIPTION = "Please modify under OPS guidance"
GLOBAL_CONFIG_MODULE_GROUP_OPTIX_NAME = "OptiX Config"
GLOBAL_CONFIG_MODULE_GROUP_OPTIX_DESCRIPTION = ""
GLOBAL_CONFIG_MODULE_GROUP_OTHER_NAME = "Other"
GLOBAL_CONFIG_MODULE_GROUP_OTHER_DESCRIPTION = ""

# Global config display (label, description, default value description), follow the rule to match the config key and the translation key
GLOBAL_CONFIG_LABEL_DRAW_MASK_TEXT = "Show text"
GLOBAL_CONFIG_DESCRIPTION_DRAW_MASK_TEXT = "Mask drawing information includes, Part ID, image result, defect details, and timestamp."
GLOBAL_CONFIG_LABEL_DRAW_MASK_CONTOUR = "Show defect contour"
GLOBAL_CONFIG_DESCRIPTION_DRAW_MASK_CONTOUR = "Draw and display the contours of defects"
GLOBAL_CONFIG_LABEL_DRAW_MASK_TEXT_COLOR = "Text color"
GLOBAL_CONFIG_DESCRIPTION_DRAW_MASK_TEXT_COLOR = (
    "Set the font color for defect details and timestamps in the Mask, defaulting to white.\n\n"
    "(The colors for part ID & image results cannot be set; defaults are red for NG and green for OK.)"
)
GLOBAL_CONFIG_LABEL_ENABLE_OVERLAY_DECISION = "Show image result"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_OVERLAY_DECISION = (
    "Display the OK/NG/LIMIT results of image\n"
    "Note: When this toggle is off, the partID will automatically close."
)
GLOBAL_CONFIG_LABEL_ENABLE_OVERLAY_PART_ID = "Show Part_ID"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_OVERLAY_PART_ID = (
    "Display the material ID in the mask image"
)
GLOBAL_CONFIG_LABEL_OVERLAY_DECISION_FONT_SIZE = "Decision font size"
GLOBAL_CONFIG_DESCRIPTION_OVERLAY_DECISION_FONT_SIZE = (
    "Image result and Part ID font size."
)
GLOBAL_CONFIG_DEFAULT_VALUE_DESCRIPTION_OVERLAY_DECISION_FONT_SIZE = (
    "Adapts to image size"
)
GLOBAL_CONFIG_LABEL_ENABLE_OVERLAY_DETAIL_RESULTS = "Show Feature details"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_OVERLAY_DETAIL_RESULTS = (
    "Display defect information, including defect result, xy, vh, mr, and area in Mask"
)
GLOBAL_CONFIG_LABEL_OVERLAY_FONT_SIZE = "Details font size"
GLOBAL_CONFIG_DESCRIPTION_OVERLAY_FONT_SIZE = (
    "Set the font size for defect details. The default is 0, which means it adapts to the image size. "
    "The recommended font size range is between 100 and 500."
)
GLOBAL_CONFIG_DEFAULT_VALUE_DESCRIPTION_OVERLAY_FONT_SIZE = "Adapts to image size"
GLOBAL_CONFIG_LABEL_ENABLE_OVERLAY_TIMESTAMP = "Show Timestamp"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_OVERLAY_TIMESTAMP = "Display the timestamp, the timestamp on the image indicates the time when image acquisition was completed."
GLOBAL_CONFIG_LABEL_OVERLAY_TIMESTAMP_FONT_SIZE = "Timestamp font size"
GLOBAL_CONFIG_DESCRIPTION_OVERLAY_TIMESTAMP_FONT_SIZE = (
    "Set the defect detail font size. Default is 0, which means it adapts to the image size."
    "This requires enabling the display of defect details. The recommended font size range is between 100 and 500."
)
GLOBAL_CONFIG_DEFAULT_VALUE_DESCRIPTION_OVERLAY_TIMESTAMP_FONT_SIZE = (
    "Adapts to image size"
)
GLOBAL_CONFIG_LABEL_MAX_NUM_LINES_TO_SHOW_ON_MASK = (
    "Maximum row of defect in the mask image"
)
GLOBAL_CONFIG_DESCRIPTION_MAX_NUM_LINES_TO_SHOW_ON_MASK = (
    "It indicates the maximum number of defect rows displayed on the Mask. "
    "A default value of 50 means that a maximum of only 50 rows of defect data will be displayed."
)
GLOBAL_CONFIG_LABEL_MASK_SEGMENT_DRAW_THRESHOLD = "Defect type threshold"
GLOBAL_CONFIG_DESCRIPTION_MASK_SEGMENT_DRAW_THRESHOLD = (
    "The threshold for defect types in the mask image: when this value is set greater than "
    "mask_segment_draw_max_num_limits, the number of defect types drawn will be limited by the latter; "
    "when it is equal to 0, there is no limit."
)
GLOBAL_CONFIG_DEFAULT_VALUE_DESCRIPTION_MASK_SEGMENT_DRAW_THRESHOLD = (
    "No limit on defect count"
)
GLOBAL_CONFIG_LABEL_MASK_SEGMENT_DRAW_MAX_NUM_LIMITS = (
    "Upper limit of defect type threshold"
)
GLOBAL_CONFIG_DESCRIPTION_MASK_SEGMENT_DRAW_MAX_NUM_LIMITS = (
    "The maximum upper limit for the defect type threshold in the mask image. "
    "If this value is set lower than mask_segment_draw_threshold, this value will be used."
)
GLOBAL_CONFIG_LABEL_SAVE_NG_MASK_QUALITY = "NG Mask compression rate"
GLOBAL_CONFIG_DESCRIPTION_SAVE_NG_MASK_QUALITY = (
    "Set the compression quality for saving NG Mask(default 25). A higher value means the image is closer to Raw "
    "but results in a larger file size. The compression rate does not change the width and height dimensions "
    "of the image, but the clarity will be reduced after compression."
)
GLOBAL_CONFIG_LABEL_SAVE_NG_MASK_RESIZE = "NG Mask scaling size"
GLOBAL_CONFIG_DESCRIPTION_SAVE_NG_MASK_RESIZE = (
    "Set the scaling ratio for saving NG Mask (default 100, no scaling). "
    "For example, 50 means both the length and width are reduced to 50% of the original dimensions."
)
GLOBAL_CONFIG_LABEL_SAVE_NG_IMAGE_QUALITY = "NG Raw compression rate"
GLOBAL_CONFIG_DESCRIPTION_SAVE_NG_IMAGE_QUALITY = (
    "Set the compression quality for saving NG Raw(default 95). The higher the value, the closer it is to the "
    "original image, resulting in a larger file size. The compression rate does not change the width or height "
    "dimensions of the image, but the clarity will be reduced after compression."
)
GLOBAL_CONFIG_LABEL_SAVE_NG_IMAGE_RESIZE = "NG Raw scaling size"
GLOBAL_CONFIG_DESCRIPTION_SAVE_NG_IMAGE_RESIZE = (
    "Set the scaling ratio for saving NG Raw(default 100, no scaling). "
    "For example, 50 means both the length and width are reduced to 50% of the original dimensions."
)
GLOBAL_CONFIG_LABEL_SAVE_OK_MASK_QUALITY = "OK Mask compression rate"
GLOBAL_CONFIG_DESCRIPTION_SAVE_OK_MASK_QUALITY = (
    "Set the compression quality for saving OK Mask(default 25). A higher value means the image is closer to Raw "
    "but results in a larger file size. The compression rate does not change the width and height dimensions "
    "of the image, but the clarity will be reduced after compression."
)
GLOBAL_CONFIG_LABEL_SAVE_OK_MASK_RESIZE = "OK Mask scaling size"
GLOBAL_CONFIG_DESCRIPTION_SAVE_OK_MASK_RESIZE = (
    "Set the scaling ratio for saving OK Mask (default 100, no scaling). "
    "For example, 50 means both the length and width are reduced to 50% of the original dimensions."
)
GLOBAL_CONFIG_LABEL_SAVE_OK_IMAGE_QUALITY = "OK Raw compression rate"
GLOBAL_CONFIG_DESCRIPTION_SAVE_OK_IMAGE_QUALITY = (
    "Set the compression quality for saving OK Raw(default 95). The higher the value, the closer it is to the "
    "original image, resulting in a larger file size. The compression rate does not change the width or height "
    "dimensions of the image, but the clarity will be reduced after compression."
)
GLOBAL_CONFIG_LABEL_SAVE_OK_IMAGE_RESIZE = "OK Raw scaling size"
GLOBAL_CONFIG_DESCRIPTION_SAVE_OK_IMAGE_RESIZE = (
    "Set the scaling ratio for saving OK Raw (default 100, no scaling). "
    "For example, 50 means both the length and width are reduced to 50% of the original dimensions."
)
GLOBAL_CONFIG_LABEL_AUTO_IMAGE_DELETION_MODE = "Deletion Mode"
GLOBAL_CONFIG_DESCRIPTION_AUTO_IMAGE_DELETION_MODE = (
    "By default, both the Raw and the Mask image are deleted, can be switched to delete only Raw. "
    "When the image storage time limit is exceeded or disk is insufficient, images will be deleted according to this configuration."
)
GLOBAL_CONFIG_LABEL_AUTO_IMAGE_DELETION_INTERVAL_SECS = "Deletion polling cycle"
GLOBAL_CONFIG_DESCRIPTION_AUTO_IMAGE_DELETION_INTERVAL_SECS = (
    "Set the trigger frequency for image deletion, to be used in conjunction with image retention days "
    "and disk space management. Default is 0.5h, meaning it checks the date and disk space every half hour "
    "to decide whether to delete images."
)
GLOBAL_CONFIG_LABEL_DISK_SPACE_AUTO_DELETE_GB = "Delete based on disk space"
GLOBAL_CONFIG_DESCRIPTION_DISK_SPACE_AUTO_DELETE_GB = (
    "Minimum Free Disk Space (Default: 300GB). When the remaining space falls below this value,"
    "the system will automatically delete the oldest image data."
)
GLOBAL_CONFIG_LABEL_DISK_SPACE_TIPS_GB = "Disk insufficient warning"
GLOBAL_CONFIG_DESCRIPTION_DISK_SPACE_TIPS_GB = (
    "Set the disk space warning threshold (default 500G). When the remaining disk space falls below this value, "
    "a low-space prompt will be displayed on the ProdX."
)
GLOBAL_CONFIG_LABEL_DISK_SPACE_HARD_LIMIT_GB = "Critical disk warning"
GLOBAL_CONFIG_DESCRIPTION_DISK_SPACE_HARD_LIMIT_GB = (
    "When the remaining disk space falls below this value (default 200G), ProdX stops running and prompt "
    "that disk space is critically low."
)
GLOBAL_CONFIG_LABEL_IMAGE_RETENTION_DAYS = "Deletion based on retention days"
GLOBAL_CONFIG_DESCRIPTION_IMAGE_RETENTION_DAYS = "Set the image retention period(default 180 days), meaning images older than 180 days will be automatically deleted."
GLOBAL_CONFIG_LABEL_AUTO_IMAGE_DELETION_TODAY_HOURS = "Daily image deletion cycle"
GLOBAL_CONFIG_DESCRIPTION_AUTO_IMAGE_DELETION_TODAY_HOURS = (
    "When images have already been deleted based on retention period but disk space is still insufficient, "
    "the system will automatically delete images today. This parameter sets the deletion cycle for today's production data. "
    "The default value is 4, meaning that if images from the past XX days have already been deleted but disk remains insufficient, "
    "images taken today at 12:00 will start being deleted at 16:00."
)
GLOBAL_CONFIG_LABEL_IMAGE_PROCESS_TIMEOUT_MS = "Image processing timeout duration"
GLOBAL_CONFIG_DESCRIPTION_IMAGE_PROCESS_TIMEOUT_MS = (
    "When too many images of 1 part, the processing time can be lengthy, and the system may not complete processing "
    "before the camera resets. This value(default 500ms) indicates the tolerance after the camera resets if image "
    "processing is still not finished. Only when this time is exceeded will it be judged as a processing timeout."
)
GLOBAL_CONFIG_LABEL_CAMERA_RESET_TIMEOUT_MS = "Camera reset waiting time"
GLOBAL_CONFIG_DESCRIPTION_CAMERA_RESET_TIMEOUT_MS = (
    "Set the tolerance for continuing to receive images after camera resets. Default 500ms, "
    "meaning images from the camera will still be received for 500ms after the camera resets."
)
GLOBAL_CONFIG_LABEL_TROUBLE_SHOOTING_TASK_GRAPH_STEPS_TIMEOUT_MS = (
    "Standard node timeout duration"
)
GLOBAL_CONFIG_DESCRIPTION_TROUBLE_SHOOTING_TASK_GRAPH_STEPS_TIMEOUT_MS = (
    "Set the processing time of standardized task graph nodes (such as image inference, "
    "applying standard thresholds, image storage, etc.) has timed out. This is used for system issue localization. "
    "The default is 500ms, when the time exceeds 500ms,"
    "troubleshooting will determine a processing timeout and record it in the system."
)
GLOBAL_CONFIG_LABEL_TROUBLE_SHOOTING_TASK_GRAPH_CUSTOM_STEPS_TIMEOUT_MS = (
    "Customized node timeout duration"
)
GLOBAL_CONFIG_DESCRIPTION_TROUBLE_SHOOTING_TASK_GRAPH_CUSTOM_STEPS_TIMEOUT_MS = (
    "Set the processing time of customized task graph nodes (such as custom image processing, "
    "2.5D customization requirements, applying customized thresholds) has timed out. "
    "This is used for system issue localization. The default is 100ms; when the time exceeds 100ms, "
    "troubleshooting will determine a processing timeout and record it in the system."
)
GLOBAL_CONFIG_LABEL_TASK_GRAPH_GATING_TIMEOUT = "Standard node branch timeout duration"
GLOBAL_CONFIG_DESCRIPTION_TASK_GRAPH_GATING_TIMEOUT = (
    "Set the timeout duration for standard task graph node. Default 180 ms. "
    "This is typically a parameter set by engineers; if adjustment is needed, please use it under the guidance of OPS."
)
GLOBAL_CONFIG_LABEL_PART_CYCLE_TIME = "Theoretical estimated CT"
GLOBAL_CONFIG_DESCRIPTION_PART_CYCLE_TIME = (
    "Used to calculate the theoretical maximum output, evaluate equipment utilization, and compare actual output "
    "with theoretical output to generate production analysis reports. The default value is 1s, "
    "meaning the assumed CT for 1 part is 1s."
)
GLOBAL_CONFIG_LABEL_ENABLE_25D = "Camera calibration"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_25D = "Once enabled, a calibration button will appear on the right side of Optix to perform the calibration."
GLOBAL_CONFIG_LABEL_V6_LIGHT_ON_ADDITIONAL_DURATION_US = "V6 extra exposure"
GLOBAL_CONFIG_DESCRIPTION_V6_LIGHT_ON_ADDITIONAL_DURATION_US = (
    "Due to the delay in camera exposure, additional exposure time is added to the Optix's general exposure time "
    "to allow the light's exposure to fully cover the camera's exposure. Default 100μs, meaning the light source's "
    "exposure will be extended by an additional 100μs. Only applies to V6 and above."
)
GLOBAL_CONFIG_LABEL_V6_LIGHT_ON_DELAY_US = "V6 exposure delay"
GLOBAL_CONFIG_DESCRIPTION_V6_LIGHT_ON_DELAY_US = (
    "It takes about 50 us for the camera to open shutter, this parameter sets the delay time. "
    "It delays the triggering of the lights during a single exposure cycle. The default is 20us "
    "meaning the lights up 20us after receiving the trigger signal. Only applies to V6 and above."
)
GLOBAL_CONFIG_LABEL_SEQUENCE_TRIGGER_DELAY = "Sequence trigger delay"
GLOBAL_CONFIG_DESCRIPTION_SEQUENCE_TRIGGER_DELAY = (
    "When camera does not support trigger_width exposure mode. Indicates the interval time between gating "
    "and triggering of Optix. The default is 24000us, means 24ms interval between the gating and triggering of the Sequence."
)
GLOBAL_CONFIG_LABEL_USE_GAMMA_CORRECT = "Gamma correction"
GLOBAL_CONFIG_DESCRIPTION_USE_GAMMA_CORRECT = (
    "To ensure HK camera performance match those of Basler. When enabled, Gamma is applied to the image after capture. "
    "This is applicable to HK cameras only."
)
GLOBAL_CONFIG_LABEL_LIVE_MODE_TRIGGER_INTERVAL_MS = "Live mode trigger interval"
GLOBAL_CONFIG_DESCRIPTION_LIVE_MODE_TRIGGER_INTERVAL_MS = (
    "Used in live mode to avoid issues such as triggering too quickly causing inference to fall behind or queue buildup. "
    "Default 50ms. The interval must be greater than 1000ms / fps. For example, for a camera with 75fps, "
    "the interval needs to be greater than 14ms."
)
GLOBAL_CONFIG_LABEL_CONTEXT_IMAGE_INTERVAL_TOLERANCE = (
    "Image acquisition time difference"
)
GLOBAL_CONFIG_DESCRIPTION_CONTEXT_IMAGE_INTERVAL_TOLERANCE = (
    "The maximum time between the IPC receiving the controller message and the image. Default 200ms, "
    "meaning the maximum between the IPC receiving the controller message and the camera image is 200ms. "
    "If it exceeds 200ms, ProdX will display a prompt indicating that the Image was received later than the controller message. "
    "A timeout will only trigger a warning and will not cause ProdX to encounter an error."
)
GLOBAL_CONFIG_LABEL_ENABLE_V6_DEFAULT_GPIO = "5V GPIO trigger"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_V6_DEFAULT_GPIO = (
    "By default 24V triggering is used (good anti-interference performance, but external trigger response is 50µs longer). "
    "You can switch to 5V triggering (worse anti-interference), with a shorter response delay to external trigger exposure (37µs)."
)
GLOBAL_CONFIG_LABEL_LIGHT_CONTROLLER_INPUT_MODE = "Light controller input mode"
GLOBAL_CONFIG_DESCRIPTION_LIGHT_CONTROLLER_INPUT_MODE = "Direct: one port = one sequence. Encoding (mixed): can use some ports as direct and others for sequence-ID encoding."
GLOBAL_CONFIG_LABEL_ENABLE_ACTIVE_LEARNING_FEATURE = "Active learning"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_ACTIVE_LEARNING_FEATURE = (
    "System automatically selects and saves the top 5 images with the highest value for each feature daily during running, "
    "based on model confidence/learning. Default is disabled."
)
GLOBAL_CONFIG_LABEL_ENABLE_MULTITHREAD_CORTEX_POSTPROCESS = "Multi-threaded of model"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_MULTITHREAD_CORTEX_POSTPROCESS = (
    "Use multi-threading to run model results, enabled by default."
)
GLOBAL_CONFIG_LABEL_NUM_CORTEX_SERVICES = "Number of Cortex Services"
GLOBAL_CONFIG_DESCRIPTION_NUM_CORTEX_SERVICES = "The number of Cortex inference service instances running in parallel for image processing. Default is 1."
GLOBAL_CONFIG_LABEL_NUM_INFERENCE_CLASS_WORKERS = "Number of threads for inference"
GLOBAL_CONFIG_DESCRIPTION_NUM_INFERENCE_CLASS_WORKERS = (
    "The number of threads to process model inference. The default is 4."
)
GLOBAL_CONFIG_LABEL_ENABLE_UNITX_SDK = "Unitx SDK"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_UNITX_SDK = (
    "Use SDK mode. Customized requirements, such as customized ProdX UI and customized image processing, "
    "require this parameter to be enabled. Disabled by default. If needed, please enable it with the assistance of OPS."
)
GLOBAL_CONFIG_LABEL_STRESS_TEST = "Stress Test"
GLOBAL_CONFIG_DESCRIPTION_STRESS_TEST = (
    "For test engineers. When enabled, it allows to test the IPC performance. "
    "Please use it with the assistance of an engineer."
)
GLOBAL_CONFIG_LABEL_MOCK_HARDWARE = "Virtual Hardware"
GLOBAL_CONFIG_DESCRIPTION_MOCK_HARDWARE = (
    "For test engineers. When enabled, it allows to test virtual HW. "
    "Please use it with the assistance of an engineer."
)
GLOBAL_CONFIG_LABEL_FLEX_DOME_CHANNEL_MAP = "LFOV Configuration"
GLOBAL_CONFIG_DESCRIPTION_FLEX_DOME_CHANNEL_MAP = (
    "For engineers, channel mapping configuration for Large FOV Dome lights. Used to map light IDs to the controller's "
    "actual logical channels, ensuring the software activates the correct lights. For example, Light 1 is logically connected to channel 8."
)
GLOBAL_CONFIG_LABEL_ENABLE_MONITORING = "Monitoring System"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_MONITORING = (
    "When enabled, the system will monitor the performance and usage data of the IPC, such as CPU, GPU, and memory utilization. "
    "Enabled by default."
)
GLOBAL_CONFIG_LABEL_EXTERNAL_IMAGE_AUTO_MODE = "Image Source Mode"
GLOBAL_CONFIG_DESCRIPTION_EXTERNAL_IMAGE_AUTO_MODE = (
    'Using the image source mode, the system will perform a "part start" action in automatic mode; '
    "image source mode is enabled by default."
)
GLOBAL_CONFIG_LABEL_NUM_SAVE_IMAGES_WORKERS = "Number of Image Saving Threads"
GLOBAL_CONFIG_DESCRIPTION_NUM_SAVE_IMAGES_WORKERS = "The number of concurrent threads used to perform the image saving task; the default value is 4."
GLOBAL_CONFIG_LABEL_NUM_CORTEX_PIPELINE_WORKERS = "Number of Inference Threads"
GLOBAL_CONFIG_DESCRIPTION_NUM_CORTEX_PIPELINE_WORKERS = (
    "The default value is 4, which represents the number of images whose inference process can be processed "
    "concurrently at the same time."
)
GLOBAL_CONFIG_LABEL_DEFAULT_LOCATION_NET_ARCHITECTURE = "Position Model Architecture"
GLOBAL_CONFIG_DESCRIPTION_DEFAULT_LOCATION_NET_ARCHITECTURE = (
    "Select the architecture for the position detection model. Default: multihead."
)
GLOBAL_CONFIG_LABEL_DEFAULT_25D_SEGMENTATION_NET_ARCHITECTURE = (
    "2.5D Model Architecture"
)
GLOBAL_CONFIG_DESCRIPTION_DEFAULT_25D_SEGMENTATION_NET_ARCHITECTURE = (
    "Select the architecture for the 2.5D segmentation model. Default: multihead_25d."
)
GLOBAL_CONFIG_LABEL_DEFAULT_SEGMENTATION_NET_ARCHITECTURE = (
    "Segmentation Model Architecture"
)
GLOBAL_CONFIG_DESCRIPTION_DEFAULT_SEGMENTATION_NET_ARCHITECTURE = (
    "Select the architecture for the segmentation model. Default: multihead."
)
GLOBAL_CONFIG_LABEL_DEFAULT_DEFECT_NET_ARCHITECTURE = "Defect Model Architecture"
GLOBAL_CONFIG_DESCRIPTION_DEFAULT_DEFECT_NET_ARCHITECTURE = (
    "Select the architecture for the defect detection model. Default: v4."
)

GLOBAL_CONFIG_LABEL_NUM_PARTS_ON_UI = "Number of Parts Displayed on ProdX UI"
GLOBAL_CONFIG_DESCRIPTION_NUM_PARTS_ON_UI = (
    "When the current number of parts is less than the configured value, "
    "the UI will not clear previous parts, even if those parts have already completed."
)

GLOBAL_CONFIG_LABEL_CAMERA_AUTO_RESET_THRESHOLD_MS = "Auto-Reset Threshold (ms)"
GLOBAL_CONFIG_DESCRIPTION_CAMERA_AUTO_RESET_THRESHOLD_MS = "Use this value as the reset timeout threshold during initial device startup; thereafter, it will be recalculated based on the device's operating cycle."

GLOBAL_CONFIG_LABEL_CAMERA_AUTO_RESET_SAFETY_BUFFER_MS = "Auto-Reset Safety Buffer (ms)"
GLOBAL_CONFIG_DESCRIPTION_CAMERA_AUTO_RESET_SAFETY_BUFFER_MS = "Adds a safety buffer time for camera auto-reset, suitable for projects with a more relaxed Cycle Time (CT)."

# Global config unit display (fixed set)
GLOBAL_CONFIG_UNIT_US = "μs"
GLOBAL_CONFIG_UNIT_MS = "ms"
GLOBAL_CONFIG_UNIT_S = "s"
GLOBAL_CONFIG_UNIT_HOUR = "h"
GLOBAL_CONFIG_UNIT_DAY = "day"
GLOBAL_CONFIG_UNIT_GB = "G"
GLOBAL_CONFIG_UNIT_PERCENT = "%"

# Global config value column (read-only), aligned with Optix sysConfig ValueCell
GLOBAL_CONFIG_VALUE_ON = "On"
GLOBAL_CONFIG_VALUE_OFF = "Off"
GLOBAL_CONFIG_MASK_TEXT_COLOR_WHITE = "White"
GLOBAL_CONFIG_MASK_TEXT_COLOR_BLACK = "Black"
GLOBAL_CONFIG_MASK_TEXT_COLOR_RED = "Red"
GLOBAL_CONFIG_MASK_TEXT_COLOR_GREEN = "Green"
GLOBAL_CONFIG_MASK_TEXT_COLOR_BLUE = "Blue"
GLOBAL_CONFIG_AUTO_IMAGE_DELETION_MODE_ORIGINAL_AND_MASK = "Delete Original + Mask"
GLOBAL_CONFIG_AUTO_IMAGE_DELETION_MODE_ORIGINAL_ONLY = "Delete Original Only, Keep Mask"
GLOBAL_CONFIG_GPIO_5V = "5V"
GLOBAL_CONFIG_GPIO_24V = "24V"
GLOBAL_CONFIG_LIGHT_CONTROLLER_DIRECT = "Direct"
GLOBAL_CONFIG_LIGHT_CONTROLLER_INDIRECT = "Encoding (mixed)"

GLOBAL_CONFIG_LABEL_ENABLE_CUSTOM_CSV = "Enable CSV"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_CUSTOM_CSV = "When enabled, PRODX will enable the storage of image and material data to CSV files, default is disabled."
