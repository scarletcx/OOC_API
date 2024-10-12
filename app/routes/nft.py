from app.routes import bp
from flask import jsonify, request
from app.services import nft_service

@bp.route('/app/v1/mint/free', methods=['POST'])
def free_mint():
    """
    免费铸造NFT接口
    
    此接口用于处理用户的免费NFT铸造请求。
    它可以用来铸造钓手(avator)或鱼竿(rod)NFT，也可以查询用户的铸造状态。
    
    请求参数:
    - user_id: 用户ID (UUID格式)
    - type: 铸造类型，可选值为 'avator' 或 'rod'。如果不提供，则查询铸造状态。
    
    返回:
    - 如果提供了type参数，返回铸造操作的结果
    - 如果没有提供type参数，返回用户的铸造状态
    """
    data = request.json
    user_id = data.get('user_id')
    mint_type = data.get('type')
    
    if not user_id:
        return jsonify({'status': 1, 'message': '缺少user_id参数'}), 400
    
    return nft_service.handle_free_mint(user_id, mint_type)

#3.10 更换钓手NFT和鱼竿NFT接口
@bp.route('/app/v1/nft/change', methods=['POST'])
def change_nft():
    """
    更换当前使用的NFT接口
    
    此接口用于更换用户当前使用的钓手(avator)或鱼竿(rod)NFT。
    
    请求参数:
    - user_id: 用户ID (UUID格式)
    - type: NFT类型，可选值为 'avator' 或 'rod'
    - nft_token: 要更换的NFT的token ID
    
    返回:
    - 更换操作的结果，包括更新后的NFT信息
    """
    data = request.json
    return nft_service.change_nft(data)
