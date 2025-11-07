from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BuildType(str, Enum):
    EXE = "exe"
    PYZ = "pyz"


class Args(BaseModel):
    """构建脚本的命令行参数模型"""

    build: Optional[BuildType] = Field(
        default=None,
        description="构建类型: 'exe' (PyInstaller) 或 'pyz' (zipapp)。如果未提供，则不执行构建。",
    )
    copy_: bool = Field(
        default=False, description="将构建产物复制到目标位置（共享目录或beta目录）。"
    )
    beta: bool = Field(
        default=False,
        description="执行beta构建，将产物复制到本地Windows目录并附加'b'到版本号。",
    )
