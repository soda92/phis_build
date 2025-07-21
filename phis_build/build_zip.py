import subprocess
from pathlib import Path
import shutil
import zipfile
import sys
from tqdm import tqdm
from datetime import date
try:
    import tomllib
except ImportError:
    # For Python < 3.11, you might need to pip install toml
    import toml as tomllib


PROJECT_ROOT = Path(__file__).resolve().parent

# --- 从配置文件加载配置 ---
try:
    with open(PROJECT_ROOT / 'config.toml', 'rb') as f:
        config = tomllib.load(f)
    PROJECT_NAME = config['project_name']
    SHARE_PATH = Path(config['share_path'])
except (FileNotFoundError, KeyError) as e:
    print(f"错误: 无法加载或解析 'config.toml' 文件。请确保文件存在且包含 'project_name' 和 'share_path'。错误: {e}")
    sys.exit(1)
# --- 配置加载结束 ---

RELEASE_DIR = PROJECT_ROOT / 'releases'
RELEASE_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = RELEASE_DIR / 'temp'
if TEMP_DIR.exists():
    # os.remove(TEMP_DIR)
    shutil.rmtree(TEMP_DIR)  # 删除临时目录以确保干净的构建
RELEASE_DIR.mkdir(parents=True, exist_ok=True)
DIST_DIR = PROJECT_ROOT / 'dist'
SPEC_FILE = PROJECT_ROOT / f'{PROJECT_NAME}.spec'
文档目录 = PROJECT_ROOT / '文档'
浏览器配置文件 = PROJECT_ROOT / '配置文件'
浏览器 = PROJECT_ROOT / 'BIN'


def copy_to_share(file: Path):
    """尝试将文件复制到网络共享位置，如果失败则忽略。"""
    try:
        share_path_dir = SHARE_PATH
        destination_file = share_path_dir / file.name

        print(f'4. 尝试复制到共享目录 {destination_file} ...')

        # 确保目标目录存在
        share_path_dir.mkdir(parents=True, exist_ok=True)

        file_size = file.stat().st_size

        with (
            open(file, 'rb') as fsrc,
            open(destination_file, 'wb') as fdst,
            tqdm(
                total=file_size, unit='B', unit_scale=True, desc=f'复制 {file.name}'
            ) as pbar,
        ):
            while True:
                chunk = fsrc.read(4096 * 1024)  # 4MB chunks
                if not chunk:
                    break
                fdst.write(chunk)
                pbar.update(len(chunk))

        print(f'\n成功复制到: {destination_file}')
        print(share_path_dir)
        print(file.name)

    except Exception as e:
        print(f'\n警告: 复制到共享目录失败，已忽略。错误: {e}')


def build():
    print('1. 使用 PyInstaller 打包...')
    subprocess.run(
        [
            sys.executable,
            '-m',
            'PyInstaller',
            '--clean',
            '--distpath',
            str(TEMP_DIR),
            '--workpath',
            str(PROJECT_ROOT / 'build'),
            str(SPEC_FILE),
        ],
        check=True,
    )


def copy_dirs():
    print('2. 复制目录到 release...')
    for d in [浏览器, 浏览器配置文件, 文档目录]:
        if d.exists():
            shutil.copytree(d, TEMP_DIR / d.name, dirs_exist_ok=True)
    执行结果目录 = TEMP_DIR / '执行结果'
    执行结果目录.mkdir(exist_ok=True)
    shutil.move(TEMP_DIR / '文档' / 'env.txt', 执行结果目录 / 'env.txt')


def copy_to_release_dir(version):
    target_dir = RELEASE_DIR / f'{PROJECT_NAME}_v{version}'
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(TEMP_DIR, target_dir, dirs_exist_ok=True)
    return target_dir


def make_zip(target_dir, version):
    zip_path = target_dir.parent / f'{PROJECT_NAME}_v{version}.zip'
    print(f'3. 压缩为 {zip_path} ...')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in target_dir.rglob('*'):
            zf.write(file, file.relative_to(target_dir.parent))
    print(f'已创建压缩包: {zip_path}')
    return zip_path


def read_and_update_version():
    """
    读取并更新版本号。
    版本格式为 YYYY.M.D.rev。
    如果最后一次构建是今天，则修订号 (rev) 增加。
    如果最后一次构建不是今天，则修订号重置为 0。
    """
    version_file = PROJECT_ROOT / 'VERSION'
    today = date.today()
    
    new_version_str = f'{today.year}.{today.month}.{today.day}.0'

    if version_file.exists():
        last_version_str = version_file.read_text(encoding='utf-8').strip()
        if last_version_str:
            try:
                parts = last_version_str.split('.')
                last_year, last_month, last_day, last_rev = map(int, parts)
                last_build_date = date(last_year, last_month, last_day)

                if last_build_date == today:
                    # 同一天构建，修订号递增
                    new_rev = last_rev + 1
                    new_version_str = f'{today.year}.{today.month}.{today.day}.{new_rev}'
                # else: 新的一天，使用上面已经设置好的默认版本号
            except (ValueError, IndexError):
                print(f"警告: VERSION 文件中的版本 '{last_version_str}' 格式无效。将从今天的日期重新开始。")
    
    # 写入新版本号
    version_file.write_text(new_version_str, encoding='utf-8')
    print(f'版本号已更新为: {new_version_str}')
    return new_version_str


# 在主流程中调用
def main():
    if '--copy-only' in sys.argv:
        print('检测到 --copy-only 参数，仅执行复制操作...')
        try:
            # 查找 releases 目录中最新的 zip 文件
            zip_files = list(RELEASE_DIR.glob(f'{PROJECT_NAME}_v*.zip'))
            if not zip_files:
                print(f'错误: 在目录 {RELEASE_DIR} 中未找到可复制的 zip 文件。')
                print('请先至少运行一次完整的构建流程。')
                sys.exit(1)

            latest_zip_file = max(zip_files, key=lambda p: p.stat().st_mtime)
            print(f'找到最新的文件: {latest_zip_file.name}')
            copy_to_share(latest_zip_file)
        except Exception as e:
            print(f'复制操作失败: {e}')
            sys.exit(1)
    else:
        print('开始完整构建流程...')
        version = read_and_update_version()
        build()
        copy_dirs()
        target_dir = copy_to_release_dir(version)
        zip_file_path = make_zip(target_dir, version)
        if '--no-copy' not in sys.argv:
            copy_to_share(zip_file_path)


if __name__ == '__main__':
    main()
