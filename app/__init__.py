from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.services import ethereum_service

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # 初始化以太坊连接
    ethereum_service.get_w3()

    from app.routes import bp 
    app.register_blueprint(bp)

    return app
