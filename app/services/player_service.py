# 此文件包含钓鱼游戏中与玩家相关操作的服务函数。
# 它实现了玩家行为和数据检索的业务逻辑。

from app.models import User, LevelExperience, FishingGroundConfig, FishingRodConfig, FishingSession, SystemConfig, FreeMintRecord
from app import db
from flask import jsonify
from sqlalchemy import func
import uuid
import time

#3.1 钓鱼准备界面状态（初始化）接口函数
def get_fishing_preparation(user_id):
    """
    获取钓鱼准备界面的状态信息

    此函数处理获取玩家进入钓鱼准备界面时所需的所有相关信息，包括免费mint记录和钓鱼次数信息。

    参数:
    - user_id: 玩家ID (UUID格式的字符串)

    返回:
    - 包含玩家钓鱼相关信息的JSON响应
    """
    
    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'status': 1, 'message': '无效的user_id格式'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 获取当前等级的最大经验值
    level_exp = LevelExperience.query.get(user.user_level)
    if not level_exp:
        return jsonify({'status': 1, 'message': '未找到等级经验信息'}), 500
    
    # 从合约更新owned_avatar_nfts和owned_rod_nfts
    
    # 检查并更新current_avatar_nft
    
    # 检查并更新current_rod_nft
    
    # 获取当前鱼竿的信息
    current_rod = FishingRodConfig.query.get(user.current_rod_nft['rodId']) if user.current_rod_nft else None

    # 获取可进入的渔场信息
    accessible_grounds = FishingGroundConfig.query.filter(FishingGroundConfig.enter_lv <= user.user_level).all()
    
    # 更新用户的accessible_fishing_grounds
    user.accessible_fishing_grounds = [ground.id for ground in accessible_grounds]
    
    # 检查并更新current_fishing_ground
    if user.current_fishing_ground is None or user.current_fishing_ground not in user.accessible_fishing_grounds:
        user.current_fishing_ground = user.accessible_fishing_grounds[-1] if user.accessible_fishing_grounds else None

    # 获取免费mint记录
    free_mint_record = FreeMintRecord.query.get(user_id)
    if not free_mint_record:
        free_mint_record = FreeMintRecord(user_id=user_id, avatar_minted=False, rod_minted=False)
        db.session.add(free_mint_record)

    # 添加钓鱼次数和恢复时间的处理逻辑
    max_fishing_count = int(SystemConfig.query.filter_by(config_key='max_fishing_count').first().config_value)
    fishing_recovery_interval = int(SystemConfig.query.filter_by(config_key='fishing_recovery_interval').first().config_value)

    current_time = int(time.time())  # 使用当前的Unix时间戳

    if user.next_recovery_time and current_time >= user.next_recovery_time:
        time_diff = current_time - user.next_recovery_time
        recovered_count = int(time_diff // fishing_recovery_interval) + 1
        user.fishing_count = min(user.fishing_count + recovered_count, max_fishing_count)
        
        if user.fishing_count < max_fishing_count:
            user.next_recovery_time += fishing_recovery_interval * recovered_count
        else:
            user.next_recovery_time = None

    db.session.commit()

    # 获取 max_fishing_count
    max_fishing_count = int(SystemConfig.query.filter_by(config_key='max_fishing_count').first().config_value)

    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'user_id': str(user.user_id),
            'user_level': user.user_level,
            'user_exp': user.user_exp,
            'max_exp': level_exp.max_exp,
            'user_gmc': float(user.user_gmc),
            'user_baits': user.user_baits,
            'current_avatar_nft': user.current_avatar_nft,
            'current_rod_nft': user.current_rod_nft,
            'owned_avatar_nfts': user.owned_avatar_nfts,
            'owned_rod_nfts': user.owned_rod_nfts,
            'battle_skill_desc_en': current_rod.battle_skill_desc_en if current_rod else None,
            'qte_skill_desc_en': current_rod.qte_skill_desc_en if current_rod else None,
            #'accessible_fishing_grounds': user.accessible_fishing_grounds,
            'current_fishing_ground': user.current_fishing_ground,
            'avatar_minted': int(free_mint_record.avatar_minted),
            'rod_minted': int(free_mint_record.rod_minted),
            'fishing_count': user.fishing_count,
            'next_recovery_time': user.next_recovery_time,
            'max_fishing_count': max_fishing_count  # 添加这一行
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
    can_enter_game = user.current_avatar_nft is not None and user.current_rod_nft is not None
    return jsonify({
        'status': 0,
        'message': '成功',
        'data': {
            'can_enter_game': can_enter_game,
            'avatar': user.current_avatar_nft['tokenId'] if user.current_avatar_nft else None,
            'rod': user.current_rod_nft['tokenId'] if user.current_rod_nft else None
        }
    })

#3.3 改变渔场接口函数
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

#3.9 等级经验数据接口函数
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

    try:
        with db.session.begin_nested():
            # 获取钓鱼经验和当前等级的最大经验值
            fishing_exp = int(SystemConfig.query.filter_by(config_key='fishing_exp').first().config_value)
            max_exp = LevelExperience.query.filter_by(user_level=user.user_level).first().max_exp

            # 计算新经验并在必要时升级
            new_exp = user.user_exp + fishing_exp
            while new_exp >= max_exp:
                user.user_level += 1
                new_exp -= max_exp
                max_exp = LevelExperience.query.filter_by(user_level=user.user_level).first().max_exp

            user.user_exp = new_exp

            # 关闭钓鱼会话
            session.session_status = False
            session.fishing_count_deducted = False
            session.end_time = func.now()

        # 提交数据库更改
        db.session.commit()

        return jsonify({
            'status': 0,
            'message': '成功',
            'data': {
                'user_level': user.user_level,
                'user_exp': user.user_exp
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 1, 'message': f'更新玩家经验失败: {str(e)}'}), 500

#3.4 钓鱼次数加一接口函数
def handle_player_status(data):
    user_id = data.get('user_id')
    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'status': 1, 'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    max_fishing_count = int(SystemConfig.query.filter_by(config_key='max_fishing_count').first().config_value)
    fishing_recovery_interval = int(SystemConfig.query.filter_by(config_key='fishing_recovery_interval').first().config_value)
    current_time = int(time.time())  # 使用当前的Unix时间戳
    
    if user.next_recovery_time and current_time >= user.next_recovery_time:
        user.fishing_count = min(user.fishing_count + 1, max_fishing_count)
        if user.fishing_count < max_fishing_count:
            user.next_recovery_time +=  fishing_recovery_interval
        else:
            user.next_recovery_time = None
    else:
        return jsonify({'status': 0, 'message': 'Recovery time has not been reached yet'}), 400

    db.session.commit()

    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'fishing_count': user.fishing_count,
            'next_recovery_time': user.next_recovery_time
        }
    })

#3.5 钓鱼会话初始化接口函数
def init_fishing_session(user_id):
    """
    初始化钓鱼会话

    此函数处理钓鱼会话的初始化，包括检查玩家的钓鱼次数和创建新的钓鱼会话。
    如果存在之前的会话记录，会先删除这些记录。

    参数:
    - user_id: 玩家ID (UUID格式的字符串)

    返回:
    - 包含会话ID和玩家当前鱼饵数量的JSON响应
    """
    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 1. 检查玩家是否拥有当前使用的钓手NFT和鱼竿NFT
    
    # 先从合约更新owned_avatar_nfts和owned_rod_nfts
    
    # 检查并更新current_avatar_nft
    
    # 检查并更新current_rod_nft
    
    if not user.current_avatar_nft or not user.current_rod_nft:
        return jsonify({'status': 0, 'message': 'Player missing necessary NFTs'}), 400

    # 2. 检查玩家当前钓鱼次数
    if user.fishing_count <= 0:
        return jsonify({'status': 0, 'message': 'Insufficient fishing count'}), 400

    # 3. 检查玩家当前鱼饵数量
    fishing_bait_cost = int(SystemConfig.query.filter_by(config_key='fishing_bait_cost').first().config_value)
    if user.user_baits < fishing_bait_cost:
        return jsonify({'status': 0, 'message': 'Insufficient bait count'}), 400

    # 4. 开始数据库事务
    try:
        with db.session.begin_nested():
            # 5. 删除该用户之前的所有会话记录
            FishingSession.query.filter_by(user_id=user_id).delete()

            # 6. 创建新的钓鱼会话
            session = FishingSession(user_id=user_id)
            db.session.add(session)

            # 7. 扣除鱼饵数量
            user.user_baits -= fishing_bait_cost
            
            # 8. 扣除钓鱼次数
            max_fishing_count = int(SystemConfig.query.filter_by(config_key='max_fishing_count').first().config_value)
            fishing_recovery_interval = int(SystemConfig.query.filter_by(config_key='fishing_recovery_interval').first().config_value)
            current_time = int(time.time())  # 使用当前的Unix时间戳

            user.fishing_count -= 1
            session.fishing_count_deducted = True
        
            if user.fishing_count < max_fishing_count and not user.next_recovery_time:
                user.next_recovery_time = current_time + fishing_recovery_interval
                
            #qte初始化
            current_rod = FishingRodConfig.query.get(user.current_rod_nft['rodId'])
            user.remaining_qte_count = current_rod.qte_count
            user.accumulated_qte_score = 0
            user.qte_hit_status_green = False
            user.qte_hit_status_red = False
            user.qte_hit_status_black = False

        # 9. 提交数据库更改
        db.session.commit()

        # 10. 返回成功响应
        return jsonify({
            'status': 1,
            'message': 'success',
            'data': {
                'fishing_count': user.fishing_count,
                'next_recovery_time': user.next_recovery_time,
                'user_baits': user.user_baits,
                'session_id': str(session.session_id),
                'qte_count ': user.remaining_qte_count,
                'accumulated_qte_score': user.accumulated_qte_score
            }
        })

    except Exception as e:
        # 如果发生错误，回滚事务
        db.session.rollback()
        return jsonify({'status': 1, 'message': f'创建钓鱼会话失败: {str(e)}'}), 500


