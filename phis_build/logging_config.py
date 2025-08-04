# filepath: phis_build/logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging():
    """配置日志记录，同时输出到控制台和文件。"""
    log_dir = Path.cwd() / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'phis_build.log'

    # 获取根 logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 如果已经有 handlers，先清除，防止重复记录
    if logger.hasHandlers():
        logger.handlers.clear()

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console_handler)

    # 文件 handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # 捕获未处理的异常
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception