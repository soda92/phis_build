import subprocess
import shutil
import zipfile
import sys
from pathlib import Path
from tqdm import tqdm
from . import config

def build():
    """使用 PyInstaller 进行打包。"""
    print('1. 使用 PyInstaller 打包...')
    subprocess.run(
        [
            sys.executable,
            '-m',
            'PyInstaller',
            '--clean',
            '--distpath',
            str(config.TEMP_DIR),
            '--workpath',
            str(config.BUILD_DIR),
            str(config.SPEC_FILE),
        ],
        check=True,
    )

def copy_dirs():
    """复制必要的目录（浏览器、配置文件、文档）到临时构建目录。"""
    print('2. 复制目录到 release...')
    for d in [config.浏览器, config.浏览器配置文件, config.文档目录]:
        if d.exists():
            shutil.copytree(d, config.TEMP_DIR / d.name, dirs_exist_ok=True)
    
    # 移动 env.txt 到特定的子目录
    执行结果目录 = config.TEMP_DIR / '执行结果'
    执行结果目录.mkdir(exist_ok=True)
    env_file_source = config.TEMP_DIR / '文档' / 'env.txt'
    if env_file_source.exists():
        shutil.move(str(env_file_source), 执行结果目录 / 'env.txt')

def copy_to_release_dir(version: str) -> Path:
    """将临时目录的内容复制到带版本号的最终发布目录。"""
    target_dir = config.RELEASE_DIR / f'{config.PROJECT_NAME}_v{version}'
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(config.TEMP_DIR, target_dir, dirs_exist_ok=True)
    return target_dir

def make_zip(target_dir: Path, version: str) -> Path:
    """将发布目录压缩成 zip 文件。"""
    zip_path = target_dir.parent / f'{config.PROJECT_NAME}_v{version}.zip'
    print(f'3. 压缩为 {zip_path} ...')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in target_dir.rglob('*'):
            zf.write(file, file.relative_to(target_dir.parent))
    print(f'已创建压缩包: {zip_path}')
    return zip_path

def copy_to_share(file: Path):
    """尝试将文件复制到网络共享位置，如果失败则忽略。"""
    try:
        destination_file = config.SHARE_PATH / file.name
        print(f'4. 尝试复制到共享目录 {destination_file} ...')

        config.SHARE_PATH.mkdir(parents=True, exist_ok=True)
        file_size = file.stat().st_size

        with (
            open(file, 'rb') as fsrc,
            open(destination_file, 'wb') as fdst,
            tqdm(total=file_size, unit='B', unit_scale=True, desc=f'复制 {file.name}') as pbar,
        ):
            while True:
                chunk = fsrc.read(4096 * 1024)  # 4MB chunks
                if not chunk:
                    break
                fdst.write(chunk)
                pbar.update(len(chunk))

        print(f'\n成功复制到: {destination_file}')
    except Exception as e:
        print(f'\n警告: 复制到共享目录失败，已忽略。错误: {e}')

def clean_temp_dir():
    """清理临时构建目录。"""
    if config.TEMP_DIR.exists():
        shutil.rmtree(config.TEMP_DIR)