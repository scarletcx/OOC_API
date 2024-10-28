from app.routes import bp
from flask import jsonify, request
from app.services import pond_service

#5.1 鱼池升级界面状态接口
@bp.route('/app/v1/pond/upgradestate', methods=['POST'])
def upgrade_pond_state():
    data = request.json
    return pond_service.get_upgrade_pond_state(data)

