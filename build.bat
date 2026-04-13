@echo off
chcp 65001 >nul
echo ========================================
echo   QR Code Transfer 工具打包脚本
echo ========================================
echo.

:: 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [1/4] 安装 PyInstaller...
    pip install pyinstaller
) else (
    echo [1/4] PyInstaller 已安装
)
echo.

:: 打包 qr-send.exe
echo [2/4] 打包 qr-send.exe (轻量版 ~23MB)...
pyinstaller --clean --noconfirm --onefile ^
    --name qr-send ^
    --exclude-module cv2 ^
    --exclude-module numpy ^
    --exclude-module pyautogui ^
    --exclude-module pyzbar ^
    --exclude-module pyscreeze ^
    --exclude-module mss ^
    --hidden-import modules.config_init ^
    send.py
echo.

:: 打包 qr-receive.exe
echo [3/4] 打包 qr-receive.exe (完整版 ~85MB)...
pyinstaller --clean --noconfirm --onefile ^
    --name qr-receive ^
    --exclude-module pyzbar ^
	--exclude-module PyQt5 ^
    --exclude-module PyQt5.QtCore ^
    --exclude-module PyQt5.QtGui ^
    --exclude-module PyQt5.QtWidgets ^
    --hidden-import modules.config_init ^
    receive.py
echo.

:: 显示结果
echo [4/4] 打包完成！
echo.
echo ========================================
echo   打包结果
echo ========================================
dir dist\qr-*.exe
echo.
echo 使用说明：
echo   1. 首次运行 exe 时会自动创建 config.ini
echo   2. qr-send.exe generate -i ^<文件/文件夹^>    生成二维码
echo   3. qr-receive.exe read -o ^<输出目录^>        读取并还原二维码
echo.
echo 注意：config.ini 会在 exe 同目录下自动生成，也可手动复制修改
echo ========================================
pause
