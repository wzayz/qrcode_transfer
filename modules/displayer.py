import tkinter as tk
from PIL import Image, ImageTk
import time
import threading
from .config_manager import config_manager
from .logger import logger

class Displayer:
    def __init__(self):
        self.display_interval = config_manager.getint('QRCode', 'DisplayInterval', 2)
        self.root = None
        self.label = None
        self.image = None
        self.is_running = False
        self.thread = None
    
    def show_single_qr(self, qr_path):
        """显示单个二维码
        
        Args:
            qr_path: 二维码图片路径
        """
        logger.info(f"显示单个二维码: {qr_path}")
        
        # 创建窗口
        self.root = tk.Tk()
        self.root.title("QR Code Display")
        self.root.geometry(f"{config_manager.getint('QRCode', 'Size')}x{config_manager.getint('QRCode', 'Size')}")
        self.root.configure(bg="white")
        
        # 居中窗口
        self.root.eval('tk::PlaceWindow . center')
        
        # 创建标签
        self.label = tk.Label(self.root, bg="white")
        self.label.pack(expand=True, fill=tk.BOTH)
        
        # 加载并显示图片
        self._load_image(qr_path)
        
        # 显示窗口
        self.root.mainloop()
    
    def show_multiple_qr(self, qr_paths, task_id="", total_size=0):
        """循环显示多个二维码
        
        Args:
            qr_paths: 二维码图片路径列表
            task_id: 任务ID
            total_size: 总文件大小（字节）
        """
        if not qr_paths:
            logger.error("没有二维码图片可显示")
            return
        
        logger.info(f"开始循环显示二维码: 共 {len(qr_paths)} 个，间隔 {self.display_interval} 秒")
        
        # 创建窗口
        self.root = tk.Tk()
        self.root.title("QR Code Display - Cycling")
        self.root.geometry(f"{config_manager.getint('QRCode', 'Size')}x{config_manager.getint('QRCode', 'Size')}")
        self.root.configure(bg="white")
        
        # 居中窗口
        self.root.eval('tk::PlaceWindow . center')
        
        # 创建标签
        self.label = tk.Label(self.root, bg="white")
        self.label.pack(expand=True, fill=tk.BOTH)
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 启动显示线程
        self.is_running = True
        self.thread = threading.Thread(target=self._cycle_display, args=(qr_paths, task_id, total_size))
        self.thread.daemon = True
        self.thread.start()
        
        # 显示窗口
        self.root.mainloop()
    
    def _cycle_display(self, qr_paths, task_id="", total_size=0):
        """循环显示二维码的线程函数
        
        Args:
            qr_paths: 二维码图片路径列表
            task_id: 任务ID
            total_size: 总文件大小（字节）
        """
        try:
            total_files = len(qr_paths)
            speed = 1 / self.display_interval  # 每秒显示的二维码数量
            
            while self.is_running:
                for i, qr_path in enumerate(qr_paths):
                    if not self.is_running:
                        break
                    
                    current_file = i + 1
                    
                    # 计算预计时间（秒）
                    estimated_time = (total_files - current_file) * self.display_interval
                    
                    # 格式化文件大小
                    def format_size(size):
                        for unit in ['B', 'KB', 'MB', 'GB']:
                            if size < 1024:
                                return f"{size:.2f} {unit}"
                            size /= 1024
                        return f"{size:.2f} TB"
                    
                    # 更新窗口标题
                    title = f"QR Code | 任务ID: {task_id} | 文件: {current_file}/{total_files} | 总大小: {format_size(total_size)} | 速度: {speed:.1f} 个/秒 | 预计剩余: {estimated_time:.0f} 秒"
                    if self.root:
                        self.root.title(title)
                    
                    logger.info(f"显示二维码: {current_file}/{total_files} - {qr_path}")
                    self._load_image(qr_path)
                    time.sleep(self.display_interval)
        except Exception as e:
            logger.exception(f"循环显示二维码失败: {e}")
    
    def _load_image(self, qr_path):
        """加载并显示图片
        
        Args:
            qr_path: 二维码图片路径
        """
        try:
            # 加载图片
            image = Image.open(qr_path)
            
            # 调整图片大小
            size = config_manager.getint('QRCode', 'Size')
            image = image.resize((size, size), Image.LANCZOS)
            
            # 转换为tkinter可用的图片格式
            self.image = ImageTk.PhotoImage(image)
            
            # 更新标签
            if self.label:
                self.label.config(image=self.image)
                self.label.image = self.image  # 防止垃圾回收
                
            # 更新窗口
            if self.root:
                self.root.update()
        except Exception as e:
            logger.exception(f"加载二维码图片失败: {e}")
    
    def _on_close(self):
        """关闭窗口时的处理"""
        logger.info("关闭二维码显示窗口")
        self.is_running = False
        if self.root:
            self.root.destroy()
    
    def stop(self):
        """停止显示"""
        logger.info("停止显示二维码")
        self.is_running = False
        if self.root:
            self.root.quit()

# 创建全局显示器实例
displayer = Displayer()