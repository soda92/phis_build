import logging
import sys
from pathlib import Path

from . import build_steps, build_zipapp, config
from .args import Args, BuildType
from .get_args import get_args
from .version import read_and_update_version

try:
    from phis_logging.logging_config import setup_logging
except ImportError:
    from .logging_config import setup_logging


def run_full_build(args: Args):
    """执行完整的构建、打包和复制流程。"""
    logging.info("开始完整构建流程...")
    build_steps.clean_temp_dir()
    config.RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    version = read_and_update_version(beta=args.beta)

    if args.build == BuildType.PYZ:
        logging.info("使用 zipapp 进行打包...")
        build_zipapp.make_package()
        build_steps.rename_pyz(version)
    else:  # 默认为 BuildType.EXE
        build_steps.build()
        build_steps.rename_executable(version)

    build_steps.copy_dirs(use_pyz=(args.build == BuildType.PYZ))
    target_dir = build_steps.copy_to_release_dir(version)
    zip_path = build_steps.make_zip(target_dir, version)

    if args.copy_:
        destination = None
        if args.beta:
            destination = Path.home() / "Windows"
            logging.info(f"Beta build: 目标目录为 {destination}")
        else:
            destination = build_steps.get_available_share_path()
            if destination:
                logging.info(f"Release build: 目标目录为 {destination}")

        if destination:
            destination.mkdir(parents=True, exist_ok=True)
            build_steps.copy_to_share(zip_path, destination)
        else:
            logging.warning("未找到可用的复制目标目录，跳过复制步骤。")

    build_steps.clean_old_releases(keep=2)
    logging.info("\n构建完成！")


def run_copy_only(args: Args):
    """仅执行将最新构建产物复制到目标位置的操作。"""
    logging.info("仅执行复制操作...")
    try:
        # 总是处理 .zip 文件，因为这是标准的构建产物
        release_items = list(config.RELEASE_DIR.glob(f"{config.PROJECT_NAME}_v*.zip"))
        if not release_items:
            logging.error(
                f"错误: 在目录 {config.RELEASE_DIR} 中未找到可复制的构建产物 (.zip)。"
            )
            sys.exit(1)

        latest_item = max(release_items, key=lambda p: p.stat().st_mtime)
        logging.info(f"找到最新的构建产物: {latest_item.name}")

        destination = None
        if args.beta:
            destination = Path.home() / "Windows"
            logging.info(f"Beta copy: 目标目录为 {destination}")
        else:
            destination = build_steps.get_available_share_path()
            if destination:
                logging.info(f"Release copy: 目标目录为 {destination}")

        if destination:
            destination.mkdir(parents=True, exist_ok=True)
            build_steps.copy_to_share(latest_item, destination)
        else:
            logging.error("错误: 所有目标路径均不可用，无法执行复制操作。")
            sys.exit(1)

    except Exception as e:
        logging.error(f"复制操作失败: {e}", exc_info=True)
        sys.exit(1)


def main():
    """脚本主入口，根据命令行参数选择执行流程。"""
    setup_logging()
    args = get_args()

    if args.build:
        run_full_build(args)
    elif args.copy_:
        run_copy_only(args)
        build_steps.clean_old_releases()
    else:
        logging.warning(
            "没有指定任何操作 (例如 --build 或 --copy)。请使用 --help 查看可用选项。"
        )


if __name__ == "__main__":
    main()
