from app.models import User, FishingSession, Fish, FishingRecord, SystemConfig, RarityDetermination, FishingRodConfig
from app import db
from sqlalchemy import func
import random
from flask import jsonify

def init_fishing_session(data):
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    if user.fishing_count <= 0:
        return jsonify({'status': 1, 'message': 'Insufficient fishing count'}), 400

    session = FishingSession(user_id=user_id)
    db.session.add(session)
    db.session.commit()

    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'user_baits': user.user_baits,
            'session_id': str(session.session_id)
        }
    })

def handle_qte(data):
    user_id = data.get('user_id')
    action_type = data.get('action_type')
    qte_colour = data.get('qte_colour')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    if action_type == 0:  # Initialize
        return initialize_qte(user)
    elif action_type == 1:  # QTE operation
        return process_qte(user, qte_colour)
    else:
        return jsonify({'status': 1, 'message': 'Invalid action type'}), 400

def initialize_qte(user):
    current_rod = FishingRodConfig.query.get(user.current_rod_nft['rodId'])
    user.remaining_qte_count = current_rod.qte_count
    user.accumulated_qte_score = 0
    user.qte_hit_status_green = False
    user.qte_hit_status_red = False
    user.qte_hit_status_black = False
    db.session.commit()

    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'remaining_qte_count': user.remaining_qte_count,
            'accumulated_qte_score': user.accumulated_qte_score
        }
    })

def process_qte(user, qte_colour):
    if user.remaining_qte_count <= 0:
        return jsonify({'status': 1, 'message': 'No remaining QTE attempts'}), 400
    
    if qte_colour not in ['red', 'green', 'black']:
        return jsonify({'status': 1, 'message': 'Invalid QTE colour'}), 400

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
        'status': 0,
        'message': 'success',
        'data': {
            'remaining_qte_count': user.remaining_qte_count,
            'accumulated_qte_score': user.accumulated_qte_score
        }
    })

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

    rarity_id = random.choices(
        rarity_determination.possible_rarity_ids,
        weights=rarity_determination.appearance_probabilities,
        k=1
    )[0]

    fish = Fish.query.filter_by(
        rarity_id=rarity_id,
        fishing_ground_id=user.current_fishing_ground
    ).order_by(func.random()).first()

    if not fish:
        return jsonify({'status': 1, 'message': 'No fish found for the given criteria'}), 500

    weight = random.uniform(fish.min_weight, fish.max_weight)

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
            'price': fish.price,
            'output': fish.output,
            'weight': round(weight, 2)
        }
    })

def get_bait_buy_state(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    max_buy_bait = SystemConfig.query.get('max_buy_bait')
    bait_price = SystemConfig.query.get('bait_price')

    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'max_buy_bait': int(max_buy_bait.config_value),
            'bait_price': float(bait_price.config_value)
        }
    })

def buy_bait(data):
    user_id = data.get('user_id')
    buy_amount = data.get('buy_amount')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    bait_price = float(SystemConfig.query.get('bait_price').config_value)
    total_price = bait_price * buy_amount

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
            'user_gmc': float(user.user_gmc)
        }
    })