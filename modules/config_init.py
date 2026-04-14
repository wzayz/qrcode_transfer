"""
配置初始化模块
运行时如果检测到 config.ini 不存在，自动生成默认配置
"""
import os
import sys


DEFAULT_CONFIG = """[General]
# 任务ID生成方式：random 或 custom
TaskIDMode = random
# 自定义任务ID（当TaskIDMode=custom时使用）
CustomTaskID =

[Compression]
# 压缩级别：0-9，0=无压缩，9=最高压缩
CompressionLevel = 9

[QRCode]
# 二维码版本：1-40，0=自动
Version = 1
# 容错率：L(7%), M(15%), Q(25%), H(30%)
ErrorCorrection = M
# 二维码大小（像素）
Size = 600
# 二维码 box_size（每个模块的像素数）
BoxSize = 10
# 边框大小（模块数）
Border = 4
# 二维码图片格式
Format = PNG
# 显示间隔时间（秒）
DisplayInterval = 2
# 数据块大小（字节）
BlockSize = 1000

[Output]
# 输出目录
OutputDir = output
# 临时文件目录
TempDir = temp

[Log]
# 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
LogLevel = INFO
# 日志文件路径
LogFile = qrcode_transfer.log
# 日志格式
LogFormat = %(asctime)s - %(levelname)s - %(task_id)s - %(message)s

[Blockchain]
# 是否启用哈希链可追溯
Enabled = True
# 哈希算法：SHA256, SHA512, MD5
HashAlgorithm = SHA256
# 哈希链文件路径
ChainFile = hash_chain.json

[QRCodeReader]
# 最大尝试次数
MaxAttempts = 30
# 每次尝试的间隔时间（秒）
AttemptInterval = 2
"""


def ensure_config_exists():
    """确保配置文件存在，如果不存在则创建默认配置"""
    # 确定配置文件路径
    if getattr(sys, 'frozen', False):
        # 打包后的环境，使用 exe 所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.dirname(__file__))

    config_path = os.path.join(base_path, 'config.ini')

    if not os.path.exists(config_path):
        print(f"配置文件不存在，正在创建默认配置: {config_path}")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG)
        print("✓ 默认配置文件已创建")

    return config_path
