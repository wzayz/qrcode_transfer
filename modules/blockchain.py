import json
import os
import time
import threading
from .config_manager import config_manager
from .logger import logger
from .validator import validator

class Block:
    """哈希块类"""
    def __init__(self, timestamp, operation_type, task_id, data_hash, previous_hash=''):
        self.timestamp = timestamp
        self.operation_type = operation_type
        self.task_id = task_id
        self.data_hash = data_hash
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """计算块的哈希值"""
        block_string = json.dumps({
            'timestamp': self.timestamp,
            'operation_type': self.operation_type,
            'task_id': self.task_id,
            'data_hash': self.data_hash,
            'previous_hash': self.previous_hash
        }, sort_keys=True)
        return validator.calculate_hash(block_string)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'timestamp': self.timestamp,
            'operation_type': self.operation_type,
            'task_id': self.task_id,
            'data_hash': self.data_hash,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }
    
    @staticmethod
    def from_dict(block_dict):
        """从字典创建块"""
        block = Block(
            block_dict['timestamp'],
            block_dict['operation_type'],
            block_dict['task_id'],
            block_dict['data_hash'],
            block_dict['previous_hash']
        )
        block.hash = block_dict['hash']
        return block

class Blockchain:
    """区块链类"""
    def __init__(self):
        self.chain_file = config_manager.get('Blockchain', 'ChainFile', 'hash_chain.json')
        self.is_enabled = config_manager.getboolean('Blockchain', 'Enabled', True)
        self.chain = []
        self._lock = threading.Lock()  # 线程锁，防止并发写入
        self.chain = self._load_chain()

        # 如果链为空，创建创世块
        if not self.chain:
            self._create_genesis_block()
    
    def _load_chain(self):
        """从文件加载哈希链"""
        if not self.is_enabled:
            return []

        logger.info(f"加载哈希链: {self.chain_file}")

        with self._lock:
            try:
                if os.path.exists(self.chain_file):
                    with open(self.chain_file, 'r', encoding='utf-8') as f:
                        chain_data = json.load(f)
                        return [Block.from_dict(block_dict) for block_dict in chain_data]
                else:
                    logger.info(f"哈希链文件不存在，将创建新链: {self.chain_file}")
                    return []
            except Exception as e:
                logger.exception(f"加载哈希链失败: {e}")
                return []
    
    def _save_chain(self):
        """保存哈希链到文件"""
        if not self.is_enabled:
            return

        logger.info(f"保存哈希链: {self.chain_file}")

        with self._lock:
            try:
                chain_data = [block.to_dict() for block in self.chain]
                # 先写入临时文件，再重命名，防止写入中断导致文件损坏
                temp_file = self.chain_file + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(chain_data, f, indent=2, ensure_ascii=False)
                os.replace(temp_file, self.chain_file)
            except Exception as e:
                logger.exception(f"保存哈希链失败: {e}")
                # 清理可能产生的临时文件
                if os.path.exists(self.chain_file + '.tmp'):
                    try:
                        os.remove(self.chain_file + '.tmp')
                    except Exception:
                        pass
    
    def _create_genesis_block(self):
        """创建创世块"""
        if not self.is_enabled:
            return
        
        logger.info("创建创世块")
        
        # 创建创世块
        genesis_block = Block(
            timestamp=time.time(),
            operation_type='genesis',
            task_id='genesis',
            data_hash='genesis_data_hash',
            previous_hash=''  # 创世块没有前一个哈希
        )
        
        self.chain.append(genesis_block)
        self._save_chain()
    
    def add_block(self, operation_type, task_id, data_hash):
        """添加新的哈希块
        
        Args:
            operation_type: 操作类型
            task_id: 任务ID
            data_hash: 数据哈希
        
        Returns:
            Block: 添加的块
        """
        if not self.is_enabled:
            logger.info("区块链功能已禁用，跳过添加块")
            return None
        
        logger.info(f"添加哈希块: 操作={operation_type}, 任务ID={task_id}")
        
        # 获取前一个块的哈希
        previous_block = self.chain[-1]
        previous_hash = previous_block.hash
        
        # 创建新块
        new_block = Block(
            timestamp=time.time(),
            operation_type=operation_type,
            task_id=task_id,
            data_hash=data_hash,
            previous_hash=previous_hash
        )
        
        # 添加到链中
        self.chain.append(new_block)
        
        # 保存链
        self._save_chain()
        
        logger.info(f"哈希块添加完成: {new_block.hash}")
        return new_block
    
    def is_chain_valid(self):
        """验证哈希链的完整性
        
        Returns:
            bool: 链有效返回True，否则返回False
        """
        if not self.is_enabled:
            return True
        
        logger.info("验证哈希链完整性")
        
        # 验证创世块
        if len(self.chain) > 0:
            genesis_block = self.chain[0]
            if genesis_block.hash != genesis_block.calculate_hash():
                logger.error("创世块哈希验证失败")
                return False
        
        # 验证其他块
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # 验证当前块的哈希
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"块 {i} 哈希验证失败")
                return False
            
            # 验证当前块的前一个哈希指向正确
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"块 {i} 前一个哈希指向错误")
                return False
        
        logger.info("哈希链完整性验证通过")
        return True
    
    def get_chain_length(self):
        """获取链的长度
        
        Returns:
            int: 链的长度
        """
        return len(self.chain)
    
    def get_block_by_index(self, index):
        """根据索引获取块
        
        Args:
            index: 索引
        
        Returns:
            Block: 块对象，不存在返回None
        """
        if index < 0 or index >= len(self.chain):
            return None
        return self.chain[index]
    
    def get_blocks_by_task_id(self, task_id):
        """根据任务ID获取块
        
        Args:
            task_id: 任务ID
        
        Returns:
            list: 块对象列表
        """
        return [block for block in self.chain if block.task_id == task_id]
    
    def get_blocks_by_operation_type(self, operation_type):
        """根据操作类型获取块
        
        Args:
            operation_type: 操作类型
        
        Returns:
            list: 块对象列表
        """
        return [block for block in self.chain if block.operation_type == operation_type]

# 创建全局区块链实例
blockchain = Blockchain()