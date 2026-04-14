本页面详细介绍 QRCode Transfer 工具中的压缩配置选项，这些配置控制文件和文件夹的压缩行为，以优化传输效率和存储使用。

## 配置概览

压缩配置位于 `config.ini` 文件的 `[Compression]` 节中，目前仅包含一个核心配置项：压缩级别。通过调整此参数，您可以在压缩速度和压缩率之间找到最佳平衡点。

Sources: [config.ini](config.ini#L10-L13)

## 压缩级别 (CompressionLevel)

压缩级别控制 ZIP 压缩算法的工作强度，取值范围为 0 到 9：

| 级别 | 描述 | 压缩速度 | 压缩率 | 适用场景 |
|------|------|----------|--------|----------|
| 0 | 无压缩 | 最快 | 无压缩 | 快速传输已压缩文件，或需要最高处理速度的场景 |
| 1-3 | 低级压缩 | 快 | 较低 | 平衡速度和压缩率，适合普通文件传输 |
| 4-6 | 中级压缩 | 中等 | 中等 | 默认推荐，适合大多数应用场景 |
| 7-9 | 高级压缩 | 慢 | 最高 | 最大化压缩率，适合大文件或带宽受限环境 |

默认配置设置为最高压缩级别（9），以最小化生成的二维码数量和传输时间。

Sources: [config.ini](config.ini#L12-L13), [modules/compressor.py](modules/compressor.py#L7-L9)

## 技术实现

压缩功能使用 Python 标准库中的 `zipfile` 模块实现，采用 DEFLATED 压缩算法。压缩级别直接传递给 `zipfile.ZipFile` 构造函数的 `compresslevel` 参数：

```python
with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED, 
                    compresslevel=self.compression_level) as zipf:
    # 压缩文件或文件夹
```

压缩器会自动处理单个文件和整个文件夹的压缩，并记录详细的压缩过程日志。

Sources: [modules/compressor.py](modules/compressor.py#L27-L49)

## 配置管理

压缩配置通过 `ConfigManager` 类进行管理，该类提供了类型安全的配置访问方法。压缩级别在 `Compressor` 类初始化时通过 `config_manager.getint()` 方法读取，如果配置文件中未指定，则使用默认值 9。

Sources: [modules/config_manager.py](modules/config_manager.py#L36-L39), [modules/compressor.py](modules/compressor.py#L7-L9)

## 最佳实践

- 对于文本文件、未压缩的图像或文档，使用较高压缩级别（7-9）可显著减小文件大小
- 对于已压缩的文件格式（如 JPEG、MP4、ZIP），使用较低压缩级别（0-1）可以节省处理时间
- 在处理速度受限的设备上，考虑降低压缩级别以提高响应速度

## 下一步

了解压缩配置后，您可以继续查看 [区块链配置](11-qu-kuai-lian-pei-zhi) 或 [日志配置](12-ri-zhi-pei-zhi) 来完善您的设置。