# coding: utf-8
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from django.conf import settings
from pydantic import BaseModel

from config import global_config
from optix_src.server.perception.libs.light.controller_class import (
    OPTIX_VERSION_TO_CONTROLLER,
)
from optix_src.server.perception.libs.light.v4_controller import V4Controller
from optix_src.server.perception.libs.light.v5_controller import V5Controller
from optix_src.server.perception.libs.light.v6_controller import V6Controller
from optix_src.server.perception.libs.light.v6_flex_controller import V6FlexController
from optix_src.server.perception.libs.light.v6midend_controller import (
    V6MidendController,
)
from optix_src.server.perception.libs.types.controller_camera_mapping import (
    CameraControllerPair,
    CameraControllerPairs,
)

CONTROLLER_CLASSES = [
    V6MidendController,
    V6FlexController,
    V6Controller,
    V5Controller,
    V4Controller,
]
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "optix_src.server.server_config.settings"
)

from unitxutils import formatted_logging

logger = formatted_logging.logging.getLogger(__name__)

try:
    from optix_src.server.perception.libs.camera import basler_camera_ids
    from optix_src.server.perception.libs.camera.basler_camera import BaslerCamera

    BASLER_CAMERA_SUPPORTED = True
except Exception as e:
    logger.info(f"Basler camera not supported. Maybe driver is not installed. {e}")
    BASLER_CAMERA_SUPPORTED = False

try:
    from optix_src.server.perception.libs.camera import haikang_camera_ids
    from optix_src.server.perception.libs.camera.camera_config import (
        camera_config_helper,
    )
    from optix_src.server.perception.libs.camera.haikang_camera import HaikangCamera
    from optix_src.server.perception.libs.camera.haikang_linescan_camera import (
        HKLineScanCamera,
    )

    HAIKANG_CAMERA_SUPPORTED = True
except Exception as e:
    logger.info(f"Haikang camerva not supported. Maybe driver is not installed. {e}")
    HAIKANG_CAMERA_SUPPORTED = False

try:
    from optix_src.server.perception.libs.camera import huaray_camera_ids
    from optix_src.server.perception.libs.camera.huaray_camera import HuarayCamera

    HUARAY_CAMERA_SUPPORTED = True
except Exception as e:
    logger.info(f"Huaray camera is supported. Maybe driver is not installed. {e}")
    HUARAY_CAMERA_SUPPORTED = False
