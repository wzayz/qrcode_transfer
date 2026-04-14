#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import uuid
import tempfile
from modules.config_manager import config_manager
from modules.logger import logger
from modules.compressor import compressor
from modules.encoder import encoder
from modules.qrcode_generator import qr_generator
from modules.displayer import displayer
from modules.validator import validator
from modules.blockchain import blockchain

# 延迟导入cv2相关模块，只在需要时导入
qr_reader = None

class QRCodeTransfer:
    def __init__(self):
        self.temp_dir = config_manager.get('Output', 'TempDir', 'temp')
        self.output_dir = config_manager.get('Output', 'OutputDir', 'output')
        
        # 确保临时目录和输出目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_task_id(self):
        """生成任务ID"""
        task_id_mode = config_manager.get('General', 'TaskIDMode', 'random')
        
        if task_id_mode == 'custom':
            custom_task_id = config_manager.get('General', 'CustomTaskID', '')
            if custom_task_id:
                return custom_task_id
        
        # 默认生成随机任务ID
        return f"TASK-{uuid.uuid4().hex[:8].upper()}"
    
    def generate_qr_codes(self, input_path, custom_task_id=None, no_display=False):
        """生成并显示二维码

        Args:
            input_path: 输入文件或文件夹路径
            custom_task_id: 自定义任务ID
            no_display: 是否跳过显示二维码
        """
        # 生成或使用自定义任务ID
        task_id = custom_task_id or self.generate_task_id()

        # 设置日志的任务ID
        logger.set_task_id(task_id)

        logger.info(f"开始生成二维码任务: {task_id}")

        temp_zip_path = None
        try:
            # 1. 压缩文件或文件夹
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False, dir=self.temp_dir) as temp_zip:
                temp_zip_path = temp_zip.name
            
            compressed_path = compressor.compress(input_path, temp_zip_path)
            
            # 计算压缩文件哈希
            compressed_hash = validator.calculate_file_hash(compressed_path)
            logger.info(f"压缩文件哈希: {compressed_hash}")
            
            # 添加到区块链
            blockchain.add_block('compress', task_id, compressed_hash)
            
            # 2. 编码为base64
            base64_str = encoder.encode_file(compressed_path)
            
            # 计算base64哈希
            base64_hash = validator.calculate_hash(base64_str)
            logger.info(f"Base64数据哈希: {base64_hash}")
            
            # 添加到区块链
            blockchain.add_block('encode', task_id, base64_hash)
            
            # 3. 分割为数据块
            data_blocks = encoder.split_into_blocks(base64_str)
            
            # 4. 生成二维码
            qr_output_dir = os.path.join(self.output_dir, f"qr_{task_id}")
            os.makedirs(qr_output_dir, exist_ok=True)
            
            qr_paths = qr_generator.generate_qr_codes(task_id, data_blocks, qr_output_dir)
            
            # 添加到区块链
            qr_hash = validator.calculate_hash(str(len(qr_paths)))
            blockchain.add_block('generate_qr', task_id, qr_hash)
            
            # 5. 显示二维码（如果未指定跳过）
            if not no_display:
                # 计算总文件大小
                total_size = sum(os.path.getsize(qr_path) for qr_path in qr_paths)
                displayer.show_multiple_qr(qr_paths, task_id, total_size)
            
            logger.info(f"二维码生成任务完成: {task_id}")
            
        except Exception as e:
            logger.exception(f"二维码生成任务失败: {e}")
            raise
        finally:
            # 清理临时文件
            if temp_zip_path and os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
                logger.info(f"清理临时文件: {temp_zip_path}")
    
    def read_qr_codes(self, output_dir):
        """读取屏幕二维码并还原数据

        Args:
            output_dir: 输出目录
        """
        global qr_reader

        # 动态导入qr_reader，避免生成二维码时导入cv2
        if qr_reader is None:
            from modules.qrcode_reader import qr_reader

        logger.info(f"开始读取二维码任务")

        temp_zip_path = None
        try:
            # 1. 从屏幕读取所有二维码
            task_blocks = qr_reader.read_all_qr_codes()
            
            if not task_blocks:
                logger.error("未读取到任何二维码数据")
                return
            
            # 处理每个任务
            for task_id, blocks in task_blocks.items():
                # 设置日志的任务ID
                logger.set_task_id(task_id)
                
                logger.info(f"处理任务: {task_id}")
                
                # 2. 合并数据块
                base64_str = encoder.merge_blocks(blocks)
                
                # 计算base64哈希
                base64_hash = validator.calculate_hash(base64_str)
                logger.info(f"Base64数据哈希: {base64_hash}")
                
                # 添加到区块链
                blockchain.add_block('decode', task_id, base64_hash)
                
                # 3. 解码为压缩文件
                with tempfile.NamedTemporaryFile(suffix='.zip', delete=False, dir=self.temp_dir) as temp_zip:
                    temp_zip_path = temp_zip.name
                
                encoder.decode_to_file(base64_str, temp_zip_path)
                
                # 计算压缩文件哈希
                compressed_hash = validator.calculate_file_hash(temp_zip_path)
                logger.info(f"压缩文件哈希: {compressed_hash}")
                
                # 添加到区块链
                blockchain.add_block('decompress', task_id, compressed_hash)
                
                # 4. 解压缩文件
                decompress_output_dir = os.path.join(output_dir, f"restored_{task_id}")
                compressor.decompress(temp_zip_path, decompress_output_dir)
                
                # 添加到区块链
                restore_hash = validator.calculate_hash(decompress_output_dir)
                blockchain.add_block('restore', task_id, restore_hash)
                
                logger.info(f"任务 {task_id} 完成，文件已还原到: {decompress_output_dir}")
        
        except Exception as e:
            logger.exception(f"读取二维码任务失败: {e}")
            raise
        finally:
            # 清理临时文件
            if temp_zip_path and os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
                logger.info(f"清理临时文件: {temp_zip_path}")
    
    def verify_chain(self):
        """验证区块链完整性"""
        logger.info("验证区块链完整性")
        
        if blockchain.is_chain_valid():
            logger.info("区块链完整性验证通过")
        else:
            logger.error("区块链完整性验证失败")
    
    def display_qr_codes(self, path):
        """显示生成的二维码
        
        Args:
            path: 二维码文件或目录路径
        """
        import re
        
        logger.info(f"开始显示二维码: {path}")
        
        try:
            qr_files = []
            
            # 处理文件或目录
            if os.path.isfile(path):
                qr_files.append(path)
                logger.info(f"找到1个二维码文件")
            elif os.path.isdir(path):
                # 查找目录中的所有二维码文件
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        qr_files.append(file_path)
                
                logger.info(f"找到 {len(qr_files)} 个二维码文件")
            else:
                logger.error(f"路径不存在: {path}")
                return
            
            # 如果有多个文件，尝试根据文件名排序
            if len(qr_files) > 1:
                # 解析文件名，提取任务ID、当前块和总块数
                def sort_key(file_path):
                    filename = os.path.basename(file_path)
                    # 匹配文件名格式: TASK-XXXX_block_1_28.png
                    match = re.match(r'.*_block_(\d+)_(\d+)\.(png|jpg|jpeg)', filename)
                    if match:
                        return (int(match.group(2)), int(match.group(1)))  # 先按总块数，再按当前块
                    return (0, 0)
                
                # 排序二维码文件
                qr_files.sort(key=sort_key)
                logger.info("二维码文件已排序")
            
            # 检查二维码完整性
            if len(qr_files) > 1:
                # 尝试从文件名中提取总块数和当前块
                task_info = {}
                for file_path in qr_files:
                    filename = os.path.basename(file_path)
                    match = re.match(r'(.+?)_block_(\d+)_(\d+)\.(png|jpg|jpeg)', filename)
                    if match:
                        task_id = match.group(1)
                        current_block = int(match.group(2))
                        total_blocks = int(match.group(3))
                        
                        if task_id not in task_info:
                            task_info[task_id] = {
                                'total_blocks': total_blocks,
                                'received_blocks': set()
                            }
                        
                        task_info[task_id]['received_blocks'].add(current_block)
                
                # 验证完整性
                for task_id, info in task_info.items():
                    missing_blocks = set(range(1, info['total_blocks'] + 1)) - info['received_blocks']
                    if missing_blocks:
                        logger.warning(f"任务 {task_id} 缺少块: {missing_blocks}")
                    else:
                        logger.info(f"任务 {task_id} 二维码完整，共 {info['total_blocks']} 个")
            
            # 提取任务ID和总文件大小
            task_id = ""
            total_size = 0
            
            # 从文件名中提取任务ID
            if len(qr_files) > 0:
                first_file = os.path.basename(qr_files[0])
                match = re.match(r'(.+?)_block_(\d+)_(\d+)\.(png|jpg|jpeg)', first_file)
                if match:
                    task_id = match.group(1)
            
            # 计算总文件大小
            for file_path in qr_files:
                total_size += os.path.getsize(file_path)
            
            # 显示二维码
            logger.info(f"开始循环显示 {len(qr_files)} 个二维码，间隔 {config_manager.getint('QRCode', 'DisplayInterval')} 秒")
            displayer.show_multiple_qr(qr_files, task_id, total_size)
            
        except Exception as e:
            logger.exception(f"显示二维码失败: {e}")
            raise

def main():
    """主函数"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='QR Code File Transfer Tool')
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 生成二维码命令
    generate_parser = subparsers.add_parser('generate', help='生成并显示二维码')
    generate_parser.add_argument('--input', '-i', required=True, help='输入文件或文件夹路径')
    generate_parser.add_argument('--task-id', '-t', help='自定义任务ID')
    generate_parser.add_argument('--no-display', action='store_true', help='跳过显示二维码，只生成文件')
    
    # 读取二维码命令
    read_parser = subparsers.add_parser('read', help='读取屏幕二维码并还原数据')
    read_parser.add_argument('--output', '-o', required=True, help='输出目录')
    
    # 验证区块链命令
    verify_parser = subparsers.add_parser('verify', help='验证区块链完整性')
    
    # 显示二维码命令
    display_parser = subparsers.add_parser('display', help='显示生成的二维码')
    display_parser.add_argument('--path', '-p', required=True, help='二维码文件或目录路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 创建QRCodeTransfer实例
    qr_transfer = QRCodeTransfer()
    
    # 根据命令执行相应操作
    if args.command == 'generate':
        qr_transfer.generate_qr_codes(args.input, args.task_id, getattr(args, 'no_display', False))
    elif args.command == 'read':
        qr_transfer.read_qr_codes(args.output)
    elif args.command == 'verify':
        qr_transfer.verify_chain()
    elif args.command == 'display':
        qr_transfer.display_qr_codes(args.path)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()