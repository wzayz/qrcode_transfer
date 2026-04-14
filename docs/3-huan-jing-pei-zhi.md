本页面将指导您完成 QR Code 文件传输工具的环境配置，确保您能够顺利运行该项目。无论您是选择使用可执行文件还是 Python 源码，都将在这里找到所需的环境设置信息。

## 系统要求

在开始配置环境之前，请确保您的系统满足以下基本要求：

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Windows 7+ | Windows 10/11 |
| 处理器 | 1 GHz 双核处理器 | 2 GHz 四核处理器或更高 |
| 内存 | 2 GB RAM | 4 GB RAM 或更高 |
| 磁盘空间 | 100 MB 可用空间 | 500 MB 可用空间 |
| 显示分辨率 | 1024×768 | 1920×1080 或更高 |

这些要求确保了二维码生成和读取过程的流畅运行，特别是对于较大文件的处理。

Sources: [README.md](README.md#L1-L50)

## Python 环境配置（源码运行方式）

如果您选择使用 Python 源码运行项目，需要先配置 Python 环境：

### Python 版本要求

项目要求 **Python 3.8 或更高版本**。您可以通过以下命令检查当前 Python 版本：

```bash
python --version
```

如果尚未安装 Python 或版本不符合要求，请访问 [Python 官方网站](https://www.python.org/downloads/) 下载并安装适合您系统的 Python 版本。

### 创建虚拟环境（推荐）

为了避免依赖冲突，建议使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv qrcode_env

# 激活虚拟环境（Windows）
qrcode_env\Scripts\activate
```

激活虚拟环境后，您会看到命令提示符前出现 `(qrcode_env)` 标识。

Sources: [README.md](README.md#L80-L100)

## 依赖库安装

项目依赖多个 Python 库，这些库在 `requirements.txt` 文件中列出。安装依赖的步骤如下：

### 使用 pip 安装依赖

在项目根目录下，运行以下命令安装所有依赖：

```bash
pip install -r requirements.txt
```

### 依赖库说明

以下是项目所需的主要依赖库及其用途：

| 库名 | 版本要求 | 用途 |
|------|----------|------|
| qrcode[pil] | >=7.4.2,<8.0.0 | 生成二维码图像 |
| pyzbar | >=0.1.9,<0.2.0 | 解析二维码内容 |
| opencv-python | >=4.8.0,<5.0.0 | 屏幕捕获和图像处理 |
| pyautogui | >=0.9.54,<0.10.0 | 屏幕交互功能 |
| pycryptodome | >=3.19.0,<4.0.0 | 加密和哈希计算 |
| pillow | >=10.0.0,<11.0.0 | 图像处理支持 |
| configparser | >=5.3.0,<6.0.0 | 配置文件管理 |
| numpy | >=1.24.0,<2.0.0 | 数值计算支持 |

Sources: [requirements.txt](requirements.txt#L1-L8)

## 配置文件设置

项目使用 `config.ini` 文件进行配置管理。该文件在首次运行时会自动生成，位于项目根目录或可执行文件同级目录。

### 配置文件结构

配置文件包含以下主要部分：

```
[General]          # 通用设置
[Compression]      # 压缩设置
[QRCode]           # 二维码生成设置
[Output]           # 输出目录设置
[Log]              # 日志设置
[Blockchain]       # 区块链设置
[QRCodeReader]     # 二维码读取设置
```

### 目录准备

虽然程序会自动创建必要的目录，但建议您提前了解以下目录结构：

```
qrcode_transfer/
├── output/         # 二维码输出目录（自动创建）
├── temp/           # 临时文件目录（自动创建）
├── config.ini      # 配置文件（首次运行自动生成）
└── qrcode_transfer.log  # 日志文件（自动生成）
```

Sources: [config.ini](config.ini#L1-L55)

## 可执行文件运行环境（推荐）

如果您选择使用预编译的可执行文件，环境配置将更加简单：

### 基本要求

- 无需安装 Python 或任何依赖库
- 只需确保系统满足前面提到的基本系统要求

### 文件说明

项目提供两个独立的可执行文件：

| 文件名 | 大小 | 功能 |
|--------|------|------|
| qr-send.exe | ~23MB | 生成并显示二维码（发送端） |
| qr-receive.exe | ~81MB | 读取屏幕二维码并还原文件（接收端） |

### 使用步骤

1. 将所需的可执行文件复制到任意目录
2. 双击运行或通过命令行运行
3. 首次运行会自动在同级目录创建 `config.ini` 配置文件
4. 根据需要修改配置文件中的参数

Sources: [README.md](README.md#L60-L80)

## 环境验证

完成配置后，建议进行以下验证步骤：

### 源码方式验证

```bash
# 检查 Python 版本
python --version

# 检查依赖是否安装成功
pip list

# 运行程序查看帮助信息
python main.py --help
```

### 可执行文件方式验证

```bash
# 查看发送端帮助信息
qr-send.exe --help

# 查看接收端帮助信息
qr-receive.exe --help
```

如果以上命令都能正常执行并显示相应信息，说明环境配置成功。

Sources: [main.py](main.py#L1-L20)

## 下一步

完成环境配置后，您可以继续阅读以下页面：

- [安装依赖](4-an-zhuang-yi-lai) - 了解更详细的依赖安装说明
- [生成二维码](5-sheng-cheng-er-wei-ma) - 学习如何使用工具生成二维码
- [读取二维码](6-du-qu-er-wei-ma) - 了解如何读取并还原二维码中的文件

祝您使用愉快！