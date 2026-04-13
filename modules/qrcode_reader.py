import cv2
import pyautogui
import numpy as np
from pyzbar.pyzbar import decode
import time
from .logger import logger
from .validator import validator
from .config_manager import config_manager

class QRCodeReader:
    def __init__(self):
        self.max_attempts = config_manager.getint('QRCodeReader', 'MaxAttempts', 30)
        self.attempt_interval = config_manager.getint('QRCodeReader', 'AttemptInterval', 2)
        logger.info("初始化二维码识别器")
    
    def capture_screen(self):
        """捕获屏幕图像
        
        Returns:
            numpy.ndarray: 屏幕图像
        """
        logger.info("捕获屏幕图像")
        
        try:
            # 捕获屏幕
            screenshot = pyautogui.screenshot()
            
            # 转换为OpenCV可用的格式
            screen_image = np.array(screenshot)
            screen_image = cv2.cvtColor(screen_image, cv2.COLOR_RGB2BGR)
            
            logger.info(f"屏幕捕获完成，分辨率: {screen_image.shape[1]}x{screen_image.shape[0]}")
            return screen_image
        except Exception as e:
            logger.exception(f"屏幕捕获失败: {e}")
            raise
    
    def read_qr_code(self, image):
        """从图像中识别二维码
        
        Args:
            image: 图像（numpy.ndarray）
        
        Returns:
            list: 识别到的二维码数据列表
        """
        logger.info("开始识别二维码")
        
        try:
            # 识别二维码
            decoded_objects = decode(image)
            
            result = []
            for obj in decoded_objects:
                # 提取二维码数据
                qr_data = obj.data.decode('utf-8')
                logger.info(f"识别到二维码: {qr_data[:50]}...")
                
                # 解析二维码数据
                parsed_data = validator.parse_qr_data(qr_data)
                result.append(parsed_data)
            
            logger.info(f"二维码识别完成，共识别到 {len(result)} 个")
            return result
        except Exception as e:
            logger.exception(f"二维码识别失败: {e}")
            return []
    
    def read_qr_from_screen(self):
        """从屏幕中识别二维码
        
        Returns:
            list: 识别到的二维码数据列表
        """
        logger.info("从屏幕中识别二维码")
        
        try:
            # 捕获屏幕
            screen_image = self.capture_screen()
            
            # 识别二维码
            result = self.read_qr_code(screen_image)
            
            return result
        except Exception as e:
            logger.exception(f"从屏幕中识别二维码失败: {e}")
            return []
    
    def read_qr_from_file(self, file_path):
        """从文件中识别二维码
        
        Args:
            file_path: 图像文件路径
        
        Returns:
            list: 识别到的二维码数据列表
        """
        logger.info(f"从文件中识别二维码: {file_path}")
        
        try:
            # 读取图像
            image = cv2.imread(file_path)
            if image is None:
                logger.error(f"无法读取图像文件: {file_path}")
                return []
            
            # 识别二维码
            result = self.read_qr_code(image)
            
            return result
        except Exception as e:
            logger.exception(f"从文件中识别二维码失败: {e}")
            return []
    
    def read_all_qr_codes(self, max_attempts=None, interval=None):
        """持续从屏幕中读取所有二维码，直到收集到完整的数据块

        Args:
            max_attempts: 最大尝试次数，默认使用配置文件中的值
            interval: 每次尝试的间隔时间（秒），默认使用配置文件中的值

        Returns:
            dict: 包含完整数据块的字典，键为任务ID，值为数据块列表
        """
        if max_attempts is None:
            max_attempts = self.max_attempts
        if interval is None:
            interval = self.attempt_interval

        logger.info(f"开始持续读取二维码，最大尝试次数: {max_attempts}，间隔: {interval} 秒")
        print(f"\n{'='*60}")
        print(f"开始识别二维码，请确保二维码已显示在屏幕上")
        print(f"最大尝试次数: {max_attempts}，间隔: {interval} 秒")
        print(f"{'='*60}\n")

        # 存储已识别的数据块
        task_data = {}
        last_progress_time = time.time()

        for attempt in range(max_attempts):
            current_time = time.time()
            # 每5秒输出一次进度提示
            if current_time - last_progress_time >= 5:
                logger.info(f"等待二维码中... 已等待 {int(current_time - last_progress_time)} 秒")
                last_progress_time = current_time

            # 从屏幕中识别二维码
            qr_results = self.read_qr_from_screen()

            # 处理识别结果
            for result in qr_results:
                task_id = result['task_id']
                total_blocks = result['total_blocks']
                current_block = result['current_block']
                data_block = result['data_block']

                # 初始化任务数据
                if task_id not in task_data:
                    task_data[task_id] = {
                        'total_blocks': total_blocks,
                        'blocks': [None] * total_blocks,
                        'received_count': 0
                    }

                # 更新任务数据
                if task_data[task_id]['blocks'][current_block - 1] is None:
                    task_data[task_id]['blocks'][current_block - 1] = data_block
                    task_data[task_id]['received_count'] += 1
                    logger.info(f"任务 {task_id}: 接收到块 {current_block}/{total_blocks}")
                    print(f"✓ 任务 {task_id}: 接收到块 {current_block}/{total_blocks}")

            # 检查是否收集到完整的数据块
            complete_tasks = []
            for task_id, data in task_data.items():
                if data['received_count'] == data['total_blocks']:
                    complete_tasks.append(task_id)
                    logger.info(f"任务 {task_id}: 已收集到所有 {data['total_blocks']} 个数据块")
                    print(f"✓✓✓ 任务 {task_id}: 已收集到所有 {data['total_blocks']} 个数据块")

            # 如果有完整的任务，返回结果
            if complete_tasks:
                result = {}
                for task_id in complete_tasks:
                    result[task_id] = task_data[task_id]['blocks']
                return result

            # 等待一段时间后再次尝试
            if attempt < max_attempts - 1:
                time.sleep(interval)

        logger.warning(f"达到最大尝试次数，未收集到完整数据块")
        print(f"\n✗ 达到最大尝试次数，未收集到完整数据块")
        return task_data

# 创建全局二维码读取器实例
qr_reader = QRCodeReader()