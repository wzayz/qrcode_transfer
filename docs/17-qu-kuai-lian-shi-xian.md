本页面深入解析 QRCode Transfer 项目中的区块链实现细节，重点关注数据结构设计、哈希计算机制、数据持久化策略和完整性验证流程。本内容面向高级开发者，需要对密码学哈希和数据结构有基础了解。

## 核心数据结构

区块链实现的核心由两个关键类构成：`Block`（区块）和 `Blockchain`（区块链）。`Block` 类封装了单个区块的数据结构和哈希计算逻辑，而 `Blockchain` 类则管理整个链的生命周期、持久化和验证操作。

### Block 类设计

`Block` 类是区块链的基本构建单元，每个区块包含时间戳、操作类型、任务 ID、数据哈希、前一区块哈希以及自身哈希。区块哈希的计算涵盖了除自身哈希外的所有字段，确保任何数据篡改都会导致哈希验证失败。

```python
class Block:
    """哈希块类"""
    def __init__(self, timestamp, operation_type, task_id, data_hash, previous_hash=''):
        self.timestamp = timestamp
        self.operation_type = operation_type
        self.task_id = task_id
        self.data_hash = data_hash
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
```
Sources: [blockchain.py](modules/blockchain.py#L8-L16)

### Blockchain 类设计

`Blockchain` 类负责管理整个区块链的生命周期，包括链的加载、保存、新区块添加和完整性验证。它通过配置文件控制区块链功能的启用状态，并使用线程锁确保并发安全。

```python
class Blockchain:
    """区块链类"""
    def __init__(self):
        self.chain_file = config_manager.get('Blockchain', 'ChainFile', 'hash_chain.json')
        self.is_enabled = config_manager.getboolean('Blockchain', 'Enabled', True)
        self.chain = []
        self._lock = threading.Lock()  # 线程锁，防止并发写入
        self.chain = self._load_chain()
```
Sources: [blockchain.py](modules/blockchain.py#L50-L57)

## 哈希计算机制

哈希计算是区块链完整性保证的核心，项目通过 `Validator` 类实现灵活的哈希算法支持。

### 算法配置与选择

系统支持 SHA256、SHA512 和 MD5 三种哈希算法，可通过配置文件动态选择。默认使用 SHA256 算法以平衡安全性和性能。

```python
class Validator:
    def __init__(self):
        # 从配置文件读取哈希算法
        hash_algorithm = config_manager.get('Blockchain', 'HashAlgorithm', 'SHA256')
        self.hash_algorithm = hash_algorithm.upper()
        logger.info(f"初始化校验器，使用哈希算法: {self.hash_algorithm}")
```
Sources: [validator.py](modules/validator.py#L8-L13)

### 区块哈希计算

每个区块的哈希通过对其关键元数据（时间戳、操作类型、任务 ID、数据哈希、前一区块哈希）进行排序后 JSON 序列化，再计算哈希值得到。这种设计确保了区块内容的任何修改都会导致哈希值变化。

```python
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
```
Sources: [blockchain.py](modules/blockchain.py#L18-L29)

## 区块链操作

### 创世块创建

当区块链首次初始化且链文件不存在时，系统会自动创建创世块。创世块没有前一区块哈希，作为整个链的起点。

```python
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
```
Sources: [blockchain.py](modules/blockchain.py#L105-L122)

### 新区块添加

添加新区块时，系统会获取链上最后一个区块的哈希作为新区块的前一哈希，创建新区块后将其追加到链中并立即持久化。

```python
def add_block(self, operation_type, task_id, data_hash):
    """添加新的哈希块"""
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
```
Sources: [blockchain.py](modules/blockchain.py#L124-L153)

### 完整性验证

区块链完整性验证通过遍历整个链，检查每个区块的哈希是否正确以及前一区块哈希是否匹配来实现。

```python
def is_chain_valid(self):
    """验证哈希链的完整性"""
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
```
Sources: [blockchain.py](modules/blockchain.py#L155-L184)

## 数据持久化策略

### 文件存储机制

区块链数据以 JSON 格式存储在文件中。为防止写入过程中断导致文件损坏，系统采用先写入临时文件再重命名的原子操作策略。

```python
def _save_chain(self):
    """保存哈希链到文件"""
    with self._lock:
        try:
            chain_data = [block.to_dict() for block in self.chain]
            # 先写入临时文件，再重命名，防止写入中断导致文件损坏
            temp_file = self.chain_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(chain_data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, self.chain_file)
```
Sources: [blockchain.py](modules/blockchain.py#L84-L103)

### 并发安全处理

通过 `threading.Lock` 实现的线程锁确保了在多线程环境下对区块链文件的读写操作不会发生竞态条件。

```python
self._lock = threading.Lock()  # 线程锁，防止并发写入
```
Sources: [blockchain.py](modules/blockchain.py#L55)

## 全局实例与集成

系统在模块加载时自动创建全局的 `blockchain` 和 `validator` 实例，供其他模块直接导入使用，简化了集成流程。

```python
# 创建全局区块链实例
blockchain = Blockchain()
```
Sources: [blockchain.py](modules/blockchain.py#L247-L249)

```python
# 创建全局校验器实例
validator = Validator()
```
Sources: [validator.py](modules/validator.py#L152-L153)

## 下一步

要了解如何验证区块链的完整性，请参阅 [数据完整性验证](18-shu-ju-wan-zheng-xing-yan-zheng)。有关区块链功能的配置选项，请查看 [区块链配置](11-qu-kuai-lian-pei-zhi)。