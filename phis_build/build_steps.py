import subprocess
import shutil
import zipfile
import sys
from pathlib import Path
from tqdm import tqdm
from . import config
import logging


def build():
    """使用 PyInstaller 进行打包。"""
    logging.info('1. 使用 PyInstaller 打包...')
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


def rename_executable(version: str):
    """将打包好的 exe 重命名以包含版本号。"""
    try:
        original_exe = config.TEMP_DIR / f'{config.PROJECT_NAME}.exe'
        if original_exe.exists():
            new_exe_name = f'{config.PROJECT_NAME}_v{version}.exe'
            original_exe.rename(original_exe.with_name(new_exe_name))
            logging.info(f'已将可执行文件重命名为: {new_exe_name}')
        else:
            logging.info(f'警告: 未在 {config.TEMP_DIR} 中找到 {original_exe.name}。')
    except Exception as e:
        logging.info(f'警告: 重命名可执行文件失败: {e}')


def copy_dirs():
    """复制必要的目录（浏览器、配置文件、文档）到临时构建目录。"""
    logging.info('2. 复制目录到 release...')
    for d in [config.浏览器, config.浏览器配置文件]:
        if d.exists():
            shutil.copytree(d, config.TEMP_DIR / d.name, dirs_exist_ok=True)

    doc_dir = config.文档目录
    target_doc_dir = config.TEMP_DIR / '文档'
    if doc_dir.exists():
        target_doc_dir.mkdir(exist_ok=True)
        files = [i for i in doc_dir.glob('*') if ('bak' not in i.name) and (not i.name.startswith('.')) and ('env.txt' not in i.name)]
        for file in files:
            shutil.copy(file, target_doc_dir / file.name)

    bin_dir = config.TEMP_DIR / 'phis_bin'
    # rename it to BIN
    if bin_dir.exists():
        bin_dir.rename(config.TEMP_DIR / 'BIN')

    # 移动 env.txt 到特定的子目录
    执行结果目录 = config.TEMP_DIR / '执行结果'
    执行结果目录.mkdir(exist_ok=True)
    env_file_source = config.TEMP_DIR / '文档' / 'env.txt'
    if env_file_source.exists():
        shutil.move(str(env_file_source), 执行结果目录 / 'env.txt')
    else:
        执行结果目录.joinpath('env.txt').write_text(
            """总操作数:3
当前处理身份证号:
已完成数量:0
""",
            encoding='utf-8',
        )


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
    logging.info(f'3. 压缩为 {zip_path} ...')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in target_dir.rglob('*'):
            zf.write(file, file.relative_to(target_dir.parent))
    logging.info(f'已创建压缩包: {zip_path}')
    return zip_path


def get_available_share_path() -> Path | None:
    """
    检查并返回第一个可访问的网络共享路径。
    """
    paths_to_check = [p for p in [config.SHARE_PATH, config.SHARE_PATH2] if p]

    for path in paths_to_check:
        if not str(path).startswith('\\\\'):
            logging.info(f'路径 {path} 不是一个有效的 UNC 路径，跳过检查。')
            continue
        try:
            logging.info(f'正在检查网络共享路径 {path} ...')
            if path.is_dir():
                logging.info(f'网络共享路径 {path} 可访问。')
                return path
            else:
                logging.info(f'警告: 共享路径 {path} 存在但不是一个目录。')
        except Exception as e:
            logging.info(f'警告: 无法访问网络共享路径 {path}。错误: {e}')

    logging.info('所有配置的共享路径均不可用。')
    return None


def copy_to_share(file: Path, share_path: Path):
    """尝试将文件复制到指定的网络共享位置。"""
    try:
        destination_file = share_path / file.name
        logging.info(f'4. 尝试复制到共享目录 {destination_file} ...')

        share_path.mkdir(parents=True, exist_ok=True)
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

        logging.info(f'\n成功复制到: {destination_file}')
    except Exception as e:
        logging.info(f'\n警告: 复制到共享目录失败，已忽略。错误: {e}')


def copy_dir_to_share(source_dir: Path, share_path: Path):
    """尝试将整个目录复制到指定的网络共享位置，并显示进度条。"""
    try:
        destination_dir = share_path / source_dir.name
        logging.info(f'4. 尝试将目录复制到共享位置 {destination_dir} ...')

        if destination_dir.exists():
            logging.info(f'警告: 目标目录 {destination_dir} 已存在。正在删除旧目录...')
            shutil.rmtree(destination_dir)

        # 1. 获取所有文件列表和总大小
        files_to_copy = [p for p in source_dir.rglob('*') if p.is_file()]
        total_size = sum(p.stat().st_size for p in files_to_copy)

        # 2. 创建进度条
        with tqdm(
            total=total_size, unit='B', unit_scale=True, desc=f'复制 {source_dir.name}'
        ) as pbar:
            # 3. 遍历并复制文件
            for src_file in files_to_copy:
                relative_path = src_file.relative_to(source_dir)
                dest_file = destination_dir / relative_path

                # 确保目标目录存在
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                # 复制文件
                shutil.copy2(src_file, dest_file)

                # 更新进度条
                pbar.update(src_file.stat().st_size)

        logging.info(f'\n成功将目录复制到: {destination_dir}')
    except Exception as e:
        logging.info(f'\n警告: 复制目录到共享位置失败，已忽略。错误: {e}')


def clean_temp_dir():
    """清理临时构建目录。"""
    if config.TEMP_DIR.exists():
        shutil.rmtree(config.TEMP_DIR)


def clean_old_releases(keep: int = 2, zip_and_folder=True):
    """清理旧的发布目录，只保留指定数量的最新版本。"""
    try:
        logging.info(f'5. 清理旧的发布目录，保留最新的 {keep} 个版本...')

        # 获取所有符合命名规则的发布目录
        release_dirs = [
            d
            for d in config.RELEASE_DIR.iterdir()
            if d.is_dir() and d.name.startswith(f'{config.PROJECT_NAME}_v')
        ]

        # 按修改时间降序排序（最新的在前）
        release_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)

        # 如果目录数量超过要保留的数量，则删除多余的
        if len(release_dirs) > keep:
            dirs_to_delete = release_dirs[keep:]
            logging.info(f'将删除以下旧目录: {[str(d.name) for d in dirs_to_delete]}')
            for d in dirs_to_delete:
                shutil.rmtree(d)
            logging.info('旧目录清理完毕。')
        else:
            logging.info('没有需要清理的旧目录。')

        if zip_and_folder:
            # 清理旧的 ZIP 文件
            zip_files = list(config.RELEASE_DIR.glob(f'{config.PROJECT_NAME}_v*.zip'))
            if len(zip_files) > keep:
                zip_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                for f in zip_files[keep:]:
                    f.unlink()
                logging.info('旧的 ZIP 文件清理完毕。')
            else:
                logging.info('没有需要清理的旧 ZIP 文件。')

    except Exception as e:
        logging.info(f'警告: 清理旧的构建结果失败: {e}')
