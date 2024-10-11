# 此文件包含钓鱼游戏中与玩家相关操作的路由定义。
# 它处理HTTP请求并将业务逻辑委托给相应的服务函数。

from app.routes import bp
from flask import jsonify, request
from app.services import player_service, fishing_service, nft_service

@bp.route('/app/v1/fishing', methods=['GET'])
def fishing_preparation():
    user_id = request.args.get('user_id')
    return player_service.get_fishing_preparation(user_id)

@bp.route('/app/v1/game/entercheck', methods=['POST'])
def game_enter_check():
    data = request.json
    return player_service.check_game_entry(data)

@bp.route('/app/v1/player/change-fishing-ground', methods=['POST'])
def change_fishing_ground():
    data = request.json
    return player_service.change_fishing_ground(data)

@bp.route('/app/v1/player/status', methods=['POST'])
def player_status():
    data = request.json
    return player_service.get_player_status(data)

@bp.route('/app/v1/player/exp', methods=['POST'])
def update_player_exp():
    data = request.json
    return player_service.update_player_exp(data)