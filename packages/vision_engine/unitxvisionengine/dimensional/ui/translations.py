

from __future__ import annotations

import os
import pathlib
import re
import sys
from typing import Any, Callable

from PySide6.QtCore import QObject, QSettings, Signal, SignalInstance
from PySide6.QtWidgets import QApplication

_DEBUG = os.environ.get("DIMENSIONAL_TRANSLATIONS_DEBUG") == "1"

LANG_EN = "en"
LANG_ZH = "zh"
LANGUAGES: dict[str, str] = {LANG_EN: "English", LANG_ZH: "中文"}

_SETTINGS_GROUP = "dimensional"
_SETTINGS_KEY = "language"


STRINGS: dict[str, dict[str, str]] = {
    # --- File menu --------------------------------------------------------
    "menu.file": {"en": "&File", "zh": "文件(&F)"},
    "menu.file.open": {"en": "&Open...", "zh": "打开(&O)..."},
    "menu.file.new": {"en": "&New...", "zh": "新建(&N)..."},
    "menu.file.open_recent": {"en": "Open &Recent", "zh": "打开最近的(&R)"},
    "menu.file.save": {"en": "&Save", "zh": "保存(&S)"},
    "menu.file.save_as": {"en": "Save &As...", "zh": "另存为(&A)..."},
    "menu.file.no_recent": {"en": "(No recent projects)", "zh": "（无最近项目）"},
    # --- Help menu --------------------------------------------------------
    "menu.help": {"en": "&Help", "zh": "帮助(&H)"},
    "menu.help.language": {"en": "&Language...", "zh": "语言(&L)..."},
    "menu.help.shortcuts": {"en": "&Keyboard Shortcuts", "zh": "键盘快捷键(&K)"},
    "menu.help.help": {"en": "&Help", "zh": "帮助(&H)"},
    # --- Language picker --------------------------------------------------
    "dlg.lang.title": {"en": "Language", "zh": "语言"},
    "dlg.lang.prompt": {"en": "Select interface language:", "zh": "选择界面语言："},
    # --- App / window -----------------------------------------------------
    "app.title": {"en": "Dimensional Measurement Tool", "zh": "尺寸测量工具"},
    "app.title_with_project": {
        "en": "Dimensional Measurement Tool - {path}",
        "zh": "尺寸测量工具 - {path}",
    },
    # --- File-menu dialogs ------------------------------------------------
    "dlg.open_project.title": {"en": "Open Project", "zh": "打开项目"},
    "dlg.new_project.title": {
        "en": "New Project - Choose Output Directory",
        "zh": "新建项目 - 选择输出目录",
    },
    "dlg.save_as.title": {
        "en": "Save Project As - Choose Directory",
        "zh": "另存项目 - 选择目录",
    },
    "msg.invalid_project.title": {"en": "Invalid Project", "zh": "无效项目"},
    "msg.invalid_project.body": {
        "en": 'No valid project found at "{path}".\nExpected a directory containing project.json.',
        "zh": "在 “{path}” 未找到有效项目。\n需要包含 project.json 的目录。",
    },
    "msg.invalid_project.body_removed": {
        "en": 'No valid project found at "{path}".\nExpected a directory containing project.json. Removed from recent list.',
        "zh": "在 “{path}” 未找到有效项目。\n需要包含 project.json 的目录。已从最近列表中移除。",
    },
    "msg.create_failed.title": {"en": "Failed to Create Project", "zh": "创建项目失败"},
    "msg.create_failed.body": {
        "en": 'Could not create project at "{path}".',
        "zh": "无法在 “{path}” 创建项目。",
    },
    "msg.save_as_failed.title": {"en": "Save As Failed", "zh": "另存为失败"},
    "msg.save_as_failed.body": {
        "en": 'Could not save project to "{path}".',
        "zh": "无法将项目保存到 “{path}”。",
    },
    # --- Tab buttons (the 7 main phases) ---------------------------------
    "tab.setup": {"en": "Setup", "zh": "设置"},
    "tab.regions": {"en": "Regions", "zh": "区域"},
    "tab.contours": {"en": "Contours", "zh": "轮廓"},
    "tab.primitives": {"en": "Primitives", "zh": "基元"},
    "tab.constructed_features": {"en": "Constructed Features", "zh": "构造特征"},
    "tab.measurements": {"en": "Measurements", "zh": "测量"},
    "tab.thresholds": {"en": "Thresholds", "zh": "阈值"},
    # --- Help dialog ------------------------------------------------------
    "dlg.help.title": {"en": "Help", "zh": "帮助"},
    "help.setup.title": {"en": "Setup", "zh": "设置"},
    "help.setup.body": {
        "en": "Open or create a project from the Setup tab. Drag images into the project or use Add Images. Right-click a thumbnail to set it as the golden part \u2014 the reference image used for annotation transfer.",
        "zh": "在“设置”选项卡中打开或创建项目。将图像拖入项目或使用“添加图像”。右键点击缩略图可将其设为黄金件 \u2014 用于标注迁移的参考图像。",
    },
    "help.regions.title": {"en": "Regions", "zh": "区域"},
    "help.regions.body": {
        "en": "Define masks for features on your parts. Add items (0) to create separate masks. Select items with 1\u20139 or click the item box. Press F2 to rename the selected item.",
        "zh": "为零件上的特征定义掩膜。按 0 添加项以创建独立的掩膜。使用 1\u20139 选择项或点击项目框。按 F2 重命名选中项。",
    },
    "help.regions_auto.title": {"en": "Auto (SAM2)", "zh": "自动 (SAM2)"},
    "help.regions_auto.body": {
        "en": (
            "Use SAM2 to generate masks from prompts. Shift + drag to draw "
            "an ROI box, Shift + click for positive points, Shift + Ctrl + "
            "click for negative points. The model runs automatically when "
            "prompts change. Use \u2018Autolabel dataset\u2019 to apply "
            "prompts across all images."
        ),
        "zh": (
            "使用 SAM2 根据提示生成掩膜。Shift + 拖动绘制 ROI 框，"
            "Shift + 点击添加正向点，Shift + Ctrl + 点击添加负向点。"
            "提示变更时模型会自动运行。使用“自动标注数据集”将提示应用到所有图像。"
        ),
    },
    "help.regions_manual.title": {"en": "Manual", "zh": "手动"},
    "help.regions_manual.body": {
        "en": "Draw polygon masks by hand. Shift + click to place vertices. Shift + click the starting point to close the contour.",
        "zh": "手动绘制多边形掩膜。Shift + 点击放置顶点。Shift + 点击起点以闭合轮廓。",
    },
    "help.regions_cortex.title": {"en": "CorteX", "zh": "CorteX"},
    "help.regions_cortex.body": {
        "en": (
            "Use a trained CorteX network. Press Shift+0 or \u2018+ Add from "
            "CorteX\u2019 to enter add mode. Select a model to auto-run "
            "inference and preview all class masks. Check classes to "
            "highlight, then click \u2018Add item(s)\u2019. On an existing "
            "CorteX item, use \u2018Run segmentation\u2019 for the current "
            "image or \u2018Run on all\u2019 for every image."
        ),
        "zh": (
            "使用训练好的 CorteX 网路。按 Shift+0 或“+ 从 CorteX 添加”进入添加模式。"
            "选择模型以自动运行推理并预览所有类别的掩膜。"
            "勾选要高亮的类别，然后点击“添加项”。"
            "在已有的 CorteX 项上，使用“运行分割”处理当前图像，或“在全部运行”处理每张图像。"
        ),
    },
    "help.contours.title": {"en": "Contour Breakdown", "zh": "轮廓分解"},
    "help.contours.body": {
        "en": "Contours are extracted automatically from region masks. Adjust breakdown settings (min length, merge angle) in the tools panel. Click a contour segment to select it.",
        "zh": "轮廓会从区域掩膜中自动提取。在工具面板中调整分解设置（最小长度、合并角度）。点击轮廓段以选中它。",
    },
    "help.primitives.title": {"en": "Primitives", "zh": "基元"},
    "help.primitives.body": {
        "en": "Fit geometric primitives to contour segments. Click a segment to select it, choose a type (line, circle, etc.) and click Add or Update. The primitive is fit to the selected contour points.",
        "zh": "将几何基元拟合到轮廓段。点击段以选中，选择类型（直线、圆等），然后点击“添加”或“更新”。基元会拟合到选中的轮廓点。",
    },
    "help.cf.title": {"en": "Constructed Features", "zh": "构造特征"},
    "help.cf.body": {
        "en": "Build higher-level features from primitives. Select one or more primitives (Shift + click for multi-select). Options appear dynamically based on your selection.",
        "zh": "由基元构建更高层次的特征。选择一个或多个基元（Shift + 点击多选）。选项会根据选择动态出现。",
    },
    "help.meas.title": {"en": "Measurements", "zh": "测量"},
    "help.meas.body": {
        "en": "Create measurements between constructed features. Select one or more features (Shift + click), then choose a measurement type. Results appear on the image and in the tree.",
        "zh": "在构造特征之间创建测量。选择一个或多个特征（Shift + 点击），然后选择测量类型。结果将在图像与树中显示。",
    },
    "help.thresholds.title": {"en": "Thresholds", "zh": "阈值"},
    "help.thresholds.body": {
        "en": "Set pass/fail tolerances for each measurement. Green indicates pass, red indicates fail. Results update across all images automatically.",
        "zh": "为每项测量设置合格/不合格容差。绿色表示合格，红色表示不合格。所有图像上的结果将自动更新。",
    },
    # --- Keybinds dialog --------------------------------------------------
    "dlg.keybinds.title": {"en": "Keyboard Shortcuts", "zh": "键盘快捷键"},
    "kb.col.shortcut": {"en": "Shortcut", "zh": "快捷键"},
    "kb.col.action": {"en": "Action", "zh": "操作"},
    "kb.section.help": {"en": "Help", "zh": "帮助"},
    "kb.section.file": {"en": "File", "zh": "文件"},
    "kb.section.navigation": {"en": "Navigation", "zh": "导航"},
    "kb.section.tabs": {"en": "Tabs", "zh": "选项卡"},
    "kb.section.items": {"en": "Items (Regions)", "zh": "项（区域）"},
    "kb.section.multiview": {"en": "Multi-view", "zh": "多视图"},
    "kb.section.regions_annot": {"en": "Regions annotation", "zh": "区域标注"},
    "kb.help.menu": {"en": "Help menu", "zh": "帮助菜单"},
    "kb.help.shortcuts": {"en": "Keyboard shortcuts", "zh": "键盘快捷键"},
    "kb.help.contextual": {"en": "Contextual help", "zh": "上下文帮助"},
    "kb.help.language": {"en": "Language", "zh": "语言"},
    "kb.file.open": {"en": "Open project", "zh": "打开项目"},
    "kb.file.new": {"en": "New project", "zh": "新建项目"},
    "kb.file.save": {"en": "Save", "zh": "保存"},
    "kb.file.save_as": {"en": "Save As", "zh": "另存为"},
    "kb.nav.fit": {"en": "Fit image to view", "zh": "适应视图"},
    "kb.nav.zoom_in": {"en": "Zoom in", "zh": "放大"},
    "kb.nav.zoom_out": {"en": "Zoom out", "zh": "缩小"},
    "kb.nav.zoom_reset": {"en": "Reset zoom to 100%", "zh": "缩放恢复到 100%"},
    "kb.nav.prev_image": {"en": "Previous image", "zh": "上一张图像"},
    "kb.nav.next_image": {"en": "Next image", "zh": "下一张图像"},
    "kb.nav.golden": {"en": "Jump to golden part", "zh": "跳转到黄金件"},
    "kb.items.select": {"en": "Select item 1-9", "zh": "选择项 1-9"},
    "kb.items.add": {"en": "Add new item", "zh": "添加新项"},
    "kb.items.add_cortex": {"en": "Add from CorteX", "zh": "从 CorteX 添加"},
    "kb.items.rename": {"en": "Rename selected item", "zh": "重命名选中项"},
    "kb.multiview.focus": {"en": "Focus tile 1-4", "zh": "聚焦视图 1-4"},
    "kb.multiview.add_nonconsec": {
        "en": "Add non-consecutive image",
        "zh": "添加非连续图像",
    },
    "kb.multiview.select_range": {"en": "Select image range", "zh": "选择图像范围"},
    "kb.regions.roi_box": {"en": "Draw ROI box", "zh": "绘制 ROI 框"},
    "kb.regions.positive": {"en": "Add positive point", "zh": "添加正向点"},
    "kb.regions.negative": {"en": "Add negative point", "zh": "添加负向点"},
    # --- workspace.py message boxes & inline dialogs ----------------------
    "msg.save_result.title": {"en": "Save result", "zh": "保存结果"},
    "msg.autolabel.title": {"en": "Autolabel", "zh": "自动标注"},
    "msg.autolabel.need_golden": {
        "en": "Set a golden image first and add prompts.",
        "zh": "请先设置黄金件图像并添加提示。",
    },
    "msg.autolabel.no_other": {
        "en": "No other images to label.",
        "zh": "没有其他图像可标注。",
    },
    "msg.autolabel_error.title": {"en": "Autolabel Error", "zh": "自动标注错误"},
    "msg.cortex.title": {"en": "Cortex", "zh": "Cortex"},
    "msg.cortex.no_models": {
        "en": "No cortex models found.",
        "zh": "未找到 Cortex 模型。",
    },
    "msg.cortex.model_not_found": {"en": "Model not found.", "zh": "未找到模型。"},
    "msg.cortex_error.title": {"en": "Cortex Error", "zh": "Cortex 错误"},
    "msg.add_items.title": {"en": "Add items", "zh": "添加项"},
    "msg.add_items.need_class": {
        "en": "Select at least one class to add.",
        "zh": "请至少选择一个要添加的类别。",
    },
    "msg.run_seg.title": {"en": "Run segmentation", "zh": "运行分割"},
    "msg.run_seg.select_item": {
        "en": "Select a cortex item first.",
        "zh": "请先选择一个 Cortex 项。",
    },
    "msg.run_seg.no_config": {
        "en": "Item has no cortex config.",
        "zh": "该项没有 Cortex 配置。",
    },
    "msg.run_all.title": {"en": "Run all", "zh": "在全部运行"},
    "msg.run_all.no_images": {"en": "No images in project.", "zh": "项目中没有图像。"},
    # --- Workspace left panel / phase UI ---------------------------------
    "group.project": {"en": "Project", "zh": "项目"},
    "group.calibration": {"en": "Calibration", "zh": "标定"},
    "group.region_tools": {"en": "Region Tools", "zh": "区域工具"},
    "btn.add_item": {"en": "+ Add item", "zh": "+ 添加项"},
    "btn.add_from_cortex": {"en": "+ Add from CorteX", "zh": "+ 从 CorteX 添加"},
    "label.more": {"en": "\u22ef more", "zh": "\u22ef 更多"},
    "placeholder.item_name": {"en": "Item name", "zh": "项名称"},
    "label.name": {"en": "Name:", "zh": "名称："},
    "label.model": {"en": "Model:", "zh": "模型："},
    "label.select_model": {"en": "Select model:", "zh": "选择模型："},
    "label.classes": {"en": "Classes:", "zh": "类别："},
    "tip.rerun_sam": {
        "en": "Rerun SAM2 with current points and box",
        "zh": "使用当前点和框重新运行 SAM2",
    },
    "tip.clear_prompts": {
        "en": "Clear points, box, and mask for current item/image",
        "zh": "清除当前项/图像的点、框和掩膜",
    },
    "tip.autolabel_dataset": {
        "en": "Apply same prompts to all images and pre-compute masks (fast switching)",
        "zh": "将相同提示应用到所有图像并预计算掩膜（快速切换）",
    },
    "tip.add_classes": {
        "en": "Add items for selected classes",
        "zh": "为选中的类别添加项",
    },
    "tip.run_cortex_current": {
        "en": "Run cortex on current image for this item",
        "zh": "在当前图像上对该项运行 Cortex",
    },
    "tab.annotation.auto": {"en": "Auto", "zh": "自动"},
    "tab.annotation.manual": {"en": "Manual", "zh": "手动"},
    "label.click_to_adjust": {
        "en": "Click to select and adjust contour.",
        "zh": "点击以选择并调整轮廓。",
    },
    # --- Thumbnail context menu ------------------------------------------
    "ctx.make_golden": {"en": "Make golden part", "zh": "设为黄金件"},
    "ctx.reveal_in_finder": {"en": "Reveal in Finder", "zh": "在访达中显示"},
    "ctx.reveal_in_explorer": {"en": "Show in Explorer", "zh": "在资源管理器中显示"},
    "ctx.reveal_in_file_manager": {
        "en": "Show in File Manager",
        "zh": "在文件管理器中显示",
    },
    # --- Intro screen -----------------------------------------------------
    "intro.welcome": {"en": "Welcome to Dimensional", "zh": "欢迎使用尺寸测量"},
    "intro.open_project": {"en": "Open Project", "zh": "打开项目"},
    "intro.new_project": {"en": "New Project", "zh": "新建项目"},
    "intro.recent": {"en": "Recent Projects", "zh": "最近的项目"},
    "intro.no_recent": {"en": "No recent projects yet.", "zh": "尚无最近项目。"},
    # --- Setup panel ------------------------------------------------------
    "label.open_recent": {"en": "Open Recent:", "zh": "打开最近的："},
    "label.file": {"en": "File:", "zh": "文件："},
    "label.unique_id": {"en": "Unique ID:", "zh": "唯一 ID："},
    "label.plane": {"en": "Plane:", "zh": "平面："},
    # --- Contour tools ----------------------------------------------------
    "group.contour_tools": {"en": "Contour Tools", "zh": "轮廓工具"},
    "tip.run_breakdown": {"en": "Rerun contour breakdown", "zh": "重新运行轮廓分解"},
    "tip.clear_mask": {
        "en": "Clear mask for current item/image",
        "zh": "清除当前项/图像的掩膜",
    },
    "tip.run_cortex_all": {
        "en": "Run cortex on all images",
        "zh": "在所有图像上运行 Cortex",
    },
    # --- Primitive tools --------------------------------------------------
    "group.primitive_tools": {"en": "Primitive Tools", "zh": "基元工具"},
    "label.type": {"en": "Type:", "zh": "类型："},
    "placeholder.optional_name": {"en": "Optional name", "zh": "可选名称"},
    "tip.add_primitive": {
        "en": "Add primitive to selected contour segment",
        "zh": "将基元添加到选中的轮廓段",
    },
    "tip.remove_primitive": {
        "en": "Remove primitive from selected segment",
        "zh": "从选中的段移除基元",
    },
    "label.width_low": {"en": "Width low:", "zh": "宽度下限："},
    "label.high": {"en": "High:", "zh": "上限："},
    "label.derivation": {"en": "Derivation:", "zh": "推导："},
    "label.color": {"en": "Color:", "zh": "颜色："},
    "label.visibility": {"en": "Visibility:", "zh": "可见性："},
    "label.circle_fit_mode": {"en": "Circle fit mode:", "zh": "圆拟合模式："},
    "label.ransac_max_iter": {
        "en": "RANSAC max iterations:",
        "zh": "RANSAC 最大迭代次数：",
    },
    "label.ransac_distance": {
        "en": "RANSAC distance threshold:",
        "zh": "RANSAC 距离阈值：",
    },
    "label.ransac_inlier": {
        "en": "RANSAC inlier ratio early stop:",
        "zh": "RANSAC 内点比例提前停止：",
    },
    "tip.refine_resample": {
        "en": "Resample points during refinement",
        "zh": "在精修过程中重采样点",
    },
    # --- Constructed features --------------------------------------------
    "group.constructed_features": {"en": "Constructed Features", "zh": "构造特征"},
    "tip.add_coord_system": {
        "en": "Add coordinate system from selection",
        "zh": "根据所选添加坐标系",
    },
    "label.line_angle": {"en": "Line angle (\u00b0):", "zh": "线角度（°）："},
    # --- Measurements -----------------------------------------------------
    "group.measurements": {"en": "Measurements", "zh": "测量"},
    "placeholder.measurement_name": {"en": "Measurement name", "zh": "测量名称"},
    "label.coordinate_system": {"en": "Coordinate system:", "zh": "坐标系："},
    "tip.coord_system_combo": {
        "en": "Coordinate system for this measurement",
        "zh": "此测量使用的坐标系",
    },
    "label.plot_visibility": {"en": "Plot visibility:", "zh": "绘图可见性："},
    "tip.invert_angle_dir0": {"en": "Invert first direction", "zh": "反转第一个方向"},
    "tip.invert_angle_dir1": {"en": "Invert second direction", "zh": "反转第二个方向"},
    "label.distance_mode_blob": {
        "en": "Distance mode (blob):",
        "zh": "距离模式（blob）：",
    },
    "label.font_size": {"en": "Font size:", "zh": "字体大小："},
    "label.offset_x": {"en": "Offset X:", "zh": "偏移 X："},
    "label.offset_y": {"en": "Offset Y:", "zh": "偏移 Y："},
    # --- Thresholds -------------------------------------------------------
    "group.thresholds": {"en": "Thresholds", "zh": "阈值"},
    "tip.save_result": {"en": "Save measurement results", "zh": "保存测量结果"},
    # --- Images bar -------------------------------------------------------
    "tip.add_images": {"en": "Add images", "zh": "添加图像"},
    "tip.delete_item": {"en": "Delete item", "zh": "删除项"},
    "btn.create_new": {"en": "Create new...", "zh": "新建..."},
    "btn.open_ellipsis": {"en": "Open...", "zh": "打开..."},
    "tip.calibration_combo": {
        "en": "Calibrations from project folder (*_calibration.json) and PC config",
        "zh": "来自项目文件夹（*_calibration.json）和 PC 配置的标定",
    },
    # --- Region Tools: Auto tab, Manual tab, Cortex pages -----------------
    "hint.regions_auto": {
        "en": "- Shift + click and drag to draw ROI box\n- Shift + click to add positive point\n- Shift + Ctrl + click to add negative point",
        "zh": "- Shift + 点击并拖动绘制 ROI 框\n- Shift + 点击添加正向点\n- Shift + Ctrl + 点击添加负向点",
    },
    "hint.regions_manual": {
        "en": "- Shift + click to add segment point\n- Shift + click the starting point to complete contour",
        "zh": "- Shift + 点击添加段点\n- Shift + 点击起点以闭合轮廓",
    },
    "btn.rerun": {"en": "Rerun", "zh": "重新运行"},
    "btn.reset": {"en": "Reset", "zh": "重置"},
    "btn.autolabel_dataset": {"en": "Autolabel dataset", "zh": "自动标注数据集"},
    "btn.add_items": {"en": "Add item(s)", "zh": "添加项"},
    "btn.select_all": {"en": "Select all", "zh": "全选"},
    "btn.deselect_all": {"en": "Deselect all", "zh": "取消全选"},
    "btn.run_segmentation": {"en": "Run segmentation", "zh": "运行分割"},
    "btn.run_on_all": {"en": "Run on all", "zh": "在全部运行"},
    "tip.manual_reset": {
        "en": "Clear mask and manual polygon for current item/image",
        "zh": "清除当前项/图像的掩膜和手动多边形",
    },
    "btn.run_breakdown": {"en": "Run breakdown", "zh": "运行分解"},
    "tip.run_breakdown_golden": {
        "en": "Run contour breakdown on golden part for selected item",
        "zh": "在黄金件上对选中的项运行轮廓分解",
    },
    "btn.expert_settings": {"en": "Expert settings", "zh": "专家设置"},
    "btn.fit_circles": {"en": "Fit circles", "zh": "拟合圆"},
    "btn.add": {"en": "Add", "zh": "添加"},
    "btn.update": {"en": "Update", "zh": "更新"},
    "btn.remove": {"en": "Remove", "zh": "移除"},
    "btn.delete": {"en": "Delete", "zh": "删除"},
    "btn.cancel": {"en": "Cancel", "zh": "取消"},
    "btn.apply": {"en": "Apply", "zh": "应用"},
    "btn.save": {"en": "Save", "zh": "保存"},
    "btn.save_result": {"en": "Save result", "zh": "保存结果"},
    "btn.benchmark": {"en": "Benchmark", "zh": "基准测试"},
    "btn.export_thresholds_csv": {"en": "Export CSV", "zh": "导出 CSV"},
    "msg.export_thresholds_csv.title": {"en": "Export CSV", "zh": "导出 CSV"},
    "msg.export_thresholds_csv.empty": {
        "en": "The thresholds table has no rows to export.",
        "zh": "阈值表没有可导出的行。",
    },
    "msg.export_thresholds_csv.saved": {
        "en": "Wrote thresholds table to:\n{path}",
        "zh": "已将阈值表写入：\n{path}",
    },
    "msg.export_thresholds_csv.error_title": {"en": "Export failed", "zh": "导出失败"},
    "msg.export_thresholds_csv.error_body": {
        "en": "Could not write {path}:\n{error}",
        "zh": "无法写入 {path}：\n{error}",
    },
    "tip.save_inspection_results": {
        "en": (
            "For each image: save inspection plot (.png) and full result "
            "(.json) under project/result/"
        ),
        "zh": "为每张图像：在 project/result/ 下保存检测图 (.png) 和完整结果 (.json)",
    },
    "label.data_hierarchy": {"en": "Data Hierarchy", "zh": "数据层级"},
    # Contour breakdown expert
    "check.use_desired_count": {"en": "Use desired count:", "zh": "使用期望数量："},
    # Primitive edit expert
    "check.resample_contour": {
        "en": "Resample contour for refine",
        "zh": "重采样轮廓用于精修",
    },
    "check.do_refine": {"en": "Do refine", "zh": "执行精修"},
    "check.flip": {"en": "Flip", "zh": "翻转"},
    "btn.remove_primitive": {"en": "Remove primitive", "zh": "移除基元"},
    # Constructed features buttons
    "btn.add_coord_system": {"en": "Add coordinate system", "zh": "添加坐标系"},
    "btn.remove_coord_system": {"en": "Remove coordinate system", "zh": "移除坐标系"},
    "check.visible": {"en": "Visible", "zh": "可见"},
    "check.flip_x": {"en": "Flip X", "zh": "翻转 X"},
    "check.flip_z": {"en": "Flip Z", "zh": "翻转 Z"},
    "btn.add_center_point": {"en": "Add Center point", "zh": "添加中心点"},
    "btn.remove_center_point": {"en": "Remove Center point", "zh": "移除中心点"},
    "btn.add_point": {"en": "Add point", "zh": "添加点"},
    "btn.remove_point": {"en": "Remove point", "zh": "移除点"},
    "btn.add_line": {"en": "Add line", "zh": "添加线"},
    "btn.remove_line": {"en": "Remove line", "zh": "移除线"},
    # Measurements buttons
    "btn.add_position": {"en": "Add Position", "zh": "添加位置"},
    "btn.remove_position": {"en": "Remove Position", "zh": "移除位置"},
    "btn.add_distance": {"en": "Add Distance", "zh": "添加距离"},
    "btn.remove_distance": {"en": "Remove Distance", "zh": "移除距离"},
    "btn.add_angle": {"en": "Add Angle", "zh": "添加角度"},
    "btn.remove_angle": {"en": "Remove Angle", "zh": "移除角度"},
    "btn.add_radius": {"en": "Add Radius", "zh": "添加半径"},
    "btn.remove_radius": {"en": "Remove Radius", "zh": "移除半径"},
    "btn.invert_dir0": {"en": "Invert Direction 0", "zh": "反转方向 0"},
    "btn.invert_dir1": {"en": "Invert Direction 1", "zh": "反转方向 1"},
    "tree.items": {"en": "Items", "zh": "项"},
    "tree.constructed_features": {"en": "Constructed Features", "zh": "构造特征"},
    "tree.measurements": {"en": "Measurements", "zh": "测量"},
    "tip.delete_selected": {
        "en": "Delete selected item or primitive",
        "zh": "删除选中的项或基元",
    },
    "tip.add_item_plus": {"en": "Add item", "zh": "添加项"},
    "dlg.autolabel_progress": {"en": "Autolabel dataset", "zh": "自动标注数据集"},
    "dlg.run_all_progress": {"en": "Run all", "zh": "在全部运行"},
    "btn.add_primitive": {"en": "Add primitive", "zh": "添加基元"},
    "combo.select_pos_meas": {
        "en": "Select a position measurement",
        "zh": "选择位置测量",
    },
    "combo.camera": {"en": "Camera", "zh": "相机"},
    "btn.new_ellipsis": {"en": "New...", "zh": "新建..."},
    # --- Benchmark dialog ------------------------------------------------
    "dlg.benchmark.title": {"en": "Benchmark", "zh": "基准测试"},
    "btn.run_benchmark": {"en": "Run Benchmark", "zh": "运行基准测试"},
    "btn.close": {"en": "Close", "zh": "关闭"},
    "status.click_run": {"en": "Click Run to start.", "zh": "点击“运行”开始。"},
    "status.no_masks": {
        "en": "No images with complete masks.",
        "zh": "没有带完整掩膜的图像。",
    },
    "status.running": {"en": "Running benchmark...", "zh": "正在运行基准测试..."},
    "status.no_images_processed": {
        "en": "No images could be processed.",
        "zh": "没有可处理的图像。",
    },
    "check.cortex_bypass": {
        "en": "Cortex: bypass cache (measure every image)",
        "zh": "Cortex：绕过缓存（测量每张图像）",
    },
    "tip.cortex_bypass": {
        "en": "When checked, Cortex inference runs on every image (no cache). Use to measure Cortex timing when cortex items exist.",
        "zh": "勾选后，Cortex 推理在每张图像上运行（不使用缓存）。存在 Cortex 项时用于测量耗时。",
    },
    "check.fixed_count": {
        "en": "Use fixed number of images",
        "zh": "使用固定数量的图像",
    },
    "tip.fixed_count": {
        "en": "Run a fixed number of iterations instead of once per image. Images cycle if the count exceeds the project image count.",
        "zh": "运行固定次数的迭代，而不是每张图像一次。若次数超过项目图像数，图像将循环使用。",
    },
    "bench.col.phase": {"en": "Phase", "zh": "阶段"},
    "bench.col.mean": {"en": "Mean (ms)", "zh": "平均值 (ms)"},
    "bench.col.std": {"en": "Std (ms)", "zh": "标准差 (ms)"},
    "bench.col.min": {"en": "Min (ms)", "zh": "最小值 (ms)"},
    "bench.col.max": {"en": "Max (ms)", "zh": "最大值 (ms)"},
    "bench.col.first": {"en": "First (ms)", "zh": "首次 (ms)"},
    # --- Dynamic help labels in tools panels -----------------------------
    "help.contours_switch_golden": {
        "en": "Switch to golden part to adjust contours.",
        "zh": "切换到黄金件以调整轮廓。",
    },
    "help.contours_click_adjust": {
        "en": "Click to select and adjust contour.",
        "zh": "点击以选择并调整轮廓。",
    },
    "help.multi_select": {
        "en": "Click to select, shift + click to select multiple.\nOptions show up based on selection.",
        "zh": "点击选择，Shift + 点击多选。\n选项根据选择动态显示。",
    },
    "help.primitive_click": {
        "en": "Click segment to select. Add or update primitive.",
        "zh": "点击段以选择。添加或更新基元。",
    },
    "btn.update_primitive": {"en": "Update primitive", "zh": "更新基元"},
    "tip.coord_system_add": {
        "en": "Origin + line or 2 points (origin, point on x-axis)",
        "zh": "原点 + 线，或 2 个点（原点、x 轴上的点）",
    },
    "tip.calibration_required": {"en": "Calibration required", "zh": "需要标定"},
    "label.network_class": {
        "en": "Network: {network}\nClass: {cls}",
        "zh": "网络：{network}\n类别：{cls}",
    },
}


def help_sections() -> list[tuple[str, str, list["_HelpChild"]]]:
    """Nested help content: [(key, title, [(sub_key, title, [(leaf_key, body)]) | (leaf_key, body)])].

    Top-level entries are (key, title, children). Children may be either a
    nested section (3-tuple) or a leaf body (2-tuple). Consumed by the help
    dialog, which renders a collapsible tree.
    """
    return [
        ("setup", tr("help.setup.title"), [("setup_body", tr("help.setup.body"))]),
        (
            "regions",
            tr("help.regions.title"),
            [
                ("regions_body", tr("help.regions.body")),
                (
                    "regions_auto",
                    tr("help.regions_auto.title"),
                    [
                        ("regions_auto_body", tr("help.regions_auto.body")),
                    ],
                ),
                (
                    "regions_manual",
                    tr("help.regions_manual.title"),
                    [
                        ("regions_manual_body", tr("help.regions_manual.body")),
                    ],
                ),
                (
                    "regions_cortex",
                    tr("help.regions_cortex.title"),
                    [
                        ("regions_cortex_body", tr("help.regions_cortex.body")),
                    ],
                ),
            ],
        ),
        (
            "contours",
            tr("help.contours.title"),
            [
                ("contours_body", tr("help.contours.body")),
            ],
        ),
        (
            "primitives",
            tr("help.primitives.title"),
            [
                ("primitives_body", tr("help.primitives.body")),
            ],
        ),
        (
            "cf",
            tr("help.cf.title"),
            [
                ("cf_body", tr("help.cf.body")),
            ],
        ),
        (
            "meas",
            tr("help.meas.title"),
            [
                ("meas_body", tr("help.meas.body")),
            ],
        ),
        (
            "thresholds",
            tr("help.thresholds.title"),
            [
                ("thresholds_body", tr("help.thresholds.body")),
            ],
        ),
    ]


_HelpChild = Any


def keybind_sections() -> list[tuple[str, list[tuple[str, str]]]]:
    """Keybinds dialog content: [(section_title, [(shortcut_display, action_text)])]."""
    return [
        (
            tr("kb.section.help"),
            [
                ("F1", tr("kb.help.menu")),
                ("Ctrl+K", tr("kb.help.shortcuts")),
                ("Ctrl+I", tr("kb.help.contextual")),
                ("Ctrl+L", tr("kb.help.language")),
            ],
        ),
        (
            tr("kb.section.file"),
            [
                ("Ctrl+O", tr("kb.file.open")),
                ("Ctrl+N", tr("kb.file.new")),
                ("Ctrl+S", tr("kb.file.save")),
                ("Ctrl+Shift+S", tr("kb.file.save_as")),
            ],
        ),
        (
            tr("kb.section.navigation"),
            [
                ("F  /  Ctrl+0", tr("kb.nav.fit")),
                ("Ctrl++ / Ctrl+=", tr("kb.nav.zoom_in")),
                ("Ctrl+-", tr("kb.nav.zoom_out")),
                ("Ctrl+Shift+1", tr("kb.nav.zoom_reset")),
                ("[", tr("kb.nav.prev_image")),
                ("]", tr("kb.nav.next_image")),
                ("Ctrl+[", tr("kb.nav.golden")),
            ],
        ),
        (
            tr("kb.section.tabs"),
            [
                ("Ctrl+1", tr("tab.setup")),
                ("Ctrl+2", tr("tab.regions")),
                ("Ctrl+3", tr("tab.contours")),
                ("Ctrl+4", tr("tab.primitives")),
                ("Ctrl+5", tr("tab.constructed_features")),
                ("Ctrl+6", tr("tab.measurements")),
                ("Ctrl+7", tr("tab.thresholds")),
            ],
        ),
        (
            tr("kb.section.items"),
            [
                ("1 - 9", tr("kb.items.select")),
                ("0", tr("kb.items.add")),
                ("Shift+0", tr("kb.items.add_cortex")),
                ("F2", tr("kb.items.rename")),
            ],
        ),
        (
            tr("kb.section.multiview"),
            [
                ("Alt+1 - Alt+4", tr("kb.multiview.focus")),
                ("Cmd/Ctrl+click", tr("kb.multiview.add_nonconsec")),
                ("Shift+click", tr("kb.multiview.select_range")),
            ],
        ),
        (
            tr("kb.section.regions_annot"),
            [
                ("Shift+drag", tr("kb.regions.roi_box")),
                ("Shift+click", tr("kb.regions.positive")),
                ("Shift+Ctrl+click", tr("kb.regions.negative")),
            ],
        ),
    ]


class _Translator(QObject):
    """Holds current language, emits ``language_changed`` on switch."""

    language_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._lang: str | None = None
        # Each entry: (setter, key, fmt). We catch RuntimeError when a bound
        # method's C++ Qt object has been deleted, and drop those entries.
        self._registry: list[tuple[Callable[[str], Any], str, dict]] = []

    def language(self) -> str:
        cached = self._lang
        if cached is not None:
            return cached
        s = QSettings()
        s.beginGroup(_SETTINGS_GROUP)
        val = s.value(_SETTINGS_KEY, LANG_EN)
        s.endGroup()
        val_str = str(val) if val is not None else LANG_EN
        resolved = val_str if val_str in LANGUAGES else LANG_EN
        self._lang = resolved
        return resolved

    def set_language(self, lang: str) -> None:
        if lang not in LANGUAGES:
            return
        if lang == self.language():
            if _DEBUG:
                print(
                    f"[translations] set_language: no change ({lang})", file=sys.stderr
                )
            return
        s = QSettings()
        s.beginGroup(_SETTINGS_GROUP)
        s.setValue(_SETTINGS_KEY, lang)
        s.endGroup()
        self._lang = lang
        if _DEBUG:
            print(
                f"[translations] set_language: applying {lang}, "
                f"registry={len(self._registry)} entries",
                file=sys.stderr,
            )
        live: list[tuple[Callable[[str], Any], str, dict]] = []
        applied = 0
        for setter, key, fmt in self._registry:
            try:
                setter(self.translate(key, **fmt))
            except RuntimeError:
                # Underlying C++ Qt widget was deleted; drop the registration.
                continue
            live.append((setter, key, fmt))
            applied += 1
        self._registry = live
        if _DEBUG:
            print(f"[translations] applied {applied} setters", file=sys.stderr)
        self.language_changed.emit()
        # Force repaint of every top-level widget so menubars / custom title
        # bars pick up the changed QAction text immediately.
        app = QApplication.instance()
        if isinstance(app, QApplication):
            for w in app.topLevelWidgets():
                try:
                    w.update()
                except RuntimeError:
                    pass
            app.processEvents()

    def translate(self, key: str, **fmt: Any) -> str:
        entry = STRINGS.get(key)
        if entry is None:
            return key.format(**fmt) if fmt else key
        text = entry.get(self._lang or self.language()) or entry.get(LANG_EN) or key
        return text.format(**fmt) if fmt else text

    def register(self, setter: Callable[[str], Any], key: str, **fmt: Any) -> None:
        setter(self.translate(key, **fmt))
        self._registry.append((setter, key, fmt))


_translator = _Translator()


def tr(key: str, **fmt: Any) -> str:
    return _translator.translate(key, **fmt)


def register(setter: Callable[[str], Any], key: str, **fmt: Any) -> None:
    _translator.register(setter, key, **fmt)


def get_language() -> str:
    return _translator.language()


def set_language(lang: str) -> None:
    _translator.set_language(lang)


def language_changed_signal() -> SignalInstance:
    return _translator.language_changed


def _audit() -> int:
    """Print any missing translations or unreferenced keys.

    Returns exit code.
    """
    problems = 0
    for key, entry in STRINGS.items():
        for lang in (LANG_EN, LANG_ZH):
            if not entry.get(lang):
                print(f"MISSING [{lang}]: {key}")
                problems += 1

    ui_root = pathlib.Path(__file__).parent
    pat = re.compile(r'tr\(\s*["\']([^"\']+)["\']')
    referenced: set[str] = set()
    for py in ui_root.rglob("*.py"):
        if py.name == "translations.py":
            continue
        for m in pat.finditer(py.read_text(encoding="utf-8")):
            referenced.add(m.group(1))
    for key in sorted(referenced):
        if key not in STRINGS:
            print(f"UNDEFINED KEY: {key}")
            problems += 1

    if problems == 0:
        print("translations audit OK")
    return 1 if problems else 0


if __name__ == "__main__":
    if "--audit" in sys.argv:
        sys.exit(_audit())
    print("Use --audit to verify translation completeness.")

