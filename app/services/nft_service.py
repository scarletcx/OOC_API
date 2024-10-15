from app.models import User, FreeMintRecord
from app import db
from flask import jsonify
import uuid

#2.1 免费mint&记录接口函数
def handle_free_mint(user_id, mint_type):
    """
    处理免费NFT铸造请求
    
    此函数处理用户的免费NFT铸造请求。
    
    参数:
    - user_id: 用户ID (UUID格式的字符串)
    - mint_type: 铸造类型，可选值为 'avatar' 或 'rod'
    
    返回:
    - 包含操作结果的JSON响应
    """
    try:
        # 将字符串形式的user_id转换为UUID对象
        user_id = uuid.UUID(user_id)
    except ValueError:
        return jsonify({'status': 1, 'message': '无效的user_id格式'}), 400

    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 获取或创建用户的免费铸造记录
    free_mint_record = FreeMintRecord.query.get(user_id)
    if not free_mint_record:
        free_mint_record = FreeMintRecord(user_id=user_id, avatar_minted=False, rod_minted=False)
        db.session.add(free_mint_record)

    # 处理铸造请求
    if mint_type not in ['avatar', 'rod']:
        return jsonify({'status': 1, 'message': '无效的铸造类型'}), 400
    
    if mint_type == 'avatar' and free_mint_record.avatar_minted:
        return jsonify({'status': 1, 'message': '钓手NFT已经铸造过了'}), 400
    
    if mint_type == 'rod' and free_mint_record.rod_minted:
        return jsonify({'status': 1, 'message': '鱼竿NFT已经铸造过了'}), 400
    
    if mint_type == 'avatar':
        free_mint_record.avatar_minted = True
        # 这里应该添加钓手NFT铸造的逻辑，并将其添加到用户的owned_avatar_nfts中
        # 例如：
        # new_avatar_nft = {"tokenId": f"NFT#{generate_token_id()}", "avatarId": 1}
        # user.owned_avatar_nfts.append(new_avatar_nft)
    elif mint_type == 'rod':
        free_mint_record.rod_minted = True
        # 这里应该添加鱼竿NFT铸造的逻辑，并将其添加到用户的owned_rod_nfts中
        # 例如：
        # new_rod_nft = {"tokenId": f"NFT#{generate_token_id()}", "rodId": 1}
        # user.owned_rod_nfts.append(new_rod_nft)
    
    db.session.commit()
    
    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'avatar_minted': int(free_mint_record.avatar_minted),
            'rod_minted': int(free_mint_record.rod_minted)
        }
    })


#3.10 更换钓手NFT和鱼竿NFT接口函数
def change_nft(data):
    """
    更换用户当前使用的NFT
    
    此函数处理用户更换当前使用的钓手(avatar)或鱼竿(rod)NFT的请求。
    
    参数:
    - data: 包含user_id, type和nft_token的字典
    
    返回:
    - 包含操作结果的JSON响应
    """
    user_id = data.get('user_id')
    nft_type = data.get('type')
    nft_token = data.get('nft_token')

    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 验证NFT类型
    if nft_type not in ['avatar', 'rod']:
        return jsonify({'status': 1, 'message': '无效的NFT类型', 'data': {'error_code': 2002, 'error_message': "类型必须是 'avatar' 或 'rod'"}}), 400

    # 根据NFT类型选择相应的NFT列表
    nft_list = user.owned_avatar_nfts if nft_type == 'avatar' else user.owned_rod_nfts
    nft = next((item for item in nft_list if item['tokenId'] == nft_token), None)

    # 检查用户是否拥有该NFT
    if not nft:
        return jsonify({'status': 1, 'message': '未找到NFT', 'data': {'error_code': 2001, 'error_message': '指定的NFT不属于该用户'}}), 404

    # 更新用户当前使用的NFT
    if nft_type == 'avatar':
        user.current_avatar_nft = nft
    else:
        user.current_rod_nft = nft

    # 提交更改到数据库
    db.session.commit()

    # 返回成功响应
    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'type': nft_type,
            'new_nft_token': nft_token
        }
    })
