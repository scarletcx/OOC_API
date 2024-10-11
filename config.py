# config.py

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 应用程序密钥
    SECRET_KEY = os.getenv('SECRET_KEY')

    # 调试模式
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

    # 游戏配置
    MAX_FISHING_COUNT = int(os.getenv('MAX_FISHING_COUNT', 5))
    FISHING_RECOVERY_INTERVAL = int(os.getenv('FISHING_RECOVERY_INTERVAL', 3600))
    FISHING_EXP = int(os.getenv('FISHING_EXP', 10))
    MAX_BUY_BAIT = int(os.getenv('MAX_BUY_BAIT', 100))
    BAIT_PRICE = float(os.getenv('BAIT_PRICE', 10.5))

    # 其他配置项可以在这里添加
    # ...

    @staticmethod
    def init_app(app):
        pass