#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime


# =========================
# 配置参数
# =========================

OUTPUT_DIR = "/home/unitx/shared_data"

IMAGE_COUNT = 10000              # 图片数量
IMAGE_SIZE = 400 * 1024        # 单张大小 400KB

LOG_FILE = os.path.join(
    OUTPUT_DIR,
    "write_speed_log.txt"
)


# =========================
# 生成模拟图片数据
# =========================

def create_image_data(size):
    """
    生成随机二进制数据
    模拟图片内容
    """
    return os.urandom(size)


# =========================
# 写入单个文件
# =========================

def write_file(filename, data):

    start = time.perf_counter()

    with open(filename, "wb") as f:
        f.write(data)

        # 强制刷新到磁盘
        f.flush()
        os.fsync(f.fileno())

    end = time.perf_counter()

    return end - start


# =========================
# 主程序
# =========================

def main():

    # 创建目录
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    print("=" * 60)
    print("开始磁盘写入测试")
    print("=" * 60)

    print(f"目录: {OUTPUT_DIR}")
    print(f"文件数量: {IMAGE_COUNT}")
    print(
        f"单文件大小: {IMAGE_SIZE/1024:.0f} KB"
    )
    print(
        f"总写入数据: "
        f"{IMAGE_COUNT*IMAGE_SIZE/1024/1024:.2f} MB"
    )

    print("-" * 60)


    # 创建400KB数据
    image_data = create_image_data(
        IMAGE_SIZE
    )


    total_bytes = 0
    speed_list = []


    # 总计时开始
    total_start = time.perf_counter()


    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as log:


        log.write(
            "图片写入速度测试日志\n"
        )

        log.write(
            "=" * 60 + "\n"
        )


        for i in range(1, IMAGE_COUNT + 1):

            filename = os.path.join(
                OUTPUT_DIR,
                f"test_image_{i:04d}.img"
            )


            start_time = datetime.now()


            cost = write_file(
                filename,
                image_data
            )


            end_time = datetime.now()


            speed = (
                IMAGE_SIZE /
                cost /
                1024 /
                1024
            )


            total_bytes += IMAGE_SIZE
            speed_list.append(speed)


            log_line = (
                f"{i:04d} | "
                f"开始: {start_time} | "
                f"结束: {end_time} | "
                f"耗时: {cost:.6f}s | "
                f"速度: {speed:.2f} MB/s\n"
            )


            log.write(log_line)


            print(
                f"[{i}/{IMAGE_COUNT}] "
                f"耗时 {cost:.4f}s "
                f"速度 {speed:.2f} MB/s"
            )



    # 总计时结束
    total_time = (
        time.perf_counter()
        -
        total_start
    )


    # 平均速度
    avg_speed = (
        total_bytes /
        total_time /
        1024 /
        1024
    )


    # 最大最小速度
    max_speed = max(speed_list)
    min_speed = min(speed_list)



    # 写入汇总日志
    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log:

        log.write("\n")
        log.write("=" * 60 + "\n")

        log.write(
            f"总文件数: {IMAGE_COUNT}\n"
        )

        log.write(
            f"总数据量: "
            f"{total_bytes/1024/1024:.2f} MB\n"
        )

        log.write(
            f"总耗时: "
            f"{total_time:.3f} 秒\n"
        )

        log.write(
            f"平均速度: "
            f"{avg_speed:.2f} MB/s\n"
        )

        log.write(
            f"最快速度: "
            f"{max_speed:.2f} MB/s\n"
        )

        log.write(
            f"最低速度: "
            f"{min_speed:.2f} MB/s\n"
        )



    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    print(
        f"总耗时: {total_time:.3f} 秒"
    )

    print(
        f"平均写入速度: "
        f"{avg_speed:.2f} MB/s"
    )

    print(
        f"最快速度: "
        f"{max_speed:.2f} MB/s"
    )

    print(
        f"最低速度: "
        f"{min_speed:.2f} MB/s"
    )

    print(
        f"日志文件: {LOG_FILE}"
    )


if __name__ == "__main__":
    main()
