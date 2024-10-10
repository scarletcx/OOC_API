from flask import Blueprint, jsonify, request
from app import database as db_ops

bp = Blueprint('routes', __name__)

@bp.route('/app/v1/player/info', methods=['POST'])
def get_player_info():
    data = request.json
    user_id = data.get('user_id')
    
    user_info = db_ops.get_user_info(user_id)
    if user_info:
        return jsonify({"status": 0, "message": "success", "data": user_info}), 200
    else:
        return jsonify({"status": 1, "message": "User not found"}), 404

# Add other route handlers here...
