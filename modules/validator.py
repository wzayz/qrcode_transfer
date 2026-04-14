import json
import hashlib
from Crypto.Hash import SHA256, SHA512, MD5
from .config_manager import config_manager
from .logger import logger

class Validator:
    def __init__(self):
        # 从配置文件读取哈希算法
        hash_algorithm = config_manager.get('Blockchain', 'HashAlgorithm', 'SHA256')
        self.hash_algorithm = hash_algorithm.upper()
        logger.info(f"初始化校验器，使用哈希算法: {self.hash_algorithm}")
    
    def calculate_hash(self, data):
        """计算数据的哈希值
        
        Args:
            data: 要计算哈希的数据（字符串或字节）
        
        Returns:
            哈希值字符串
        """
        try:
            # 确保数据是字节类型
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # 根据配置选择哈希算法
            if self.hash_algorithm == 'SHA256':
                hash_obj = SHA256.new(data)
            elif self.hash_algorithm == 'SHA512':
                hash_obj = SHA512.new(data)
            elif self.hash_algorithm == 'MD5':
                hash_obj = MD5.new(data)
            else:
                # 默认使用SHA256
                hash_obj = SHA256.new(data)
            
            return hash_obj.hexdigest()
        except Exception as e:
            logger.exception(f"哈希计算失败: {e}")
            raise
    
    def verify_hash(self, data, expected_hash):
        """验证数据的哈希值
        
        Args:
            data: 要验证的数据（字符串或字节）
            expected_hash: 期望的哈希值
        
        Returns:
            bool: 验证通过返回True，否则返回False
        """
        try:
            actual_hash = self.calculate_hash(data)
            result = actual_hash == expected_hash
            
            if not result:
                logger.warning(f"哈希验证失败: 实际={actual_hash}, 期望={expected_hash}")
            
            return result
        except Exception as e:
            logger.exception(f"哈希验证失败: {e}")
            return False
    
    def calculate_file_hash(self, file_path):
        """计算文件的哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            哈希值字符串
        """
        try:
            # 根据配置选择哈希算法
            if self.hash_algorithm == 'SHA256':
                hash_obj = SHA256.new()
            elif self.hash_algorithm == 'SHA512':
                hash_obj = SHA512.new()
            elif self.hash_algorithm == 'MD5':
                hash_obj = MD5.new()
            else:
                hash_obj = SHA256.new()
            
            # 分块读取文件并计算哈希
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception as e:
            logger.exception(f"文件哈希计算失败: {e}")
            raise
    
    def verify_file_hash(self, file_path, expected_hash):
        """验证文件的哈希值

        Args:
            file_path: 文件路径
            expected_hash: 期望的哈希值

        Returns:
            bool: 验证通过返回True，否则返回False
        """
        try:
            actual_hash = self.calculate_file_hash(file_path)
            result = actual_hash == expected_hash

            if not result:
                logger.warning(f"文件哈希验证失败: 文件={file_path}, 实际={actual_hash}, 期望={expected_hash}")

            return result
        except Exception as e:
            logger.exception(f"文件哈希验证失败: {e}")
            return False

    def parse_qr_data(self, qr_json):
        """解析二维码数据（从 qrcode_generator 移入，避免 receive 端依赖 qrcode 库）

        Args:
            qr_json: 二维码中的JSON字符串

        Returns:
            解析后的字典
        """
        try:
            data = json.loads(qr_json)
            logger.info(f"解析二维码数据: 任务ID={data.get('task_id')}, 总块数={data.get('total_blocks')}, 当前块={data.get('current_block')}")

            # 验证数据完整性
            required_fields = ['task_id', 'total_blocks', 'current_block', 'data_block', 'block_hash']
            for field in required_fields:
                if field not in data:
                    logger.error(f"二维码数据缺少必要字段: {field}")
                    raise ValueError(f"二维码数据缺少必要字段: {field}")

            # 验证数据块哈希
            if not self.verify_hash(data['data_block'], data['block_hash']):
                logger.error(f"二维码数据块哈希验证失败: 任务ID={data.get('task_id')}, 当前块={data.get('current_block')}")
                raise ValueError(f"二维码数据块哈希验证失败")

            return data
        except json.JSONDecodeError as e:
            logger.error(f"二维码数据JSON解析失败: {e}")
            raise
        except Exception as e:
            logger.error(f"二维码数据解析失败: {e}")
            raise

# 创建全局校验器实例
validator = Validator()