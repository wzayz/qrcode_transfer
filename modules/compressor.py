import zipfile
import os
from .config_manager import config_manager
from .logger import logger

class Compressor:
    def __init__(self):
        self.compression_level = config_manager.getint('Compression', 'CompressionLevel', 9)
    
    def compress(self, input_path, output_path=None):
        """压缩文件或文件夹为zip格式
        
        Args:
            input_path: 要压缩的文件或文件夹路径
            output_path: 压缩文件输出路径，默认为input_path.zip
        
        Returns:
            压缩文件路径
        """
        if not os.path.exists(input_path):
            logger.error(f"输入路径不存在: {input_path}")
            raise FileNotFoundError(f"输入路径不存在: {input_path}")
        
        # 如果未指定输出路径，使用默认路径
        if output_path is None:
            if os.path.isdir(input_path):
                output_path = f"{input_path}.zip"
            else:
                output_path = f"{os.path.splitext(input_path)[0]}.zip"
        
        logger.info(f"开始压缩: {input_path} -> {output_path}")
        
        try:
            with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED, 
                                compresslevel=self.compression_level) as zipf:
                if os.path.isfile(input_path):
                    # 压缩单个文件
                    zipf.write(input_path, os.path.basename(input_path))
                    logger.info(f"压缩文件: {input_path} -> {output_path}")
                else:
                    # 压缩文件夹
                    for root, dirs, files in os.walk(input_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, input_path)
                            zipf.write(file_path, arcname)
                            logger.debug(f"压缩文件: {file_path} -> {arcname}")
                    logger.info(f"压缩文件夹: {input_path} -> {output_path}")
            # 获取压缩文件大小
            compressed_size = os.path.getsize(output_path)
            logger.info(f"压缩完成: {input_path} -> {output_path} (大小: {compressed_size} bytes)")
            return output_path
        
        except Exception as e:
            logger.error(f"压缩失败: {input_path} -> {output_path} ({e})")
            # 清理可能产生的不完整文件
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logger.info(f"已清理不完整的压缩文件: {output_path}")
                except Exception as cleanup_error:
                    logger.warning(f"清理失败文件时出错: {cleanup_error}")
            raise
    
    def decompress(self, zip_path, output_dir):
        """解压缩zip文件
        
        Args:
            zip_path: zip文件路径
            output_dir: 输出目录
        
        Returns:
            输出目录路径
        """
        if not os.path.exists(zip_path):
            logger.error(f"zip文件不存在: {zip_path}")
            raise FileNotFoundError(f"zip文件不存在: {zip_path}")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"开始解压缩: {zip_path} -> {output_dir}")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(output_dir)
                logger.info(f"解压缩完成，共 {len(zipf.namelist())} 个文件")
                for file in zipf.namelist():
                    logger.debug(f"解压缩文件: {file}")
            
            return output_dir
        except Exception as e:
            logger.exception(f"解压缩失败: {e}")
            raise

# 创建全局压缩器实例
compressor = Compressor()