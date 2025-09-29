import sys
from .get_args import get_args
import logging
from . import config, build_steps, build_zipapp
from .version import read_and_update_version
from phis_logging import setup_logging


def run_full_build(no_zip: bool, no_copy: bool, use_pyz: bool = False):
    """
    执行完整的构建、打包和复制流程。

    :param no_zip: 如果为 True，则不压缩，直接复制目录。
    :param no_copy: 如果为 True，则不执行最后的复制操作。
    :param use_pyz: 如果为 True，则使用 zipapp 进行打包。
    """
    logging.info("开始完整构建流程...")
    build_steps.clean_temp_dir()
    config.RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    version = read_and_update_version()
    if not use_pyz:
        build_steps.build()
        build_steps.rename_executable(version)
    else:
        logging.info("使用 zipapp 进行打包...")
        build_zipapp.make_package()
        build_steps.rename_pyz(version)

    build_steps.copy_dirs(use_pyz=use_pyz)
    target_dir = build_steps.copy_to_release_dir(version)

    # 检查共享路径是否可用
    available_share_path = build_steps.get_available_share_path()

    # 根据参数和共享路径可用性决定是压缩还是直接复制目录
    if no_zip and available_share_path:
        logging.info("检测到 --no-zip 参数且共享目录可用，将直接复制目录。")
        if not no_copy:
            build_steps.copy_dir_to_share(target_dir, available_share_path)
    else:
        if no_zip and not available_share_path:
            logging.warning(
                "警告: 指定了 --no-zip 但所有共享目录均不可用，将强制创建 ZIP 文件。"
            )

        zip_file_path = build_steps.make_zip(target_dir, version)
        if not no_copy:
            if available_share_path:
                build_steps.copy_dir_to_share(target_dir, available_share_path)
            else:
                logging.info("共享目录不可用，跳过复制文件步骤。")

    build_steps.clean_old_releases(keep=2)
    logging.info("\n构建完成！")


def run_copy_only(folder=True):
    """仅执行将最新构建产物复制到共享目录的操作。"""
    logging.info("检测到 --copy-only 参数，仅执行复制操作...")
    try:
        release_items = list(config.RELEASE_DIR.glob(f"{config.PROJECT_NAME}_v*"))
        if folder:
            release_items = [item for item in release_items if item.is_dir()]
        if not release_items:
            logging.error(
                f"错误: 在目录 {config.RELEASE_DIR} 中未找到可复制的构建产物。"
            )
            logging.error("请先至少运行一次完整的构建流程。")
            sys.exit(1)

        latest_item = max(release_items, key=lambda p: p.stat().st_mtime)
        logging.info(f"找到最新的构建产物: {latest_item.name}")

        available_share_path = build_steps.get_available_share_path()
        if available_share_path:
            if latest_item.is_dir():
                build_steps.copy_dir_to_share(latest_item, available_share_path)
            else:
                build_steps.copy_to_share(latest_item, available_share_path)
        else:
            logging.error("错误: 所有共享路径均不可用，无法执行复制操作。")
            sys.exit(1)

    except Exception as e:
        logging.error(f"复制操作失败: {e}", exc_info=True)
        sys.exit(1)


def main():
    """脚本主入口，根据命令行参数选择执行流程。"""
    setup_logging()

    args = get_args()
    if args.copy_only:
        run_copy_only()
        build_steps.clean_old_releases()
    else:
        run_full_build(no_zip=args.no_zip, no_copy=args.no_copy, use_pyz=args.zipapp)


if __name__ == "__main__":
    main()
