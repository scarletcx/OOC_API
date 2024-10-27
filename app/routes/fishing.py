from app.routes import bp
from flask import jsonify, request
from app.services import fishing_service

#3.6 鱼饵购买界面状态接口
@bp.route('/app/v1/bait/buystate', methods=['POST'])
def bait_buy_state():
    data = request.json
    user_id = data.get('user_id')
    return fishing_service.get_bait_buy_state(user_id)

#3.7 购买鱼饵接口
@bp.route('/app/v1/bait/buy', methods=['POST'])
def buy_bait():
    data = request.json
    return fishing_service.buy_bait(data)

#3.8 QTE初始化/QTE剩余次数和分数接口
@bp.route('/app/v1/fishing/qte', methods=['POST'])
def fishing_qte():
    data = request.json
    return fishing_service.handle_qte(data)

#4.1 获鱼信息接口
@bp.route('/app/v1/fish/info', methods=['POST'])
def get_fish_info():
    data = request.json
    return fishing_service.get_fish_info(data)

#4.2 卖鱼接口
@bp.route('/app/v1/fish/sell', methods=['POST'])
def sell_fish():
    data = request.json
    return fishing_service.sell_fish(data)

#4.3 放入鱼池接口
@bp.route('/app/v1/fish/pool', methods=['POST'])
def put_fish_pool():
    data = request.json
    return fishing_service.put_fish_pool(data)  