from app.models import User, FishingSession, Fish, FishingRecord, SystemConfig, RarityDetermination, FishingRodConfig, LevelExperience, FishingGroundConfig
from app import db
from sqlalchemy import func
import random
from flask import jsonify
import uuid
from decimal import Decimal
import numpy as np

#3.8 QTE剩余次数和分数接口函数
def handle_qte(data):
    user_id = data.get('user_id')
    qte_colour = data.get('qte_colour')

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

    current_rod = FishingRodConfig.query.get(user.current_rod_nft['rodId'])
    
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

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    session = FishingSession.query.get(session_id)
    if not session or not session.session_status or not session.fishing_count_deducted:
        return jsonify({'status': 1, 'message': 'Invalid session or session expired'}), 400

    rarity_determination = RarityDetermination.query.filter(
        RarityDetermination.fishing_ground_id == user.current_fishing_ground,
        RarityDetermination.qte_min <= user.accumulated_qte_score,
        RarityDetermination.qte_max >= user.accumulated_qte_score
    ).first()

    if not rarity_determination:
        return jsonify({'status': 1, 'message': 'Unable to determine fish rarity'}), 500

    rarity_id = int(np.random.choice(
        rarity_determination.possible_rarity_ids,
        p=[float(prob) for prob in rarity_determination.appearance_probabilities],
        size=1
    )[0])  # 将 numpy.int32 转换为 Python int

    fish = Fish.query.filter_by(
        rarity_id=rarity_id,
        fishing_ground_id=user.current_fishing_ground
    ).order_by(func.random()).first()

    if not fish:
        return jsonify({'status': 1, 'message': 'No fish found for the given criteria'}), 500

    weight = Decimal(random.uniform(float(fish.min_weight), float(fish.max_weight)))

    fishing_record = FishingRecord(
        user_id=user_id,
        fish_id=fish.fish_id,
        fish_name=fish.fish_name,
        fish_picture_res=fish.fish_picture_res,
        rarity_id=fish.rarity_id,
        fishing_ground_id=fish.fishing_ground_id,
        fishing_ground_name=fish.fishing_ground_name,
        price=fish.price,
        output=fish.output,
        weight=weight
    )
    db.session.add(fishing_record)
    db.session.commit()

    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'fish_id': fish.fish_id,
            'fish_name': fish.fish_name,
            'fish_picture_res': fish.fish_picture_res,
            'rarity_id': fish.rarity_id,
            'fishing_ground_id': fish.fishing_ground_id,
            'fishing_ground_name': fish.fishing_ground_name,
            'price': str(fish.price),
            'output': str(fish.output),
            'weight': str(round(weight, 2))
        }
    })

#3.6 鱼饵购买界面状态接口函数
def get_bait_buy_state(user_id):
    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'status': 1, 'message': '无效的user_id格式'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    max_buy_bait = SystemConfig.query.get('max_buy_bait')
    bait_price = SystemConfig.query.get('bait_price')

    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'max_buy_bait': int(max_buy_bait.config_value),
            'bait_price': str(Decimal(bait_price.config_value))
        }
    })

#3.7 购买鱼饵接口函数
def buy_bait(data):
    user_id = data.get('user_id')
    buy_amount = data.get('buy_amount')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    bait_price = Decimal(SystemConfig.query.get('bait_price').config_value)
    total_price = bait_price * Decimal(buy_amount)

    if user.user_gmc < total_price:
        return jsonify({'status': 1, 'message': 'Insufficient GMC for purchase'}), 400

    user.user_gmc -= total_price
    user.user_baits += buy_amount
    db.session.commit()

    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'user_baits': user.user_baits,
            'user_gmc': str(user.user_gmc)
        }
    })
