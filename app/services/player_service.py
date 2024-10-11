# 此文件包含钓鱼游戏中与玩家相关操作的服务函数。
# 它实现了玩家行为和数据检索的业务逻辑。

from app.models import User, LevelExperience, FishingGroundConfig, FishingRodConfig, FishingSession, SystemConfig
from app import db
from flask import jsonify
from sqlalchemy import func

def get_fishing_preparation(user_id):
    """
    检索玩家的钓鱼准备数据。
    
    :param user_id: 玩家的ID
    :return: 包含钓鱼准备数据的JSON响应
    """
    # 从数据库获取用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 获取当前等级的最大经验值
    max_exp = LevelExperience.query.filter_by(level=user.user_level).first().max_exp
    
    # 获取当前鱼竿配置
    current_rod = FishingRodConfig.query.get(user.current_rod_nft['rodId'])

    # 获取可进入的钓鱼场地
    accessible_fishing_grounds = FishingGroundConfig.query.filter(FishingGroundConfig.enter_lv <= user.user_level).all()
    accessible_fishing_ground_ids = [ground.id for ground in accessible_fishing_grounds]

    # 如有必要，更新当前钓鱼场地
    if user.current_fishing_ground not in accessible_fishing_ground_ids:
        user.current_fishing_ground = accessible_fishing_ground_ids[0]
        db.session.commit()

    # 准备响应数据
    return jsonify({
        'status': 0,
        'message': '成功',
        'data': {
            'user_id': user.user_id,
            'user_level': user.user_level,
            'user_exp': user.user_exp,
            'max_exp': max_exp,
            'user_gmc': float(user.user_gmc),
            'user_baits': user.user_baits,
            'current_avator_nft': user.current_avator_nft,
            'current_rod_nft': user.current_rod_nft,
            'owned_avator_nfts': user.owned_avator_nfts,
            'owned_rod_nfts': user.owned_rod_nfts,
            'battle_skill_desc_en': current_rod.battle_skill_desc_en,
            'qte_skill_desc_en': current_rod.qte_skill_desc_en,
            'accessible_fishing_grounds': accessible_fishing_ground_ids,
            'current_fishing_ground': user.current_fishing_ground
        }
    })

def check_game_entry(data):
    """
    检查玩家是否可以进入游戏。
    
    :param data: 包含user_id的字典
    :return: 指示玩家是否可以进入游戏的JSON响应
    """
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 检查玩家是否同时拥有头像和鱼竿NFT
    can_enter_game = user.current_avator_nft is not None and user.current_rod_nft is not None
    return jsonify({
        'status': 0,
        'message': '成功',
        'data': {
            'can_enter_game': can_enter_game,
            'avator': user.current_avator_nft['tokenId'] if user.current_avator_nft else None,
            'rod': user.current_rod_nft['tokenId'] if user.current_rod_nft else None
        }
    })

def change_fishing_ground(data):
    """
    更改玩家当前的钓鱼场地。
    
    :param data: 包含user_id和ground_id的字典
    :return: 包含更新后钓鱼场地的JSON响应
    """
    user_id = data.get('user_id')
    ground_id = data.get('ground_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 获取玩家可进入的钓鱼场地
    accessible_fishing_grounds = FishingGroundConfig.query.filter(FishingGroundConfig.enter_lv <= user.user_level).all()
    accessible_fishing_ground_ids = [ground.id for ground in accessible_fishing_grounds]

    # 检查请求的场地是否可进入
    if ground_id not in accessible_fishing_ground_ids:
        return jsonify({'status': 1, 'message': '玩家无权进入此钓鱼场地'}), 400

    # 更新玩家当前的钓鱼场地
    user.current_fishing_ground = ground_id
    db.session.commit()

    return jsonify({
        'status': 0,
        'message': '成功',
        'data': {
            'ground_id': ground_id
        }
    })

def update_player_exp(data):
    """
    钓鱼后更新玩家的经验。
    
    :param data: 包含user_id和session_id的字典
    :return: 包含更新后玩家等级和经验的JSON响应
    """
    user_id = data.get('user_id')
    session_id = data.get('session_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 验证钓鱼会话
    session = FishingSession.query.get(session_id)
    if not session or not session.session_status or not session.fishing_count_deducted:
        return jsonify({'status': 1, 'message': '无效的会话或经验已添加'}), 400

    # 获取钓鱼经验和当前等级的最大经验值
    fishing_exp = int(SystemConfig.query.get('fishing_exp').config_value)
    max_exp = LevelExperience.query.filter_by(level=user.user_level).first().max_exp

    # 计算新经验并在必要时升级
    new_exp = user.user_exp + fishing_exp
    if new_exp >= max_exp:
        user.user_level += 1
        user.user_exp = new_exp - max_exp
    else:
        user.user_exp = new_exp

    # 关闭钓鱼会话
    session.session_status = False
    session.fishing_count_deducted = False
    session.end_time = func.now()

    db.session.commit()

    return jsonify({
        'status': 0,
        'message': '成功',
        'data': {
            'user_level': user.user_level,
            'user_exp': user.user_exp
        }
    })