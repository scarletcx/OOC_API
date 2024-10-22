# 此文件包含钓鱼游戏中与玩家相关操作的路由定义。
# 它处理HTTP请求并将业务逻辑委托给相应的服务函数。

from app.routes import bp
from flask import jsonify, request
from app.services import player_service

#3.1 钓鱼准备界面状态（初始化）接口
@bp.route('/app/v1/fishing', methods=['POST'])
def get_fishing_preparation():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'status': 0, 'message': 'Missing user_id parameter'}), 400
    return player_service.get_fishing_preparation(user_id)

#3.2 游戏进入条件检查接口
@bp.route('/app/v1/game/entercheck', methods=['POST'])
def game_enter_check():
    data = request.json
    return player_service.check_game_entry(data)

#3.3 改变渔场接口
@bp.route('/app/v1/player/change-fishing-ground', methods=['POST'])
def change_fishing_ground():
    data = request.json
    return player_service.change_fishing_ground(data)

#3.4 钓鱼次数加一接口
@bp.route('/app/v1/player/status', methods=['POST'])
def player_status():
    """
    钓鱼次数加一接口

    请求参数:
    - user_id: 玩家ID (CHAR(42))

    返回:
    - 包含玩家钓鱼次数和下一次恢复时间的JSON响应
    """
    data = request.json
    return player_service.handle_player_status(data)

#3.5 钓鱼会话初始化接口
@bp.route('/app/v1/fishing/init', methods=['POST'])
def init_fishing_session():
    """
    钓鱼会话初始化接口

    此接口用于初始化钓鱼会话，检查玩家是否有足够的钓鱼次数，并创建新的钓鱼会话。

    请求参数:
    - user_id: 玩家ID (UUID格式)

    返回:
    - 包含会话ID和玩家当前鱼饵数量的JSON响应
    """
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'status': 0, 'message': 'Missing user_id parameter'}), 400
    
    return player_service.init_fishing_session(user_id)

#3.9 等级经验数据接口
@bp.route('/app/v1/player/exp', methods=['POST'])
def update_player_exp():
    data = request.json
    return player_service.update_player_exp(data)