from datetime import date
from . import config
import logging


def read_and_update_version(beta: bool = False):
    """
    读取并更新版本号。
    版本格式为 YYYY.M.D.rev。
    如果 beta 为 True，则附加 'b'。
    """
    today = date.today()

    # 默认新版本号（当天第一次构建）
    new_version_str = f"{today.year}.{today.month}.{today.day}.0"

    if config.VERSION_FILE.exists():
        # 移除可能存在的 'b' 后缀以正确解析版本
        last_version_str = (
            config.VERSION_FILE.read_text(encoding="utf-8").strip().rstrip("b")
        )
        if last_version_str:
            try:
                parts = last_version_str.split(".")
                last_year, last_month, last_day, last_rev = map(int, parts)
                last_build_date = date(last_year, last_month, last_day)

                if last_build_date == today:
                    # 同一天构建，修订号递增
                    new_rev = last_rev + 1
                    new_version_str = (
                        f"{today.year}.{today.month}.{today.day}.{new_rev}"
                    )
                # else: 新的一天，使用上面已经设置好的默认版本号
            except (ValueError, IndexError):
                logging.info(
                    f"警告: VERSION 文件中的版本 '{last_version_str}' 格式无效。将从今天的日期重新开始。"
                )

    final_version_str = new_version_str
    if beta:
        final_version_str += "b"

    # 写入新版本号
    config.VERSION_FILE.write_text(final_version_str, encoding="utf-8")
    logging.info(f"版本号已更新为: {final_version_str}")
    return final_version_str
