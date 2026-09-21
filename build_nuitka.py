"""Nuitka 打包脚本：编译为单文件 exe，启动更快（无需每次解压）

通过 NUITKA_CACHE_DIR 把缓存目录重定向到项目内，避免写入受限的系统目录。
首次运行会自动下载 Nuitka 专用的 MinGW64 编译器（一次性），之后编译会快很多。
"""
import os
import subprocess
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

# 把 Nuitka 缓存（含编译器下载、模块缓存）重定向到项目目录内
cache_dir = os.path.join(current_dir, 'nuitka_cache')
os.makedirs(cache_dir, exist_ok=True)
env = os.environ.copy()
env['NUITKA_CACHE_DIR'] = cache_dir
# 强制 UTF-8 编码，规避 gcc 处理中文路径时的“非法字节序列”错误
env['PYTHONUTF8'] = '1'
env['PYTHONIOENCODING'] = 'utf-8'
env['LC_ALL'] = 'C.UTF-8'
env['LANG'] = 'C.UTF-8'

args = [
    sys.executable, '-m', 'nuitka',
    '--standalone',              # 独立打包，包含所有依赖
    '--onefile',                 # 合并为单个 exe
    '--enable-plugin=pyqt5',     # 启用 PyQt5 插件，正确处理 Qt 依赖
    '--windows-console-mode=disable',  # 不显示控制台窗口
    '--windows-icon-from-ico=icon.ico',
    '--include-data-files=config.py=config.py',
    '--include-data-files=icon.ico=icon.ico',
    # 排除无用的大模块，减小体积、加快启动
    '--nofollow-import-to=tkinter',
    '--nofollow-import-to=matplotlib',
    '--nofollow-import-to=numpy',
    '--nofollow-import-to=PIL',
    '--nofollow-import-to=scipy',
    '--nofollow-import-to=pytest',
    # —— 程序只用到 QtCore / QtGui / QtWidgets，以下 PyQt5 子模块及对应
    #    Qt DLL 完全未使用，排除后可显著瘦身（已逐一启动验证不影响功能）——
    '--nofollow-import-to=PyQt5.QtQml',
    '--nofollow-import-to=PyQt5.QtQuick',
    '--nofollow-import-to=PyQt5.QtQuickWidgets',
    '--nofollow-import-to=PyQt5.QtMultimedia',
    '--nofollow-import-to=PyQt5.QtMultimediaWidgets',
    '--nofollow-import-to=PyQt5.QtPrintSupport',
    '--nofollow-import-to=PyQt5.QtSvg',
    '--nofollow-import-to=PyQt5.QtDBus',
    '--nofollow-import-to=PyQt5.QtWebSockets',
    '--nofollow-import-to=PyQt5.QtNetwork',
    # 排除随上述模块带入、但本程序不需要的原生 DLL（Qt 库、OpenSSL、插件）
    '--noinclude-dlls=qt5quick*.dll',
    '--noinclude-dlls=qt5qml*.dll',
    '--noinclude-dlls=qt5multimedia*.dll',
    '--noinclude-dlls=qt5printsupport*.dll',
    '--noinclude-dlls=qt5svg*.dll',
    '--noinclude-dlls=qt5dbus*.dll',
    '--noinclude-dlls=qt5websockets*.dll',
    '--noinclude-dlls=qt5network*.dll',
    # 串口通信不涉及 HTTPS，可去掉 OpenSSL
    '--noinclude-dlls=libcrypto-*.dll',
    '--noinclude-dlls=libeay32.dll',
    '--noinclude-dlls=ssleay32.dll',
    # Qt 插件：只保留 platforms/qwindows(显示)、styles(风格)、imageformats/qico(图标)
    '--noinclude-dlls=*/qt-plugins/mediaservice/*',
    '--noinclude-dlls=*/qt-plugins/printsupport/*',
    '--noinclude-dlls=*/qt-plugins/platformthemes/*',
    '--noinclude-dlls=*/qt-plugins/iconengines/*',
    '--noinclude-dlls=*/qt-plugins/platforms/qwebgl.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qgif.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qjpeg.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qicns.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qsvg.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qtga.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qtiff.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qwbmp.dll',
    '--noinclude-dlls=*/qt-plugins/imageformats/qwebp.dll',
    '--assume-yes-for-downloads',  # 自动确认下载编译器
    '--output-dir=dist_nuitka',
    '--output-filename=串口应答调试助手.exe',
    'uart_assistant.py',
]

print(f"开始 Nuitka 打包，当前目录: {current_dir}")
print(f"Nuitka 缓存目录: {cache_dir}")
print(f"打包参数: {' '.join(args[2:])}")

result = subprocess.run(args, cwd=current_dir, env=env)
sys.exit(result.returncode)
