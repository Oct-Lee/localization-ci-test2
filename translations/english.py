IMPORT_PROJECT_ERROR_MODEL_VERSION_NOT_SPECIFIED = "The Cortex version is not specified in the import file. Please ensure the latest Cortex is running and export the project again to import."
IMPORT_PROJECT_ERROR_INVALID_IMPORTED_VERSION = "The imported project's Cortex version {} must match the current version of Cortex {} at the major and minor levels, allowing differences only in the patch level. For example, version 5.3.1 is compatible with 5.3.0 but not with 5.2.1. Please upgrade Cortex to import this project."
IMPORT_PROJECT_ERROR_PICKLING_ERROR = (
    "Error importing: please check if the file is corrupted or damaged."
)
CAMERA_NOT_FOUND_ERROR = "Camera [{camera_id}] not found. Please check whether the 'camera_id' parameter of the configuration file is correct"
POSTGRES_CONNECT_OTHER = "Database port 5432 is error. Check port status and retry"
DOCKER_CONTAINER_NOT_RUNNING = "Software dependency container error. Try restarting the software or IPC to recovery"
ERROR_FILE_PROPERTIES_NOT_FOUND = "{} not existed"
CONTROLLER_CAPTURE_NAME_INVALID = "The capture names '{capture_names}' are configured incorrectly and are not exist in OptiX's db, please check the config in OptiX."
GLOBAL_CONFIG_DESCRIPTION_DISK_SPACE_HARD_LIMIT_GB = (
    "When the remaining disk space falls below this value (default 200G), ProdX stops running and prompt "
    "that disk space is critically low."
)
GLOBAL_CONFIG_DESCRIPTION_TROUBLE_SHOOTING_TASK_GRAPH_STEPS_TIMEOUT_MS = (
    "Set the processing time of standardized task graph nodes (such as image inference, "
    "applying standard thresholds, image storage, etc.) has timed out. This is used for system issue localization. "
    "The default is 500ms, when the time exceeds 500ms,"
    "troubleshooting will determine a processing timeout and record it in the system."
)
GLOBAL_CONFIG_DESCRIPTION_TROUBLE_SHOOTING_TASK_GRAPH_CUSTOM_STEPS_TIMEOUT_MS = (
    "Set the processing time of customized task graph nodes (such as custom image processing, "
    "2.5D customization requirements, applying customized thresholds) has timed out. "
    "This is used for system issue localization. The default is 100ms; when the time exceeds 100ms, "
    "troubleshooting will determine a processing timeout and record it in the system."
)
GLOBAL_CONFIG_DESCRIPTION_V6_LIGHT_ON_DELAY_US = (
    "It takes about 50 us for the camera to open shutter, this parameter sets the delay time. "
    "It delays the triggering of the lights during a single exposure cycle. The default is 20us "
    "meaning the lights up 20us after receiving the trigger signal. Only applies to V6 and above."
)
GLOBAL_CONFIG_DESCRIPTION_SEQUENCE_TRIGGER_DELAY = (
    "When camera does not support trigger_width exposure mode. Indicates the interval time between gating "
    "and triggering of Optix. The default is 24000us, means 24ms interval between the gating and triggering of the Sequence."
)
GLOBAL_CONFIG_DESCRIPTION_USE_GAMMA_CORRECT = (
    "To ensure HK camera performance match those of Basler. When enabled, Gamma is applied to the image after capture. "
    "This is applicable to HK cameras only."
)
GLOBAL_CONFIG_LABEL_ENABLE_MULTITHREAD_CORTEX_POSTPROCESS = "Multi-threaded of model"
GLOBAL_CONFIG_DESCRIPTION_ENABLE_CUSTOM_CSV = "When enabled, PRODX will enable the storage of image and material data to CSV files, default is disabled."