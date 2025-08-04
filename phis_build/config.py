import sys
from pathlib import Path
import os
import logging

try:
    import tomllib
except ImportError:
    # For Python < 3.11, you might need to pip install toml
    import toml as tomllib

# --- 基本路径 ---
PROJECT_ROOT = Path(os.getcwd())
"""项目根目录"""

CONFIG_FILE = PROJECT_ROOT / 'phis_build.toml'

if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(
        encoding='utf-8',
        data="""
# 配置文件示例
# 请根据实际情况修改以下内容
project_name = "NAME"
share_path = "//192.168.a.b/11/22/33"
# share_path2 = "//192.168.c.d/share" # (可选) 第二个备用共享路径
""",
    )
    logging.info(f'配置文件 {CONFIG_FILE} 不存在，已创建示例文件。请根据实际情况修改。')
    exit(1)

# --- 从 toml 加载配置 ---
try:
    with open(CONFIG_FILE, 'rb') as f:
        _config = tomllib.load(f)
    PROJECT_NAME = _config['project_name']
    SHARE_PATH = Path(_config['share_path'].replace('/', '\\'))
    _share_path2_str = _config.get('share_path2')
    SHARE_PATH2 = Path(_share_path2_str.replace('/', '\\')) if _share_path2_str else None
except (FileNotFoundError, KeyError) as e:
    logging.info(f"错误: 无法加载或解析 '{CONFIG_FILE.name}' 文件。")
    logging.info(f"请确保该文件存在于 '{PROJECT_ROOT}' 目录下，")
    logging.info(f"并且包含了 'project_name' 和 'share_path' 键。")
    logging.info(f'详细错误: {e}')
    sys.exit(1)

# --- 派生路径和常量 ---
RELEASE_DIR = PROJECT_ROOT / 'releases'
"""存放最终发布版本和压缩包的目录"""

TEMP_DIR = RELEASE_DIR / 'temp'
"""用于构建过程的临时目录"""

DIST_DIR = PROJECT_ROOT / 'dist'
"""PyInstaller 的默认输出目录 (在此脚本中未使用，但作为参考)"""

BUILD_DIR = PROJECT_ROOT / 'build'
"""PyInstaller 的工作目录"""

SPEC_FILE = PROJECT_ROOT / f'{PROJECT_NAME}.spec'
"""PyInstaller 的 .spec 配置文件路径"""

if not SPEC_FILE.exists():
    SPEC_FILE.write_text(
        encoding='utf-8',
        data=f"""# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['{PROJECT_NAME}.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.venv/Lib/site-packages/ddddocr/common_old.onnx', 'ddddocr'),
        ('.venv/Lib/site-packages/ddddocr/common.onnx', 'ddddocr'),
        ('.venv/Lib/site-packages/onnxruntime/capi/onnxruntime_providers_shared.dll', 'onnxruntime\capi'),
        ('.venv/Lib/site-packages/onnxruntime/capi/onnxruntime_pybind11_state.pyd', 'onnxruntime\capi'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{PROJECT_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
""",
    )
    logging.info(f'未找到 {SPEC_FILE}，已创建默认的 PyInstaller 配置文件。')

VERSION_FILE = PROJECT_ROOT / 'VERSION'
"""存储版本号的文件"""

# --- 源目录 ---
文档目录 = PROJECT_ROOT / '文档'
浏览器配置文件 = PROJECT_ROOT / '配置文件'
浏览器 = PROJECT_ROOT / 'BIN'
