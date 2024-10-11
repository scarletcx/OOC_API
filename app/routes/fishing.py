from app.routes import bp
from flask import jsonify, request
from app.services import fishing_service

@bp.route('/app/v1/fishing/init', methods=['POST'])
def init_fishing_session():
    data = request.json
    return fishing_service.init_fishing_session(data)

@bp.route('/app/v1/fishing/qte', methods=['POST'])
def fishing_qte():
    data = request.json
    return fishing_service.handle_qte(data)

@bp.route('/app/v1/fish/info', methods=['POST'])
def get_fish_info():
    data = request.json
    return fishing_service.get_fish_info(data)

@bp.route('/app/v1/bait/buystate', methods=['GET'])
def bait_buy_state():
    user_id = request.args.get('user_id')
    return fishing_service.get_bait_buy_state(user_id)

@bp.route('/app/v1/bait/buy', methods=['POST'])
def buy_bait():
    data = request.json
    return fishing_service.buy_bait(data)