from app.models import User, FishingSession, Fish, FishingRecord, SystemConfig, RarityDetermination, FishingRodConfig, LevelExperience, FishingGroundConfig
from app import db
from sqlalchemy import func
import random
from flask import jsonify
from app.services import ethereum_service
from decimal import Decimal
import numpy as np
import os
from web3.exceptions import Web3Exception, TimeExhausted
import time
from dotenv import load_dotenv
from app.services.variables import t_fish_id, t_fish_name, t_fish_picture_res, t_rarity_id, t_fishing_ground_id, t_fishing_ground_name, t_price, t_output, t_weight
# 加载环境变量
load_dotenv(override=True)




#3.6 鱼饵购买界面状态接口函数
def get_bait_buy_state(user_id):
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    max_buy_bait = SystemConfig.query.get('max_buy_bait')
    bait_price = SystemConfig.query.get('bait_price')

    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'max_buy_bait': int(max_buy_bait.config_value),
            'bait_price': str(Decimal(bait_price.config_value))
        }
    })

#3.7 购买鱼饵接口函数
def buy_bait(data):
    user_id = data.get('user_id')
    #获取购买数量并转换成uint256数据类型，0 是 data.get('buy_amount', 0) 的默认值
    buy_amount = int(data.get('buy_amount', 0))
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404
    
    ##向合约发起购买鱼饵操作并等待交易完成
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

    txn = user_contract.functions.buyBaitsAdmin(user_id, buy_amount).build_transaction({
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
    #从合约更新user_gmc
    gmc_contract = ethereum_service.get_gmc_contract()
    user.user_gmc = gmc_contract.functions.balanceOf(user_id).call() * (10 ** -18)  # .call() 用于在本地执行合约函数，不会发起链上交易
    #从合约更新鱼饵数量
    user.user_baits = user_contract.functions.getBaitCount(user_id).call()
    db.session.commit()

    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'user_baits': user.user_baits,
            'user_gmc': str(user.user_gmc)
        }
    })

#3.8 QTE剩余次数和分数接口函数
def handle_qte(data):
    user_id = data.get('user_id')
    qte_colour = data.get('qte_colour')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404
    else:
        return process_qte(user, qte_colour)        

def process_qte(user, qte_colour):
    if user.remaining_qte_count <= 0:
        return jsonify({'status': 0, 'message': 'No remaining QTE attempts'}), 400
    
    if qte_colour not in ['red', 'green', 'black']:
        return jsonify({'status': 0, 'message': 'Invalid QTE colour'}), 400

    current_rod = FishingRodConfig.query.get(user.current_rod_nft['skinId']+1)
    
    if user.remaining_qte_count == current_rod.qte_count:
        user.accumulated_qte_score += current_rod.qte_progress_change

    user.accumulated_qte_score += (user.qte_hit_status_green + user.qte_hit_status_red) * current_rod.consecutive_hit_bonus

    if qte_colour == 'green':
        user.qte_hit_status_green = True
        user.accumulated_qte_score += current_rod.green_qte_progress
    elif qte_colour == 'red':
        user.qte_hit_status_red = True
        user.accumulated_qte_score += current_rod.red_qte_progress
    else:
        user.qte_hit_status_black = True

    user.remaining_qte_count -= 1
    db.session.commit()

    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'remaining_qte_count': user.remaining_qte_count,
            'accumulated_qte_score': user.accumulated_qte_score
        }
    })

#4.1 获鱼信息接口函数
def get_fish_info(data):
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    session = FishingSession.query.get(session_id)
    if not session or not session.session_status :
        return jsonify({'status': 0, 'message': 'Invalid session or session expired'}), 400

    # 根据用户当前的钓鱼场地和累计的QTE分数，查询稀有度确定记录
    rarity_determination = RarityDetermination.query.filter(
        RarityDetermination.fishing_ground_id == user.current_fishing_ground,  # 钓鱼场地ID匹配
        RarityDetermination.qte_min <= user.accumulated_qte_score,  # QTE分数大于等于最小值
        RarityDetermination.qte_max >= user.accumulated_qte_score  # QTE分数小于等于最大值
    ).first()  # 获取匹配的记录

    if not rarity_determination:
        return jsonify({'status': 0, 'message': 'Unable to determine fish rarity'}), 500

    # 从可能的稀有度ID中随机选择一个稀有度ID
    rarity_id = int(np.random.choice(
        rarity_determination.possible_rarity_ids,  # 可能的稀有度ID列表
        p=[float(prob) for prob in rarity_determination.appearance_probabilities],  # 各稀有度ID出现的概率
        size=1  # 选择一个稀有度ID
    )[0])  # 将 numpy.int32 转换为 Python int

    fish = Fish.query.filter_by(
        rarity_id=rarity_id,
        fishing_ground_id=user.current_fishing_ground
    ).order_by(func.random()).first()

    if not fish:
        return jsonify({'status': 0, 'message': 'No fish found for the given criteria'}), 500

    weight = Decimal(random.uniform(float(fish.min_weight), float(fish.max_weight)))
    
    #将鱼的信息赋值给变量
    global t_fish_id, t_fish_name, t_fish_picture_res, t_rarity_id, t_fishing_ground_id, t_fishing_ground_name, t_price, t_output, t_weight
    t_fish_id = fish.fish_id
    t_fish_name = fish.fish_name
    t_fish_picture_res = fish.fish_picture_res
    t_rarity_id = fish.rarity_id
    t_fishing_ground_id = fish.fishing_ground_id
    t_fishing_ground_name = fish.fishing_ground_name
    t_price = fish.price
    t_output = fish.output
    t_weight = weight
    
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'fish_id': t_fish_id,
            'fish_name': t_fish_name,
            'fish_picture_res': t_fish_picture_res,
            'rarity_id': t_rarity_id,
            'fishing_ground_id': t_fishing_ground_id,
            'fishing_ground_name': t_fishing_ground_name,
            'price': str(t_price),
            'output': str(t_output),
            'weight': str(round(t_weight, 2))
        }
    })
    
#4.2 卖鱼接口函数
def sell_fish(data):
    user_id = data.get('user_id')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404
    # 卖鱼逻辑
    #检查用户是否拥有鱼
    global t_fish_id, t_price
    if not t_fish_id:
        return jsonify({'status': 0, 'message': 'No fish found'}), 400
    ##向合约发起mintGMC操作并等待交易完成
    # 获取Web3实例以连接以太坊网络
    w3 = ethereum_service.get_w3()
    gmc_contract = ethereum_service.get_gmc_contract()
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

    txn = gmc_contract.functions.mint(user_id, int(t_price * (10 ** 18))).build_transaction({
        'chainId': int(os.getenv('CHAIN_ID')),  # 链ID，用于确定是主网还是测试网
        'gas': 2000000,  # 交易的最大 gas 限制
        'gasPrice': gas_price,  # 使用计算得到的 gas 价格
        'nonce': nonce,  # 发送者账户的交易计数
    })
    
    
    # 签名交易
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=os.getenv('MINTER_PRIVATE_KEY'))
    # 发送交易
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    except Exception as e:
        return jsonify({'status': 0, 'message': f'Failed to send transaction: {e}'}), 500
    
    # 增加等待时间并添加重试逻辑
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            break
        except TimeExhausted:
            if attempt == max_attempts - 1:
                return jsonify({'status': 0, 'message': 'Transaction timed out'}), 500
            time.sleep(10)  # 等待10秒后重试
            
    #将缓存数据恢复默认值（只用修改t_fish_id）
    t_fish_id = None
    #从合约更新user_gmc
    gmc_contract = ethereum_service.get_gmc_contract()
    user.user_gmc = gmc_contract.functions.balanceOf(user_id).call() * (10 ** -18)  # .call() 用于在本地执行合约函数，不会发起链上交易
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'user_gmc': str(user.user_gmc)
        }
    })  
    
#4.3 放入鱼池接口函数
def put_fish_pool(data):
    user_id = data['user_id']
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404
    global t_fish_id, t_fish_name, t_fish_picture_res, t_rarity_id, t_fishing_ground_id, t_fishing_ground_name, t_price, t_output, t_weight
    #检查用户是否拥有鱼
    if not t_fish_id:
        return jsonify({'status': 0, 'message': 'No fish found'}), 400
    fishing_record = FishingRecord(
        user_id=user_id,
        fish_id=t_fish_id,
        fish_name=t_fish_name,
        fish_picture_res=t_fish_picture_res,
        rarity_id=t_rarity_id,
        fishing_ground_id=t_fishing_ground_id,
        fishing_ground_name=t_fishing_ground_name,
        price=t_price,
        output=t_output,
        weight=t_weight
    )
    db.session.add(fishing_record)  
    db.session.commit()
    #将缓存数据恢复默认值（只用修改t_fish_id）
    t_fish_id = None
    return jsonify({
        'status': 1,
        'message': 'success'
    })