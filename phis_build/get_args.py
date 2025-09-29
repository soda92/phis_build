import argparse
from functools import lru_cache as cache


@cache
def get_args():
    parser = argparse.ArgumentParser(description="PHIS 自定义构建系统。")

    parser.add_argument(
        "--copy-only",
        action="store_true",
        help="不执行构建，仅将最新的 ZIP 包复制到共享目录。",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        default=False,
        help="执行构建，但不创建 ZIP 压缩包，而是直接复制整个目录。",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="执行构建，但最后不将产物（ZIP 或目录）复制到共享目录。",
    )

    parser.add_argument(
        "--no-config-tool",
        action="store_true",
        default=False,
        help="不生成配置工具脚本"
    )

    parser.add_argument(
        "--zipapp", "-z", action="store_true", help="使用 zipapp 模块打包应用程序。"
    )

    args = parser.parse_args()
