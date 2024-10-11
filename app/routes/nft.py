from app.routes import bp
from flask import jsonify, request
from app.services import nft_service

@bp.route('/app/v1/mint/free', methods=['POST'])
def free_mint():
    data = request.json
    return nft_service.handle_free_mint(data)

@bp.route('/app/v1/nft/change', methods=['POST'])
def change_nft():
    data = request.json
    return nft_service.change_nft(data)