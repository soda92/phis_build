from pathlib import Path
import tomli as tomllib
from typing import List, Tuple
import shutil
import logging
from . import config

SRC_ROOT = Path.cwd()

# pyproject.toml 路径
PYPROJECT = SRC_ROOT / "pyproject.toml"


def get_packages() -> List[Path]:
    """
    从 pyproject.toml 中获取 packages 列表。
    :return: 包含所有包名的列表。
    """
    global PYPROJECT
    with open(PYPROJECT, "rb") as f:
        data = tomllib.load(f)

    # 读取 sdist 下的 packages 配置
    def get_var(data, s: str):
        attrs = s.split(".")
        for attr in attrs:
            data = data.get(attr, {})
        return data

    packages = get_var(data, "tool.hatch.build.targets.sdist").get("packages", [])
    packages = list(map(SRC_ROOT.joinpath, packages))
    return packages


def get_sources() -> Tuple[List[Path], List[Path], Path]:
    """
    获取需要打包的目录和文件。
    返回: (目录列表, 其他py文件列表, 主py文件)
    """
    cwd = Path.cwd()
    # 需要包含的新目录
    required_dirs = []

    # 检查旧的目录（为了向后兼容）
    if cwd.joinpath("comment").exists():
        required_dirs.append(cwd.joinpath("comment"))
    if cwd.joinpath("compements").exists():
        required_dirs.append(cwd.joinpath("compements"))

    # 查找所有 .py 文件
    python_files = list(cwd.glob("*.py"))

    # 主脚本现在固定为 engine/yxmb_compat_engine/__main__.py

    main_py = cwd / "__main__.py"
    if not main_py.exists():
        raise ValueError(
            "未找到主脚本 __main__.py"
        )

    # 其他py文件
    other_python_files = [p for p in python_files if p.name != main_py.name]

    return required_dirs, other_python_files, main_py


def make_package():
    """
    构建 pyz 包。
    """
    build_dir = Path.cwd() / "build"
    src_dir = build_dir / "src"
    if src_dir.exists():
        shutil.rmtree(src_dir)
    src_dir.mkdir(parents=True, exist_ok=True)

    # 复制 packages
    packages = get_packages()
    for p in packages:
        shutil.copytree(p, src_dir / p.name, dirs_exist_ok=True)

    version_file = config.VERSION_FILE
    shutil.copy(version_file, src_dir / "phis_build" / version_file.name)

    # 复制需要的目录和文件
    dirs, files, main_py = get_sources()
    for d in dirs:
        shutil.copytree(d, src_dir / d.name, dirs_exist_ok=True)
    for f in files:
        shutil.copy(f, src_dir / f.name)
    shutil.copy(main_py, src_dir / main_py.name)

    # 创建 pyz 文件
    pyz_file = build_dir / "app.pyz"
    zip_file = pyz_file.with_suffix(".zip")
    if zip_file.exists():
        zip_file.unlink()
    shutil.make_archive(str(zip_file.with_suffix("")), "zip", src_dir)
    if pyz_file.exists():
        pyz_file.unlink()
    # 将 zip 重命名为 pyz
    zip_file.rename(pyz_file)
    shutil.copy(pyz_file, Path.cwd() / "app.pyz")
    if src_dir.exists():
        shutil.rmtree(src_dir)
    logging.info(f"打包完成: {pyz_file}")


if __name__ == "__main__":
    make_package()
