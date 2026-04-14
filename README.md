# QR Code 文件传输工具

一个基于 Python 的文件传输工具，通过二维码实现文件或文件夹的传输。支持压缩、加密、区块链可追溯等功能，提供 **Python 源码** 和 **独立可执行文件** 两种使用方式。

---

## 📖 目录

- [功能特点](#-功能特点)
- [快速开始](#-快速开始)
  - [方式一：使用可执行文件（推荐）](#方式一使用可执行文件推荐)
  - [方式二：使用 Python 源码](#方式二使用-python-源码)
- [使用方法](#-使用方法)
  - [发送端 (qr-send)](#发送端-qr-send)
  - [接收端 (qr-receive)](#接收端-qr-receive)
- [工作原理](#-工作原理)
- [配置文件](#-配置文件)
- [项目结构](#-项目结构)
- [技术栈](#-技术栈)
- [打包说明](#-打包说明)
- [安全性](#-安全性)
- [注意事项](#-注意事项)
- [故障排除](#-故障排除)

---

## ✨ 功能特点

### 🔄 二维码生成
- 将文件或文件夹压缩为 zip 格式
- 转换为 base64 编码
- 生成包含元数据的二维码
  - 任务 ID
  - 总二维码个数
  - 当前二维码索引
  - 数据块
  - 数据块哈希值
- 按设定时间循环显示二维码

### 📸 二维码读取
- 从屏幕捕获二维码
- 自动识别多个二维码
- 校验数据完整性
- 还原为原始文件或文件夹

### ⚙️ 灵活配置
- 首次运行时自动生成 `config.ini`
- 支持自定义任务 ID
- 可配置二维码大小、质量、容错率
- 可配置显示间隔时间和数据块大小

### 📝 日志记录
- 详细的操作日志
- 支持多级别日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 日志包含任务 ID，便于追踪

### 🔗 区块链可追溯
- 基于哈希链的操作记录
- 每个操作生成哈希块
- 支持链完整性验证
- 确保操作可追溯、不可篡改

---

## 🚀 快速开始

### 方式一：使用可执行文件（推荐）

无需安装 Python，直接运行即可。

| 文件 | 大小 | 功能 |
|------|------|------|
| `qr-send.exe` | ~23MB | 生成并显示二维码（发送端） |
| `qr-receive.exe` | ~81MB | 读取屏幕二维码并还原文件（接收端） |

1. 将 `qr-send.exe` 或 `qr-receive.exe` 复制到任意目录
2. 首次运行时会自动在同级目录创建 `config.ini` 配置文件
3. 根据需要修改 `config.ini` 中的参数
4. 按照下方 [使用方法](#-使用方法) 运行命令

### 方式二：使用 Python 源码

**环境要求**: Python 3.8+

1. 克隆或下载项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行主程序：
   ```bash
   python main.py --help
   ```

---

## 📖 使用方法

### 发送端 (qr-send)

用于将文件或文件夹生成二维码。

#### 可执行文件方式

```bash
# 生成并显示二维码
qr-send.exe generate -i <文件或文件夹路径>

# 使用自定义任务 ID
qr-send.exe generate -i <文件或文件夹路径> -t MY_TASK_001

# 只生成二维码文件，不显示
qr-send.exe generate -i <文件或文件夹路径> --no-display

# 显示已生成的二维码
qr-send.exe display -p <二维码文件或目录路径>
```

#### Python 源码方式

```bash
# 生成并显示二维码
python send.py generate -i <文件或文件夹路径>

# 使用自定义任务 ID
python send.py generate -i <文件或文件夹路径> -t MY_TASK_001

# 只生成二维码文件，不显示
python send.py generate -i <文件或文件夹路径> --no-display

# 显示已生成的二维码
python send.py display -p <二维码文件或目录路径>
```

### 接收端 (qr-receive)

用于读取屏幕上的二维码并还原文件。

#### 可执行文件方式

```bash
# 读取屏幕二维码并还原文件
qr-receive.exe read -o <输出目录>

# 验证区块链完整性
qr-receive.exe verify
```

#### Python 源码方式

```bash
# 读取屏幕二维码并还原文件
python receive.py read -o <输出目录>

# 验证区块链完整性
python receive.py verify
```

---

## 🔍 工作原理

### 生成流程（发送端）

```
文件/文件夹 → 压缩为 zip → 计算哈希 → base64 编码 → 分割数据块 → 生成二维码 → 循环显示
                                    ↓
                              记录到哈希链
```

1. 压缩文件或文件夹为 zip 格式
2. 计算压缩文件的哈希值
3. 将压缩文件转换为 base64 编码
4. 分割为多个数据块
5. 为每个数据块生成二维码，包含元数据和哈希值
6. 将操作记录添加到哈希链
7. 按设定时间间隔循环显示二维码

### 读取流程（接收端）

```
屏幕捕获 → 识别二维码 → 解析数据 → 验证哈希 → 合并数据块 → base64 解码 → 解压缩 → 还原文件
                                    ↓
                              记录到哈希链
```

1. 从屏幕捕获图像
2. 识别二维码
3. 解析二维码数据，提取元数据
4. 验证数据哈希值
5. 收集所有数据块
6. 合并数据块为完整的 base64 字符串
7. 转换为压缩文件
8. 解压缩为原始文件或文件夹
9. 将操作记录添加到哈希链

---

## ⚙️ 配置文件

首次运行时会自动在可执行文件同目录创建 `config.ini`，也可直接复制并修改。

### [General]
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `TaskIDMode` | 任务 ID 生成方式（`random` 或 `custom`） | `random` |
| `CustomTaskID` | 自定义任务 ID（当 TaskIDMode=custom 时使用） | 空 |

### [Compression]
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `CompressionLevel` | 压缩级别（0-9，0=无压缩，9=最高压缩） | `9` |

### [QRCode]
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `Version` | 二维码版本（1-40，0=自动） | `1` |
| `ErrorCorrection` | 容错率（L-7%, M-15%, Q-25%, H-30%） | `M` |
| `Size` | 二维码大小（像素） | `600` |
| `BoxSize` | 每个模块的像素数 | `10` |
| `Border` | 边框大小（模块数） | `4` |
| `Format` | 二维码图片格式 | `PNG` |
| `DisplayInterval` | 显示间隔时间（秒） | `2` |
| `BlockSize` | 数据块大小（字节） | `1000` |

### [Output]
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `OutputDir` | 输出目录 | `output` |
| `TempDir` | 临时文件目录 | `temp` |

### [Log]
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `LogLevel` | 日志级别 | `INFO` |
| `LogFile` | 日志文件路径 | `qrcode_transfer.log` |
| `LogFormat` | 日志格式 | `%(asctime)s - %(levelname)s - %(task_id)s - %(message)s` |

### [Blockchain]
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `Enabled` | 是否启用哈希链 | `True` |
| `HashAlgorithm` | 哈希算法（SHA256, SHA512, MD5） | `SHA256` |
| `ChainFile` | 哈希链文件路径 | `hash_chain.json` |

### [QRCodeReader]
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `MaxAttempts` | 最大尝试识别次数 | `30` |
| `AttemptInterval` | 识别间隔时间（秒） | `2` |

---

## 📁 项目结构

```
qrcode_transfer/
├── main.py              # 主程序入口（完整功能）
├── send.py              # 发送端入口（轻量版）
├── receive.py           # 接收端入口（完整版）
├── config.ini           # 配置文件
├── requirements.txt     # 依赖库列表
├── build.bat            # 一键打包脚本
├── README.md            # 项目说明文档
├── qrcode_transfer.log  # 日志文件
├── hash_chain.json      # 哈希链文件
├── output/              # 输出目录
│   └── qr_<任务ID>/     # 生成的二维码文件
├── temp/                # 临时文件目录
├── dist/                # 打包后的可执行文件
│   ├── qr-send.exe      # 发送端（~23MB）
│   └── qr-receive.exe   # 接收端（~81MB）
└── modules/             # 功能模块
    ├── config_manager.py # 配置管理
    ├── config_init.py    # 配置初始化（自动生成 config.ini）
    ├── logger.py         # 日志管理
    ├── compressor.py     # 压缩解压缩
    ├── encoder.py        # base64编码解码
    ├── qrcode_generator.py # 二维码生成
    ├── displayer.py      # 二维码显示
    ├── qrcode_reader.py  # 二维码识别
    ├── validator.py      # 数据校验
    └── blockchain.py     # 哈希链管理
```

---

## 🛠 技术栈

- **语言**: Python 3.8+
- **依赖库**:
  | 库 | 用途 | 使用端 |
  |----|------|--------|
  | `qrcode[pil]` | 二维码生成 | 发送端 |
  | `pillow` | 图像处理 | 两端 |
  | `pyzbar` | 二维码识别 | 接收端 |
  | `opencv-python` | 图像处理 | 接收端 |
  | `pyautogui` | 屏幕捕获 | 接收端 |
  | `pycryptodome` | 哈希计算 | 两端 |
  | `tkinter` | GUI 显示 | 发送端 |
  | `numpy` | 数组处理 | 接收端 |

---

## 📦 打包说明

项目提供一键打包脚本 `build.bat`，运行后会自动生成 `qr-send.exe` 和 `qr-receive.exe`。

### 打包优化

| 优化项 | 说明 |
|--------|------|
| 依赖分离 | send 端排除 cv2/numpy/pyautogui/pyzbar，节省约 130MB |
| 排除冗余 GUI | receive 端排除 PyQt5，节省约 60MB |
| UPX 压缩 | 使用 PyInstaller 内置 UPX 压缩可执行文件 |
| 配置运行时生成 | config.ini 不再打包，首次运行时自动生成 |
| DLL 嵌入 | pyzbar 所需的 libiconv.dll 和 libzbar-64.dll 自动打包 |

### 重新打包

```bash
# Windows
build.bat
```

---

## 🔒 安全性

1. **数据完整性**: 每个数据块都有 SHA256 哈希值，确保传输过程中数据不被篡改
2. **操作可追溯**: 基于区块链的哈希链，所有操作都有记录，不可篡改
3. **灵活配置**: 支持调整二维码容错率，提高识别成功率
4. **临时文件管理**: 自动清理临时文件，确保安全

---

## ⚠️ 注意事项

1. 二维码大小和数据块大小会影响生成的二维码数量
2. 建议在光线充足的环境下使用，提高二维码识别成功率
3. 大屏幕显示二维码效果更好
4. 对于大文件，生成的二维码数量会较多，请耐心等待
5. 接收端运行时，请确保二维码已清晰显示在屏幕上

---

## 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| 二维码无法识别 | 检查光线、二维码大小和质量，调整配置文件中的 `ErrorCorrection` 和 `Size` 参数 |
| 生成速度慢 | 降低压缩级别（`CompressionLevel`）或增大数据块大小（`BlockSize`） |
| 内存占用高 | 增大数据块大小，减少二维码数量 |
| 日志过大 | 调整日志级别为 INFO 或 WARNING |
| 接收端识别失败 | 确保二维码清晰显示，调整 `MaxAttempts` 和 `AttemptInterval` 参数 |
| 配置文件不存在 | 首次运行会自动创建，也可从项目目录复制 `config.ini` |

---

## 📝 版本历史

### v1.0.0
- 初始版本
- 实现基本的二维码生成和读取功能
- 支持配置管理
- 支持日志记录
- 支持区块链可追溯
- 打包为独立可执行文件

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**使用说明**: 本工具仅用于合法用途，请勿用于传输非法内容。
