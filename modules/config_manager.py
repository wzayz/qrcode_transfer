import configparser
import os

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        # 禁用插值功能，避免日志格式中的%(asctime)s等占位符被错误处理
        self.config = configparser.ConfigParser(interpolation=None)
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        self.config.read(self.config_path, encoding='utf-8')
    
    def get(self, section, option, fallback=None, cast_type=None):
        """获取配置项值
        
        Args:
            section: 配置节
            option: 配置项
            fallback: 默认值
            cast_type: 转换类型
        
        Returns:
            配置项值
        """
        try:
            value = self.config.get(section, option, fallback=fallback)
            if cast_type is not None:
                value = cast_type(value)
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section, option, fallback=None):
        """获取整数类型配置项"""
        return self.get(section, option, fallback, int)
    
    def getfloat(self, section, option, fallback=None):
        """获取浮点数类型配置项"""
        return self.get(section, option, fallback, float)
    
    def getboolean(self, section, option, fallback=None):
        """获取布尔类型配置项"""
        return self.get(section, option, fallback, bool)
    
    def set(self, section, option, value):
        """设置配置项值"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
    
    def save(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_all(self):
        """获取所有配置"""
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config[section])
        return result

# 创建全局配置管理器实例
# 支持打包后的环境：在可执行文件同目录查找 config.ini，不存在则生成
import sys
from .config_init import ensure_config_exists

# 确保配置文件存在
ensure_config_exists()

if getattr(sys, 'frozen', False):
    # 打包后的环境，使用 exe 所在目录
    base_path = os.path.dirname(sys.executable)
else:
    # 开发环境
    base_path = os.path.dirname(os.path.dirname(__file__))

config_path = os.path.join(base_path, 'config.ini')
config_manager = ConfigManager(config_path)