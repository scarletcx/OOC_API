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
    MAX_FISHING_COUNT = 10
    FISHING_RECOVERY_INTERVAL = 10800
    FISHING_EXP = 5
    MAX_BUY_BAIT = 99
    BAIT_PRICE = 5.0
    FISHING_BAIT_COST = 1
    INITIAL_BAIT_COUNT = 30
    INITIAL_FISHING_COUNT = 10
    INITIAL_GMC = 0
    # 其他配置项可以在这里添加
    # ...

    @staticmethod
    def init_app(app):
        pass
