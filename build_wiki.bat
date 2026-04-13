@echo off
chcp 65001 >nul
echo ========================================
echo   Wiki 文档转静态网页
echo ========================================
echo.

:: 检查 MkDocs
pip show mkdocs >nul 2>&1
if errorlevel 1 (
    echo [1/3] 安装 MkDocs 和 Material 主题...
    pip install mkdocs mkdocs-material
) else (
    echo [1/3] MkDocs 已安装
)
echo.

:: 复制文档
echo [2/3] 复制 Wiki 文档...
if not exist docs mkdir docs
xcopy /Y /E .zread\wiki\versions\2026-04-13-163505\*.md docs\ >nul
echo 已复制文档到 docs/
echo.

:: 构建网站
echo [3/3] 生成静态网站...
mkdocs build -f docs\mkdocs.yml
echo.

:: 显示结果
echo ========================================
echo   构建完成！
echo ========================================
echo.
echo 静态网站位置: docs-site\
echo 大小: ~3.6 MB
echo.
echo 预览方式：
echo   1. 直接双击 docs-site\index.html
echo   2. 或者运行: cd docs-site ^&^& python -m http.server 8000
echo   3. 然后浏览器访问: http://localhost:8000
echo.
echo 部署方式：
echo   可将 docs-site\ 目录部署到 GitHub Pages、Vercel、Nginx 等
echo ========================================
pause
