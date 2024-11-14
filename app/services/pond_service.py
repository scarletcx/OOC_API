from app.models import User, PondConfig, FishingRecord, Bubble
from flask import jsonify
from app.services import ethereum_service
from app import db
from web3.exceptions import TimeExhausted
import time
from decimal import Decimal

#5.1 鱼池升级界面状态接口函数
def get_upgrade_pond_state(data):
    """
    获取鱼池升级界面状态信息
    
    参数:
    - data: 包含user_id的字典
    
    返回:
    - 包含当前鱼池等级信息和下一等级信息的JSON响应
    """
    try:
        user_id = data.get('user_id').strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404
        
    # 获取当前等级的鱼池配置
    current_pond = PondConfig.query.get(user.pond_level)
    if not current_pond:
        return jsonify({'status': 0, 'message': 'Current pond level config not found'}), 404
        
    # 获取下一等级的鱼池配置
    next_pond = PondConfig.query.get(user.pond_level + 1)
    if not next_pond:
        return jsonify({'status': 0, 'message': 'Next pond level config not found'}), 404
        
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'current_pond_level': user.pond_level,
            'upgrade_cost': float(current_pond.upgrade_cost),
            'current_fishs_max': current_pond.fishs_max,
            'current_interest': float(current_pond.interest),
            'next_fishs_max': next_pond.fishs_max,
            'next_interest': float(next_pond.interest)
        }
    })

#5.2 鱼池升级接口函数
def upgrade_pond(data):
    try:
        user_id = data.get('user_id').strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404
    
    tx_hash = data.get('tx_hash')
    
    # 获取当前等级的鱼池配置
    current_pond = PondConfig.query.get(user.pond_level)
    if not current_pond:
        return jsonify({'status': 0, 'message': 'Current pond level config not found'}), 404
    
    upgrade_cost = current_pond.upgrade_cost
    #判断用户是否有足够的GMC升级鱼池
    if user.user_gmc < upgrade_cost:
        return jsonify({'status': 0, 'message': 'Not enough GMC'}), 400
    
    #执行升级操作
    # 获取Web3实例以连接以太坊网络
    w3 = ethereum_service.get_w3()
    user_contract = ethereum_service.get_user_contract()
    
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
    #更新后端鱼池等级：user.pound_level += 1
    user.pond_level += 1
    
    db.session.commit()
    
    # 获取当前等级的鱼池配置
    current_pond = PondConfig.query.get(user.pond_level)
    if not current_pond:
        return jsonify({'status': 0, 'message': 'Current pond level config not found'}), 404
    
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'user_gmc': user.user_gmc,
            'pond_level': user.pond_level,
            'fishs_max': current_pond.fishs_max,
        }
    })

#5.3 泡泡产币更新接口函数
'''
函数逻辑：
外层逻辑：根据user_id获取用户信息，判断用户是否在游戏内，若不在游戏内，返回错误信息。验证过滤后，获取更新后的用户的bubble_gmc并返回给前端。
内层逻辑：（bubble_gmc的更新逻辑）
FishingRecord里该用户对应的所有鱼都会产币，每条鱼的三小时产币量为该表里的output,每条鱼从caught_at时间开始，每3小时产币一次，并在产币后更新下次产币时间，直到下次产币时间大于当前时间。每条鱼产币后，更新output_stock。
每次调用该接口时，遍历FishingRecord里该用户对应的所有鱼，产币后更新output_stock。然后分别统计该用户rarity_id=1，rarity_id=2，rarity_id=3，rarity_id=4，rarity_id=5，rarity_id=6的鱼的output_stock之和分别作为该用户bubble_gmc.gmc_star1,bubble_gmc.gmc_star2,bubble_gmc.gmc_star3,bubble_gmc.gmc_star4,bubble_gmc.gmc_star5,bubble_gmc.gmc_star6并更新到user表。
'''
def update_bubble(data):
    try:
        user_id = data.get('user_id').strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 获取用户的所有钓鱼记录
    fishing_records = FishingRecord.query.filter_by(user_id=user_id).all()
    current_time = int(time.time())  # 当前时间的Unix时间戳

    # 获取每种rarity_id的产币上限
    bubble_limits = {f"{bubble.id}": bubble.gmc_max for bubble in Bubble.query.all()}
    
    #获取user.bubble_gmc
    user_bubble_gmc = user.bubble_gmc

    # 遍历每条鱼，更新产币逻辑
    for record in fishing_records:
        if int(user_bubble_gmc[f"gmc_star{record.rarity_id}"]) == 0 :
            record.output_stock = 0
            if record.next_output_time == None:
                record.next_output_time = current_time + 60  # 每3小时产币一次  
        while record.next_output_time and record.next_output_time <= current_time:
            if int(user_bubble_gmc[f"gmc_star{record.rarity_id}"]) == bubble_limits[f"{record.rarity_id}"]:
                #record.output_stock = 0
                record.next_output_time = None   
            else:
                record.output_stock += record.output
                record.next_output_time += 60  # 每3小时产币一次

    # 统计不同rarity_id的鱼的output_stock之和
    bubble_gmc = {
        "gmc_star1": 0,
        "gmc_star2": 0,
        "gmc_star3": 0,
        "gmc_star4": 0,
        "gmc_star5": 0,
        "gmc_star6": 0
    }
    
    
    
    for record in fishing_records:
        if record.rarity_id == 1:
            if bubble_gmc["gmc_star1"] + float(record.output_stock) > bubble_limits["1"]:
                bubble_gmc["gmc_star1"] = bubble_limits["1"]
            else:
                bubble_gmc["gmc_star1"] += float(record.output_stock)
        elif record.rarity_id == 2:
            if bubble_gmc["gmc_star2"] + float(record.output_stock) > bubble_limits["2"]:
                bubble_gmc["gmc_star2"] = bubble_limits["2"]
            else:
                bubble_gmc["gmc_star2"] += float(record.output_stock)
        elif record.rarity_id == 3:
            if bubble_gmc["gmc_star3"] + float(record.output_stock) > bubble_limits["3"]:   
                bubble_gmc["gmc_star3"] = bubble_limits["3"]
            else:
                bubble_gmc["gmc_star3"] += float(record.output_stock)
        elif record.rarity_id == 4:
            if bubble_gmc["gmc_star4"] + float(record.output_stock) > bubble_limits["4"]:
                bubble_gmc["gmc_star4"] = bubble_limits["4"]
            else:   
                bubble_gmc["gmc_star4"] += float(record.output_stock)
        elif record.rarity_id == 5:
            if bubble_gmc["gmc_star5"] + float(record.output_stock) > bubble_limits["5"]:
                bubble_gmc["gmc_star5"] = bubble_limits["5"]
            else:   
                bubble_gmc["gmc_star5"] += float(record.output_stock)
        elif record.rarity_id == 6:
            if bubble_gmc["gmc_star6"] + float(record.output_stock) > bubble_limits["6"]:
                bubble_gmc["gmc_star6"] = bubble_limits["6"]
            else:   
                bubble_gmc["gmc_star6"] += float(record.output_stock)

    # 更新用户的bubble_gmc
    user.bubble_gmc = bubble_gmc
    db.session.commit()

    return jsonify({
        'status': 1,
        'message': 'success',
        'data': user.bubble_gmc
    })

#5.4 收集泡泡gmc接口函数
def collect_bubble(data):
    try:
        user_id = data.get('user_id').strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404   
     
    star_level = data.get('star_level')

    user.collected_gmc += Decimal(user.bubble_gmc[f"gmc_star{star_level}"])
    user.bubble_gmc[f"gmc_star{star_level}"] = 0 
    db.session.add(user)  # 明确告诉 ORM 该对象已被修改
    db.session.commit()
    
    db.session.refresh(user)  # 刷新对象，确保数据从数据库中获取

    
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'collected_gmc': user.collected_gmc,
            'bubble_gmc': user.bubble_gmc,  
        }
    })
