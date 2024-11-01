from app.routes import bp
from flask import jsonify, request
from app.services import nft_service

#2.2 mint监听接口
@bp.route('/app/v1/mint/event', methods=['POST'])
def free_mint():
    """
    mint监听接口
    
    此接口用于监听用户的mint操作。
    它可以用来铸造钓手(avatar)或鱼竿(rod)NFT。
    
    请求参数:
    - user_id: 用户ID (钱包地址)
    - type: 铸造类型，可选值为 'avatar' 或 'rod'
    - tx_hash: 交易哈希
    
    返回:
    - 监听结果
    """
    data = request.json
    return nft_service.handle_mint_event(data)

#2.3 免费mint鱼竿接口
@bp.route('/app/v1/free_mint/rod', methods=['POST'])
def mint_rod():
    data = request.json
    return nft_service.free_mint_rod(data)

#3.10 更换钓手NFT和鱼竿NFT界面状态接口
@bp.route('/app/v1/nft/change/status', methods=['POST'])
def change_nft_status():
    data = request.json
    return nft_service.change_nft_status(data)

#3.11 更换钓手NFT和鱼竿NFT接口
@bp.route('/app/v1/nft/change', methods=['POST'])
def change_nft():
    """
    更换当前使用的NFT接口
    
    此接口用于更换用户当前使用的钓手(avatar)或鱼竿(rod)NFT。
    
    请求参数:
    - user_id: 用户ID (UUID格式)
    - type: NFT类型，可选值为 'avatar' 或 'rod'
    - nft_token: 要更换的NFT的token ID
    
    返回:
    - 更换操作的结果，包括更新后的NFT信息
    """
    data = request.json
    return nft_service.change_nft(data)
