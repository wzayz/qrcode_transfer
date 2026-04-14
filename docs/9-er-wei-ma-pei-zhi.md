本页详细介绍二维码配置相关参数，这些参数直接影响二维码的生成质量、数据容量、可读性和存储效率。二维码配置位于配置文件的 `[QRCode]` 节中，系统启动时由 `ConfigManager` 加载，并在 `QRCodeGenerator` 中实际应用。

## 配置选项总览

下表列出了所有二维码配置项及其作用：

| 配置项 | 说明 | 取值范围 | 默认值 |
|--------|------|----------|--------|
| Version | 二维码版本 | 0-40（0=自动） | 1 |
| ErrorCorrection | 容错率 | L(7%), M(15%), Q(25%), H(30%) | M |
| Size | 二维码图片大小（像素） | 正整数 | 600 |
| BoxSize | 每个模块的像素数 | 正整数 | 10 |
| Border | 边框大小（模块数） | 非负整数 | 4 |
| Format | 图片格式 | PNG, JPG 等 | PNG |
| DisplayInterval | 显示间隔时间（秒） | 正数 | 2 |
| BlockSize | 数据块大小（字节） | 正整数 | 1000 |

Sources: [config.ini](config.ini#L18-L29) [modules/config_init.py](modules/config_init.py#L23-L33)

## 核心配置项详解

### 版本（Version）

二维码版本决定了二维码的尺寸和数据容量。版本 1 为最小尺寸（21×21 模块），版本 40 为最大尺寸（177×177 模块）。每个高级版本比前一版本每边增加 4 个模块。

系统支持手动指定版本或自动选择：
- 当设置为 0 时，系统会让二维码库根据数据量自动选择合适的版本
- 当设置为 1-40 时，系统会使用指定的版本

这种设计提供了灵活性，既可以让系统自动优化，也允许用户根据特定需求手动控制。

```python
# 创建二维码对象，根据配置选择是否自动版本
qr = qrcode.QRCode(
    version=self.version if self.version > 0 else None,  # 0表示自动选择版本
    error_correction=self.error_correction,
    box_size=self.box_size,
    border=self.border,
)
```

Sources: [modules/qrcode_generator.py](modules/qrcode_generator.py#L17-L19#L56-L62)

### 容错率（ErrorCorrection）

容错率决定了二维码在部分损坏或污损情况下仍能被正确读取的能力。系统提供四个级别的容错率：

- **L (7%)**: 最低容错率，能恢复 7% 的数据，适用于环境清洁、二维码不易损坏的场景
- **M (15%)**: 中等容错率，默认设置，在大多数场景下提供良好的平衡
- **Q (25%)**: 较高容错率，适用于二维码可能出现部分污损的场景
- **H (30%)**: 最高容错率，能恢复 30% 的数据，适用于恶劣环境或二维码可能严重损坏的情况

容错率的选择需要在数据容量和可靠性之间进行权衡：更高的容错率会减少可存储的数据量，但提供更强的错误恢复能力。

Sources: [modules/qrcode_generator.py](modules/qrcode_generator.py#L17-L19)

### 尺寸配置（Size, BoxSize 和 Border）

**Size** 配置决定了最终生成的二维码图片的像素大小。系统默认值为 600×600 像素，这个尺寸在大多数显示设备和打印场景下都能提供良好的可读性。

**BoxSize** 配置指定了二维码中每个模块（黑白点）的像素大小。默认值为 10 像素，这意味着每个模块在最终图像中占据 10×10 像素的空间。

实际实现中，系统首先使用 `box_size` 生成二维码，然后使用高质量的 `LANCZOS` 算法将图像调整到目标 `size`，确保图像清晰：

```python
box_size=self.box_size,  # 使用配置中的 box_size
# ...
img = img.resize((self.size, self.size), Image.LANCZOS)
```

**Border** 配置指定了二维码周围空白边框的大小，单位是模块数（而非像素）。默认值为 4 个模块，这是 QR 码标准推荐的最小边框尺寸，有助于二维码阅读器准确定位二维码。

Sources: [modules/qrcode_generator.py](modules/qrcode_generator.py#L20-L22#L68-L69)

### 数据块大小（BlockSize）

数据块大小决定了每个二维码中存储的数据量（以字节为单位）。默认值为 1000 字节，这意味着系统会将原始数据分割成多个不超过 1000 字节的块，每个块生成一个单独的二维码。

数据块大小的选择需要考虑以下因素：
- 较小的块大小：生成更多二维码，但每个二维码的复杂度更低，读取更可靠
- 较大的块大小：减少二维码数量，但每个二维码复杂度更高，可能需要更高版本和更低容错率

Sources: [config.ini](config.ini#L29)

## 配置加载与应用流程

二维码配置的加载和应用遵循以下流程：

1. **配置初始化**：`config_init` 模块在系统启动时确保配置文件存在，如不存在则生成默认配置
2. **配置加载**：`ConfigManager` 在初始化时读取 `config.ini` 文件
3. **参数获取**：`QRCodeGenerator` 在初始化时通过 `config_manager` 获取相关配置
4. **实际应用**：配置参数在 `generate_qr_code` 方法中被用于创建和定制二维码

这种设计实现了配置与代码的分离，使系统更易于维护和定制。

Sources: [modules/config_manager.py](modules/config_manager.py#L1-L83) [modules/config_init.py](modules/config_init.py#L1-L86)

## 配置建议

根据不同的使用场景，我们提供以下配置建议：

| 场景 | 推荐配置 | 理由 |
|------|----------|------|
| 常规文件传输 | Version=0, ErrorCorrection=M, Size=600, BoxSize=10, BlockSize=1000 | 自动选择版本，在可靠性和效率间取得平衡 |
| 打印在纸质文档 | Version=0, ErrorCorrection=H, Size=800, BoxSize=12, BlockSize=800 | 提高容错率，适应可能的纸张污损 |
| 屏幕传输演示 | Version=0, ErrorCorrection=L, Size=500, BoxSize=8, BlockSize=1500 | 减少二维码数量，加快传输速度 |
| 小屏幕显示 | Version=0, ErrorCorrection=M, Size=400, BoxSize=6, BlockSize=600 | 适应小屏幕显示，确保可读性 |

## 下一步

了解完二维码配置后，您可以继续阅读[压缩配置](10-ya-suo-pei-zhi)和[区块链配置](11-qu-kuai-lian-pei-zhi)，全面掌握系统的配置选项。如需了解二维码生成的详细流程，请参考[二维码生成流程](15-er-wei-ma-sheng-cheng-liu-cheng)。