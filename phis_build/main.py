import sys
import argparse
from . import config, build_steps
from .version import read_and_update_version

def run_full_build(no_zip: bool, no_copy: bool):
    """
    执行完整的构建、打包和复制流程。

    :param no_zip: 如果为 True，则不压缩，直接复制目录。
    :param no_copy: 如果为 True，则不执行最后的复制操作。
    """
    print('开始完整构建流程...')
    build_steps.clean_temp_dir()
    config.RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    version = read_and_update_version()
    build_steps.build()
    build_steps.rename_executable(version)
    build_steps.copy_dirs()
    target_dir = build_steps.copy_to_release_dir(version)

    # 根据参数决定是压缩还是直接复制目录
    if no_zip:
        print("检测到 --no-zip 参数，跳过压缩步骤。")
        if not no_copy:
            build_steps.copy_dir_to_share(target_dir)
    else:
        zip_file_path = build_steps.make_zip(target_dir, version)
        if not no_copy:
            build_steps.copy_to_share(zip_file_path)
    
    build_steps.clean_old_releases(keep=2)
    print("\n构建完成！")

def run_copy_only():
    """仅执行将最新构建产物复制到共享目录的操作。"""
    print('检测到 --copy-only 参数，仅执行复制操作...')
    try:
        zip_files = list(config.RELEASE_DIR.glob(f'{config.PROJECT_NAME}_v*.zip'))
        if not zip_files:
            print(f'错误: 在目录 {config.RELEASE_DIR} 中未找到可复制的 zip 文件。')
            print('请先至少运行一次完整的构建流程。')
            sys.exit(1)

        latest_zip_file = max(zip_files, key=lambda p: p.stat().st_mtime)
        print(f'找到最新的文件: {latest_zip_file.name}')
        build_steps.copy_to_share(latest_zip_file)
    except Exception as e:
        print(f'复制操作失败: {e}')
        sys.exit(1)

def main():
    """脚本主入口，根据命令行参数选择执行流程。"""
    parser = argparse.ArgumentParser(description="PHIS 自定义构建系统。")

    parser.add_argument(
        '--copy-only',
        action='store_true',
        help='不执行构建，仅将最新的 ZIP 包复制到共享目录。'
    )
    parser.add_argument(
        '--no-zip',
        action='store_true',
        default=True,
        help='执行构建，但不创建 ZIP 压缩包，而是直接复制整个目录。'
    )
    parser.add_argument(
        '--no-copy',
        action='store_true',
        help='执行构建，但最后不将产物（ZIP 或目录）复制到共享目录。'
    )

    args = parser.parse_args()

    if args.copy_only:
        run_copy_only()
    else:
        run_full_build(no_zip=args.no_zip, no_copy=args.no_copy)

if __name__ == '__main__':
    main()