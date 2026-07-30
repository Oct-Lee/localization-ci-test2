import os
import time
import uuid
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image
import json
from concurrent.futures import ThreadPoolExecutor
import threading

class ImageStorageProgram:
    def __init__(self, config_file='config.json'):
        """
        初始化存图程序
        :param config_file: 配置文件路径
        """
        self.config = self.load_config(config_file)
        
        # 主存储配置
        self.base_path = Path(self.config['base_path'])
        self.image_size = self.config['image_size']  # 图像大小约300KB
        self.total_images = self.config['total_images']  # 190张图
        self.time_limit = self.config['time_limit']  # 21秒
        self.repeat_times = self.config['repeat_times']  # 重复执行次数
        self.round_interval = self.config.get('round_interval', 2)  # 轮次间隔，默认2秒
        
        # 第二存储配置（大图PNG）
        self.secondary_enabled = self.config.get('secondary_enabled', True)
        if self.secondary_enabled:
            self.secondary_path = Path(self.config['secondary_base_path'])
            self.secondary_image_size = self.config['secondary_image_size']  # 18MB
            self.secondary_image_format = self.config.get('secondary_image_format', 'PNG')
            self.secondary_quality = self.config.get('secondary_quality', 95)
            
            # 确保第二存储路径存在
            self.secondary_path.mkdir(parents=True, exist_ok=True)
            print(f"第二存储路径: {self.secondary_path}")
            print(f"第二存储图像大小: {self.secondary_image_size}KB")
        
        # 计算每张图的写入间隔
        self.write_interval = self.time_limit / self.total_images
        
        # 确保基础路径存在
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 线程安全计数器
        self.image_counter = 0
        self.counter_lock = threading.Lock()
        
        print(f"初始化完成 - 基础路径: {self.base_path}")
        print(f"每张图写入间隔: {self.write_interval:.3f}秒")
        print(f"总图像数: {self.total_images}张")
        print(f"轮次间隔: {self.round_interval}秒")
        
    def load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            # 主存储配置
            "base_path": "/home/unitx/unitx_data/data/production/output",
            "image_size": 18000,  # 图像大小KB, 18MB = 18000KB
            "total_images": 190,  # 每个SN的图像数量
            "time_limit": 21,  # 写入时间限制（秒）
            "repeat_times": 500,  # 重复执行次数
            "round_interval": 2,  # 轮次间隔（秒）
            "image_format": "PNG",  # 图像格式
            "image_quality": 100,  # 图像质量（1-100）
            "use_threading": False,  # 是否使用多线程
            "max_workers": 1,  # 最大线程数
            
            # 第二存储配置（大图PNG）
            "secondary_enabled": True,
            "secondary_base_path": "/home/unitx/shared_data",
            "secondary_image_size": 400,  
            "secondary_image_format": "JPEG",
            "secondary_quality": 100
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"读取配置文件失败: {e}，使用默认配置")
                return default_config
        else:
            # 创建默认配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            print(f"创建默认配置文件: {config_file}")
            return default_config
    
    def generate_sn(self):
        """生成虚拟SN"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:8]
        return f"SN{timestamp}{random_suffix}"
    
    def create_image(self, target_size_kb, format='JPEG'):
        """
        创建指定大小的图像
        :param target_size_kb: 目标大小（KB）
        :param format: 图像格式
        :return: PIL Image对象
        """
        # PNG和JPEG压缩比不同
        if format.upper() == 'PNG':
            # PNG是无损压缩，压缩比大约1:1.5
            compression_ratio = 1.5
        else:
            # JPEG有损压缩，压缩比大约1:10
            compression_ratio = 10
        
        # 估算图像尺寸
        target_bytes = target_size_kb * 1024
        pixels_needed = int(target_bytes * compression_ratio / 3)
        
        # 计算宽高比，使用1.5:1的宽高比
        width = int(np.sqrt(pixels_needed * 1.5))
        height = int(width * 2 / 3)
        
        # 确保至少1x1
        width = max(1, width)
        height = max(1, height)
        
        # 生成随机彩色图像
        img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        return img
    
    def save_single_image(self, sn_path, image_index, secondary=False):
        """
        保存单张图像
        :param sn_path: SN目录路径
        :param image_index: 图像索引
        :param secondary: 是否为第二存储
        :return: 保存信息
        """
        start_time = time.time()
        
        try:
            # 根据存储类型选择配置
            if secondary:
                target_size = self.secondary_image_size
                format_type = self.secondary_image_format
                quality = self.secondary_quality
                base_path = self.secondary_path
                suffix = "_png"  # 用于区分文件名
            else:
                target_size = self.image_size
                format_type = self.config['image_format']
                quality = self.config['image_quality']
                base_path = self.base_path
                suffix = ""
            
            # 生成图像文件名
            if secondary:
                filename = f"img_{image_index:04d}.png"
            else:
                filename = f"img_{image_index:04d}.jpg"
            
            filepath = sn_path / filename
            
            # 创建图像
            img = self.create_image(target_size, format_type)
            
            # 保存图像
            save_kwargs = {'optimize': True}
            if format_type.upper() != 'PNG':
                save_kwargs['quality'] = quality
            
            img.save(filepath, format_type, **save_kwargs)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # 验证文件大小
            actual_size = os.path.getsize(filepath) / 1024  # KB
            
            # 如果PNG文件大小偏差太大，重新生成
            if format_type.upper() == 'PNG':
                # PNG文件可能比预期大或小，尝试调整尺寸
                if actual_size < target_size * 0.7 or actual_size > target_size * 1.3:
                    # 重新计算尺寸
                    ratio = target_size / actual_size
                    new_width = int(img.width * np.sqrt(ratio))
                    new_height = int(img.height * np.sqrt(ratio))
                    new_width = max(1, new_width)
                    new_height = max(1, new_height)
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    img_resized.save(filepath, format_type, **save_kwargs)
                    actual_size = os.path.getsize(filepath) / 1024
            
            # 生成文件信息
            return {
                'index': image_index,
                'filename': filename,
                'size_kb': actual_size,
                'elapsed_time': elapsed,
                'path': str(filepath),
                'secondary': secondary
            }
            
        except Exception as e:
            print(f"保存图像 {image_index} ({'PNG' if secondary else 'JPEG'}) 失败: {e}")
            return None
    
    def save_images_for_sn(self, sn):
        """
        为指定SN保存所有图像（包括主存储和第二存储）
        :param sn: SN字符串
        :return: 执行结果
        """
        # 构建主存储目录路径
        date_str = datetime.now().strftime('%Y%m%d')
        sn_path = self.base_path / date_str / sn
        sn_path.mkdir(parents=True, exist_ok=True)
        
        # 构建第二存储目录路径
        secondary_sn_path = None
        if self.secondary_enabled:
            secondary_sn_path = self.secondary_path / date_str / sn
            secondary_sn_path.mkdir(parents=True, exist_ok=True)
        
        print(f"开始写入SN: {sn}")
        print(f"  主存储路径: {sn_path}")
        if secondary_sn_path:
            print(f"  第二存储路径: {secondary_sn_path}")
        print(f"共{self.total_images}张图，预计耗时: {self.time_limit}秒")
        
        start_time = time.time()
        results = []
        
        # 使用线程池处理
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            
            for i in range(1, self.total_images + 1):
                # 提交主存储任务
                future = executor.submit(self.save_single_image, sn_path, i, False)
                futures.append(future)
                
                # 如果启用第二存储，提交第二存储任务
                if self.secondary_enabled and secondary_sn_path:
                    future_secondary = executor.submit(self.save_single_image, secondary_sn_path, i, True)
                    futures.append(future_secondary)
                
                # 控制写入节奏
                time.sleep(self.write_interval / 2)  # 因为有两个存储任务
            
            # 收集结果
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)
        
        total_elapsed = time.time() - start_time
        
        # 统计信息
        jpeg_results = [r for r in results if not r['secondary']]
        png_results = [r for r in results if r['secondary']]
        
        print(f"SN: {sn} 写入完成!")
        print(f"  JPEG: 成功 {len(jpeg_results)}/{self.total_images}张, "
              f"大小: {sum(r['size_kb'] for r in jpeg_results)/1024:.2f} MB")
        if png_results:
            print(f"  PNG:  成功 {len(png_results)}/{self.total_images}张, "
                  f"大小: {sum(r['size_kb'] for r in png_results)/1024:.2f} MB")
        print(f"  实际耗时: {total_elapsed:.3f}秒")
        print(f"  平均每张: {total_elapsed/len(results):.3f}秒")
        print(f"  存储路径: {sn_path}")
        if secondary_sn_path:
            print(f"  PNG路径: {secondary_sn_path}")
        
        return {
            'sn': sn,
            'path': str(sn_path),
            'secondary_path': str(secondary_sn_path) if secondary_sn_path else None,
            'total_images': self.total_images,
            'jpeg_results': {
                'count': len(jpeg_results),
                'total_size_mb': sum(r['size_kb'] for r in jpeg_results) / 1024
            },
            'png_results': {
                'count': len(png_results),
                'total_size_mb': sum(r['size_kb'] for r in png_results) / 1024
            } if png_results else None,
            'elapsed_seconds': total_elapsed,
            'avg_time_per_image': total_elapsed / len(results) if results else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def run(self):
        """运行程序主循环"""
        print(f"\n开始执行存图任务")
        print(f"共需执行 {self.repeat_times} 轮，每轮间隔 {self.round_interval} 秒")
        print(f"每轮写入 {self.total_images} 张图，目标耗时 {self.time_limit} 秒")
        if self.secondary_enabled:
            print(f"同时写入第二存储 (PNG, {self.secondary_image_size}KB)")
        print("=" * 60)
        
        execution_results = []
        
        for run_count in range(1, self.repeat_times + 1):
            print(f"\n{'='*20} 第 {run_count}/{self.repeat_times} 轮 {'='*20}")
            
            # 生成新的SN
            sn = self.generate_sn()
            
            # 记录本轮开始时间
            round_start_time = time.time()
            
            # 执行写入
            result = self.save_images_for_sn(sn)
            execution_results.append(result)
            
            # 计算本轮实际耗时
            round_elapsed = time.time() - round_start_time
            
            # 如果还有下一次执行，等待指定间隔
            if run_count < self.repeat_times:
                print(f"\n⏰ 本轮耗时: {round_elapsed:.2f}秒")
                print(f"⏰ 等待 {self.round_interval} 秒后执行下一轮...")
                
                # 等待指定间隔
                wait_start = time.time()
                while time.time() - wait_start < self.round_interval:
                    remaining = self.round_interval - (time.time() - wait_start)
                    if remaining > 0:
                        if int(remaining) % 1 == 0:
                            print(f"\r   剩余等待时间: {remaining:.1f}秒", end='', flush=True)
                        time.sleep(0.1)
                print()
        
        # 输出总结
        print("\n" + "=" * 60)
        print("✅ 所有任务执行完成!")
        print(f"总执行轮数: {len(execution_results)}")
        
        # 计算总体统计信息
        total_elapsed = sum(r['elapsed_seconds'] for r in execution_results)
        total_jpeg_size = sum(r['jpeg_results']['total_size_mb'] for r in execution_results)
        total_png_size = sum(r['png_results']['total_size_mb'] for r in execution_results if r['png_results'])
        
        print(f"📊 总体统计:")
        print(f"  JPEG总数据量: {total_jpeg_size:.2f} MB")
        if total_png_size > 0:
            print(f"  PNG总数据量: {total_png_size:.2f} MB")
            print(f"  总数据量: {total_jpeg_size + total_png_size:.2f} MB")
        print(f"  总耗时: {total_elapsed:.2f} 秒")
        print(f"  平均每轮耗时: {total_elapsed/len(execution_results):.2f} 秒")
        
        # 保存执行日志
        self.save_execution_log(execution_results)
        
        return execution_results
    
    def save_execution_log(self, results):
        """保存执行日志"""
        log_file = self.base_path / f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'config': self.config,
            'executions': results,
            'total_executions': len(results),
            'total_jpeg_size_mb': sum(r['jpeg_results']['total_size_mb'] for r in results),
            'total_png_size_mb': sum(r['png_results']['total_size_mb'] for r in results if r['png_results']),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            print(f"📝 执行日志已保存: {log_file}")
        except Exception as e:
            print(f"保存日志失败: {e}")


def main():
    """主函数"""
    app = ImageStorageProgram('config.json')
    app.run()


if __name__ == "__main__":
    main()