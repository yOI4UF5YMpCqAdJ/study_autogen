import logging
import os
from datetime import datetime

def setup_logger(name):
    """
    设置日志配置
    
    参数:
        name: str, 日志器名称
    
    返回:
        logging.Logger: 配置好的日志器实例
    """
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建固定日志文件名，只包含年月
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m')}.log")
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 如果logger已经有处理器，就不再添加
    if not logger.handlers:
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
