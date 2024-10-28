from app.models import User, PondConfig
from flask import jsonify

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
        
    # 查询用户当前鱼池等级
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

