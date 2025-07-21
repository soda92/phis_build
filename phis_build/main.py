import sys
from . import config, build_steps
from .version import read_and_update_version

def run_full_build():
    """执行完整的构建、打包和复制流程。"""
    print('开始完整构建流程...')
    build_steps.clean_temp_dir()
    config.RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    
    version = read_and_update_version()
    build_steps.build()
    build_steps.copy_dirs()
    target_dir = build_steps.copy_to_release_dir(version)
    zip_file_path = build_steps.make_zip(target_dir, version)
    
    if '--no-copy' not in sys.argv:
        build_steps.copy_to_share(zip_file_path)
    
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
    if '--copy-only' in sys.argv:
        run_copy_only()
    else:
        run_full_build()

if __name__ == '__main__':
    main()