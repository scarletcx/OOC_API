# 此文件包含钓鱼游戏中与玩家相关操作的服务函数。
# 它实现了玩家行为和数据检索的业务逻辑。

from app.models import User, LevelExperience, FishingGroundConfig, FishingRodConfig, FishingSession, SystemConfig, FreeMintRecord, Bubble, FishingRecord, PondConfig
from app import db
from flask import jsonify
from sqlalchemy import func
from app.services import ethereum_service
import time
import os
import json
from web3.exceptions import TimeExhausted
#2.1 用户注册接口函数
def register_player(user_id):
    # user_id = data.get('user_id')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    #检查用户是否存在
    user = User.query.get(user_id)
    if user:
        return jsonify({'status': 0, 'message': 'User already exists'}), 400    
    
    #在合约上创建用户
    ##向合约发起添加用户操作并等待交易完成
    # 获取Web3实例以连接以太坊网络
    w3 = ethereum_service.get_w3()
    user_contract = ethereum_service.get_user_contract()
    minter_address = os.getenv('MINTER_ADDRESS')
    
    if not minter_address:
        raise ValueError("MINTER_ADDRESS environment variable is not set")
    
    # 确保地址是校验和格式
    checksum_address = w3.to_checksum_address(minter_address)
    nonce = w3.eth.get_transaction_count(checksum_address, 'pending')
    
    # 获取当前的 gas 价格
    try:
        gas_price = w3.eth.gas_price
        # 如果需要，可以稍微提高 gas 价格
        #gas_price = int(gas_price * 1.1)  # 提高 10%
    except Exception as e:
        print(f"无法获取 gas 价格: {e}")
        # 如果无法获取 gas 价格，使用一个默认值
        gas_price = w3.to_wei(20, 'gwei')  # 使用 20 Gwei 作为默认值

    try:
        txn = user_contract.functions.addUser(user_id).build_transaction({
            'chainId': int(os.getenv('CHAIN_ID')),  # 链ID，用于确定是主网还是测试网
            'gas': 2000000,  # 交易的最大 gas 限制
            'gasPrice': gas_price,  # 使用计算得到的 gas 价格
            'nonce': nonce,  # 发送者账户的交易计数
        })

        # 签名交易
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=os.getenv('MINTER_PRIVATE_KEY'))
        # 发送交易
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # 增加等待时间并添加重试逻辑
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                break
            except TimeExhausted:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(10)  # 等待10秒后重试
    except Exception as e:
        return jsonify({'status': 0, 'message': f'Error creating user on contract: {str(e)}'}), 500
    
    #在后端创建用户
    user = User(user_id=user_id)
    initial_gmc_config = SystemConfig.query.filter_by(config_key='initial_gmc').first()
    initial_bait_count_config = SystemConfig.query.filter_by(config_key='initial_bait_count').first()
    initial_fishing_count_config = SystemConfig.query.filter_by(config_key='initial_fishing_count').first()
    
    if not initial_gmc_config or not initial_bait_count_config or not initial_fishing_count_config:
        return jsonify({'status': 0, 'message': 'System configuration error'}), 500
    
    user.user_gmc = initial_gmc_config.config_value
    user.user_baits = initial_bait_count_config.config_value
    user.fishing_count = initial_fishing_count_config.config_value
    user.bubble_gmc = {"gmc_star1": 0,
                        "gmc_star2": 0,
                        "gmc_star3": 0,
                        "gmc_star4": 0,
                        "gmc_star5": 0,
                        "gmc_star6": 0
                      }
    
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': 1, 'message': 'success'}), 200

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
        # 将字符串形式的user_id转换为CHAR(42)
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 获取当前等级的最大经验值
    level_exp = LevelExperience.query.get(user.user_level)
    if not level_exp:
        return jsonify({'status': 0, 'message': 'Level experience not found'}), 500
    
    # 更新用户的owned_avatar_nfts
    avatar_contract = ethereum_service.get_avatar_contract()
    owned_nfts = avatar_contract.functions.getOwnedNFTs(user_id).call()
    user.owned_avatar_nfts = [{"tokenId": str(nft[0]), "skinId":  nft[1]} for nft in owned_nfts]
    ##增加初始免费钓手
    user.owned_avatar_nfts.append({
        "tokenId": "666666",
        "skinId": "010101050408080108"
    })
    db.session.commit()        
    # 如果current_avatar_nft为空，设置为最新铸造的NFT
    if user.current_avatar_nft is None and user.owned_avatar_nfts:
        user.current_avatar_nft = user.owned_avatar_nfts[-1]
    #检查current_avatar_nft是否存在于owned_avatar_nfts中
    if user.current_avatar_nft and user.current_avatar_nft not in user.owned_avatar_nfts:
        user.current_avatar_nft = user.owned_avatar_nfts[-1]
    
    # 更新用户的owned_rod_nfts
    rod_contract = ethereum_service.get_rod_contract()
    owned_nfts = rod_contract.functions.getOwnedNFTs(user_id).call()
    user.owned_rod_nfts = [{"tokenId": str(nft[0]), "skinId": nft[1]} for nft in owned_nfts]
    db.session.commit()        
    # 如果current_rod_nft为空，设置为最新铸造的NFT
    if user.current_rod_nft is None and user.owned_rod_nfts:
        user.current_rod_nft = user.owned_rod_nfts[-1]
    #检查current_rod_nft是否存在于owned_rod_nfts中
    if user.current_rod_nft and user.current_rod_nft not in user.owned_rod_nfts:
        user.current_rod_nft = user.owned_rod_nfts[-1]  
    db.session.commit()
    
    # 获取当前鱼竿的信息
    current_rod = FishingRodConfig.query.get(user.current_rod_nft['skinId']+1) if user.current_rod_nft else None

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
    
    #更新GMC
    #从合约更新user_gmc
    gmc_contract = ethereum_service.get_gmc_contract()
    user.user_gmc = int(gmc_contract.functions.balanceOf(user_id).call() * (10 ** -18))  # .call() 用于在本地执行合约函数，不会发起链上交易
    # #从合约更新鱼饵数量
    # user_contract = ethereum_service.get_user_contract()
    # user.user_baits = user_contract.functions.getBaitCount(user_id).call()
    db.session.commit()
    
    current_avatar_nft = user.current_avatar_nft
    if current_avatar_nft and 'skinId' in current_avatar_nft:
        current_avatar_nft['skinId'] = f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmezqXViXKGVJizodoVT88xJv7vw3kYVyj7hJnRC3cZ9K8/{current_avatar_nft['skinId']}.png" if current_avatar_nft['skinId'].startswith('01') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmVwfRBC7Pi2TMdWL1PDt7S5yPcL2uerTu5A5WYWretgrD/{current_avatar_nft['skinId']}.png" if current_avatar_nft['skinId'].startswith('02') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmUVWsU9gmfBjnzhxpXXLTEp9P7fgykCmydbetsACxuTgJ/{current_avatar_nft['skinId']}.png"
        
    current_rod_nft = user.current_rod_nft
    if current_rod_nft and 'skinId' in current_rod_nft:
        skinId = current_rod_nft['skinId']
        current_rod_nft['skinId'] = f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{skinId}.png"
         
    owned_avatar_nfts = [
            {
                'tokenId': nft['tokenId'],
                'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmezqXViXKGVJizodoVT88xJv7vw3kYVyj7hJnRC3cZ9K8/{nft['skinId']}.png" if nft['skinId'].startswith('01') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmVwfRBC7Pi2TMdWL1PDt7S5yPcL2uerTu5A5WYWretgrD/{nft['skinId']}.png" if nft['skinId'].startswith('02') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmUVWsU9gmfBjnzhxpXXLTEp9P7fgykCmydbetsACxuTgJ/{nft['skinId']}.png"
            }
            for nft in user.owned_avatar_nfts
        ]
        
    owned_rod_nfts = [
            {
                'tokenId': nft['tokenId'],
                'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{nft['skinId']}.png"
            }
            for nft in user.owned_rod_nfts
        ]
    
    # 获取bubble_gmc_max的值
    bubbles = Bubble.query.filter(Bubble.id.between(1, 6)).all()
    bubble_gmc_max = {f"gmc_max{bubble.id}": bubble.gmc_max for bubble in bubbles}
    
    # 获取用户鱼的数量
    user_fishers_count = FishingRecord.query.filter_by(user_id=user_id).count()
    
    # 获取当前等级的鱼池配置
    current_pond = PondConfig.query.get(user.pond_level)
    if not current_pond:
        return jsonify({'status': 0, 'message': 'Current pond level config not found'}), 404
    
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'user_id': str(user.user_id),
            'user_level': user.user_level,
            'pound_level':user.pond_level,
            'user_fishers_count': user_fishers_count,
            'fishs_max': current_pond.fishs_max,
            'user_exp': user.user_exp,
            'max_exp': level_exp.max_exp,
            'user_gmc': user.user_gmc,
            'collected_gmc': user.collected_gmc,
            'bubble_gmc': user.bubble_gmc,
            'bubble_gmc_max': bubble_gmc_max,
            'user_baits': user.user_baits,
            'current_avatar_nft': current_avatar_nft,
            'current_rod_nft': current_rod_nft,
            'owned_avatar_nfts': owned_avatar_nfts,
            'owned_rod_nfts': owned_rod_nfts,
            'battle_skill_desc_en': current_rod.battle_skill_desc_en if current_rod else None,
            'qte_skill_desc_en': current_rod.qte_skill_desc_en if current_rod else None,
            #'accessible_fishing_grounds': user.accessible_fishing_grounds,
            'current_fishing_ground': user.current_fishing_ground,
            #'avatar_minted': int(free_mint_record.avatar_minted),
            'rod_minted': int(free_mint_record.rod_minted),
            'fishing_count': user.fishing_count,
            'next_recovery_time': user.next_recovery_time,
            'max_fishing_count': max_fishing_count  # 添加这一行
        }
    })

#3.2 游戏进入条件检查接口函数
def check_game_entry(data):
    """
    检查玩家是否可以进入游戏。
    
    :param data: 包含user_id的字典
    :return: 指示玩家是否可以进入游戏的JSON响应
    """
    # 将字符串形式的user_id转换为CHAR(42)
    user_id = data.get('user_id').strip()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 检查玩家是否同时拥有头像和鱼竿NFT
    can_enter_game = user.current_avatar_nft is not None and user.current_rod_nft is not None
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'can_enter_game': can_enter_game,
            'avatar': user.current_avatar_nft if user.current_avatar_nft else None,
            'rod': user.current_rod_nft if user.current_rod_nft else None
        }
    })

#3.3 改变渔场接口函数
def change_fishing_ground(data):
    """
    更改玩家当前的钓鱼场地。
    
    :param data: 包含user_id和ground_id的字典
    :return: 包含更新后钓鱼场地的JSON响应
    """
    user_id = data.get('user_id').strip()
    # 将字符串形式的ground_id转换为INT
    ground_id = int(data.get('ground_id'))

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 获取玩家可进入的钓鱼场地
    accessible_fishing_grounds = FishingGroundConfig.query.filter(FishingGroundConfig.enter_lv <= user.user_level).all()
    accessible_fishing_ground_ids = [ground.id for ground in accessible_fishing_grounds]

    # 检查请求的场地是否可进入
    if ground_id not in accessible_fishing_ground_ids:
        return jsonify({'status': 0, 'message': 'Player is not authorized to enter this fishing ground'}), 400

    # 更新玩家当前的钓鱼场地
    user.current_fishing_ground = ground_id
    db.session.commit()

    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'ground_id': ground_id
        }
    })

#3.4 钓鱼次数加一接口函数
def handle_player_status(data):
    user_id = data.get('user_id')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    max_fishing_count = int(SystemConfig.query.filter_by(config_key='max_fishing_count').first().config_value)
    fishing_recovery_interval = int(SystemConfig.query.filter_by(config_key='fishing_recovery_interval').first().config_value)
    current_time = int(time.time())  # 使用当前的Unix时间戳
    
    if user.next_recovery_time and current_time >= user.next_recovery_time:
        user.fishing_count = user.fishing_count + 1
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
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 1. 检查玩家是否拥有当前使用的钓手NFT和鱼竿NFT
    
    # 更新用户的owned_avatar_nfts
    avatar_contract = ethereum_service.get_avatar_contract()
    owned_nfts = avatar_contract.functions.getOwnedNFTs(user_id).call()
    user.owned_avatar_nfts = [{"tokenId": str(nft[0]), "skinId":  nft[1]} for nft in owned_nfts]
    ##增加初始免费钓手
    user.owned_avatar_nfts.append({
        "tokenId": "666666",
        "skinId": "010101050408080108"
    })
    db.session.commit()        
    # 如果current_avatar_nft为空，或者current_avatar_nft不存在于owned_avatar_nfts里，直接返回报错信息：当前avatar不存在，请更换有效的avatar（换成英文版的提示）
    if user.current_avatar_nft is None or user.current_avatar_nft not in user.owned_avatar_nfts:
        return jsonify({'status': 0, 'message': 'Current avatar does not exist, please change to a valid avatar'}), 400
    
    # 更新用户的owned_rod_nfts
    rod_contract = ethereum_service.get_rod_contract()
    owned_nfts = rod_contract.functions.getOwnedNFTs(user_id).call()
    user.owned_rod_nfts = [{"tokenId": str(nft[0]), "skinId": nft[1]} for nft in owned_nfts]
    db.session.commit()        
    # 如果current_rod_nft为空，或者current_rod_nft不存在于owned_rod_nfts里，直接返回报错信息：当前rod不存在，请更换有效的rod（换成英文版的提示）
    if user.current_rod_nft is None or user.current_rod_nft not in user.owned_rod_nfts:
        return jsonify({'status': 0, 'message': 'Current rod does not exist, please change to a valid rod'}), 400

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
            
        
            if user.fishing_count < max_fishing_count and not user.next_recovery_time:
                user.next_recovery_time = current_time + fishing_recovery_interval
                
            #qte初始化
            current_rod = FishingRodConfig.query.get(user.current_rod_nft['skinId']+1)
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
                'qte_count': user.remaining_qte_count,
                'accumulated_qte_score': user.accumulated_qte_score
            }
        })

    except Exception as e:
        # 如果发生错误，回滚事务
        db.session.rollback()
        return jsonify({'status': 0, 'message': f'Failed to create fishing session: {str(e)}'}), 500


#3.9 等级经验数据接口函数
def update_player_exp(data):
    """
    钓鱼后更新玩家的经验。
    
    :param data: 包含user_id和session_id的字典
    :return: 包含更新后玩家等级和经验的JSON响应
    """
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 验证钓鱼会话
    session = FishingSession.query.get(session_id)
    if not session or not session.session_status :
        return jsonify({'status': 0, 'message': 'Invalid session or experience already added'}), 400

    try:
        with db.session.begin_nested():
            # 获取单次钓鱼经验和当前等级的最大经验值
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
            session.end_time = func.now()

        # 提交数据库更改
        db.session.commit()

        return jsonify({
            'status': 1,
            'message': 'success',
            'data': {
                'user_level': user.user_level,
                'user_exp': user.user_exp
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 0, 'message': f'Failed to update player experience: {str(e)}'}), 500