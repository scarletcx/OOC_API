from app.routes import bp
from flask import jsonify, request
from app.services import pond_service

#5.1 鱼池升级界面状态接口
@bp.route('/app/v1/pond/upgradestate', methods=['POST'])
def upgrade_pond_state():
    data = request.json
    return pond_service.get_upgrade_pond_state(data)

#5.2 鱼池升级接口
@bp.route('/app/v1/pond/upgrade', methods=['POST'])
def upgrade_pond():
    data = request.json
    return pond_service.upgrade_pond(data)

#5.3 泡泡产币更新接口
@bp.route('/app/v1/pond/bubble/output', methods=['POST'])
def update_bubble():
    data = request.json
    return pond_service.update_bubble(data)

#5.4 收集泡泡gmc接口
@bp.route('/app/v1/pond/bubble/collect', methods=['POST'])
def collect_bubble():
    data = request.json
    return pond_service.collect_bubble(data)    

#5.5 claim接口
@bp.route('/app/v1/pond/claim', methods=['POST'])
def claim():
    data = request.json
    return pond_service.claim(data) 