import argparse
from functools import lru_cache as cache

from .args import Args, BuildType


@cache
def get_args() -> Args:
    """使用 argparse 解析命令行参数并返回一个 Args pydantic 模型实例。"""
    parser = argparse.ArgumentParser(description="PHIS 自定义构建系统。")

    parser.add_argument(
        "--build",
        type=str,
        choices=[bt.value for bt in BuildType],
        default=None,  # 没有默认构建操作
        help="构建类型: 'exe' (PyInstaller) 或 'pyz' (zipapp)。如果未提供，则不执行构建。",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="将构建产物复制到目标位置（共享目录或beta目录）。",
    )
    parser.add_argument(
        "--beta",
        action="store_true",
        help="执行beta构建，将产物复制到本地Windows目录并附加'b'到版本号。",
    )

    parsed_args = parser.parse_args()

    # 从解析的参数创建 Args 模型实例
    args_model = Args(
        build=BuildType(parsed_args.build) if parsed_args.build else None,
        copy_=parsed_args.copy,
        beta=parsed_args.beta,
    )
    return args_model
