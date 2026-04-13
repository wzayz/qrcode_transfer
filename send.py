#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR Code 文件发送工具 - 生成并显示二维码
轻量版，不包含二维码读取功能
"""
import os
import sys
import argparse
import uuid
import tempfile

# 只导入 send 端需要的模块，避免导入 cv2/numpy/pyautogui 等重量级依赖
from modules.config_manager import config_manager
from modules.logger import logger
from modules.compressor import compressor
from modules.encoder import encoder
from modules.qrcode_generator import qr_generator
from modules.displayer import displayer
from modules.validator import validator
from modules.blockchain import blockchain


class QRCodeSender:
    def __init__(self):
        self.temp_dir = config_manager.get('Output', 'TempDir', 'temp')
        self.output_dir = config_manager.get('Output', 'OutputDir', 'output')
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_task_id(self):
        task_id_mode = config_manager.get('General', 'TaskIDMode', 'random')
        if task_id_mode == 'custom':
            custom_task_id = config_manager.get('General', 'CustomTaskID', '')
            if custom_task_id:
                return custom_task_id
        return f"TASK-{uuid.uuid4().hex[:8].upper()}"

    def generate_qr_codes(self, input_path, custom_task_id=None, no_display=False):
        task_id = custom_task_id or self.generate_task_id()
        logger.set_task_id(task_id)
        logger.info(f"开始生成二维码任务: {task_id}")

        temp_zip_path = None
        try:
            # 1. 压缩文件
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False, dir=self.temp_dir) as temp_zip:
                temp_zip_path = temp_zip.name
            compressed_path = compressor.compress(input_path, temp_zip_path)
            compressed_hash = validator.calculate_file_hash(compressed_path)
            logger.info(f"压缩文件哈希: {compressed_hash}")
            blockchain.add_block('compress', task_id, compressed_hash)

            # 2. 编码为 base64
            base64_str = encoder.encode_file(compressed_path)
            base64_hash = validator.calculate_hash(base64_str)
            logger.info(f"Base64数据哈希: {base64_hash}")
            blockchain.add_block('encode', task_id, base64_hash)

            # 3. 分割数据块
            data_blocks = encoder.split_into_blocks(base64_str)

            # 4. 生成二维码
            qr_output_dir = os.path.join(self.output_dir, f"qr_{task_id}")
            os.makedirs(qr_output_dir, exist_ok=True)
            qr_paths = qr_generator.generate_qr_codes(task_id, data_blocks, qr_output_dir)
            qr_hash = validator.calculate_hash(str(len(qr_paths)))
            blockchain.add_block('generate_qr', task_id, qr_hash)

            # 5. 显示二维码
            if not no_display:
                total_size = sum(os.path.getsize(qr_path) for qr_path in qr_paths)
                displayer.show_multiple_qr(qr_paths, task_id, total_size)

            logger.info(f"二维码生成任务完成: {task_id}")
            print(f"\n✓ 任务完成: {task_id}")
            print(f"✓ 二维码已保存到: {qr_output_dir}")
            print(f"✓ 共生成 {len(qr_paths)} 个二维码")

        except Exception as e:
            logger.exception(f"二维码生成任务失败: {e}")
            print(f"\n✗ 任务失败: {e}")
            raise
        finally:
            if temp_zip_path and os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

    def display_qr_codes(self, path):
        import re
        logger.info(f"开始显示二维码: {path}")

        try:
            qr_files = []
            if os.path.isfile(path):
                qr_files.append(path)
            elif os.path.isdir(path):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        qr_files.append(file_path)

            if len(qr_files) > 1:
                def sort_key(file_path):
                    filename = os.path.basename(file_path)
                    match = re.match(r'.*_block_(\d+)_(\d+)\.(png|jpg|jpeg)', filename)
                    if match:
                        return (int(match.group(2)), int(match.group(1)))
                    return (0, 0)
                qr_files.sort(key=sort_key)

            task_id = ""
            total_size = 0
            if len(qr_files) > 0:
                first_file = os.path.basename(qr_files[0])
                match = re.match(r'(.+?)_block_(\d+)_(\d+)\.(png|jpg|jpeg)', first_file)
                if match:
                    task_id = match.group(1)
            for file_path in qr_files:
                total_size += os.path.getsize(file_path)

            displayer.show_multiple_qr(qr_files, task_id, total_size)

        except Exception as e:
            logger.exception(f"显示二维码失败: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description='QR Code 文件发送工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 生成二维码
    generate_parser = subparsers.add_parser('generate', help='生成并显示二维码')
    generate_parser.add_argument('--input', '-i', required=True, help='输入文件或文件夹路径')
    generate_parser.add_argument('--task-id', '-t', help='自定义任务ID')
    generate_parser.add_argument('--no-display', action='store_true', help='跳过显示二维码，只生成文件')

    # 显示二维码
    display_parser = subparsers.add_parser('display', help='显示生成的二维码')
    display_parser.add_argument('--path', '-p', required=True, help='二维码文件或目录路径')

    args = parser.parse_args()
    sender = QRCodeSender()

    if args.command == 'generate':
        sender.generate_qr_codes(args.input, args.task_id, getattr(args, 'no_display', False))
    elif args.command == 'display':
        sender.display_qr_codes(args.path)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
