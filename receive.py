#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR Code 文件接收工具 - 读取屏幕二维码并还原文件
完整版，包含二维码识别和解码功能
"""
import os
import sys
import argparse
import tempfile

from modules.config_manager import config_manager
from modules.logger import logger
from modules.compressor import compressor
from modules.encoder import encoder
from modules.validator import validator
from modules.blockchain import blockchain

# 延迟导入重量级模块，只在需要时加载
qr_reader = None
displayer = None


class QRCodeReceiver:
    def __init__(self):
        self.temp_dir = config_manager.get('Output', 'TempDir', 'temp')
        self.output_dir = config_manager.get('Output', 'OutputDir', 'output')
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def read_qr_codes(self, output_dir):
        global qr_reader
        if qr_reader is None:
            from modules.qrcode_reader import qr_reader

        logger.info(f"开始读取二维码任务")
        print("\n开始识别二维码，请确保二维码已显示在屏幕上...")

        temp_zip_path = None
        try:
            # 1. 从屏幕读取所有二维码
            task_blocks = qr_reader.read_all_qr_codes()

            if not task_blocks:
                logger.error("未读取到任何二维码数据")
                print("\n✗ 未读取到任何二维码数据")
                return

            # 处理每个任务
            for task_id, blocks in task_blocks.items():
                logger.set_task_id(task_id)
                logger.info(f"处理任务: {task_id}")
                print(f"\n处理任务: {task_id}")

                # 2. 合并数据块
                base64_str = encoder.merge_blocks(blocks)
                base64_hash = validator.calculate_hash(base64_str)
                logger.info(f"Base64数据哈希: {base64_hash}")
                blockchain.add_block('decode', task_id, base64_hash)

                # 3. 解码为压缩文件
                with tempfile.NamedTemporaryFile(suffix='.zip', delete=False, dir=self.temp_dir) as temp_zip:
                    temp_zip_path = temp_zip.name
                encoder.decode_to_file(base64_str, temp_zip_path)

                compressed_hash = validator.calculate_file_hash(temp_zip_path)
                logger.info(f"压缩文件哈希: {compressed_hash}")
                blockchain.add_block('decompress', task_id, compressed_hash)

                # 4. 解压缩文件
                decompress_output_dir = os.path.join(output_dir, f"restored_{task_id}")
                compressor.decompress(temp_zip_path, decompress_output_dir)

                restore_hash = validator.calculate_hash(decompress_output_dir)
                blockchain.add_block('restore', task_id, restore_hash)

                logger.info(f"任务 {task_id} 完成，文件已还原到: {decompress_output_dir}")
                print(f"✓ 任务 {task_id} 完成")
                print(f"✓ 文件已还原到: {decompress_output_dir}")

        except Exception as e:
            logger.exception(f"读取二维码任务失败: {e}")
            print(f"\n✗ 任务失败: {e}")
            raise
        finally:
            if temp_zip_path and os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

    def verify_chain(self):
        logger.info("验证区块链完整性")
        if blockchain.is_chain_valid():
            logger.info("区块链完整性验证通过")
            print("✓ 区块链完整性验证通过")
        else:
            logger.error("区块链完整性验证失败")
            print("✗ 区块链完整性验证失败")


def main():
    parser = argparse.ArgumentParser(description='QR Code 文件接收工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 读取二维码
    read_parser = subparsers.add_parser('read', help='读取屏幕二维码并还原数据')
    read_parser.add_argument('--output', '-o', required=True, help='输出目录')

    # 验证区块链
    subparsers.add_parser('verify', help='验证区块链完整性')

    args = parser.parse_args()
    receiver = QRCodeReceiver()

    if args.command == 'read':
        receiver.read_qr_codes(args.output)
    elif args.command == 'verify':
        receiver.verify_chain()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
