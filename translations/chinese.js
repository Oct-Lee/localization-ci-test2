const TranslationsCnst = {
  form_required: ' *',
  loading: '载入中 ...',
  loading_license_check:
    '如果一直卡在这里，您的license可能不正常。请联系 info@unitxlabs.com',
  loading_back_to_homepage: '返回首页',
  loading_back_to_last_page: '返回上一页',
  refresh: '刷新',
  no_data: '暂无数据',

  inference_time: '判定用时%s秒',

  auth_error_username_empty: '用户名不能为空',
  auth_error_password_empty: '密码不能为空',
  auth_error_with_reason: '登陆失败：',
  auth_username: '用户名',
  auth_password: '密码',
  auth_login: '登陆',

  drawer_learn_defect: '学习缺陷',
  drawer_learn_location: '学习定位',
  drawer_production_report: '产线数据',
  drawer_cosmetic_incremental: '缺陷：进阶',
  drawer_cosmetic_review_train: '缺陷：审阅：训练集',
  drawer_cosmetic_review_validate: '缺陷：审阅：验证集',
  drawer_cosmetic_train: '缺陷：训练与部署',
  drawer_cosmetic_validate: '缺陷：验证',
  drawer_cosmetic_location_incremental: '定位：进阶',
  drawer_cosmetic_location_review_train: '定位：审阅：训练集',
  drawer_cosmetic_location_review_validate: '定位：审阅：验证集',
  drawer_cosmetic_location_train: '定位：训练与部署',
  drawer_cosmetic_location_validate: '定位：验证',
  drawer_remote_config: '远程配置',
  drawer_password_management: '密码管理',

  error: '错误',
  error_contains_special_characters:
    '不能含有这些字符: ".", "/", "\\", "~", 空格',
  error_cannot_be_empty: '不能为空',
  error_must_be_number: '必须是数字',
  error_must_be_int: '必须是整数',
  error_must_be_gte_zero: '必须大于等于零',
  error_must_be_gt_zero: '必须大于0',

  nc_name: '模型名称',
  network_name_cannot_be_modified_while_training_network:
    '模型正在训练中，无法修改模型名称',
  feature_type_cannot_be_modified: '特征类型不能被修改',
  nc_preprocess_crop_start_x: '切割 X 起始(像素)',
  nc_preprocess_crop_start_y: '切割 Y 起始(像素)',
  nc_preprocess_crop_end_x: '切割 X 终止(像素)',
  nc_preprocess_crop_end_y: '切割 Y 终止(像素)',
  nc_resize_width: '缩放 X (像素)',
  nc_resize_height: '缩放 Y (像素)',
  nc_success_save: '成功！保存了算法设置',
  nc_status_train: '上次训练完成时间:',
  nc_status_suggestion: '预计建议完成时间:',
  nc_status_train_model_not_exist: '训练模型不存在。训练一次就能看到。',
  nc_status_deploy: '已部署的模型版本：',
  nc_status_deploy_outdated: '训练了更新的模型，重新部署来使用最新的模型。',
  nc_status_deploy_model_not_exist: '生产模型不存在。部署一次就能看到。',
  nc_status_deploy_model_success: '%s 的模型成功部署到了 %s',

  network_status_label: '%s 张照片',
  network_status_label_location_train_set:
    '训练集: %s 张照片。验证集: %s 张照片。',
  network_status_label_defect_train_set:
    '训练集: %s 张 NG 照片。%s 张 OK 照片。验证集: %s 张 NG 照片。%s 张 OK 照片。',
  network_status_pre_process:
    'x起始: %s, x终止: %s, y起始: %s, y终止: %s, 缩放宽: %s, 缩放高: %s',
  network_status_post_process: '%s 阈值规则',
  network_status_validate: '%s 验证照片',
  network_config_tip: '在Central中配置模型方案并部署到ProdX运行',
  image_import_failed: '导入图片失败',
  image_import_zero_images: '没有导入任何照片。请确认文件夹里确实有照片存在',
  image_import_success_n_images: '成功！导入了 $N_IMAGE 张照片',
  image_import_duplicate_n_images: '$N_IMAGE 张照片为重复。没有导入这些照片。',

  deploy_confirmation_defect_name_discrepancy_head:
    '警告：检测到所选模型版本与已部署版本之间的缺陷名称不一致：',
  deploy_confirmation_defect_name_discrepancy_new: '- 新增: %s',
  deploy_confirmation_defect_name_discrepancy_removed: '- 删除: %s',
  deploy_confirmation_defect_name_discrepancy_recommendation_main:
    '建议前往生产数据页面，检查或更新该缺陷的阈值设置，然后将模型与阈值一起部署。',
  deploy_confirmation_defect_name_discrepancy_recommendation_renaming:
    '- 如果您已更新缺陷名称，请记住删除使用先前缺陷名称的阈值，并使用新名称重新创建它们。',
  deploy_confirmation_defect_name_discrepancy_recommendation_deletion:
    '- 如果您正在删除缺陷，请不要忘记删除相关的阈值。',
  deploy_confirmation_defect_name_discrepancy_confirm: '您要取消此部署吗？',
  deploy_confirmation_defect_name_discrepancy_cancel: '是的，取消部署',
  deploy_confirmation_defect_name_discrepancy_continue: '不，仍然继续部署',

  deploy_trainstatus: '训练状态：',
  deploy_numok: '已标签OK数：',
  deploy_numng: '已标签NG数：',
  deploy_trainscratch: '从零训练',
  deploy_deployprod: '部署模型 与 阈值',
  deploy_validate_model: '验证模型',
  deploy_validate_validating: '验证中',
  export_validation_result: '下载验证结果',
  export_validation_success: '下载成功！',

  deploy_imagelevelfr: '误判率（照片）',
  deploy_goodimagesfailed: '误判照片',
  deploy_partlevelfr: '误判率（物料）',
  deploy_goodpartsfailed: '误判物料',
  deploy_partlevelfa: '漏判率（物料）',
  deploy_badpartsaccepted: '漏判物料',

  deploy_train: '训练',
  deploy_network_validation_results: '验证结果',
  deploy_validate: '验证',
  deploy_post_process: '后处理阈值',
  deploy_deploy: '部署',
  deploy_train_setting: '训练设置',

  incremental_label_shape: '标签类型',
  incremental_cancel: '取消',
  incremental_instructions: '标签说明：',
  incremental_addnode: '添加节点：键盘D键，或鼠标左键',
  incremental_label_undo: '撤销：键盘Z键',
  incremental_endshape: '完成图形：键盘S键，或鼠标右键',
  incremental_remove: '删除：鼠标右键点击',
  incremental_switch_suggestion: '切换显示/隐藏建议：键盘F键',
  incremental_remove_shape: '删除图形：鼠标右键点击图形内',
  incremental_currentlabels: '已有标签',
  incremental_nextlabeltype: '选择当前标签种类',
  incremental_save: '保存标签',
  incremental_discard: '丢弃',
  incremental_showmask: '判定图案/标签',
  incremental_trainset: '标签',
  incremental_trainset_with_inference_result: '标签（使用判定结果）',
  incremental_trainset_with_inference_result_confirm:
    '使用判定结果标签会删除已有标签，确认继续吗？',
  incremental_trainset_with_inference_result_no_classification_type:
    '判定结果包含了不存在的缺陷种类，请重新训练模型。',
  incremental_capture: '采像下一个物料',
  incremental_labelareyousure: '标签还未存储，确认继续吗？',
  incremental_labelareyousure_save: '标签还未存储，确认要保存吗？',
  incremental_successdiscard: '丢弃：',
  incremental_faildiscard: '无法丢弃照片：',
  incremental_successsave: '保存：',
  incremental_failsave: '无法保存照片：',
  incremental_success_remove_label: '删除标签：',
  incremental_stilleditingshape:
    '目前正在编辑一个标签，这个标签不会被保存。确认要继续吗？',
  incremental_confirm_ok_has_polygons:
    '确认要保存为 OK 吗？这会删除该照片中的 NG 标签',
  incremental_label_icon_point: '点',
  incremental_label_icon_line_segment: '线段',
  incremental_label_icon_circle: '圆',
  incremental_label_icon_polygon: '多边形',
  incremental_label_icon_magic_brush: '魔术棒',
  incremental_label_icon_auto_label: '智能标注',
  incremental_label_auto_label_warning:
    '警告：当前的点击创建了多个分离的标注。添加新的点击将影响所有未完成的标注。',
  incremental_label_auto_label_out_of_bounds_warning:
    '警告: 当前的点击超出了图像范围',
  auto_label_switch_while_training_error:
    '警告：当前有模型正在训练，请等待模型训练结束后再使用智能标注',
  incremental_label_toggle_tool_defect: '切换工具：多边形：1，智能标注：2',
  incremental_label_toggle_tool_features: '切换工具：点：1，线段：2，圆：3',
  incremental_label_toggle_subtract: '切换添加/抹去标签：键盘X键',
  incremental_start_magic_brush: '魔术棒开始：键盘D键，或按住鼠标左键',
  incremental_end_magic_brush: '魔术棒结束：键盘D键，或松开鼠标左键',
  incremental_auto_label_additive_point: '添加正采样点：鼠标左键',
  incremental_auto_label_additive_info:
    '- 让智能标注模型选取该采样点以及相似区域',
  incremental_auto_label_subtractive_point: '添加负采样点：鼠标右键',
  incremental_auto_label_subtractive_info:
    '- 让智能标注模型排除该采样点以及相似区域',
  incremental_auto_label_finish: '完成图形： 键盘S键',
  incremental_remove_shape_ng_picker: '删除标签',
  incremental_show_labels: '标签',
  incremental_show_suggestions: '显示智能标注建议',
  incremental_subtract_off: '添加标签',
  incremental_subtract_on: '抹去标签',
  incremental_discard_all_confirm: '这会丢弃所有没有标签的照片，确定吗？',
  incremental_val_image: '验证集',
  incremental_error_prefix: '错误',
  incremental_label_tab_label_guide: '标注指南',
  incremental_empty_label_info: '没有标注',

  validate_showmask: '显示判定图案/标签',
  validate_mask_type_prediction: '判定图案',
  validate_mask_type_label: '标签',
  validate_reviewbutton: '显示标签',
  validate_removebutton: '删除',
  validate_removefail: '错误：无法删除照片',
  validate_trainset: '标签',
  validate_trainset_with_inference_result: '标签（使用判定结果）',

  reviewv2_noimages: '没有标签过的照片',
  reviewv2_instructions: '按删除标签，该照片会回到进阶标签中去',
  reviewv2_removebutton: '删除标签',
  reviewv2_removeconfimation: '照片已删除', // failback alert when we cant remove item from filesrvc sidebar
  reviewv2_removefail: '错误：无法删除照片',
  reviewv2_train_to_validation: '移到验证集',
  reviewv2_validation_to_train: '移到训练集',
  reviewv2_train_to_validation_tooltips: '生成图片无法添加到验证集',
  reviewv2_image_moved_to_validation: '照片已移动到验证集。',
  reviewv2_image_moved_to_training: '照片已移动到训练集。',

  topbar_logout: '登出',
  topbar_quit: '退出',
  topbar_cannot_exit: '无法退出: ',

  tstatus_setupdir: '初始化训练文件',
  tstatus_training: '训练中',
  tstatus_donetraining: '从零训练完成',
  tstatus_failed: '训练报错：',
  tstatus_inctraining: '进阶训练',
  tstatus_doneinctraining: '进阶训练完成',
  tstatus_train_failed: '训练失败',

  incremental_imbalancedwarning:
    'OK/NG数量不均匀：OK照片数为OKCOUNT张，NG照片数为NGCOUNT张',
  filesidebar_search: '搜索',
  filesidebar_filter: '过滤',
  filesidebar_sort: '排序',
  filesidebar_sort_name: '文件名称',
  filesidebar_sort_import_time: '导入时间',
  filesidebar_discard_all: '丢弃所有没有标签的照片',
  filesidebar_view_all: '所有标签',
  filesidebar_real_image: '原图',
  filesidebar_filter_options: '过滤项',
  filesidebar_training_dataset_filter: '训练集过滤器',
  filesidebar_image_type: '照片类型',
  part_statistics_add_false_detection_type_inaccurate_detection: '不精确检测',
  filesidebar_real_image: '原图',
  filesidebar_asc: '升序',
  filesidebar_desc: '降序',
  image_okng_after_px_thresh: '照片',

  training_dataset_filter_name: '训练集过滤器名称',
  training_dataset_filter_application: '应用过滤器',
  training_dataset_filter_save: '保存过滤器',
  training_dataset_filter_option_add: '添加过滤选项',
  filter_option_image_source_placeholder: '请选择图片来源',
  filter_option_part_type_placeholder: '请选择物料类型',
  filter_option_view_placeholder: '请选择视图',
  filter_option_cc_placeholder: '请选择CC',
  filter_option_add: '添加筛选条件',
  filter_option_add_failed: '添加筛选条件失败',
  filter_option: '筛选条件',
  no_image_alert: '请导入照片',
  no_label_alert: '无标签照片',

  post_proc_not_set: '未设置',

  type_create: '新建',
  type_export: '导出',
  type_import: '导入',

  ng_search_bar_placeholder: '搜索 NG 名称',
  ng_create_create: '新建 NG 种类',
  ng_current_types: '当前 NG 种类',
  ng_current_add: '添加 NG 种类',
  ng_manage: '管理 NG 种类',
  ng_create_name: '名称',
  ng_edit_update: '保存NG种类',
  ng_edit_delete: '删除NG种类',
  ng_edit_delete_confirm:
    '警告：删除此 NG 类型将自动删除所有相关标签，但您需要在所有机器上的生产数据页面中删除使用此 NG 类型的阈值。您确定吗？',
  ng_edit_renaming_and_deleting_confirm_header: '警告：关于更改标签名称：',
  ng_edit_renaming_and_deleting_confirm_body_train_and_redeploy:
    '要使新名称生效，必须从头开始重新训练模型并重新部署。在重新训练和重新部署之前执行的任何涉及该缺陷类型的操作（例如添加新阈值）可能会导致异常状态。',
  ng_edit_renaming_and_deleting_confirm_body_selecting_old_versions:
    '回退部署旧版本的模型也可能导致新设置的阈值失效。',
  ng_edit_renaming_and_deleting_confirm_confirm:
    '您是否了解这些风险并希望保存更改？',
  ng_color: '颜色',

  location_search_bar_placeholder: '搜索定位名称',
  location_current_types: '当前定位种类',
  location_type_add: '添加定位种类',
  location_type_manage: '管理位置类型',
  location_type_create_create: '新建定位种类',
  location_type_edit_update: '保存定位种类',
  location_type_edit_delete: '删除定位种类',
  location_type_create_name: '名称',
  location_type_delete_confirm:
    '删除这个定位种类，会删除所有相关的标签。确定吗？',
  location_type_edit_confirm:
    '将要更改这个定位种类。需要从零训练，更改才会生效。',

  nc_update: '保存算法设置',
  nc_edit: '编辑算法设置',
  show_original_network_config_datasets: '显示已保存特征数据集',
  nc_create: '新建算法设置',
  nc_edit_differ_confirm:
    '检测到特征映射变更，将保留原算法设置，自动创建新的算法设置，确定更改吗？',

  pre_proc_explanations: '解释',
  pre_proc_save: '存储预处理',
  pre_proc_edit_confirm: '将要更改这个预处理设置。需要从零训练，更改才会生效。',
  pre_proc_cancel_confirm: '有预处理的改动没有保存，确定取消吗？',
  pre_proc_over_res_limit: '缩放 X * Y 不能超过',

  network_defect_network: '缺陷算法',
  network_location_network: '定位算法',
  network_manage_ct: '管理 NG 种类',
  network_manage_location_type: '管理定位种类',
  network_create: '新建',
  network_auto_create: '自动创建',
  network_auto_created_cc_not_selected: '请选择一个采集配置(CC)',
  network_auto_create_skipped: '跳过自动创建模型：1. 该采集配置的特征映射可能已存在于某个网络中。 2. 所选CC可能没有带标签的特征图像。',
  network_auto_create_skipped_no_cc: '跳过自动创建模型：没有采集配置(CC) 用于该物料类型',
  network_manual_create: '创建模型',
  network_failed_to_create: '创建网络失败：',
  network_unexpected_error: '创建网络时发生意外错误。请再试一次。',
  network_deploy: '部署',
  network_import_image: '导入图像',
  network_edit: '设置',
  network_clone: '复制',
  network_merge: '合并标签',
  network_import: '导入模型',
  network_export: '导出',
  network_delete: '删除',
  nc_confirm_delete: '这将删除模型。你确认吗？',
  nc_confirm_double_delete: '这将删除你之前训练的模型。你真的确认吗？',
  netwrok_to_be_merged: '被合并标签的模型',
  network_list: '模型列表',
  network_please_select: '请选择',
  network_image_size: '图片尺寸',
  network_ng_types: 'NG 类型',
  network_location_types: '定位种类',
  network_label_select_all: '全选',
  network_current: '当前模型',
  network_name: '模型名称',
  network_crop_size: '裁剪尺寸',
  network_label: '标签',
  network_review_train: '审阅标签',
  network_pre_process: '预处理',
  network_train_from_scratch_confirm:
    '从头训练会覆盖之前训练的模型，你确认吗？',
  network_train_from_scratch: '从头训练',
  network_train_incremental_confirm:
    '进阶训练适合学习新加入的照片。如果更改了之前照片的标签，需要从头训练。确认开始进阶训练吗？',
  network_train_incremental: '进阶训练',
  network_train_with_label_scoring: '咨询AI获得标注建议',
  network_cancel_train: '取消训练',
  network_train_remove: '确认取消训练吗？',
  network_add_dataset_button: '添加数据集',
  network_validate: '验证',
  network_post_process: '后处理',
  network_train_error_backtest_running: '正在跑模型模拟，无法训练',
  network_train_error_production_running: '训练模型之前必须把跑机软件关闭',
  network_table_list_title: 'CC 模型列表',
  canvas_error_no_empty_type: 'NG 种类不能为空',

  validate_confusion_matrix_header: '混淆矩阵',
  validate_confusion_matrix_label_header: '照片标签',
  validate_classification_type_table_header: '交并比表',
  validate_classification_type_table_ng_header: 'NG 种类',
  validate_classification_type_table_iou_header: '交并比',
  validate_confusion_matrix_archived_feature_error:
    '此功能已存档。请恢复它以查看该数据集的验证结果。',

  validate_location_point: '点',
  validate_location_line: '线',
  validate_location_circle: '圆',
  validate_location_number_matrix_location_type: '定位种类',
  validate_location_number_matching_table: '的数量匹配表',
  validate_location_number_matrix_match: '数量符合标签',
  validate_location_number_matrix_not_match: '数量不符合标签',
  validate_location_point_distance_table: '点的位置误差（距离）表',
  validate_location_line_distance_table: '线端点的位置误差（距离）表',
  validate_location_circle_distance_table:
    '圆心的位置误差（距离）表，圆半径长度的误差表',
  validate_location_point_distance_x_axis_label: '判定vs标签: 点平均距离',
  validate_location_line_distance_x_axis_label: '判定vs标签: 线端点平均距离',
  validate_location_circle_center_distance_x_axis_label:
    '判定vs标签: 圆心平均距离',
  validate_location_circle_radius_distance_x_axis_label:
    '判定vs标签: 圆半径平均误差',
  validate_location_distance_y_axis_label: '照片数量',

  location_post_process_settings_point_order: '点排序规则',
  location_post_process_settings_none: '无',
  location_post_process_settings_point_order_x: 'X 轴',
  location_post_process_settings_point_order_y: 'Y 轴',
  location_post_process_settings_point_order_rz: 'Rz 轴',
  location_post_process_settings_not_set: '未设置',

  location_stats_points: '点',
  location_stats_lines: '线',
  location_stats_circles: '圆',
  location_stats_circle_center: '圆心',
  location_stats_circle_radius: '半径',

  average: '平均值',
  standard_deviation: '标准差',

  production_report_false_detection_correct: '正确',
  production_report_false_detection_fr: '过杀',
  production_report_false_detection_fa: '漏杀',

  production_report_type_table: '表格',
  production_report_type_chart: '分析图',
  production_report_type_chart_total_volumn: '总产量',
  production_report_type_chart_defect_breakdown: '缺陷分类',
  shift_overview_table_title_overview_table: '物料汇总表',
  shift_overview_table_title_ng_table: 'NG分类表',
  shift_overview_table_title_limit_table: 'LIMIT分类表',
  shift_overview_table_info_title_ng_table: 'NG分类表',
  shift_overview_table_info_title_limit_table: 'LIMIT分类表',
  shift_overview_table_info_body_ng_table:
    '表格内数值为所属日期的物料中包含某种NG类别的物料个数，以及占当天总物料数的百分比。这些物料应判定为NG（特殊的后处理逻辑除外）。',
  shift_overview_table_info_body_limit_table:
    '表格内数值为所属日期的物料中包含某种LIMIT类别的物料个数，以及占总物料数的百分比。这些物料应判定为NG或LIMIT（特殊的后处理逻辑除外）。',
  shift_overview_table_total: '总数',
  shift_overview_table_sum: '汇总',
  shift_overview_table_human_ng: '人NG',
  shift_overview_table_human_ok: '人OK',
  shift_overview_table_human_ng_auto_ok: '人NG，机器OK',
  shift_overview_table_human_ok_auto_prefix: '人OK，机器',
  shift_overview_table_auto_prefix: '机器',
  shift_view_images_warning:
    '只有保存了原图或者判定图案的照片会出现在这里。如果想要看到所有照片，在跑机软件里面打开保存原图或者判定图案。',
  shift_view_images_show_mask: '显示判定结果',
  shift_view_images_no_mask: '这张图片没有保存判定图案',
  shift_view_images_no_image: '这张判定图案没有保存原图',

  shift_view_false_detection: '误检',
  shift_view_false_detection_fr_select_ng_info:
    '请选择已检测出的但是期望是 OK 的 NG 类型。',
  shift_view_false_detection_fa_select_ng_info: '请选择漏检的 NG 类型。',
  shift_view_false_detection_submit: '标记误检',
  shift_view_false_detection_clear: '清空误检',

  shift_view_note: '笔记',
  shift_view_author_note_to_image: '请输入姓名',
  shift_view_note_to_image: '请输入注释',
  shift_view_add_note_to_image: '添加注释',
  shift_view_prompt_to_leave_add_note_page:
    '离开这个页面将清空未保存的图片注释，确定吗？',
  shift_view_edit_note_indicator: '编辑',
  shift_view_delete_note_indicator: '删除',
  shift_view_prompt_to_delete_image_note: '确定删除这份图片注释吗？',
  shift_view_prompt_to_edit_image_note: '请输入要编辑的内容：',
  shift_view_note_edited_tag: '(已编辑)',
  shift_view_note_last_edited_by: '最后编辑于：',
  shift_view_note_not_allow_to_edit: '只允许在产线数据页面中编辑或删除图片笔记',

  shift_view_add_image_to_train: '加入神经网路',
  shift_view_add_image_to_train_network: '神经网路',
  shift_view_add_image_to_train_initial: '照片加入了%s。',
  shift_view_add_image_to_train_keep: '照片已经在%s的训练集里。',
  shift_view_add_image_to_train_test: '照片已经在%s的验证集里。',

  shift_view_add_image_to_feature_dataset: '将图像添加到特征数据集中',
  shift_view_images_import_image_fetch_project_error: '获取项目失败，请重试。',
  shift_view_images_import_image_dialog_title: '将图像添加到特征数据集中',
  shift_view_images_import_image_dialog_select_project_tooltip:
    '仅显示网络所属且与图像相关的项目。',
  shift_view_images_import_image_dialog_select_project: '项目',
  shift_view_images_import_image_to_feature_dataset_button:
    '将图像添加到特征数据集中',
  shift_view_images_import_image_to_feature_dataset_button_disabled_tooltip:
    '必须选择一个项目、一个产品类型和至少一个特征类型才能将图像添加到特征数据集中。',
  shift_view_images_import_image_to_feature_dataset_failed: '导入图像失败。',
  shift_view_images_import_image_to_feature_dataset_success_n_images:
    '成功！已将图像导入到 $N_IMAGE 个特征数据集中。',
  shift_view_images_import_image_to_feature_dataset_duplicate_n_images:
    '图像已存在于 $N_IMAGE 个特征数据集中，未被重复导入。',

  shift_view_image_info_icon_info: '图片信息',
  shift_view_image_info_icon_download: '下载图片',
  shift_view_image_info_icon_download_button: '下载',
  shift_view_image_info_icon_download_raw: '原图',
  shift_view_image_info_icon_download_production: 'mask图',
  shift_view_image_info_image_size: '图片大小',
  shift_view_image_info_image_resolution: '分辨率',
  shift_view_image_info_image_machine: '产线机器',
  shift_view_image_info_image_networks: '模型',
  shift_view_image_info_image_capture_date: '拍照日期',
  production_report_header_production_data: '产线数据',
  production_report_header_simulation: '产线数据模拟',
  production_report_header_threshold: '阈值',
  production_report_header_export: '导出',
  production_report_header_refresh: '刷新',
  production_report_generate_pdf: '生成PDF',
  width_set_but_length_not_set: '如果设置了宽的阈值，必须也设置长的阈值',
  width_greater_than_length: '宽的阈值必须小于等于长的阈值',
  production_report_invalid_threshold: '有些模型的阈值设置有错误:',
  production_report_run_simulation_production: '模拟产线数据',
  production_report_run_simulation_false_detection: '模拟误检数据',
  production_report_simulation_deploy: '部署',
  production_report_simulation_in_progress: '模拟中',
  production_report_simulation_time_remaining: '模拟剩余时间',
  production_report_simulation_time_remaining_not_available:
    '模拟剩余时间：数据准备完成后，将提供估计时间',
  production_report_simulation_finished: '模拟完成',
  production_report_simulation_disabled_when_production_running_tooltip:
    '运行模拟前请先关闭跑机软件。如果状态在关闭后没有更新，请刷新页面',
  production_report_broken_models_deploy_tooltip:
    '这些模型选择了训练失败的版本：',
  production_report_backtest_deploy_confirm_network_and_threshold_change:
    '即将部署新训练的模型和更新的阈值，确定吗？',
  production_report_backtest_deploy_confirm_network_only_change:
    '即将部署新训练的模型，确定吗？',
  production_report_backtest_deploy_confirm_threshold_only_change:
    '即将部署更新的阈值，确定吗？',
  production_report_backtest_deploy_success: '部署成功。',
  production_report_backtest_deploy_failure: '部署失败。',
  production_report_backtest_deploy_confirmation: '你确定部署以下改动吗？',
  production_report_backtest_deploy_confirmation_when_threshold_diff_is_disabled:
    '确定部署更改吗？',

  production_report_backtest_deploy_no_changes: '没有改动需要部署',
  production_report_backtest_threshold_changes_not_deployed:
    '你还没有部署更改的阈值。确定要离开吗？',
  production_report_backtest_central_postprocessing: '用本机的后处理进行模拟.',
  production_report_export_success: '数据成功导出',
  production_report_backtest_threshold_only:
    '只用阈值模拟。如果不选，则会重新用模型做判定。',

  select_file: '选择文件',
  select_directory: '选择目录',
  select_all: '全选',

  customer_data_backup: '客户数据备份',
  customer_data_backup_success: '客户数据备份成功',
  customer_data_backup_failure: '客户数据备份失败：',
  customer_data_restore: '客户数据还原',
  customer_data_restore_warn:
    '注意：客户数据还原之后，当前数据会被覆盖，无法找回。',
  customer_data_restore_success: '客户数据还原成功，请重启 CorteX。',
  customer_data_restore_failure: '客户数据还原失败：',

  production_threshold_optimization_post_process: '后处理',
  production_threshold_optimization_before_change: '更改前:',
  production_threshold_optimization_view_image_app_name_prefix: '（模拟）',
  production_threshold_optimization_view_image_message:
    '判定图案是基于原来的阈值的。基于新阈值模拟的OK/NG可能会与判定图案不同。',
  production_threshold_optimization_px_width: '宽',
  production_threshold_optimization_px_length: '长',
  production_threshold_optimization_px_horizontal: '水平',
  production_threshold_optimization_px_vertical: '竖直',
  production_threshold_optimization_px_area: '面积',
  production_threshold_optimization_defect_count: '数量',
  production_threshold_optimization_px: '（像素）',
  production_threshold_optimization_mm: '（毫米）',
  production_threshold_optimization_header_network: '模型',
  production_threshold_optimization_header_class: '缺陷种类',

  remotes_self: '本机',
  remotes_deploy_dialog_title: '部署模型 [%s] 到产线机',
  remotes_deploy_tooltip: '部署模型',
  remotes_ungrouped: '未分组',
  remotes_deploy_disabled_tooltip:
    '这个模型只能在新版本的跑机软件里运行，请先升级产线机软件。',
  remotes_device_name_column: '机器名称',
  remotes_select_title: '所有产线机',
  remotes_disconnected: '无法连接',
  remotes_invalid_name: '无效名称',
  remotes_invalid_name_tooltip:
    '无效名称：远程名称只能包含字符 A-Z、a-z、中文字符、0-9、.、_ 和 -。',
  remotes_name_too_long: '无效名称：远程名称必须少于 63 个字符。',
  remote_name_cannot_start_end_with_special_character:
    '无效名称：远程名称不能以点、连字符或下划线开头或结尾',
  remotes_name_cannot_have_consecutive_special_character:
    '无效名称：远程名称不能具有连续的点、连字符或下划线。',
  remotes_cannot_have_empty_name: '名称字段不能为空',
  remotes_removed: '已删除',
  remotes_pack_installer: '制作离线安装包',
  remotes_installer_ready: '离线安装包已完成。位置：',

  analytics_jobs_title: '自动发送报告设置',
  analytics_date_modified: '更改日期',
  analytics_email_address: '邮箱地址(用逗号区分多个邮箱)',
  analytics_device: '机器',
  analytics_mailing_list: '邮箱',
  analytics_schedule: '发送时间',
  analytics_status: '状态',
  analytics_create: '新建',
  analytics_running: '已启用',
  analytics_paused: '已暂停',
  analytics_locale: 'zh_CN',
  analytics_deleteJob_confirmation: '确定要删除这个任务吗',
  analytics_save_job: '保存',
  analytics_cancel: '取消',
  analytics_test_send: '测试',
  analytics_testsend_success: '测试报告发送成功！',
  analytics_testsend_fail: '测试报告发送失败：',
  analytics_testsend_invalidformat: '收件人邮件地址错误.',
  analytics_testsend_timeout: '网络连接失败.',

  preprocess_error_negative_resize: '缩放长宽必须大于0',
  preprocess_error_negative_width_crop: '切割起始宽度必须小于终止宽度',
  preprocess_error_negative_height_crop: '切割起始高度必须小于终止高度',
  preprocess_error_upscale_width_crop: '缩放宽必须小于等于切割后的宽',
  preprocess_error_upscale_height_crop: '缩放高必须小于等于切割后的高',

  view_all_sets_button: '全部',
  view_train_set_button: '训练集',
  view_validate_set_button: '验证集',

  label_out_of_crop_warn: '请注意：裁剪范围之外的标签将不参与模型训练。',

  model_version: '模型版本',
  model_version_select_confirmation: '确定切换模型版本吗？',
  model_version_delete_confirmation: '确定删除这个模型版本吗：%s?',
  model_version_error_loading: '错误：正在训练',
  model_version_none_found: '模型不存在',
  model_version_selected_model_version: '选择的模型版本：%s',
  model_version_untracked: '未知',
  model_version_not_found: '未知',
  model_version_select_broken_model: '训练失败',

  backtest_table_header_network: '模型',
  backtest_table_header_version: '版本',
  backtest_table_header_deployed: '产线版本',
  backtest_table_deployed_not_selected: '未选择',

  threshold_tool_tip_network_not_found_on_central:
    '这些已部署的网络目前未在中央机器上找到。',
  threshold_tool_tip_network_not_found_on_central_suffix:
    '因此，这些网络的功能（如模拟和阈值调整/编辑/分析）不可用。',

  threshold_table_readme_button: '使用说明',
  threshold_table_readme_title: '使用说明',

  threshold_table_readme_modal_how_to_start: '如何开始：',
  threshold_table_readme_modal_how_to_start_item1: '将模型部署到目标机器。',
  threshold_table_readme_modal_how_to_start_item2:
    '在 StartX 中创建捕获配置和网络之间的映射。',

  threshold_table_readme_modal_caution: '注意：',
  threshold_table_readme_modal_caution_threshold_creation_limitation:
    '阈值创建限制',
  threshold_table_readme_modal_caution_threshold_creation_limitation_item1:
    '无法在位置网络中创建阈值。',

  threshold_table_readme_modal_caution_threshold_renaming_feature_label:
    '重命名特征标签：',
  threshold_table_readme_modal_caution_threshold_renaming_feature_label_item1:
    '请按以下步骤操作：',
  threshold_table_readme_modal_caution_threshold_renaming_feature_label_item1_step1:
    '更改标签名称。',
  threshold_table_readme_modal_caution_threshold_renaming_feature_label_item1_step2:
    '使用新标签从头开始重新训练模型。',
  threshold_table_readme_modal_caution_threshold_renaming_feature_label_item1_step3:
    '将新模型部署到目标机器。',
  threshold_table_readme_modal_caution_threshold_renaming_feature_label_item1_step4:
    '删除使用旧标签名称的阈值，并用新标签名称创建新的阈值。',

  threshold_table_readme_modal_caution_threshold_deleting_feature_label:
    '删除特征标签：',
  threshold_table_readme_modal_caution_threshold_deleting_feature_label_item1:
    '请按以下步骤操作：',
  threshold_table_readme_modal_caution_threshold_deleting_feature_label_item1_step1:
    '从模型中删除标签。',
  threshold_table_readme_modal_caution_threshold_deleting_feature_label_item1_step2:
    '从头开始重新训练模型。',
  threshold_table_readme_modal_caution_threshold_deleting_feature_label_item1_step3:
    '将新模型部署到目标机器。',
  threshold_table_readme_modal_caution_threshold_deleting_feature_label_item1_step4:
    '删除使用已删除标签的阈值。',

  threshold_table_readme_modal_editing_thresholds: '编辑阈值：',
  threshold_table_readme_modal_editing_thresholds_edit_thresholds: '编辑阈值：',
  threshold_table_readme_modal_editing_thresholds_edit_thresholds_item1:
    '点击目标阈值行末的笔图标。',
  threshold_table_readme_modal_editing_thresholds_add_thresholds: '添加阈值：',
  threshold_table_readme_modal_editing_thresholds_add_thresholds_item1:
    '按表格上方的添加按钮并选择特征名称。对于没有现有阈值的特征，点击带有“[ ]”图标的行中的笔图标以添加阈值。',
  threshold_table_readme_modal_editing_thresholds_delete_thresholds:
    '删除阈值：',
  threshold_table_readme_modal_editing_thresholds_delete_thresholds_item1:
    '按表格上方的 %s 按钮包含目标阈值。选择您要删除的阈值所在的行并点击垃圾桶图标。要退出删除模式，请按 %s 按钮。',

  threshold_table_readme_modal_troubleshooting: '故障排除：',
  threshold_table_readme_modal_troubleshooting_target_network_not_found:
    '未找到目标模型：',
  threshold_table_readme_modal_troubleshooting_target_network_not_found_item1:
    '确认在 StartX 中存在采像设置配置的映射。',
  threshold_table_readme_modal_troubleshooting_new_label_not_displayed_or_old_label_displayed:
    '新标签未显示/旧标签显示：',
  threshold_table_readme_modal_troubleshooting_new_label_not_displayed_or_old_label_displayed_item1:
    '确保包含新标签的模型已被训练和部署。',

  threshold_table_searchbar_network: '按模型筛选...',
  threshold_table_searchbar_feature: '按特征筛选...',
  threshold_table_searchbar_status: '按状态筛选...',

  threshold_table_status_enabled: '启用',
  threshold_table_status_disabled: '禁用',
  threshold_table_status_valid: '有效',
  threshold_table_status_invalid: '无效',
  threshold_table_status_empty: '空',
  threshold_table_status_not_empty: '非空',
  threshold_table_status_applicable: '适用',
  threshold_table_status_not_applicable: '不适用',

  threshold_table_header_status: '状态',
  threshold_table_header_enabled: '启用',
  threshold_table_header_feature: '特征',
  threshold_table_header_Decision: '决策',
  threshold_table_header_Modifier: '聚合维度',
  threshold_table_header_Criteria: '判定条件',
  threshold_table_cell_invalid: '无效',
  threshold_table_cell_enabled: '启用',
  threshold_table_cell_disabled: '禁用',

  threshold_table_cell_status_icon_invalid_tooltip: '无效阈值',
  threshold_table_cell_status_icon_empty_tooltip: '未设置阈值',
  threshold_table_cell_status_icon_not_applicable_tooltip:
    '已部署的模型版本不存在此缺陷',

  threshold_table_edit_form_header_new_threshold: '创建阈值',
  threshold_table_edit_form_header_existing_threshold: '编辑阈值',

  threshold_table_edit_form_decision_input_label: '决策',

  threshold_table_edit_form_save_and_close_button: '保存并关闭',
  threshold_table_edit_form_discard_button: '丢弃',
  threshold_table_edit_form_threshold_type: '阈值类型',
  threshold_table_edit_form_threshold_type_only_modifier: '仅聚合维度',
  threshold_table_edit_form_threshold_type_only_criteria: '仅标准',
  threshold_table_edit_form_threshold_type_modifier_and_criteria:
    '修改器和标准',
  threshold_table_edit_form_threshold_type_invalid_message:
    '至少一个聚合维度或判定条件必须完成。',
  threshold_table_edit_form_validation_error_invalid_input:
    '检测到无效输入：\n\n%s',

  threshold_table_form_validation_error_submit_decision: '决策',
  threshold_table_validation_error_submit_modifier: '聚合维度',
  threshold_table_validation_error_submit_criteria: '判定条件',
  threshold_table_validation_error_submit_measurement: '无聚合维度',
  threshold_table_validation_error_submit_operator: '操作符',
  threshold_table_validation_error_submit_value: '值',

  threshold_table_edit_form_enabled: '启用',
  threshold_table_edit_form_feature_name: '特征名称',
  threshold_table_edit_form_decision: '决策',
  threshold_table_edit_form_modifier: '聚合维度',
  threshold_table_edit_form_modifier_measurement_count_label: '计数',
  threshold_table_edit_form_modifier_measurement_total_area_label: '总面积',
  threshold_table_edit_form_modifier_measurement_no_modifier_label:
    '无聚合维度',
  threshold_table_edit_form_modifier_operator: '操作符',
  threshold_table_edit_form_modifier_value: '值',
  threshold_table_edit_form_criteria: '判定条件',
  threshold_table_edit_form_criteria_measurement: '测量',
  threshold_table_edit_form_criteria_measurement_no_criteria: '无判定条件',
  threshold_table_edit_form_criteria_operator: '操作符',
  threshold_table_edit_form_criteria_value: '值',

  threshold_table_error_loading_defects_and_colors:
    '加载缺陷和颜色数据时出错：%s',
  threshold_table_error_loading_deployed_features:
    '在网络 %s 中加载特征时出错。可能没有部署任何模型。',
  threshold_table_error_loading_thresholds: '加载阈值数据时出错：%s',

  threshold_table_delete_thresholds_confirmation: '确定要删除选定的阈值吗？',
  threshold_table_add_new_threshold_button: '新建阈值 +',
  threshold_table_filtering_clear_button: '清除',

  threshold_table_edit_form_validation_missing_value: '缺少值。',
  threshold_table_edit_form_validation_not_convertible_from_string_to_number:
    '字符串必须可以转换为数字。',
  threshold_table_edit_form_validation_negative_number: '数字必须是非负的。',
  threshold_table_edit_form_validation_not_integer: '数字必须是整数。',
  threshold_table_edit_form_validation_missing_decision: '缺少决策。',
  threshold_table_edit_form_validation_missing_operator: '缺少操作符。',
  threshold_table_edit_form_validation_operator_required:
    '使用判定条件时需要操作符。',
  threshold_table_edit_form_validation_value_required: '使用判定条件时需要值。',
  threshold_table_edit_form_validation_condition_type_error:
    '聚合维度或判定条件至少需要完成一个。',

  threshold_table_edit_form_tooltip_modifier:
    '修饰符是应用于特征的聚合条件。如果存在标准，则在应用标准之后实施修饰符。',
  threshold_table_edit_form_tooltip_criteria:
    '标准作为特征的段级条件。如果存在标准，则在实施修饰符之前应用这些标准。',

  threshold_table_edit_form_explanation_lead:
    '当前阈值设定是如何影响物料缺陷判定的：',
  threshold_table_edit_form_explanation_part_decision:
    '物料会判定为%s，只要有一张或以上物料图片被判定为%s。',
  threshold_table_edit_form_explanation_part_image_decision_criteria_only:
    '物料图片会判定为%s, 只要有一个或以上%s特征满足%s。',
  threshold_table_edit_form_explanation_part_image_decision_modifier_only:
    '物料图片会判定为%s, 如果%s特征的%s满足%s条件。',
  threshold_table_edit_form_explanation_part_image_decision_modifier_criteria:
    '物料图片会判定为%s, 如果%s缺陷的%s满足%s条件，并且每个%s特征满足%s',
  threshold_table_edit_form_explanation_condition_separator_and: '和',

  threshold_table_edit_form_save_and_close_button_dialog_message:
    '您确定要保存阈值吗？',
  threshold_table_edit_form_discard_button_dialog_message:
    '您确定要放弃新的阈值吗？',
  threshold_table_edit_form_discard_button_yes_button_label: '是，丢弃',

  threshold_validation_error_invalid_char: "错误：只能使用数字和'-'",
  threshold_validation_error_misplaced_dash: "错误：在'-'前后必须有数字",
  threshold_validation_error_bad_order: "错误：'-'左边的数字必须小于右边的数字",
  threshold_validation_error_extra_dash: "错误：只能最多使用一个'-'",

  threshold_active_invalid_rule: '当前更改存在无效阈值规则',
  threshold_add_threshold_button: '添加阈值',
  threshold_delete_mode_on_button: '删除模式开启',
  threshold_delete_mode_off_button: '删除模式关闭',
  threshold_decision_button: '判定结果',
  threshold_criteria_button: '判定条件 +',
  threshold_criteria_measurement_button: '测量对象',
  threshold_criteria_operator_button: '运算符',

  threshold_measurement_mr_length: '长（像素）',
  threshold_measurement_mr_width: '宽（像素）',
  threshold_measurement_horizontal_width: '水平（像素）',
  threshold_measurement_vertical_height: '竖直（像素）',
  threshold_measurement_area: '面积（像素）',
  threshold_measurement_defect_ctr_point_x_coor: '缺陷中心点X坐标',
  threshold_measurement_defect_ctr_point_y_coor: '缺陷中心点Y坐标',

  threshold_modifier_placeholder: '聚合维度',
  threshold_modifier_invalid_placeholder: '无效聚合',
  threshold_modifier_radio_count: '数量',
  threshold_modifier_radio_total_area: '总面积',

  threshold_criteria_measurement_placeholder: '测量对象',
  threshold_criteria_operator_placeholder: '运算符',

  threshold_validation_status_decision: '判定结果',
  threshold_validation_status_modifier: '聚合维度',
  threshold_validation_status_criteria: '判定条件',

  threshold_tooltip_part_1: '可以支持两种格式：',
  threshold_tooltip_part_2:
    '一个数字X，大于X的缺陷会判定为NG，小于等于X的缺陷会被判定为OK。',
  threshold_tooltip_part_3:
    'X-Y格式的两个数字，大于Y的缺陷会被判定为NG，大于X并且小于等于Y的缺陷会被判定为极限，小于等于X的缺陷会被判定为OK。',

  threshold_tooltip_invalid_rule_with_three_missing_fields:
    '检测到无效条件。请填入 %s，%s和%s。',
  threshold_tooltip_invalid_rule_with_two_missing_fields:
    '检测到无效条件。请填入 %s，和%s 。',
  threshold_tooltip_invalid_rule_with_one_missing_field:
    '检测到无效条件。请填入 %s 。',

  count_threshold_tooltip_part_2:
    '一个数字X，大于等于X的缺陷会判定为NG，小于X的缺陷会被判定为OK。',
  count_threshold_tooltip_part_3:
    'X-Y格式的两个数字，大于等于Y的缺陷会被判定为NG，大于等于X并且小于Y的缺陷会被判定为极限，小于X的缺陷会被判定为OK。',
  count_threshold_tooltip_part_4: '注：数量阈值和其余阈值规则不一样',

  threshold_confirmation_delete_threshold: '您确定要删除此阈值吗？\n\n\n',
  threshold_confirmation_rule_status: '状态',
  threshold_confirmation_rule_feature: '特征',
  threshold_confirmation_rule_decision: '判定结果',
  threshold_confirmation_rule_modifier: '聚合维度',
  threshold_confirmation_rule_no_modifier: '无聚合维度',
  threshold_confirmation_rule_invalid_modifier: '无效聚合维度',
  threshold_confirmation_rule_criteria: '判定条件',
  threshold_confirmation_rule_no_criteria: '无判定条件',
  threshold_confirmation_rule_invalid_criteria: '无效判定条件',
  threshold_confirmation_rule_status_active: '生效',
  threshold_confirmation_rule_status_inactive: '禁用',
  threshold_confirmation_rule_not_specified: '未指定',

  manual_result_missing_warning_title: '警告',
  manual_result_missing_warning_message:
    '有些物料没有人工数据，所以人OK+人NG不一定能达到100%。',

  backtest_table_model_diff: '选择的模型版本和部署的不同',
  backtest_table_threshold_diff: '阈值有改动',

  diff_report_title: '差异报告',
  diff_report_details: '详情',
  diff_report_default_machine: '默认机器',
  diff_report_remotes: '远程机器',
  diff_report_execute: '执行',
  diff_report_all_settings_match: '所有设置都一致',
  diff_report_diff_settings: '不同的设置',
  diff_report_productionpy_heading: '产线设置',
  diff_report_customconfig_heading: '自定义设置',
  diff_report_software_versions_heading: '软件版本',
  diff_report_models_thresholds_heading: '模型和阈值',
  diff_report_deploy_row: '部署',
  diff_report_active_machines: '激活的机器',
  diff_report_prod_diff: '产线设置差异',
  diff_report_custom_config_diff: '自定义设置差异',
  diff_report_synced: 'N/A',
  diff_report_see_data: '查看数据',
  diff_report_prodpy_mismatch: ' 处不同。',
  diff_report_model_versions_and_thresholds: '模型版本和阈值',
  diff_report_postprocessing_thresholds: '后处理阈值',
  diff_report_network_thresholds: '模型阈值',
  diff_report_prodpy_base_dialog_title: '产线配置所属机器： ',
  diff_report_software_version_diff: '软件版本',
  diff_report_deploy_models_thresholds: '部署模型和阈值',
  diff_report_deploy_title: '部署',
  diff_report_models_thresholds_disabled:
    '模型和阈值被禁用，请检查产线设置文件',
  diff_report_base_machine: '部署源： ',
  diff_report_to_machines: '部署目标：',
  diff_report_mismatch: '不匹配',
  diff_report_missing: '缺失',
  diff_report_extra: '额外',
  diff_report_disabled_tooltip: '请先修复部署源和目标之间的设置差异。',

  dialog_confirm: '确认',
  dialog_cancel: '取消',
  dialog_ok: '确定',
  dialog_submit: '提交',

  // Golden Part Validation Const
  golden_part_header: '物料点验验证',
  golden_part_configuration_header: '物料点验验证配置',
  golden_part_creat_new_button: '创建新配置',
  golden_part_config_modal_header_create: '创建配置',
  golden_part_config_modal_header_edit: '编辑配置',
  golden_part_config_modal_add_button: '添加',
  golden_part_config_modal_clear_button: '清除',
  golden_part_config_modal_create_cc_button: '创建采像设置和NG规则',
  golden_part_config_modal_foot_create_button: '创建',
  golden_part_config_modal_foot_save_button: '保存',
  golden_part_config_modal_foot_cancel_button: '取消',
  golden_part_part_id: '物料标识',
  golden_part_part_decision: '预期物料决策',
  golden_part_cc_name: '采像设置名称',
  golden_part_network_name: '模型名称',
  golden_part_ng_types: 'NG类型',
  golden_part_config_modal_create_cc_rule_tooltip:
    "点击'添加'以添加新的采像设置配置规则。点击'清除'以清除并隐藏表单。",
  golden_part_config_edit_button: '编辑',
  golden_part_config_delete_button: '删除',
  golden_part_config_general_error_msg:
    '错误：配置包含未在production.py中找到的过时值。请检查下面的错误并修复。',
  golden_part_config_camera_config_tooltip_error:
    '错误：检查production.py中的采像设置名称：%s，并确保其正确。请更新采像设置名称。',
  golden_part_config_network_tooltip_error:
    '错误：验证所选采像设置在production.py中对应模型名称：%s是否有效。请更新模型名称。',
  golden_part_config_ng_tooltip_error:
    '错误：在所选网络的class.csv文件中找不到某些NG类型。请更新NG名称。',

  golden_part_config_delete_confirmation:
    '此操作不可逆转，将永久删除此配置规则。确定要继续吗？',
  golden_part_form_delete_icon_tooltip: '删除此采像设置规则',
  golden_part_form_cc_rules_label: '采像设置规则',
  // Golden Part Validation Config Errors
  golden_part_config_store_fetch_error: '错误：无法获取配置。',
  golden_part_form_error_partid_empty: '物料标识不能为空。',
  golden_part_form_error_partid_invalid: '物料标识不能包含特殊字符。',
  golden_part_form_error_partid_duplicate: '物料标识已存在。',
  golden_part_form_error_part_decision_invalid: '物料决策不能为空',
  golden_part_form_error_ccname_invalid: '找不到采像设置名称：%s。',
  golden_part_form_error_network_name_invalid: '找不到模型：%s。',
  golden_part_form_ccrule_error_saving_before_add:
    '错误：请先添加采像设置和NG规则，然后再添加。',
  golden_part_form_error_no_ngtypes_for_network:
    '错误：此模型没有可用的NG类型。请选择另外模型。',
  golden_part_form_error_no_ngtypes_selected:
    '错误：未选择任何NG类型。请至少选择一个NG类型。',
  golden_part_form_error_ngtypes_invalid: '找不到NG类型：%s。',
  golden_part_form_error_empty_ngtypes:
    '错误：未选择任何NG类型。请确保所有模型至少选择一个NG类型。',
  golden_part_form_error_invalid_ng_types_selected:
    '错误：当前模型%s中找不到NG类型：%s。',
  golden_part_form_error_save_config: '发现错误，请在保存前修复问题。',
  golden_part_form_error_missing_required_config:
    '错误：无法保存配置。请在创建之前填写所有必填字段。',
  golden_part_form_error_empty_cc_mapping:
    '采像设置和NG规则不能为空。请添加采像设置和NG规则。',
  golden_part_config_parsing_error:
    '无法解析配置文件。请修复配置文件中的错误或创建一个新配置。',
  golden_part_config_not_found_error: '未找到可用的配置',
  golden_part_start_new_config_instructions:
    '点击"创建新配置"按钮开始，或点击"帮助文件"查看启动指南。',
  golden_part_config_readme: '帮助文件',

  golden_part_config_readme_title: '入门指南：',
  golden_part_config_readme_how_to_start: '如何开始：',
  golden_part_config_readme_click_to_start: '点击"创建新配置"按钮开始。',
  golden_part_config_readme_rules_title: '物料点验验证配置文件的规则：',
  golden_part_config_readme_rules_bullet_file_location:
    '物料点验验证配置文件位于 ~/unitx_data/config/golden_part_validation_config.json。',
  golden_part_config_readme_rules_bullet_requried_fields:
    '必填字段包括：物料 ID、预期物料决策、采像设置配置。',
  golden_part_config_readme_rules_bullet_part_id:
    '物料标识应该是唯一的。如果您没有物料标识，您可以使用配置的位置 n，其中 n 代表索引。',
  golden_part_config_readme_rules_bullet_part_decision:
    '预期物料决策应该是 OK、NG 或 LIMIT。',
  golden_part_config_readme_rules_bullet_cc_rules:
    '如果选择了采像设置配置，则为新的物料点验验证配置需要模型和 NG 类型。',
  golden_part_config_readme_rules_bullet_cc_2_c:
    '采像设置和模型来自 Production.py。',
  golden_part_config_readme_rules_bullet_network2ng_types:
    '相关部署模型的 NG 类型来自模型的 Class.csv 文件。',
  golden_part_config_readme_rules_bullet_cc_rules_three:
    '一个物料验证配置可以有多个采像设置规则。',
  golden_part_config_readme_rules_bullet_cc_rules_four:
    '每个采像设置规则可以有一个采像设置，以及不同的模型和其 NG 类型。',
  golden_part_config_readme_close_button: '关闭',

  // Remote Config
  remote_config_table_header_group: '组名',
  remote_config_requier: '请输入必填项目',
  remote_config_table_header_name: '远程名称',
  remote_config_table_header_ip: 'IPv4 地址',
  remote_config_table_header_toggle: '启用连接',
  remote_config_add_remote: '添加远程设备',
  remote_config_edit_remote: '编辑远程设备',
  remote_config_scroll_to_top: '上',
  remote_config_text_field_name: '名称',
  remote_config_text_field_ip: 'IPv4 地址',
  remote_config_text_field_group: '组名',
  remote_config_status: '连接状态',
  remote_config_dialog_confirm: '确认',
  remote_config_remove_remote_confirm: '确定要删除此远程设备吗？',
  remote_config_ip_exists: 'IP地址已被使用!',
  remote_config_name_exists: '远程名称已被使用!',
  remote_config_ping_success:
    '成功对远程计算机进行 Ping，但挂载失败。请验证来自中央计算机的 SSH 密钥是否存储在远程计算机上。如需进一步的故障排除帮助，请参阅 Notion 上的远程配置文档。',
  remote_config_ping_fail:
    '无法对远程计算机进行 Ping。请检查远程计算机是否开启并连接到与中央计算机相同的网络。还要检查提供的 IPv4 地址是否正确。如需进一步的故障排除帮助，请参阅 Notion 上的远程配置文档。',
  remote_config_fetch_fail:
    '无法获取远程配置。请检查 ~/unitx_data/config 中 remotes.json 的内容，并确保其包含“remotes”。',
  remote_config_ip_invalid:
    '无效的 IPv4 地址。必须为 X.X.X.X 的形式，其中每个 X 都是从 0 到 255 的数字。',
  remote_config_last_update: '最新更新：',

  // Network Archive
  network_archive_title: '已存档的算法',
  network_archived_date: '存档于 %s',
  network_confirm_restore: '这将恢复算法。您确定吗？',
  network_archive_confirm:
    '这将归档算法。已归档的算法不支持训练和编辑标签。您确定吗？',

  network_archive_button: '归档',
  network_restore_button: '恢复算法',
  network_restore_with_archived_features_tooltip: '恢复算法和已归档的特征',
  networks_table_archived_feature_tooltip: '已归档的算法',

  network_archived_label: '已归档',

  snackbar_network_restored_msg: '算法已恢复',
  snackbar_network_rearchived_msg: '算法重新归档',
  snackbar_network_unarchived_msg: '取消算法归档',
  snackbar_network_archived_msg: '算法已归档',
  snackbar_network_deleted_msg: '算法已删除',
  snackbar_undo_action: '撤销',

  defect_network_label: '缺陷算法',
  location_network_label: '定位算法',

  archived_no_label_to_review: '没有标签需要审核。',
  archived_no_model_trained: '训练不存在。',

  viewing_archived_network_warning:
    '您正在查看一个已归档的算法。标签仅供查看。要编辑标签，请恢复算法。',
  archived_networks_actions_disabled_warning: '算法已归档时，操作被禁用。',

  existing_archived_network_error:
    'There is an existing archived network with this name',
  existing_active_network_error: 'There is an existing network with this name',

  broken_model_version_selected_error: '选择了损坏的训练版本',
  search_bar_label: '搜索',
  search_bar_placeholder: '按训练名称搜索',
  learn_app_search_bar_label: '搜索',
  learn_app_search_bar_placeholder: '按训练名称搜索',
  learn_app_sort_by_label: '按照',

  sort_key_option_date_created: '创建日期',
  sort_key_option_date_last_trained: '最新模型版本',
  sort_key_option_name: '名称',

  sort_by_date_ascending: '最早的优先',
  sort_by_date_descending: '最新的优先',

  sort_by_letter_language_a_z: 'A - Z',
  sort_by_letter_language_z_a: 'Z - A',

  production_report_v2_empty_analytics_no_analytics: '尚无分析数据',
  production_report_v2_empty_analytics_no_analytics_subtext:
    '当您在上面的日历中应用日期范围后，这里将显示所有分析数据。',
  production_report_v2_empty_analytics_no_data:
    '所选日期范围内无可用数据。请' +
    '选择新的日期范围，或确保已收集所需日期的数据。',
  production_report_v2_empty_analytics_production_data: '产线数据',
  production_report_v2_empty_analytics_ng_type_chart: 'NG类型图表',
  production_report_v2_date_picker_day1: '星期日',
  production_report_v2_date_picker_day2: '星期一',
  production_report_v2_date_picker_day3: '星期二',
  production_report_v2_date_picker_day4: '星期三',
  production_report_v2_date_picker_day5: '星期四',
  production_report_v2_date_picker_day6: '星期五',
  production_report_v2_date_picker_day7: '星期六',
  production_report_v2_date_picker_last_7_days: '过去7天',
  production_report_v2_date_picker_last_30_days: '过去30天',
  production_report_v2_date_picker_yesterday: '昨天',
  production_report_v2_date_picker_today: '今天',
  production_report_v2_date_picker_custom: '自定义',
  production_report_v2_date_picker_select_date: '选择日期和时间范围',
  production_report_v2_date_picker_reset_button: '重置',
  production_report_v2_date_picker_submit_button: '提交日期范围',

  production_report_v2_time_period_am: '上午',
  production_report_v2_time_period_pm: '下午',
  production_report_v2_hours: '小时',
  production_report_v2_minutes: '分钟',
  production_report_v2_time_picker_error: '无效的时间。请选择有效的时间',
  production_report_v2_time_picker_cancel: '取消',
  production_report_v2_time_picker_ok: '确定',
  production_report_v2_time_picker_label_from: '从',
  production_report_v2_time_picker_label_to: '至',
  production_report_v2_time_picker_enter_time: '输入时间',

  production_report_v2_date_picker_to_divider: '至',

  // Production V2 Table
  production_report_v2_short_month_names_jan: '1月',
  production_report_v2_short_month_names_feb: '2月',
  production_report_v2_short_month_names_mar: '3月',
  production_report_v2_short_month_names_apr: '4月',
  production_report_v2_short_month_names_may: '5月',
  production_report_v2_short_month_names_jun: '6月',
  production_report_v2_short_month_names_jul: '7月',
  production_report_v2_short_month_names_aug: '8月',
  production_report_v2_short_month_names_sep: '9月',
  production_report_v2_short_month_names_oct: '10月',
  production_report_v2_short_month_names_nov: '11月',
  production_report_v2_short_month_names_dec: '12月',

  production_report_v2_table_date_grouping_days: '天',
  production_report_v2_table_date_grouping_weeks: '周',
  production_report_v2_table_date_grouping_months: '月',

  production_report_v2_table_title_production_data: '产线数据',
  production_report_v2_table_title_false_detection_data: '误检数据',
  production_report_v2_table_title_table: '表',
  production_report_v2_table_title_overview_table: '概览表',
  production_report_v2_table_title_ng_type: 'NG类型概览',
  production_report_v2_table_title_limit: 'LIMIT类型概览',
  production_report_v2_table_title_false_detection_part_overview_table:
    '物料维度数据: 产线数据中标记为 过杀/漏杀 的物料个数。',
  production_report_v2_table_title_false_detection_image_overview_table:
    '照片维度数据: 产线数据中标记为 过杀/漏杀 的照片张数。',
  production_report_v2_table_title_fr_type:
    '过杀: 对于每个 NG 类型, 检测结果为 NG 但是期望结果是 OK 的照片张数(目标是0)。',
  production_report_v2_table_title_fa_type:
    '漏杀: 对于每个 NG 类型, 检测结果为 OK 但是期望结果是 NG 的照片张数(目标是0)。',
  production_report_v2_table_week_label: '周',
  production_report_v2_shows_simulated_data: '显示模拟数据',
  production_report_v2_clear_simulation_button: '清除模拟数据',
  production_report_v2_sim_tag_running: '运行中',
  production_report_v2_sim_tag_sim: '模拟',
  production_report_v2_table_app_name_simulation: '模拟',

  production_report_v2_analytics_tab: '阈值分析数据',
  production_report_v2_thresholds_tab: '阈值',
  production_report_v2_production_data_tab: '产线数据',
  production_report_v2_false_detection_data_tab: '误检数据',
  production_report_v2_false_detection_tooltip:
    '如果有模拟数据，箭头左边表示手动标记的 过杀/漏杀 数据，箭头右边表示模拟数据。',
  production_report_v2_no_records_for_simulation:
    '选择的数据范围内没有模拟的记录。',
  production_report_v2_date_picker_day: '天',
  production_report_v2_date_picker_at: '在',

  production_report_v2_deploying_thresholds_in_progress: '正在部署阈值',
  production_report_v2_running_simulation_in_progress: '正在运行模拟',
  production_report_v2_prepare_simulation: '正在准备模拟数据',
  production_report_v2_not_all_data_shown_tooltip:
    '在表格中不显示没有生产数据的天。',
  production_report_v2_refresh_button: '刷新',
  production_report_v2_simulation_title_tooltip:
    '如果您熟悉我们的旧软件版本，模拟执行与回测相同的特征。',
  production_report_v2_switching_date_range_warning:
    '切换日期范围将清除当前的模拟数据',
  production_report_v2_switching_date_range_warning_while_running_backtest:
    '目前正在进行模拟。切换日期范围将停止此模拟。',
  production_report_v2_date_range_start_time: '开始时间',
  production_report_v2_date_range_end_time: '结束时间',
  production_report_v2_simulation_missing_images_tooltips:
    '由于缺少原图或图像处理异常，某些物料的模拟被跳过。',

  production_report_v2_long_month_names_jan: '1月',
  production_report_v2_long_month_names_feb: '2月',
  production_report_v2_long_month_names_mar: '3月',
  production_report_v2_long_month_names_apr: '4月',
  production_report_v2_long_month_names_may: '5月',
  production_report_v2_long_month_names_jun: '6月',
  production_report_v2_long_month_names_jul: '7月',
  production_report_v2_long_month_names_aug: '8月',
  production_report_v2_long_month_names_sep: '9月',
  production_report_v2_long_month_names_oct: '10月',
  production_report_v2_long_month_names_nov: '11月',
  production_report_v2_long_month_names_dec: '12月',

  production_report_v2_simulation_time_remaining: '模拟剩余时间',
  production_report_v2_simulation_finished: '模拟完成',

  production_report_v2_part_type_select_title: '物料类型',
  production_report_v2_part_type_select_all_label: '全部',

  // Loss Chart
  validate_network_loss_chart_title: '损失图表',
  validate_network_loss_chart_prompt_title: '什么是损失？',
  validate_network_loss_chart_explanation_only_train_loss: '仅训练损失 (loss)',
  validate_network_loss_chart_explanation_train_and_val_loss:
    '训练损失（loss）和验证损失（val_loss)',
  validate_network_loss_chart_explanation_good_fitting: '良好拟合',
  validate_network_loss_chart_explanation_underfitting: '欠拟合',
  validate_network_loss_chart_explanation_overfitting: '过拟合',
  validate_network_loss_chart_only_train_loss_good_sub_bullet:
    '训练损失的整体趋势是下降的，并最终接近零。',
  validate_network_loss_chart_underfitting_sub_bullet_one:
    '训练损失的整体趋势不一致下降，而是波动较大。',
  validate_network_loss_chart_underfitting_sub_bullet_two:
    '训练损失的整体趋势下降，但在最后的迭代中，损失值大于0.1。在这种情况下，您可以使用训练增量。',
  validate_network_loss_chart_train_and_val_loss_sub_bullet:
    '训练损失和验证损失都显示出整体一致下降的趋势，它们的最终值趋于接近零。',
  validate_network_loss_chart_train_overfitting_sub_bullet:
    '训练损失显示出整体下降的趋势，而验证损失要么一开始下降然后上升，要么首先下降然后波动。',

  validate_network_loss_chart_moving_average_title: '移动平均',
  validate_network_loss_chart_explanation_moving_average:
    '损失曲线（loss 与 val loss）有很多噪声，有时很难判断整体趋势。移动平均损失曲线（moving average 与 val moving average）通过计算一段时间窗口内的数据点平均值，来平滑短期波动并突出长期趋势或周期。如果从标准损失曲线中难以辨认趋势，请使用移动平均损失曲线。',

  network_validation_loss_chart_log_loss: 'log(损失)',
  network_validation_loss_chart_log_moving_average: 'log(移动平均)',
  network_validation_loss_chart_log_val_loss: 'log(验证损失)',
  network_validation_loss_chart_log_val_moving_average: 'log(验证移动平均)',
  network_validation_loss_chart_incremental: '递增',
  // NG Analysis Chart
  production_report_v2_ng_present_chart_title: '分析数据',
  production_report_v2_ng_present_chart_subheading_breakdown: 'NG类型分布',
  production_report_v2_ng_present_chart_subheading_percent_explanation:
    '占物料总数的%',
  production_report_v2_ng_present_chart_subheading_number_explanation:
    '作为含缺陷物料的#',
  production_report_v2_ng_present_chart_switch_numbers: '数量',
  production_report_v2_ng_present_chart_switch_percent: '百分比',
  production_report_v2_ng_present_chart_ng_data: 'NG数据',
  production_report_v2_ng_present_chart_lim_data: '极限数据',
  production_report_v2_ng_present_chart_y_axis_label: '含缺陷物料',
  production_report_v2_ng_present_chart_x_axis_label: 'NG存在',

  production_report_v2_ng_analysis_chart_title: '缺陷测量分布',
  production_report_v2_ng_analysis_chart_subheading: '按缺陷类型的测量分布',
  production_report_v2_ng_measurement_mrl: 'MRL (最小矩形长度)',
  production_report_v2_ng_measurement_mrw: 'MRW (最小矩形宽度)',
  production_report_v2_ng_measurement_hw: 'HW (水平宽度)',
  production_report_v2_ng_measurement_vh: 'VH (垂直高度)',
  production_report_v2_ng_measurement_area: 'A (面积)',
  production_report_v2_ng_measurement_count: 'C (计数)',
  production_report_v2_ng_measurement_total_area: 'TA (总面积)',

  production_report_v2_ng_measurement_mrl_explanation: '最小包围框的长度。',
  production_report_v2_ng_measurement_mrw_explanation: '最小包围框的宽度。',
  production_report_v2_ng_measurement_hw_explanation:
    '与x轴对齐的包围框的宽度。',
  production_report_v2_ng_measurement_vh_explanation:
    '与x轴对齐的包围框的高度。',
  production_report_v2_ng_measurement_area_explanation: '形状内的像素总数。',
  production_report_v2_ng_measurement_count_explanation:
    '零件上缺陷实例的数量。',
  production_report_v2_ng_measurement_total_area_explanation:
    '零件上每个缺陷实例面积的总和。',

  production_report_v2_ng_analysis_chart_selected_area_less_than: '小于或等于',
  production_report_v2_ng_analysis_chart_selected_area_greater_than:
    '大于或等于',

  network_validation_page_iou_prompt_title: '什么是交并比（IoU?)',
  network_validation_page_iou_explanation_paragraph_one:
    '交并比（IoU）：通过测量模型预测的像素区域与用户标注的像素区域之间的重叠程度来评估模型性能，100%表示完美的预测匹配，0表示没有重叠。',
  network_validation_page_iou_explanation_paragraph_two:
    'IoU 被用作物体检测任务的评估矩阵，因为它同时考虑了边界框的位置和大小。高 IoU 分数表明预测的边界框与地面实况边界框非常吻合。',

  production_report_v2_ng_measurement_mrl_name_only: '最小矩形长度',
  production_report_v2_ng_measurement_mrw_name_only: '最小矩形宽度',
  production_report_v2_ng_measurement_hw_name_only: '水平宽度',
  production_report_v2_ng_measurement_vh_name_only: '垂直高度',
  production_report_v2_ng_measurement_area_name_only: '面积',
  production_report_v2_ng_measurement_count_name_only: '计数',
  production_report_v2_ng_measurement_total_area_name_only: '总面积',

  production_report_v2_graph_options_title: '图表选项',
  production_report_v2_graph_options_data_range: '数据范围',
  production_report_v2_data_range_tooltip_msg:
    '通过拖动下方的滑块来细化显示的日期范围。您可以通过填写开始和结束字段来创建自定义范围。',
  production_report_v2_graph_options_data_range_start: '开始',
  production_report_v2_graph_options_data_range_end: '结束',
  production_report_v2_graph_options_bin_size: '区间大小',
  production_report_v2_graph_options_update_bin_size: '更新区间大小',
  production_report_v2_graph_options_bin_size_tooltip_msg:
    '选择一个箱子大小以确定直方图条的宽度。箱子大小的选择将根据在日期范围内选择的数据量而变化。',

  production_report_action_label_view_images_button: '查看图像',
  production_report_v2_ng_analysis_selector_percentage_of_all_parts:
    '(%s%的所有零件)',
  production_report_v2_select_ng_type: '选择一个缺陷类型',

  production_report_v2_info_label_instances_of_ng: '%s的实例',
  production_report_v2_info_label_instances_of_ng_percent: '占该缺陷实例的%s%',
  production_report_v2_info_label_parts_with_ng: '带有%s的零件',
  production_report_v2_info_label_parts_with_ng_percent: '占有该缺陷物料的%s',
  production_report_v2_info_label_of_all_parts: '在全部物料中的占比',
  production_report_v2_info_label_num_parts_out_of_all_parts:
    '在全部%s个物料中，有%s个物料含有符合条件的缺陷',
  production_report_v2_summary_data_instances: '个%s实例',
  production_report_v2_parts_containing: '包含的零件%s',
  production_report_v2_info_label_statistics_summary: '统计摘要',

  production_report_v2_error_message_bin_size_too_small:
    '请增加箱子大小以查看更宽的数据范围。',
  production_report_v2_error_message_range_too_large:
    '请增加箱子大小以查看更宽的数据范围。',
  production_report_v2_error_message_tooltip:
    '由于数据范围较大，图表的查看选项被限制在每次不到200个柱形以防止图表过于混乱和难以理解。要查看更多数据，请增加区间大小或减小数据范围。',

  production_report_v2_threshold_analytics_tab: '阈值分析数据',
  production_report_v2_threshold_tab: '阈值',

  production_report_v2_aggregate_measurement_type_msg:
    '这是一种将零件上所有NG实例聚合在一起的测量方法。因此，在查看此测量类型时，实例数将始终与零件数匹配。',
  production_report_v2_custom_calendar_open_msg:
    '您正在选择自定义范围中。请在查看新数据之前完成选择范围。',

  production_report_v2_ng_type_breakdown_title_tooltip:
    '仅显示在应用阈值后确定为NG的缺陷。',
  production_report_v2_defect_measurement_distribution_title_tooltip:
    '在应用阈值之前，CorteX检测到的所有缺陷测量的分布。',

  production_report_v2_minimap_does_not_rerender_error:
    '当箱子大小太小而无法显示整个数据范围时，迷你地图不会显示所有箱子。',

  production_report_v2_chart_data_range_control_invalid_number: '无效数字',
  production_report_v2_chart_data_range_control_out_of_bounds_start_too_large:
    '开始不能大于结束',
  production_report_v2_chart_data_range_control_out_of_bounds_end_too_small:
    '结束不能小于开始',
  production_report_v2_chart_data_out_of_bounds: '超出范围',
  production_report_v2_chart_data_range_control_need_to_submit:
    '按Enter进行更改',
  production_report_v2_defect_chart_loading_message:
    '正在渲染具有大数据范围的图表。',
  production_report_v2_could_not_fetch_production_version_error:
    '错误：无法获取产线机软件版本。',
  production_report_v2_no_network_found_for_machine:
    '未找到此计算机的网络配置。',
  production_report_v2_no_defects_to_analyze_title: '无缺陷可分析',
  production_report_v2_no_defects_to_analyze_message:
    '虽然有零件运行，但在此日期范围内运行的零件上未检测到任何缺陷。点击“生产数据”选项卡查看有关零件运行的数据。',
  production_report_v2_disabled_view_images:
    '此选择已禁用图像查看。您可以通过选择≤或查看所有图像来查看图像。',

  production_report_v3_part_statistics_data: '物料统计数据',
  production_report_v3_part_statistics_tab_ng: 'NG 物料',
  production_report_v3_part_statistics_tab_limit: 'Limit 物料',
  production_report_v3_part_statistics_tab_ok: 'OK 物料',
  production_report_v3_part_statistics_tab_abnormal: '异常物料',
  production_report_v3_part_statistics_table_column_view_images: '查看图像',
  production_report_v3_part_statistics_table_column_part_id: '物料 ID',
  production_report_v3_part_statistics_table_column_inspection_end_time:
    '检测结束时间',
  production_report_v3_part_statistics_table_column_ng_reason: 'NG 原因',
  production_report_v3_part_statistics_table_column_limit_reason: 'LIMIT 原因',
  production_report_v3_part_statistics_table_column_include_feature:
    '是否包含缺陷?',
  production_report_v3_part_statistics_table_column_defect_quantity: '缺陷数量',
  production_report_v3_part_statistics_table_column_feature_type: '缺陷类型',
  production_report_v3_part_statistics_table_column_abnormality_type:
    '异常类型',
  production_report_v3_part_statistics_table_column_image_mismatch:
    '异常图像数量',
  production_report_v3_part_statistics_search: '搜索',
  production_report_v3_part_statistics_table_cell_all: '全部',
  production_report_v3_part_statistics_table_cell_yes: '是',
  production_report_v3_part_statistics_table_cell_no: '否',
  production_report_v3_part_statistics_table_cell_more: '多图',
  production_report_v3_part_statistics_table_cell_few: '少图',
  production_report_v3_part_statistics_feature_select_placeholder: '选择缺陷',
  production_report_v3_part_statistics_has_feature_placeholder: '是否包含缺陷?',

  production_report_v3_feature_statistics_overview: '概览',
  production_report_v3_feature_statistics_no_threshold: '当前未配置阈值',
  production_report_v3_feature_statistics_no_threshold_set:
    '请前往“阈值配置”页面设置',
  production_report_v3_feature_statistics_image: '图像',
  production_report_v3_feature_statistics_ng_image: 'NG 图像',
  production_report_v3_feature_statistics_high_value_image: '高价值图像',
  production_report_v3_feature_statistics_data: '统计数据',
  production_report_v3_feature_measurement_judgement: '判断',
  production_report_v3_feature_measurement_decision: '结果',
  production_report_v3_THRESHOLD_MEASURE_TYPE_AREA: '面积',
  production_report_v3_THRESHOLD_MEASURE_TYPE_MIN_RECTANGLE_LENGTH:
    '最小矩形长度',
  production_report_v3_THRESHOLD_MEASURE_TYPE_MIN_RECTANGLE_WIDTH:
    '最小矩形宽度',
  production_report_v3_THRESHOLD_MEASURE_TYPE_HORIZONTAL_WIDTH: '水平宽度',
  production_report_v3_THRESHOLD_MEASURE_TYPE_VERTICAL_HEIGHT: '竖直高度',
  production_report_v3_THRESHOLD_MEASURE_CENTER_X_COOR: '缺陷中心点X坐标',
  production_report_v3_THRESHOLD_MEASURE_CENTER_Y_COOR: '缺陷中心点Y坐标',
  production_report_v3_THRESHOLD_MEASURE_TYPE_COUNT: '总数量',
  production_report_v3_THRESHOLD_MEASURE_TYPE_TOTAL_AREA: '总面积',
  production_report_v3_feature_chart: '图表',
  production_report_v3_feature_chart_title_and: '与',
  production_report_v3_feature_chart_material_quantity: '物料数量',
  production_report_v3_quality_data_tab: '质量数据',
  production_report_v3_part_statistics_coordinates: '坐标',
  network_validation_results_confusion_matrix_title: '混淆矩阵',
  network_validation_results_confusion_matrix_prediction_title: '预测',
  network_validation_results_confusion_matrix_ground_truth_title: '实际',
  network_validation_results_training_confusion_matrix: '训练',
  network_validation_results_validation_confusion_matrix: '验证',
  network_validation_results_no_confusion_matrix: '未找到混淆矩阵',

  model_validation_result_page_validation_results: '验证结果',
  model_validation_result_page_model_version: '模型版本',
  model_validation_result_page_train_network: '训练网络',
  model_validation_result_page_select_features: '选择特征',
  model_validation_result_page_select_part_types: '选择产品类型',
  model_validation_result_page_select_cc: '选择 CC',
  model_validation_result_page_all_part_types: '所有产品类型',
  model_validation_result_page_validation: '验证',
  model_validation_result_page_training: '训练',
  model_validation_result_page_validation_lower: '验证',
  model_validation_result_page_training_lower: '训练',
  model_validation_result_page_positive: '正类',
  model_validation_result_page_negative: '负类',
  model_validation_result_page_true: '真',
  model_validation_result_page_select_tags:'选择标签',
  model_validation_result_page_false: '假',
  model_validation_result_page_predicted: '预测',
  model_validation_result_page_actual: '实际',
  model_validation_result_page_iou: 'IoU',
  model_validation_result_page_confusion_matrix_overview_table_caption:
    '这是特征验证结果的概览。您可以选择特定的产品类型，查看详细的验证结果和图像。',
  model_validation_result_page_loading: '加载中...',
  model_validation_result_page_error_loading: '加载错误',
  model_validation_result_page_image_ids: '图像 IDs',
  model_validation_result_page_error_validation_result_not_found:
    '未找到（特征：%s，产品类型：%s）的验证结果。',
  model_validation_result_page_confusion_matrix_empty_dataset:
    '由于%s数据集是空的，因此无法获得混淆矩阵和 IoU。',

  text_length_validation: '字符长度为%s-%s',

  network_filter: '筛选器',
  network_clear_filter: '清除筛选器',
  network_tags: '模型标签',
  network_tag_add: '添加标签',
  network_tag_name: '名称',
  network_tag_create: '创建模型标签',
  network_tag_update: '更新模型标签',
  network_tag_delete_confirm: '确定删除这个标签吗？',
  network_tag_existing_error: '已存在此名称的标签。',

  cannot_have_same_network_name_when_cloning_error:
    '复制的模型必须具有唯一的名称。已经存在一个使用此名称的模型。',
  cannot_have_same_archived_network_name_when_cloning_error:
    '复制的模型必须具有唯一的名称。已经存在一个已归档的模型使用此名称。',

  defect_name_renaming_error: '已存在此名称的缺陷。请选择一个不同的名称。',
  location_name_renaming_error:
    'A location type with this name already exists. Please select a different name',

  show_image_diff_list_toggle_label: '显示照片差异列表',
  view_images_sort_new_images_first: '新照片优先',
  view_images_sort_old_images_first: '移除的照片优先',
  view_images_show_image_diff_list_tooltip:
    '启用照片差异列表将使用加号图标突出显示此单元格中的新照片，并使用斜体灰色文本和减号图标显示已从此单元格中移除的照片。',
  view_images_response_too_large_error:
    '无法加载图片库：请求的图片数量大于允许的最大 200,000 张图片：',
  view_images_response_too_large_workaround:
    '按物料类型过滤或选择较小的日期范围来查看它们，或查看特定缺陷类型的图像。',
  threshold_tuning_panel_defect_type: '缺陷类型：',
  threshold_tuning_panel_image_production_decision: '照片生产数据决定：',
  threshold_tuning_panel_image_simulation_decision: '照片模拟数据决定：',
  threshold_tuning_panel_error_loading_networks: '加载网络时出错：%s',
  threshold_tuning_panel_error_loading_features: '加载特征时出错： %s',

  image_diff_list_removed_image_tooltip:
    '照片存在于产线数据中，但在模拟后已从单元格中移除。',
  image_diff_list_new_image_tooltip:
    '照片在模拟后出现在此单元格中，但在产线数据中不存在。',

  clear_all_reviewed_images_button: '清除所有已审核照片',
  mark_image_as_reviewed_button: '将照片标记为已审核',
  mark_image_as_unreviewed_button: '将照片标记为未审核',
  failed_to_clear_images_alert: '出现问题。无法清除照片审核状态。',
  confirm_clear_all_images_reviewed:
    '这将把所有照片标记为未审核，包括当前数据范围之外的照片。确定吗？',

  threshold_tuning_threshold_tune_button: '运行模拟阈值调整',
  threshold_tuning_threshold_update_running_message: '正在运行 模拟阈值调整',
  threshold_tuning_threshold_update_image_decision:
    '运行模拟阈值调整后的图像决策：',
  threshold_tuning_threshold_update_defect_decision:
    '图像缺陷决策运行模拟阈值调整：',
  threshold_tuning_table_header_before: '之前（产线数据）',
  threshold_tuning_table_header_after: '之后（模拟阈值调整后）',
  threshold_tuning_part_percentages: '结果',
  threshold_tuning_data_ok_percent: 'OK物料百分比',
  threshold_tuning_data_ng_percent: 'NG物料百分比',
  threshold_tuning_data_limit_percent: 'LIMIT物料百分比',
  threshold_tuning_data_image_decision: '图像决策',
  threshold_tuning_data_image_defect_decision: '图像缺陷决策',
  threshold_tuning_results: '模拟阈值调整结果',
  threshold_tuning_threshold_update_error_backtest_in_progress:
    '在模拟进行时无法运行模拟阈值调整。请等待当前模拟完成。',
  threshold_tuning_threshold_update_error_broken_model:
    '在模拟进行时无法运行模拟阈值调整。请选择一个有效的模型版本。',
  threshold_tuning_threshold_update_error_deploying_thresholds:
    '在模拟进行时无法运行模拟阈值调整。请等待阈值部署完成。',
  threshold_tuning_threshold_update_error_invalid_thresholds:
    '在模拟进行时无法运行模拟阈值调整。请修复下面的阈值或将无效的阈值切换为无效状态。',
  threshold_tuning_threshold_update_error_general:
    '出现问题。模拟阈值调整未能完成。请重试。',
  threshold_tuning_tooltip_information:
    '运行模拟阈值调整类似于运行轻量级模拟。将使用当前保存的阈值重新计算此单元格当前日期范围内所有图像的图像决策和缺陷决策，并在下方报告新结果。不会生成新图像，并且在离开此页面后这些数据将被删除。',
  threshold_tuning_defect_threshold_title: '阈值',
  threshold_tuning_defect_threshold_tooltip: '此处仅显示当前缺陷 %s 的阈值。',
  threshold_tuning_threshold_update_already_running_error:
    '模拟阈值调整已在运行中。请等待当前模拟阈值调整完成后。',
  threshold_tuning_update_last_run_time: '上次模拟阈值调整运行时间：',
  threshold_tuning_update_view_chart_tooltip:
    '运行模拟阈值调整以查看阈值的图表。无效阈值无法生成图表。',
  threshold_tuning_update_view_chart_button: '查看图表',
  threshold_tuning_update_hide_chart_button: '隐藏图表',
  threshold_tuning_update_refresh_charts_button: '刷新图表',
  threshold_tuning_chart_generation_error:
    '错误：无法为此阈值生成图表。请重试。',
  threshold_tuning_chart_last_generated_time: '上次生成图表时间：',
  threshold_tuning_no_chart_generated:
    '没有为此阈值 %s %s 生成图表，因为没有找到匹配的数据。',
  threshold_tuning_leaving_page_clears_data_warning_dialog:
    '离开页面将清除当前所有的模拟阈值调整数据。确定吗？',
  threshold_tuning_leaving_page_while_threshold_tuning_warning_dialog:
    '阈值调优正在运行中。离开页面将导致阈值调优停止运行。确定吗？',

  threshold_tuning_image_reviewed: '已审核',
  threshold_tuning_snackbar_image_reviewed: '照片已标记为已审核。',
  threshold_tuning_snackbar_image_unreviewed: '照片已标记为未审核。',
  threshold_tuning_threshold_update_clear_simulation_data_warning_dialog:
    '运行阈值调优将清除生产数据表中的模拟数据。确定吗？',

  threshold_tuning_image_diff_new_image_status: '[新]',
  threshold_tuning_image_diff_removed_image_status: '[删]',
  threshold_tuning_no_charts_for_modifiers_without_criteria:
    '无法显示没有判定条件的聚合维度图表。请添加判定条件以查看图表。',

  model_error_text: '错误: 模型正在训练',

  simulation_num_images_loaded_percentage: '加载了%s%的数据来运行模拟。',
  image_marked_for_review_tooltip: '照片已标记为已审核。',
  threshold_tuning_results_results_for_date_range: '在日期范围 %s 的物料结果',

  deploy_threshold_section_header: '部署阈值',
  deploy_button_clear_review_markers_on_deploy:
    '在部署时保留照片审核标记。如果未选中，默认将清除照片审核标记。',
  suggestion_report_range: '建议报告范围',
  suggestion_report_range_tooltip: '确定性： 请根据建议修改标签。',
  suggestion_report_range_tooltip_2: '不确定性：请根据真实情况修改标签',
  suggestion_description: '标注AI助手建议结果说明',
  label_scoring_heatmap_description: '标注AI助手在OK图上建议结果说明',
  suggestion_ng_description:
    'AI标注助手在OK图上有小缺陷的情况说明：有明显的高对比度的小范围清晰区域.',
  suggestion_ignore_description:
    'AI标注助手在OK图没有缺陷的情况说明:没有任何区域因高对比度而突出,可以忽略此类建议.',
  suggestion_ok_description:
    'AI标注助手在OK图上有大面积缺陷的情况说明:有明显的高对比度的大面积区域.',
  suggestion_color_1: '确定结果色阶',
  suggestion_color_2: '不确定结果色阶',
  suggestion_color_3: '背景颜色',

  central_machine: '训练机',
  edge_machine: '产线机',

  password_input: '请输入密码',
  password_admin_info: '如不知管理员密码，请联系 UnitX 销售人员获取。',
  password_edge_version_low: '此机器软件版本不支持密码管理。',
  password_set_password_success: '成功：设置密码成功',
  password_set_password_failure: '设置密码失败：',
  password_operation_type_admin: '管理员',
  password_operation_type_remote_config: '远程配置',
  password_operation_type_threshold_manage: '阈值管理',
  password_operation_type_switch_production_type: '切换产品型号',
  password_table_column_operation_type: '操作类型',
  password_table_column_edge_machines: '产线机',
  password_table_column_password: '密码',
  password_table_column_edit: '操作',
  password_table_column_enable: '启用',
  password_invalid: '密码长度至少为6个字符。',
  password_incorrect: '密码错误',

  labeled_tab: '已标注',
  unlabeled_tab: '未标注',
  current_feature: '当前特征',
  current_part_type: '当前产品类型',
  LabelFeatureDateSetAppName: '当前特征类型 : ',
  label_feature_no_exist_button: '图像中不存在该特征',
  label_feature_exit_button: '图像中存在该特征',
  toggle_with_spacebar: '使用空格键切换不同视图',
  toggle_with_left_right_arrow_keys: '使用左/右方向键切换不同视图。',

  project_page_title: '项目',
  projects_page_create_new_project_button: '创建新项目',
  projects_page_no_projects_yet: '尚无项目',
  projects_page_validate_project_name_already_exists:
    '具有此名称的项目已存在。',
  projects_page_validate_project_name_too_long: '项目名称不能超过100个字符',
  project_page_validate_project_name_too_short: '项目名称不能为空。',
  projects_page_delete_project_confirmation: '您确定要删除此项目吗？',
  projects_page_project_card_edit_action: '编辑',
  projects_page_project_card_delete_action: '删除',
  projects_page_project_card_last_updated_time: '最后更新: %s',
  projects_page_edit_project_dialog_edit_project_title: '编辑项目',
  projects_page_edit_project_dialog_edit_project_name: '编辑项目名称',
  projects_page_edit_project_dialog_edit_project_description: '编辑项目描述',
  projects_page_project_dialog_cancel: '取消',
  projects_page_project_dialog_save: '保存',
  project_page_create_project_dialog_create_project_title: '创建项目',
  project_page_create_project_dialog_new_project: '项目名称',
  project_page_create_project_dialog_description: '描述',
  project_page_open_project_button: '打开项目',
  project_page_project_dialog_project_description:
    '项目描述必须少于1000个字符。',
  project_page_error_fetching_projects:
    '无法获取项目。请尝试刷新或重启CorteX。',
  project_page_search_bar_prompt: '搜索项目',

  project_page_part_types_header: '产品类型',
  project_page_project_description_header: '描述',
  project_page_manage_part_types_for_product: '管理产品类型',

  project_page_export_project_button: '导出',
  project_page_export_project_button_title: '导出项目',
  project_page_export_project_dialog_title: '导出项目:',
  project_page_export_project_dialog_export_button: '导出',
  project_page_export_project_dialog_cancel_button: '取消',
  project_page_export_project_dialog_exporting: '正在导出...',
  project_page_export_project_dialog_export_success: '项目导出成功！',
  project_page_export_project_dialog_export_failed_with_error:
    '导出项目失败。错误:',
  project_page_export_project_dialog_download_message:
    '此操作将从该项目中导出以下内容到一个 pickle 文件：',
  project_page_export_project_dialog_download_message_images: '图像',
  project_page_export_project_dialog_download_message_feature_dataset:
    '特征数据集数据',
  project_page_export_project_dialog_find_exported_file_message:
    '导出的文件将自动保存到您的下载文件夹。',
  project_page_export_project_dialog_find_exported_file_folder_name: '(~/下载)',
  project_page_import_project_button: '导入项目',
  project_page_import_project_dialog_title: '导入项目',
  project_page_import_project_dialog_help_text:
    '选择一个项目导出文件（.pickle）进行导入',
  project_page_import_project_file_label: '导入文件',
  project_page_import_project_file_placeholder: '选择项目文件',
  project_page_import_project_dialog_cancel_button: '取消',
  project_page_import_project_dialog_import_button: '导入',
  project_page_import_project_dialog_importing: '正在导入...',
  project_page_import_project_success: '项目导入成功',
  project_page_import_project_error: '项目导入失败.',
  project_page_import_project_error_no_response: '无法导入项目。请重试。',
  project_page_import_project_error_dialog: '项目导入失败:',
  project_page_import_project_invalid_file:
    '请选择一个有效的项目导出文件（.pickle）',
  project_page_import_project_missing_file:
    '请选择一个项目 pickle 文件进行导入',

  manage_feature_dialog_search_placeholder: '按特征名称搜索',
  manage_feature_dialog_search_label: '搜索',
  manage_feature_dialog_segment_feature_tab: '分割',
  manage_feature_dialog_location_feature_tab: '位置',
  manage_feature_dalog_feature_action_edit: '编辑',
  manage_feature_dalog_feature_action_delete: '删除',
  manage_feature_dialog_empty_feature_name_error: '特征名称不能为空。',
  manage_feature_dialog_feature_name_too_long_error:
    '特征名称不能超过100个字符。',
  manage_feature_dialog_create_feature_title: '创建%s类型特征',
  manage_feature_dialog_create_feature_button: '创建特征',
  manage_feature_dialog_update_feature_button: '更新特征',
  manage_feature_dialog_edit_feature_button: '编辑特征',
  manage_feature_dialog_delete_feature_button: '删除特征',
  manage_feature_dialog_part_type_multi_select: '产品类型',
  manage_feature_dialog_create_segment_feature: '创建分割特征',
  manage_feature_dialog_create_location_feature: '创建位置特征',
  manage_feature_dialog_part_type_required:
    '特征必须与至少一种产品类型相关联。',
  manage_feature_dialog_feature_type: '特征类型：%s',
  manage_feature_dialog_feature_property: '特征属性：',
  manage_feature_dialog_feature_property_survey: '特征属性：调查',
  manage_feature_dialog_feature_label_shape_type: '特征标签形状类型: %s',
  product_page_app_name_title: '项目产品页面：%s',
  product_page_page_title: '%s的产品类型',
  product_page_no_part_types_yet_msg: '尚无产品类型',
  product_page_error_fetching_part_types: '获取产品类型时出错',
  product_page_create_part_type_button: '创建产品类型',
  product_page_manage_all_feature_types_button: '管理所有特征类型',
  product_page_product_feature_list_segment_features_header: '分割特征',
  product_page_product_feature_list_location_features_header: '位置特征',
  product_page_product_feature_list_add_new_segment_feature_button:
    '添加分割特征类型',
  product_page_product_feature_list_add_new_location_feature_button:
    '添加位置特征类型',
  product_page_product_feature_25d_feature_warning:
    '2.5D标志关闭，但包含2.5D特征。 要对该功能进行操作，请在StarX中打开该标志。\n2.5D特征: %s',
  product_page_product_card_description: '描述',
  product_page_product_card_delete_button: '删除',
  product_page_product_card_edit_button: '编辑',
  product_page_create_product_dialog_product_name: '产品类型名称',
  product_page_create_product_dialog_product_description: '描述',
  product_page_create_product_dialog_product_title: '创建产品类型',
  product_page_edit_product_dialog_product_title: '编辑产品类型',
  product_page_edit_product_dialog_product_name: '产品类型名称',
  product_page_edit_product_dialog_product_description: '描述',
  product_page_product_search_bar: '搜索产品类型',
  product_page_delete_part_type_confirmation: '您确定要删除此产品类型吗？',
  product_page_manage_feature_types_for_product: '管理特征类型',
  product_page_manage_feature: '管理特征',
  product_page_product_name_validation_name_exists: '产品类型名称已存在。',
  product_page_product_name_validation_name_too_long:
    '产品类型名称必须少于100个字符。',
  product_page_product_name_validation_name_empty: '产品类型名称不能为空。',
  product_page_product_description_validation_too_long: '产品类型描述过长。',

  manage_feature_types_error_fetching_feature_types:
    '无法获取特征类型。请稍后再试。',
  manage_feature_types_feature_dialog_feature_name: '特征名称',

  manage_feature_types_feature_dialog_label_shape_type: '选择标签形状类型',
  manage_feature_types_feature_dialog_label_shape_type_required:
    '位置特征需要标签形状类型',
  manage_feature_types_feature_dialog_label_shape_type_point: '点',
  manage_feature_types_feature_dialog_label_shape_type_line_segment: '线段',
  manage_feature_types_feature_dialog_label_shape_type_circle: '圆形',

  threshold_tuning_threshold_update_error_cleaning_up_simulation_data:
    '清除历史模拟数据以启动新阈值模拟调整时发生错误。请等待几秒钟后再试一次。',

  core_project_page_title: '项目工作区',
  core_project_page_view_images_tab: '1. 审查图片',
  core_project_page_label_feature_dataset_tab: '2. 标注特征数据集',
  core_project_page_train_network: '3. 训练网络',
  feature_centric_exit_warning:
    '刚才的标签还没有保存如果此时退出标记过程，则标签将被丢弃。请确认是否要退出贴标流程?',
  filesidebar_discard_warning:
    '这个图像只有一个特征。此时丢弃图像也将从图像中删除指定的产品类型和特征',
  feature_centric_exit: '退出标记',

  archived_projects_page_title: '已归档项目',
  archived_projects_error_fetching_projects:
    '无法获取已归档的项目。请尝试刷新或重启CorteX。',
  archived_projects_no_projects_yet: '暂无已归档项目',
  archived_project_restore_project_success_notification: '项目恢复成功！',
  archived_project_restore_project_error_notification:
    '恢复项目失败。请再试一次。',
  archived_project_restore_project_confirmation: '您确定要恢复此项目吗？',
  archived_project_restore_project_button: '恢复项目',
  view_archived_projects_button: '查看已归档项目',
  computing_power_scheduling_button: '算力调度',
  project_page_archive_project_success: '项目已成功归档！',
  project_page_archive_project_error: '归档项目失败。请再试一次。',
  project_page_archive_button: '归档',
  project_page_archive_button_confirmation: '您确定要归档此项目吗？',
  individual_project_archive_page_title: '%s的项目归档',
  individual_project_archive_page_feature_archive_tab: '特征归档',
  individual_project_archive_page_network_archive_tab: '网络归档',
  feature_archive_restore_feature_success_notification: '特征恢复成功！',
  feature_archive_restore_feature_error_notification:
    '特征恢复失败。请再试一次。',
  feature_archive_restore_button: '恢复',
  feature_archive_restore_confirmation: '您确定要恢复此特征吗？',
  open_individual_project_archive_button: '查看归档项目数据',
  feature_confirm_archive_action_message:
    '您确定要存档此功能吗？存档的功能无法在活动网络中使用。',
  feature_archive_archive_button: '归档',
  feature_archived_success_notification: '特征归档成功！',
  feature_archived_error_notification: '特征归档失败。请再试一次。',

  file_side_bar_sort_property_image_name: '图像名称',
  file_side_bar_sort_property_import_time: '导入时间',
  file_side_bar_sort_property_last_updated: '最后更新时间',
  file_side_bar_filter_part_type_title: '产品类型',
  file_side_bar_filter_feature_title: '特征',

  feature_dataset_error_fetching_images:
    '获取图像时出错。请尝试刷新或重新启动CorteX。',

  label_feature_dataset_page_erorr_fetching_datasets:
    '无法获取功能数据集。请尝试刷新或重新启动CorteX。',
  label_feature_dataset_page_no_datasets_yet:
    '尚无功能数据集。尝试将功能分配给产品类型并将图像分配给此产品类型和功能。',
  label_feature_dataset_only_display_empty_feature_dataset_switch:
    '仅显示空功能数据集',
  label_feature_dataset_feature_absent_tooltip: '已标记为特征不存在',
  label_feature_dataset_labeled_tooltip: '已标注',
  feature_dataset_image_count_not_available: '不可用',
  feature_dataset_action_view_images_button: '管理数据集',
  feature_dataset_action_add_images_to_dataset_button: '将图像添加到数据集',
  feature_dataset_action_images_imported_confirmation: '图像导入成功！',
  feature_dataset_table_part_type_header: '产品类型',
  feature_dataset_table_total_images_header: '总图像数',
  feature_dataset_table_training_images_header: '训练图像',
  feature_dataset_table_validation_images_header: '验证图像',
  feture_dataset_table_actions_header: '操作',
  feature_dataset_search_prompt: '搜索功能数据集',
  feature_dataset_segmentation_features_title: '分割特征数据集',
  feature_dataset_location_features_title: '位置特征数据集',
  feature_dataset_view_options: '查看选项',

  feature_dataset_review_image_unassigned_tab: '未分配',
  feature_dataset_review_image_assigned_tab: '已分配',
  feature_dataset_review_image_search_bar_place_holder: '按名称搜索图片',
  feature_dataset_update_assigned_types_button: '更新分配类型',
  feature_dataset_feature_in_image_tab: '图像中的特征',
  feature_dataset_feature_not_in_image_tab: '图像中没有的特征',
  feature_dataset_feature_in_image_option_info:
    '在图像中标记特征有助于网络更好地学习并减少误检结果。',
  feature_dataset_feature_not_in_image_option_info:
    '标记不存在于此图像中的特征有助于网络区分特征与背景，并减少漏检结果。',
  feature_dataset_update_assigned_types_button_disabled_tooltip:
    '必须选择一个产品类型和至少一种特征才能更新此图像的分配。',

  feature_dataset_discard_image_warning:
    '确定要将此图像从项目中删除吗？此操作无法撤销。',
  feature_dataset_discard_image_button: '从项目中删除图像',
  feature_dataset_select_part_type_prompt: '选择产品类型',

  feature_image_update_assigned_images_success_message: '成功更新分配的类型！',
  feature_image_update_assigned_images_error_message:
    '更新分配的类型失败。请再试一次。',

  networks_incremental_with_at_least_one_head_required: '至少需要一个头',
  networks_feature_map_required: '至少需要一个特征映射',
  networks_feature_map_with_at_least_one_feature_required: '至少需要一个特征',
  networks_feature_map_with_too_many_features: '特征图最多只能包含 %s 个特征',
  networks_feature_map_with_at_least_one_part_type_required:
    '至少需要一个产品类型',
  networks_no_network_config_selected: '未选择网络配置',

  networks_table_title: '网络',
  segmentation_networks_table_title: '分割网络',
  location_networks_table_title: '位置网络',
  networks_table_filter_list: '筛选列表',
  networks_table_clear_filter_button: '清除筛选器',
  networks_table_name_column_header: '名称',
  networks_table_tags_column_header: '标签',
  networks_table_features_column_header: '特征',
  networks_table_status_column_header: '状态',
  networks_table_part_types_column_header: '产品类型',
  networks_table_created_at_column_header: '创建时间',
  networks_table_updated_at_column_header: '修改时间',
  networks_table_trained_at_column_header: '训练时间',
  networks_table_actions_column_header: '操作',
  networks_table_rows_per_page: '每页行数',
  networks_resize_ratio: '调整比例',
  networks_resize_ratio_validate: '调整比例必须为正整数',
  networks_resize_ratio_warning: '⚠ 缩放比例处于警告范围，可能会影响模型质量。请考虑增加缩放比例。',
  networks_resize_ratio_info: '缩放比例分类 — 过小: 1-%s, 警告: %s-%s, 良好: %s-100',
  networks_resize_ratio_error_labels_too_small_warning: '⚠ 一些标签太小无法用于训练（在当前缩放比例下小于5×5或3×3），可能会影响模型质量。请考虑增加标签大小。',
  networks_resize_ratio_info_dialog_title: '缩放比例说明',
  networks_resize_ratio_explanation: '缩放比例会分别应用于图像的宽度和高度。',
  networks_calculating_resize_ratio: '正在计算缩放比例阈值...',
  networks_feature_map: '特征映射',
  networks_feature_type: '特征类型',
  current_network_config_feat_map_title: '当前网络配置特征映射',

  network_training_status_created_at: '创建时间',
  network_training_status_project_name: '项目名称',
  network_training_status_part_type: '产品类型',
  network_training_status_model_version: '模型名称版本',
  network_training_status_application: '功能',
  network_training_status_application_segmentation: '分割',
  network_training_status_application_location: '定位',
  network_training_status_training_status: '状态',
  network_training_status_training_status_pending: '等待中',
  network_training_status_training_status_running: '运行中',
  network_training_status_training_status_complete: '完成',
  network_training_status_training_status_failed: '失败',
  network_training_status_training_status_canceled: '已取消',
  network_training_status_details: '详情',
  network_training_status_refresh: '刷新',
  network_training_status_last_refresh_time: '上次刷新时间',

  empty_dataset_tooltip: '空数据集',
  compact_mode_tooltip: '紧凑模式',
  fullscreen_mode_tooltip: '全屏模式',
  card_view_tooltip: '卡片视图',
  table_view_tooltip: '表视图',
  model_version_gallery_title: '网络/版本',
  model_version_gallery_empty: '尚无模型版本',
  model_versions_per_page: '每页显示模型数量',
  model_version_feat_map_diff_no_changes: '没有变化',
  model_version_details_title: '模型版本详情',
  model_version_information_title: '信息',
  model_version_feature_map_title: '特征映射',
  model_version_feature_data_title: '特征数据',
  model_version_feature_comparison_title: '特征比较',
  model_version_feature_migration_title: '特征迁移',
  model_version_trained_from_scratch: '从头开始训练',
  model_version_trained_incremental: '增量训练自 %s',
  model_version_delete_prompt: '确定要删除此模型版本吗？',
  model_version_cancel_training_prompt: '确定要取消此模型版本的训练吗？',
  model_version_delete_button: '删除',
  model_version_deploy_untrained_error: '无法部署未训练的模型版本。',
  model_version_deploy_archived_features_disabled:
    '无法部署未完成的模型版本。请检查特征是否已归档。',
  model_version_description: '描述',
  model_version_description_can_not_exceed_1000_characters:
    '描述不能超过1000个字符。',
  model_version_inference_results: '推理结果',
  model_version_validation_result_disabled:
    '未训练的模型版本无法查看验证结果。',
  model_version_validation_result_description:
    '[模型评估] 查看选择特征数据集中的标记和未标记图像的模型验证结果。',
  model_version_inference_result_disabled: '未训练的模型版本无法查看推理结果。',
  model_version_inference_result_description:
    '[推理结果] 查看选择特征数据集中的标记和未标记图像的模型推理结果。',
  model_version_table_header_version: '版本',
  model_version_table_header_training_type: '训练类型',
  model_version_table_header_parent_model_version: '父模型版本',
  model_version_table_header_training_status: '训练状态',
  model_version_table_header_model_evaluation: '模型评估',
  model_version_table_header_training_action: '训练',
  model_version_table_header_deploy_action: '部署',
  model_version_table_header_delete_action: '删除',
  model_version_training_time_minutes: '分钟',
  model_version_training_time_seconds: '秒',
  took: '花了',

  network_config_has_extra_features:
    '网络配置包含额外的特征。请参考特征比较部分。',
  network_config_is_missing_features: '网络配置缺少特征。请参考特征比较部分。',
  network_config_is_missing_part_types:
    '网络配置缺少产品类型。请参考特征比较部分。',

  network_train_in_queue_disabled: '训练已禁用。该网络处于训练队列中。',
  network_train_from_scratch_archived_features_disabled:
    '从头开始训练未完成。请检查特征是否已归档。',
  network_train_from_scratch_empty_datasets_disabled:
    '从头开始训练未完成。请检查数据集是否为空。',
  network_train_from_scratch_default_tooltip: '从头开始训练。',
  network_train_incremental_not_trained_disabled: '增量训练未完成。',
  network_train_incremental_archived_features_disabled:
    '增量训练未完成。请检查特征是否已归档。',
  network_train_incremental_empty_datasets_disabled:
    '增量训练未完成。请检查数据集是否为空。',
  network_train_incremental_default_tooltip: '增量训练',

  training_setup_start_training_button: '开始训练',
  training_setup_selected_heads_description:
    '选定的特征将在当前特征数据集上进行训练。',
  training_setup_bypassed_heads_description:
    '该模型仍将检测绕过的特征，但不会在当前特征数据集上对它们进行训练。',
  training_setup_selected_features: '已选择的特征',
  training_setup_bypassed_features: '已绕过的特征',
  training_setup_validation_error: '请至少选择一个特征进行训练',
  training_setup_auto_assign_validation_images: '自动分配验证图像',
  training_setup_hide_valid: '隐藏合格项',
  training_setup_network_level_validation: '网络验证',
  training_setup_labeled_dataset_level_validation: '标记数据集验证',
  training_setup_feature_level_validation: '特征级验证',
  training_setup_feature_level_criteria: '带有所需标签的总训练图像',
  training_setup_network_level_criteria: '网络级别标准',
  training_setup_labeled_dataset_level_criteria: '标记数据集级别标准',
  training_setup_labeled_dataset_level_criteria_tooltip:
    'GenX AI生成的图片不会被添加到验证集',
  training_setup_network_level_no_issue: '无问题',
  training_setup_network_level_issue: '发现网络级别问题。',
  training_setup_labeled_dataset_level_no_issue: '无问题',
  training_setup_labeled_dataset_level_issue: '发现数据集级别问题。',
  training_setup_feature_level_no_issue: '未发现特征级别问题。',
  training_setup_feature_level_issue: '发现特征级问题。',
  current_required_image_prefix: '当前/需要',
  filled_quota_title: '已填充配额(%)',

  move_all_to_selected: '全部移动到已选择',
  move_all_to_bypassed: '全部移动到绕过',
  move_flagged_to_selected: '移动标记到已选择',
  move_flagged_to_bypassed: '移动标记到绕过',
  archived_project_last_archived_timestamp: '存档于: %s',
  project_name_contains_invalid_character_message:
    '项目名称中唯一允许的特殊字符是 - 和 . 和 [] 以及 _',

  deleted_base_model: '已删除基础模型版本',

  raw_image: '原始图像',
  view_inference_results: '查看推理结果',
  selected_feature: '已选择的特征',
  selected_part_type: '已选择的产品类型',
  view_inference_results_by_dataset: '按数据集查看推理结果',
  dataset_select: '数据集选择',
  data_select_error: '请选择特征和产品类型',
  inference_results_for: '推理结果',
  validation_results_for: '验证结果',
  segmentation_inference_result_tooltip_coordinates: 'XY: 点的坐标。',
  segmentation_inference_result_tooltip_vh_bounding_boxes:
    'VH: 垂直和水平的最小边界框尺寸。',
  segmentation_inference_result_tooltip_mr_bounding_boxes:
    'MR: 最小矩形的最小边界框尺寸。',
  location_inference_result_tooltip_points: 'XY: 点的坐标。',
  location_inference_result_tooltip_lines: 'XY: 线的起点和终点坐标。',
  location_inference_result_tooltip_circles: 'XY: 圆心坐标。R: 圆的半径。',
  invalid_dataset: '无效数据集',
  no_inference_result: '模型未能检测到当前特征在此图像上。',

  product_page_num_results_showing: '显示 %s / %s 产品类型',
  product_page_default_result_text: '显示 %s 个产品类型（最多允许 %s 个）',
  disabled_create_part_type_button_tooltip:
    '无法为项目创建超过 30 个产品类型。请创建一个新项目。',
  project_page_num_results_showing: '显示 %s / %s 项目',
  project_page_default_result_text: '显示 %s 个项目',

  virtualized_file_side_bar_filter_settings_2_filters_applied:
    '已应用 2 个筛选器',
  virtualized_file_side_bar_filter_settings_1_filter_applied:
    '已应用 1 个筛选器',
  cortex_exit_confirmation_dialog: '您确定要退出CorteX吗？',
  cortex_exit_confirmation_training_in_progress_dialog_warning:
  '您确定要退出 CorteX 吗？\n 当前正在进行网络训练，但在退出 CorteX 后训练将继续在后台进行。',
  cortex_exit_confirmation_training_in_progress_dialog_warning_logged_out:
    '您确定要退出 CorteX 吗？\n 先前已启动的网络训练可能仍在进行中。在退出 CorteX 后，训练将继续在后台进行。如需查看训练状态，请重新登录。',

  cortex_exit_button: '退出',
  generate_feature: '生成特征',

  manage_feature_dialog_feature_property_required: '特征属性为必填项',
  feature_property_question: '当前创建的特征属于下列哪个选项？',
  feature_property_option_yes: '是',
  feature_property_option_yes_desc:
    '需要结合OK一起查看，单独查看无法判断为NG。',
  feature_property_option_no: '否',
  feature_property_option_no_desc: '无需对比OK，缺陷单独可判断是否为NG。',
  feature_property_option_not_sure: '不确定',
  feature_property_option_not_sure_desc: '如果您不确定选择什么，可以选择这个。',
  feature_property_manual_result:
    '根据您的调查问卷答复，未生成任何特征属性。请手动选择缺陷特征属性。',
  feature_property_option_independent: '独立特征',
  feature_property_option_independent_desc:
    '缺陷独立存在，与周围背景无关联，缺陷范围边界明显，如：压痕、划痕、凹坑',
  feature_property_option_background_related: '背景相关特征',
  feature_property_option_background_related_desc:
    '缺陷与周围背景相连，缺陷边界不明显，需要结合背景判断是否为缺陷，如：褶皱和撕裂、铜粉和磨损痕迹、橘皮和划痕',
  feature_property_option_structural_feature: '结构特征',
  feature_property_option_structural_feature_desc:
    '缺陷会影响工件的整体结构或形状，如折损、异常弯曲、形状缺失等。',
  feature_property_option_surface_feature: '表面特征',
  feature_property_option_surface_feature_desc:
    '缺陷只影响工件表面，不改变工件整体结构或形状，如漏金属、异物、污渍等。',
  feature_property_resolution_is: '根据您的选择，特征为: ',
  current_feature_property: '当前特征属性',
  open_feature_property_questionnaire: '修改特征属性',
  network_config_has_different_feature_properties:
    '特征属性已修改，进阶训练特征不可用，请重新开始训练',
  feature_properties: '特征属性',
  properties: '特性',
  feature_context_dependency_background_dependent_label: '背景依赖',
  feature_context_dependency_self_contained_label: '表面独立',

  example_defect_object_missing_caption: '目标缺失',
  example_defect_different_color_caption: '颜色异常',
  example_defect_stains_caption: '脏污',
  example_defect_pitted_dent_caption: '凹坑',
  example_defect_indentation_caption: '压伤',
  example_defect_scratch_caption: '刮伤',
  example_defect_wrinkles_and_tears_caption: '褶皱和撕裂',
  example_defect_copper_powder_and_abrasion_marks_caption: '铜粉和磨损',
  example_defect_orange_peel_and_scratch: '橘皮和刮痕',
  example_defect_exposed_metal_caption: '露金属',
  example_defect_fod_caption: '异物',
  example_defect_bending_deformation_caption: '弯曲变形',
  example_defect_beveled_caption: '歪斜',
  example_defect_unevenness_and_irregularity_caption: '凹坑和凸起',

  feature_property_questionnaire_next_button: '下一步',
  feature_property_questionnaire_finish_button: '结束',
  feature_property_questionnaire_back_button: '回去',

  feature_crop_property_background_dependent_suggestion:
    '您可以为此特征添加更多带有“特征不在图像中”的图像，以帮助网络学习该特征。',
  feature_crop_property_self_contained_suggestion:
    '在训练期间，该特征将根据标签自动裁剪，请在图像中标记所有特征。',
  feature_and_part_type_title: '特征 x 产品类型',
  suggestion: '特征属性AI指引',
  feature_property_disclaimer_question:
    '您可以通过重新填写问卷修改特征属性，修改后需要从头训练模型，不能基于当前版本进阶训练。',
  feature_property_disclaimer_prompt:
    '模型识别效果可能会有所变化。确定要修改特征属性？ ',
  feature_property_question_required: '请选择特征属性。',
  generate_image: '生成式图片',
  generate_discard_image_warning: '添加到生成图片中的图片不能丢弃!',
  feature_archive_disabled_tooltip_message:
    '无法归档该特征，因为它出现在一个活动网络中。',
  still_editing_label:
    '还有一个未完成的标签。继续操作将丢弃未完成的标签。你确定吗？',

  filter_labeled_image_option_image_has_feature: '有特征',
  filter_labeled_image_option_image_no_feature: '无特征',

  label_evaluation_snackbar_ignore_button: '忽略',
  label_evaluation_snackbar_view_button: '查看',
  label_evaluation_show_evaluations_switch_disabled_tooltip:
    '此功能没有可用的标签评估。运行标签评估以生成结果。',
  label_evaluation_label_page_show_evaluation_switch: '评估',
  label_evaluation_label_page_label_evaluation_radio_button_label: '评估',
  label_evaluation_status_chip_completed: '评估已完成',
  label_evaluation_status_chip_waiting: '等待评估：队列位置%s',
  label_evaluation_status_chip_in_progress: '评估进行中：%s',
  label_evaluation_status_chip_in_progress_before_countdown:
    '评估进行中：正在准备数据',
  label_evaluation_status_chip_failed: '评估失败',
  label_evaluation_status_chip_cancelled: '评估已取消',
  label_evaluation_run_button: '运行标签评估',
  label_evaluation_cancel_button: '取消标签评估',
  label_evaluation_success_snackbar_message: '标签评估：特征%s完成。',
  label_evaluation_failed_snackbar_message: '评估失败: 特性 %s 未能完成。',
  label_evaluation_label_page_title: '标签评估',
  label_evaluation_label_page_evaluation_time: '于%s生成的评估结果可供查看',
  label_evaluation_label_page_new_eval_completed:
    '新评估结果已准备好，刷新以查看',
  label_evaluation_label_page_title_tooltip: '显示上一次完成的标签评估结果。',
  label_evaluation_refresh_successful_snackbar_message: '刷新评估结果成功',

  part_type_feature_config: '特征配置',
  part_type_view_config: '视野配置',
  part_type_no_view_config_message: '无视野配置',
  feature_list: '特征列表',
  view_list: '视野列表',
  create_view: '创建视野',
  edit_view: '编辑视野',
  view_name: '视野名称',
  cc_name: 'CC名称',
  camera_source: '设备来源',
  Add_controller_CCs: '添加控制器CCs',
  Add_camera_CCs: '添加相机CCs',
  Add_CCs: '添加CCs',
  Sequence: '打光序列',
  Update_time: '更新时间',
  Switch_Sequence: '切换序列',
  Manage_Sequence: '管理打光序列',
  Delete_Sequence: '删除打光序列',
  Delete_Sequence_warning: '确定要删除此打光序列吗？',
  Delete_Sequence_tootip: '该序列已被使用，不能删除',
  Clear_Sequence_warning: '确定要清除当前打光序列吗？CC与特征关系也将一并清除',
  Switch_Sequence_warning: '切换序列将覆盖当前序列，并需要重新配置CC与特征',
  Sequence_no_data: '暂无打光序列',
  Sequence_no_data_text: '请先在OptiX上传打光序列',
  Sequence_validation_failed: '序列验证失败',
  Sequence_validation_unknown_error: '未知错误',
  Sequence_already_used: '该序列已在同一物料类型中使用',
  Sequence_no_longer_valid_reconfig:
    '该序列不再有效。请重新配置序列并重新上传。',
  Add_CCs_tooltip: '请先选择打光序列',
  Add_CCs_tooltip_warning: '2.5D视野不能有一个以上的CC。',
  Disabled_25D_tooltip_warning:
    '配置禁用了 2.5D；除删除外，无法对视图/CC 执行其他操作。',
  view_config_info_message: '这个视觉解决方案用于ProdX的运行时配置',
  view_config_min_max_info_message:
    '请确保视图名称与序列名称一致，否则在运行ProdX的时出现错误',
  open_central: '进行部署',
  external_image_source_id: '图源ID',
  image_width: '图片宽度',
  image_height: '图片高度',
  image_channel: '图片通道',
  image_width_label: '宽',
  image_height_label: '高',
  sequence_mode: '序列模式',
  network_tab_default: '默认的',
  backend_train_server_resp_cancelled: '取消',
  backend_train_server_resp_training_in_progress: '正在训练',
  backend_train_server_resp_training_in_progress_info: '训练中',
  backend_train_server_resp_added_to_queue: '已经加入训练序列',
  backend_train_server_resp_training_done: '训练完成',
  network_view_config_messgae: '没有视图配置的模型不能在ProdX环境中运行',
  select_data_time: '选择时间日期',
  label_evaluation_train_schedule_type: '标签评估',
  statistics_by_shift: '按班次统计',
  statistics_by_day: '按天统计',
  start_date: '开始时间',
  end_date: '结束时间',
  time_hour: '小时',
  time_minute: '分钟',
  shift_configuration: '班次配置',
  today: '今天',
  last_2_days: '过去 2 天',
  last_3_days: '过去 3 天',
  last_7_days: '过去 7 天',
  last_30_days: '过去 30 天',
  confirm: '确认',
  shift_note: '至少2个班次，只需要设置开始时间',
  shift: '班次',
  add_shift: '添加班次',
  shift_rule_number: '至少需要设置2个班次',
  shift_rule_time: '班次总时间必须等于24小时',
  label_evaluation_not_enough_labeled_images_warning:
    '特征数据集必须至少包含2张标注图像才能开始标注评估。',

  two_five_d_reset_camera_view_button: '重置相机视角',
  two_five_d_image_view_slider: '滑块',

  part_statistics: '物料统计',
  ng_defect_statistics: 'NG缺陷统计',
  limit_defect_statistics: '限制缺陷统计',
  part_value: '数量',
  part_percentage: '百分比',
  statistics_no_data: '暂无数据',
  statistics_no_data_text: ' 请先选择其他时间范围国后再查询',
  statistics_high_value_data_expired_title: '高价值图像已过期。',
  statistics_high_value_data_expired_subtitle: '由于 3 天的数据保留策略，高价值图像数据已不可用。请选择更近期的时间范围。',
  statistics_high_value_data_cleared_title: '部署后高价值图像已被清除。',
  statistics_high_value_data_cleared_subtitle: '新的部署重置了高价值图像数据。请重新运行生产流程以生成新的高价值图像。',
  statistics_high_value_data_not_found_title: '未找到高价值图像。',
  statistics_high_value_data_not_found_subtitle: '所选特征未找到高价值图像。模型可能已经表现良好，或者您可以手动添加 NG 图像以增强训练效果。',
  shift_rule_max_number: '最多只能设置5个班次',
  part_statistics_date: '日期',
  part_statistics_shift: '班次',
  part_statistics_total: '总数',
  part_statistics_abnormal: '异常数量',
  part_statistics_abnormalRate: '异常率',
  part_statistics_normal: '正常数量',
  part_statistics_ok: '良品数量',
  part_statistics_ng: '不良品数量',
  part_statistics_limit: '临界品数量',
  part_statistics_yieldRate: '良率',
  top_5_highest_quantity: '数量最高的前五名',
  top_5_lowest_quantity: '数量最低的前五名',
  customize_defect_selection: '自定义缺陷选择',

  feature_list_empty: '必须提供功能列表',
  two_five_d_error_loading_image_msg: '加载图片错误',
  two_five_d_error_loading_enable_25d:
    '从 StartX 加载 2.5D 设置时出现错误。请前往 StartX 中的“System Config”并检查“enable_25d”配置项。',

  twoFiveD_rotate_instruction: '旋转：Shift + 鼠标左键拖动',
  twoFiveD_zoom_instruction: '缩放：Shift + 鼠标滚轮',
  twoFiveD_pan_instruction: '平移：Shift + 鼠标右键拖动',
  twoFiveD_addnode: '添加节点：D / 鼠标左键点击网格',
  twoFiveD_endshape: '结束形状：S / 鼠标右键点击网格',

  twoFiveD_switch_mean_image: '切换到均值图像: Shift + 1',
  twoFiveD_switch_normal_image: '切换到法线图像: Shift + 2',
  twoFiveD_switch_height_image: '切换到高度图像: Shift + 3',
  production_report_v3_part_statistics_feature_select_placeholder_feature:
    '缺陷',
  production_report_v3_part_statistics_feature_select_placeholder_view: '视野',
  two_five_d_image_viewer_instructions: '2.5D 图像查看器说明',
  shift_time_conflict: '班次时间不能重叠，请选择不同的时间。',
  shift_time_checked: '轮班时间小于30分钟，请选择不同的时间。',
  feature_quantity: '特征量',
  show_judgment_pattern: '显示判断模式',
  part_type: '产品类型',
  image_set_feature_dateset_text: '原图会添加到对应的数据集中，请及时标注',
  part_statistics_filter_option_all: '所有图片',
  part_statistics_manual_review: '手动审核',
  part_statistics_filter_option_ok: 'OK图片',
  part_statistics_filter_option_ng: 'NG图片',
  part_statistics_filter_option_limit: '临界品图片',
  part_statistics_filter_option_abnormal: '异常图片',
  part_statistics_load_image_error: '加载图片错误',
  part_statistics_view_option: '视野切换',
  part_statistics_delete_confirmation: '删除确认',
  part_statistics_add_image_time: '添加时间 :',
  part_statistics_delete_confirmation_text: '确定要删除',
  part_statistics_check_image_tip:
    '当前图片已添加误判类型，但尚未保存至数据集如切换图片，您所做的修改将不会保存',
  part_statistics_add_false_detection_type: '添加误检类型',
  part_statistics_add_false_detection_type_placeholder: '请选择误检类型',
  part_statistics_add_false_detection_hide_bounding_box: '隐藏图像上的框',
  part_statistics_add_false_detection_show_bounding_box: '显示图像上的框',
  part_statistics_add_false_detection_message: '请添加缺陷类型',
  part_statistics_add_feature_quality: '添加到特征质量集',
  part_statistics_images_dialog_confim_image_basic_info: '图片基本信息',
  part_statistics_images_dialog_confim_image_tip: '图片将被添加到以下数据集中',
  part_statistics_add_quility_message: '图像已添加到质量集',
  part_statistics_quality_standards_view_list: '视野列表',
  shift_view_add_image_to_feature_quality: '添加到特征质量集',
  part_statistics_feature_finish_message: '图片的所有特征已添加到训练集',
  part_statistics_labeled_Feature: '已标注特征',
  part_statistics_images_manual_review_tip: `
  在系统判定结果不准确的情况下，进行人工复判
  1、阈值判定不准确时，忽略系统的判断结果，标记实际缺陷
  将其加入质量集进行阈值优化
  2、模型精度不足时，将其加入特征数据并重新训练模型
  `,
  part_statistics_images_manual_review_tab_feature: '特征数据集',
  part_statistics_images_manual_review_tab_quality: '质量数据集',
  quality_standards: '质量标准',
  shift_view_images_no_view: '视野未找到',
  ng_feature: 'NG特征',
  ok_feature: 'OK特征',
  filter_by_type: '按类型过滤',
  high_value_image_filter_by_label: '按类型筛选',
  high_value_image_filter_all_option: '所有图片',
  high_value_image_filter_high_value_option: '高价值图片',
  high_value_image_section_title: '高价值图片',
  high_value_image_section_description: '该图像已被标记为当前特征的高价值图像，基于最新部署的模型分析结果。',
  high_value_image_section_description_add: '将其添加到特征数据集中可能有助于提升模型性能。',
  high_value_image_section_description_note: '注意：',
  high_value_image_section_description_note_text: '高价值图像将在每次新模型部署后或 3 天后自动清除。',

  limit_feature: '临界特征',
  threshold_v2_production_type: '生产类型',
  threshold_v2_part_type: '部件类型',
  threshold_v2_deploy: '部署',
  threshold_v2_version: '阈值版本：',
  threshold_v2_all_feature: '所有特性',
  threshold_v2_all_status: '所有状态',
  threshold_v2_all_status_enabled: '启用',
  threshold_v2_all_status_disabled: '禁用',
  threshold_v2_table_view: '视图',
  threshold_v2_table_status: '状态',
  threshold_v2_table_judgment: '判断结果',
  threshold_v2_table_operator: '操作',
  threshold_v2_not_found_title: '未找到符合选择标准的阈值',
  threshold_v2_not_found_sub_title: '请调整选择标准',
  threshold_v2_tip_is_delete: '您确定要删除此阈值吗？',
  threshold_v2_tip_view_not_found: '视图未找到',
  threshold_v2_tip_is_deploy: '您确定要部署此阈值吗？',
  threshold_v2_tip_deploy_ok: '部署成功',
  shift_view_images_add_success: '图像添加成功',
  shift_view_images_updated_success: '图像更新成功',
  threshold_v2_running_production_line_tip: '当前%s产线目前正在运行',
  error_creating_image_record_for_image_viewer:
    '创建图像查看器的图像记录时出错: %s',
  error_creating_image_record_no_mask_url: '图像包含掩码，但无法获取掩码 URL。',
  error_creating_image_no_uuid:
    '图像缺失 UUID 。请确保图像数据包含有效的 UUID。',

  threshold_config: '阈值配置',
  threshold_simulation: '阈值模拟',
  threshold_simulation_disable: '阈值已被禁用',
  threshold_simulation_date: '日期',
  threshold_simulation_update_success: '阈值更新成功',
  threshold_simulation_nodata_tip:
    '当前零件类型未配置阈值条件，无法使用模拟功能',
  threshold_simulation_nodata_tip_sub: '请先完成阈值配置',
  threshold_simulation_nodata_tip_button: '开始配置',
  threshold_simulation_disable_tip: '禁用的阈值不会包含在 FA 和 FR 计算中',
  threshold_simulation_start_all_yield: '模拟良率',
  threshold_simulation_save_single: '保存此阈值',
  threshold_simulation_update: '更新到阈值配置',
  threshold_simulation_update_hint_1: '请确认是否将最新数据同步到阈值配置中，',
  threshold_simulation_update_hint_2: '更新后无法撤销。',
  threshold_simulation_update_hint_3:
    '如果需要使用更新后的阈值，请在阈值配置界面中将阈值同步到生产线上。',
  threshold_simulation_update_hint_4: '共修改了%s处，使用当前阈值。',
  threshold_simulation_update_table_col_feature: '特征',
  threshold_simulation_update_table_col_view: '视图',
  threshold_simulation_update_table_col_before: '更新前',
  threshold_simulation_update_table_col_after: '更新后',
  threshold_simulation_yield: '良率',
  threshold_simulation_fr: '过杀率',
  threshold_simulation_fa: '漏杀率',
  threshold_simulation_tip_infos: {
    hover_info: '查看回测功能使用指南助您快速优化阈值!',
    header: '欢迎使用阈值模拟功能',
    feature_1: {
      title: '功能介绍',
      content: '帮助用户快速对阈值进行优化和调整，通过对推理结果的再次判定，实现对良率、FA和FR的计算，每次修改阈值请先使用阈值模拟的功能'
    },
    feature_2: {
      title: '使用说明',
      content_1_1: 'A. 为了快速得到结果，模拟时仅使用 ',
      content_1_2: '阈值+后处理再次计算良率、FA、FR，该过程没有模型参与',
      content_2_1: 'B. 良率结果由产线数据计算得出，',
      content_2_2: '代表着实际的生产情况，',
      content_2_3: 'FA和FR由质量标准数据集得出，',
      content_2_4: '代表着客户的质量标准，',
      content_2_5: '为了得到更加全面的结果，请按照要求添加质量标准数据集',
      content_3_1: 'C. 阈值模拟界面中 ',
      content_3_2: '只能针对阈值的数值进行修改，不支持新增和删除阈值条件'
    },
    feature_3: {
      title: '使用建议',
      content_1_1: '模拟时间控制在 1-3 天，尽量不超过 7 天，',
      content_1_2: '时间范围大时，模拟耗时多',
      content_2_1: '每次仅优化一条阈值，并平衡良率、FA和FR，',
      content_2_2: '得到可接受的结果后，再优化下一条阈值',
      content_3_1: '调整时建议多使用柱状图的',
      content_3_2: '功能，',
      content_3_3: '可以直观查看',
      content_3_4: '缺陷在产线数据中的数量分布情况，',
      content_3_5: '请结合柱状图的分布对阈值进行微调'
    }
  },
  image_assigner_label_cc: 'CC',
  image_information: '图像信息',
  training_set_ok: '训练集OK',
  training_set_ng: '训练集NG',
  validation_set_ok: '验证集OK',
  validation_set_ng: '验证集NG',
  no_available_views_for_feature_type: '此物料中没有支持该图像类型的视图。',

  camera_source_camera_only: '仅相机',
  camera_source_third_party_camera: '第三方相机',
  camera_source_tcp: 'TCP',
  view_sequence_mode_two_d: 'CC/2D',
  view_sequence_mode_min_max: 'Min/Max',
  view_sequence_mode_two_five_d: '2.5D',
  all_checked: '全选',
  no_images_available_tooltip: "由于生产中关闭了图像保存，未保存此物料的原始图像或掩码图像。",
  no_images_saved_for_part_in_production: "生产中未保存此物料的图像。",
  part_search_alert:'查询结果为最近',
  part_search_no_result:'暂无搜索结果',
  part_search_recent_search:'最近搜索',
  part_search_view_history:'最近查看',
  part_search_recent_search_no_result:'暂无搜索记录',
  part_search_placeholder:'请输入物料ID',
  part_search_recent_search_3_days:'最近3天',
  part_search_recent_search_7_days:'最近7天',
  part_search_recent_search_30_days:'最近30天',

  yes: '是',
  no: '否',
  enabled: '启用',
  disabled: '禁用',
  invalid_float_error: '必须是有效数字（例如 0.001 或 1e-3）',
  num_epochs_helper: '完整遍历训练数据集的次数，大于或等于 2 的整数。',
  hyper_parameters: '超参数',
  num_epochs: '训练轮数',
  learning_rate: '学习率',
  label_smoothing: '标签平滑',
  warmup_pct_default: '热身百分比',
  warmdown_start_pct: '冷却开始百分比',
  weight_decay: '权重衰减',
  reset_hyperparameters: '重置超参数',

  validation_invalid_number: '请输入有效的数字',
  validation_must_be_integer: '必须为整数',
  validation_greater_than_one_required: '必须大于1',
};

export default TranslationsCnst;

