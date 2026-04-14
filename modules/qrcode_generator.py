import qrcode
import json
import os
from PIL import Image
from .config_manager import config_manager
from .logger import logger
from .validator import Validator

class QRCodeGenerator:
    def __init__(self):
        # 从配置文件读取二维码参数
        self.version = config_manager.getint('QRCode', 'Version', 1)
        error_correction = config_manager.get('QRCode', 'ErrorCorrection', 'H')
        self.error_correction = getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}')
        self.size = config_manager.getint('QRCode', 'Size', 600)
        self.box_size = config_manager.getint('QRCode', 'BoxSize', 10)  # 新增 box_size 配置
        self.border = config_manager.getint('QRCode', 'Border', 4)
        self.format = config_manager.get('QRCode', 'Format', 'PNG')

        # 创建校验器实例
        self.validator = Validator()
    
    def generate_qr_code(self, task_id, total_blocks, current_block, data_block, output_path):
        """生成包含元数据的二维码
        
        Args:
            task_id: 任务ID
            total_blocks: 总二维码个数
            current_block: 当前二维码个数
            data_block: 数据块
            output_path: 输出二维码图片路径
        
        Returns:
            输出二维码图片路径
        """
        # 计算数据块哈希值
        block_hash = self.validator.calculate_hash(data_block)
        
        # 构建二维码数据
        qr_data = {
            'task_id': task_id,
            'total_blocks': total_blocks,
            'current_block': current_block,
            'data_block': data_block,
            'block_hash': block_hash
        }
        
        # 转换为JSON字符串
        qr_json = json.dumps(qr_data, ensure_ascii=False)
        
        logger.info(f"生成二维码: 任务ID={task_id}, 总块数={total_blocks}, 当前块={current_block}, 输出={output_path}")
        
        try:
            # 创建二维码对象，使用配置文件中的版本
            qr = qrcode.QRCode(
                version=self.version if self.version > 0 else None,  # 0表示自动选择版本
                error_correction=self.error_correction,
                box_size=self.box_size,  # 使用配置中的 box_size
                border=self.border,
            )
            
            # 添加数据
            qr.add_data(qr_json)
            qr.make(fit=True)
            
            # 创建图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 调整图片大小
            img = img.resize((self.size, self.size), Image.LANCZOS)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 保存图片
            img.save(output_path, format=self.format)
            logger.info(f"二维码生成完成: {output_path}")
            
            return output_path
        except Exception as e:
            logger.exception(f"二维码生成失败: {e}")
            raise
    
    def generate_qr_codes(self, task_id, data_blocks, output_dir):
        """生成多个二维码
        
        Args:
            task_id: 任务ID
            data_blocks: 数据块列表
            output_dir: 输出目录
        
        Returns:
            生成的二维码图片路径列表
        """
        total_blocks = len(data_blocks)
        qr_paths = []
        
        logger.info(f"开始生成多个二维码: 任务ID={task_id}, 总块数={total_blocks}, 输出目录={output_dir}")
        
        for i, data_block in enumerate(data_blocks):
            current_block = i + 1
            output_path = os.path.join(output_dir, f"{task_id}_block_{current_block}_{total_blocks}.{self.format.lower()}")
            qr_path = self.generate_qr_code(task_id, total_blocks, current_block, data_block, output_path)
            qr_paths.append(qr_path)
        
        logger.info(f"所有二维码生成完成，共 {len(qr_paths)} 个")
        return qr_paths
    
    def parse_qr_data(self, qr_json):
        """解析二维码数据
        
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
            if not self.validator.verify_hash(data['data_block'], data['block_hash']):
                logger.error(f"二维码数据块哈希验证失败: 任务ID={data.get('task_id')}, 当前块={data.get('current_block')}")
                raise ValueError(f"二维码数据块哈希验证失败")
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"二维码数据JSON解析失败: {e}")
            raise
        except Exception as e:
            logger.error(f"二维码数据解析失败: {e}")
            raise

# 创建全局二维码生成器实例
qr_generator = QRCodeGenerator()