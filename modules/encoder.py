import base64
import os
from .logger import logger
from .config_manager import config_manager

class Encoder:
    def __init__(self):
        self.block_size = config_manager.getint('QRCode', 'BlockSize', 2000)
    
    def encode_file(self, file_path):
        """将文件转换为base64编码
        
        Args:
            file_path: 要编码的文件路径
        
        Returns:
            base64编码字符串
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        logger.info(f"开始编码文件: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                base64_str = base64.b64encode(data).decode('utf-8')
            
            logger.info(f"文件编码完成，base64长度: {len(base64_str)} 字符")
            return base64_str
        except Exception as e:
            logger.exception(f"文件编码失败: {e}")
            raise
    
    def decode_to_file(self, base64_str, output_path):
        """将base64编码转换为文件
        
        Args:
            base64_str: base64编码字符串
            output_path: 输出文件路径
        
        Returns:
            输出文件路径
        """
        logger.info(f"开始解码到文件: {output_path}")
        
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            data = base64.b64decode(base64_str.encode('utf-8'))
            
            with open(output_path, 'wb') as f:
                f.write(data)
            
            logger.info(f"解码完成，文件大小: {len(data)} 字节")
            return output_path
        except Exception as e:
            logger.exception(f"解码失败: {e}")
            raise
    
    def split_into_blocks(self, base64_str, block_size=None):
        """将base64字符串分割成多个数据块
        
        Args:
            base64_str: base64编码字符串
            block_size: 每个数据块的大小，默认使用配置文件中的值
        
        Returns:
            数据块列表
        """
        if block_size is None:
            block_size = self.block_size
        
        logger.info(f"开始分割数据块，总长度: {len(base64_str)}, 块大小: {block_size}")
        
        # 计算数据块数量
        num_blocks = (len(base64_str) + block_size - 1) // block_size
        logger.info(f"数据块总数: {num_blocks}")
        
        # 分割数据块
        blocks = [base64_str[i*block_size : (i+1)*block_size] for i in range(num_blocks)]
        
        logger.info(f"数据块分割完成，共 {len(blocks)} 个数据块")
        return blocks
    
    def merge_blocks(self, blocks):
        """合并数据块为完整的base64字符串

        Args:
            blocks: 数据块列表

        Returns:
            完整的base64字符串
        """
        if not blocks:
            logger.error("数据块列表为空")
            raise ValueError("数据块列表为空")

        # 验证所有数据块都是字符串类型
        for i, block in enumerate(blocks):
            if not isinstance(block, str):
                logger.error(f"数据块 {i} 类型错误: 期望 str，实际 {type(block)}")
                raise TypeError(f"数据块 {i} 类型错误: 期望 str，实际 {type(block)}")

        # 检查是否有空块
        empty_blocks = [i for i, block in enumerate(blocks) if not block]
        if empty_blocks:
            logger.warning(f"发现空数据块，索引: {empty_blocks}")

        logger.info(f"开始合并数据块，共 {len(blocks)} 个数据块")

        base64_str = ''.join(blocks)
        logger.info(f"数据块合并完成，总长度: {len(base64_str)}")

        return base64_str
    
    def encode_data(self, data):
        """将二进制数据转换为base64编码
        
        Args:
            data: 二进制数据
        
        Returns:
            base64编码字符串
        """
        logger.info(f"开始编码数据，长度: {len(data)} 字节")
        
        base64_str = base64.b64encode(data).decode('utf-8')
        logger.info(f"数据编码完成，base64长度: {len(base64_str)} 字符")
        
        return base64_str
    
    def decode_data(self, base64_str):
        """将base64编码转换为二进制数据
        
        Args:
            base64_str: base64编码字符串
        
        Returns:
            二进制数据
        """
        logger.info(f"开始解码数据，base64长度: {len(base64_str)} 字符")
        
        data = base64.b64decode(base64_str.encode('utf-8'))
        logger.info(f"数据解码完成，长度: {len(data)} 字节")
        
        return data

# 创建全局编码器实例
encoder = Encoder()