import argparse
try:
    from phis_logging.logging_config import setup_logging
except ImportError:
    from .logging_config import setup_logging
from .main import run_full_build


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="PHIS Build Tool")
    parser.add_argument("--no-zip", action="store_true", help="不压缩，直接复制目录")
    parser.add_argument("--no-copy", action="store_true", help="不执行最后的复制操作")
    parser.add_argument("--use-pyz", "-z", action="store_true", help="使用 zipapp 打包")
    parser.add_argument("--same-ver", action="store_true", help="不更新版本号")

    args = parser.parse_args()

    run_full_build(
        no_zip=args.no_zip,
        no_copy=args.no_copy,
        use_pyz=args.use_pyz,
    )


if __name__ == "__main__":
    main()
