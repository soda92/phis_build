import sys
from pathlib import Path
import os
try:
    import tomllib
except ImportError:
    # For Python < 3.11, you might need to pip install toml
    import toml as tomllib

# --- 基本路径 ---
PROJECT_ROOT = Path(os.getcwd())
"""项目根目录"""

# --- 从 config.toml 加载配置 ---
try:
    with open(PROJECT_ROOT / 'config.toml', 'rb') as f:
        _config = tomllib.load(f)
    PROJECT_NAME = _config['project_name']
    SHARE_PATH = Path(_config['share_path'])
except (FileNotFoundError, KeyError) as e:
    print(f"错误: 无法加载或解析 'config.toml' 文件。")
    print(f"请确保该文件存在于 '{PROJECT_ROOT}' 目录下，")
    print(f"并且包含了 'project_name' 和 'share_path' 键。")
    print(f"详细错误: {e}")
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

VERSION_FILE = PROJECT_ROOT / 'VERSION'
"""存储版本号的文件"""

# --- 源目录 ---
文档目录 = PROJECT_ROOT / '文档'
浏览器配置文件 = PROJECT_ROOT / '配置文件'
浏览器 = Path(__file__).resolve().parent.parent / 'phis_bin'