本文档旨在帮助您解决在使用二维码文件传输程序过程中可能遇到的常见问题。

## 依赖项问题

### 问题现象
运行程序时出现 `ModuleNotFoundError` 或 `ImportError`。

### 可能原因
- 未安装所需依赖库
- 依赖库版本不兼容

### 解决方案
1. 确保已按照 [安装依赖](4-an-zhuang-yi-lai) 中的步骤安装了所有依赖项。
2. 检查 requirements.txt 中的版本约束，特别是 numpy<=2.0.0，因为某些依赖可能与 numpy 2.0+ 不兼容。
3. 如果使用虚拟环境，请确保已激活正确的虚拟环境。

Sources: [requirements.txt](requirements.txt#L1-L8)

## 二维码生成问题

### 问题现象：Invalid version (was 41, expected 1 to 40)
生成二维码时抛出 `ValueError: Invalid version (was 41, expected 1 to 40)`。

### 可能原因
从日志和代码分析来看，该错误是由于单个数据块包含的数据量过大，超出了二维码最大版本（40）的容量限制。

### 解决方案
1. 减小 `config.ini` 中 `[QRCode]` 部分的 `BlockSize` 值。默认值为 1000 字节，但您可以尝试更小的值，例如 500 或 800。
2. 或者增加二维码的容错率或调整其他参数，但减小数据块大小是最直接有效的方法。

Sources: [config.ini](config.ini#L18-L27), [modules/qrcode_generator.py](modules/qrcode_generator.py#L63)

### 问题现象：二维码无法识别
生成的二维码在读取时无法被识别。

### 可能原因
- 二维码尺寸过小
- 容错率设置过低
- 生成的图片质量不佳

### 解决方案
1. 在 `config.ini` 中适当增大 `Size` 参数（例如从 600 增加到 800）。
2. 提高 `ErrorCorrection` 级别（例如从 M 提高到 Q 或 H）。
3. 确保显示二维码时没有缩放或变形。

Sources: [config.ini](config.ini#L18-L27)

## 二维码读取问题

### 问题现象：无法从屏幕读取到任何二维码
运行读取功能时，程序提示“未读取到任何二维码数据”。

### 可能原因
- 二维码未完整显示在屏幕上
- 屏幕分辨率或缩放问题导致图像识别困难
- 摄像头权限问题（如果使用摄像头，但本程序使用屏幕捕获）

### 解决方案
1. 确保二维码完整显示在屏幕上，没有被其他窗口遮挡。
2. 调整屏幕分辨率或缩放比例，确保二维码清晰可见。
3. 检查 `config.ini` 中的 `DisplayInterval` 参数，确保有足够的时间让程序捕获每个二维码。
4. 尝试增加 `qrcode_reader.py` 中 `read_all_qr_codes` 方法的 `max_attempts` 和 `interval` 参数值。

Sources: [modules/qrcode_reader.py](modules/qrcode_reader.py#L106-L178)

### 问题现象：无法收集到完整的数据块
程序读取了部分二维码，但提示“未收集到完整数据块”。

### 可能原因
- 二维码显示速度过快
- 程序捕获间隔过长
- 某些二维码未能被成功识别

### 解决方案
1. 增大 `config.ini` 中的 `DisplayInterval` 值，使每个二维码显示更长时间。
2. 确保在读取过程中不要切换窗口或遮挡二维码。
3. 检查日志文件，查看是否有二维码识别失败的记录。

Sources: [config.ini](config.ini#L26)

## 配置文件问题

### 问题现象：程序无法找到配置文件或配置项
程序启动时提示无法读取配置或使用默认值。

### 可能原因
- config.ini 文件不存在或路径不正确
- 配置文件格式错误
- 配置项名称拼写错误

### 解决方案
1. 确保 config.ini 文件位于程序的根目录下。
2. 检查 config.ini 文件的格式，确保所有节和键都正确闭合。
3. 参考 [配置文件概述](8-pei-zhi-wen-jian-gai-shu) 中的说明，验证配置项的正确性。

Sources: [config.ini](config.ini#L1-L47), [modules/config_manager.py](modules/config_manager.py)

## 区块链完整性问题

### 问题现象：区块链完整性验证失败
运行验证功能时，程序提示“区块链完整性验证失败”。

### 可能原因
- hash_chain.json 文件被意外修改
- 数据传输过程中发生了篡改
- 程序在某个步骤中未能正确记录哈希值

### 解决方案
1. 检查 hash_chain.json 文件是否被修改。
2. 如果是测试环境，可以删除 hash_chain.json 文件，程序会重新创建创世块。
3. 检查日志文件，查看是否有任何步骤未能正确添加哈希块。

Sources: [modules/blockchain.py](modules/blockchain.py), [config.ini](config.ini#L40-L47)

## 日志查看与调试

### 如何启用调试日志
如果遇到问题，您可以启用调试日志以获取更详细的信息。

### 操作步骤
1. 打开 config.ini 文件。
2. 找到 `[Log]` 部分。
3. 将 `LogLevel` 的值从 `INFO` 改为 `DEBUG`。
4. 重新运行程序，查看 qrcode_transfer.log 文件中的详细日志。

Sources: [config.ini](config.ini#L34-L38), [modules/logger.py](modules/logger.py#L1-L76)

## 获取更多帮助

如果以上解决方案未能解决您的问题，请：
1. 查看 [常见问题](20-chang-jian-wen-ti) 页面，看看是否有相关问题的解答。
2. 检查 qrcode_transfer.log 文件，获取详细的错误信息。
3. 参考 [最佳实践](22-zui-jia-shi-jian) 页面，确保您正确使用了程序。