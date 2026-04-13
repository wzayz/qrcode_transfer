import logging
import os
from .config_manager import config_manager

class TaskIdFilter(logging.Filter):
    """日志过滤器，用于注入 task_id 字段"""
    def __init__(self, task_id="unknown"):
        super().__init__()
        self.task_id = task_id

    def filter(self, record):
        record.task_id = self.task_id
        return True

class TaskLogger:
    def __init__(self, task_id="unknown"):
        self.task_id = task_id
        self.task_id_filter = TaskIdFilter(task_id)
        self.logger = logging.getLogger("qrcode_transfer")
        self._setup_logger()

    def _setup_logger(self):
        """配置日志记录器"""
        # 从配置文件获取日志配置
        log_level = config_manager.get("Log", "LogLevel", "INFO")
        log_file = config_manager.get("Log", "LogFile", "qrcode_transfer.log")
        log_format = config_manager.get("Log", "LogFormat", "%(asctime)s - %(levelname)s - %(task_id)s - %(message)s")

        # 设置日志级别
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 添加 task_id 过滤器
        self.logger.addFilter(self.task_id_filter)

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # 创建格式化器
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def set_task_id(self, task_id):
        """设置任务ID"""
        self.task_id = task_id
        self.task_id_filter.task_id = task_id
    
    def debug(self, message):
        """记录调试级别日志"""
        self.logger.debug(message)

    def info(self, message):
        """记录信息级别日志"""
        self.logger.info(message)

    def warning(self, message):
        """记录警告级别日志"""
        self.logger.warning(message)

    def error(self, message):
        """记录错误级别日志"""
        self.logger.error(message)

    def critical(self, message):
        """记录严重级别日志"""
        self.logger.critical(message)

    def exception(self, message):
        """记录异常日志"""
        self.logger.exception(message)

# 创建全局日志实例
logger = TaskLogger()