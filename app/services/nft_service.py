from app.models import User, FreeMintRecord
from app import db
from flask import jsonify
import uuid
from app.services import ethereum_service
import os
from dotenv import load_dotenv
from web3.exceptions import Web3Exception, TimeExhausted
import time

# 加载环境变量
load_dotenv(override=True)

#2.2 mint监听接口函数
def handle_mint_event(data):
    user_id = data.get('user_id')
    mint_type = data.get('type')
    tx_hash = data.get('tx_hash')
    try:
        # 将字符串形式的user_id转换为CHAR(42)
        user_id = user_id.strip()
    except ValueError:
        # 如果user_id格式无效，返回错误响应
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400

    # 查询用户信息
    user = User.query.get(user_id)
    if not user:
        # 如果用户不存在，返回错误响应
        return jsonify({'status': 0, 'message': 'User not found'}), 404
    '''
    # 获取或创建用户的免费铸造记录
    free_mint_record = FreeMintRecord.query.get(user_id)
    if not free_mint_record:
        # 如果记录不存在，创建新记录
        free_mint_record = FreeMintRecord(user_id=user_id, avatar_minted=False, rod_minted=False)
        db.session.add(free_mint_record)
    '''
    # 验证铸造类型
    if mint_type not in ['avatar', 'rod']:
        # 如果铸造类型无效，返回错误响应
        return jsonify({'status': 0, 'message': 'Invalid mint type'}), 400
    # 执行铸造监听
    try:
        if mint_type == 'avatar':
            # 获得监听铸造钓手得到的参数
            tokenId, skinId = mint_avatar(tx_hash)
            #free_mint_record.avatar_minted = True
            if skinId[0]+skinId[1] == '02':
                event_data = {'tokenId': tokenId, 'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmVwfRBC7Pi2TMdWL1PDt7S5yPcL2uerTu5A5WYWretgrD/{skinId}.png"}
            elif skinId[0]+skinId[1] == '03':
                event_data = {'tokenId': tokenId, 'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmUVWsU9gmfBjnzhxpXXLTEp9P7fgykCmydbetsACxuTgJ/{skinId}.png"}
            
            # 更新用户的owned_avatar_nfts
            avatar_contract = ethereum_service.get_avatar_contract()
            owned_nfts = avatar_contract.functions.getOwnedNFTs(user_id).call()
            user.owned_avatar_nfts = [{"tokenId": str(nft[0]), "skinId": nft[1]} for nft in owned_nfts]
            #增加初始免费钓手
            user.owned_avatar_nfts.append({
                "tokenId": "666666",
                "skinId": "010101050408080108"
            })
            db.session.commit()
        else:
            # 获得监听鱼竿铸造得到的参数
            tokenId, skinId = mint_rod(tx_hash)
            #free_mint_record.rod_minted = True
            event_data = {'tokenId': tokenId, 'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{skinId}.png"}
            
            # 更新用户的owned_rod_nfts
            rod_contract = ethereum_service.get_rod_contract()
            owned_nfts = rod_contract.functions.getOwnedNFTs(user_id).call()
            user.owned_rod_nfts = [{"tokenId": str(nft[0]), "skinId": nft[1]} for nft in owned_nfts]
            db.session.commit()
    
        db.session.commit()
         
        owned_avatar_nfts = [
            {
                'tokenId': nft['tokenId'],
                'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmezqXViXKGVJizodoVT88xJv7vw3kYVyj7hJnRC3cZ9K8/{nft['skinId']}.png" if nft['skinId'].startswith('01') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmVwfRBC7Pi2TMdWL1PDt7S5yPcL2uerTu5A5WYWretgrD/{nft['skinId']}.png" if nft['skinId'].startswith('02') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmUVWsU9gmfBjnzhxpXXLTEp9P7fgykCmydbetsACxuTgJ/{nft['skinId']}.png"
            }
            for nft in user.owned_avatar_nfts
        ]
        
        owned_rod_nfts = [
            {
                'tokenId': nft['tokenId'],
                'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{nft['skinId']}.png"
            }
            for nft in user.owned_rod_nfts
        ]
            
        response_data = {
            'status': 1,
            'message': 'success',
            'data': {
                #'avatar_minted': int(free_mint_record.avatar_minted),
                #'rod_minted': int(free_mint_record.rod_minted),
                #'tx_hash': tx_hash,
                'event_data': event_data,
                'owned_avatar_nfts': owned_avatar_nfts,
                'owned_rod_nfts': owned_rod_nfts,
            }
        }
        
        return jsonify(response_data)
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 0, 'message': f'Minting failed: {str(e)}'}), 500

def mint_avatar(tx_hash):
    """
    在以太坊测试网上铸造钓手NFT并监听FishermanMinted事件
    
    参数:
    - wallet_address: 玩家的以太坊钱包地址
    
    返回:
    - 交易哈希、监听事件获得的参数
    """
    print('调用mint_avatar')
    w3 = ethereum_service.get_w3()
    avatar_contract = ethereum_service.get_avatar_contract()
    
    # 增加等待时间并添加重试逻辑
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            break
        except TimeExhausted:
            if attempt == max_attempts - 1:
                raise
            time.sleep(10)  # 等待10秒后重试
    
    # 获取FishermanMinted事件
    fisherman_minted_event = avatar_contract.events.FishermanMinted().process_receipt(tx_receipt)
    if fisherman_minted_event:
        tokenId = fisherman_minted_event[0]['args']['tokenId']
        skinId = fisherman_minted_event[0]['args']['fishermanType']
    else:
        tokenId = None
        skinId = None
    return tokenId, skinId

def mint_rod(tx_hash):
    w3 = ethereum_service.get_w3()
    rod_contract = ethereum_service.get_rod_contract()
    
    # 增加等待时间并添加重试逻辑
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            break
        except TimeExhausted:
            if attempt == max_attempts - 1:
                raise
            time.sleep(10)  # 等待10秒后重试
    
    # 获取RodMinted事件
    rod_minted_event = rod_contract.events.RodMinted().process_receipt(tx_receipt)
    if rod_minted_event:
        tokenId = rod_minted_event[0]['args']['tokenId']
        skinId = rod_minted_event[0]['args']['rodType']
    else:
        tokenId = None
        skinId = None

    return tokenId, skinId

#2.3 免费mint鱼竿接口
def free_mint_rod(data):
    user_id = data.get('user_id')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400 
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404 
    # 获取或创建用户的免费铸造记录
    free_mint_record = FreeMintRecord.query.get(user_id)
    if not free_mint_record:
        # 如果记录不存在，创建新记录
        free_mint_record = FreeMintRecord(user_id=user_id, rod_minted=False)
        db.session.add(free_mint_record)
    # 检查用户是否已经免费铸造过鱼竿
    if free_mint_record.rod_minted:
        return jsonify({'status': 0, 'message': 'User has already minted a rod'}), 400  
    ##向合约发起购买鱼饵操作并等待交易完成
    # 获取Web3实例以连接以太坊网络
    w3 = ethereum_service.get_w3()
    rod_contract = ethereum_service.get_rod_contract()
    minter_address = os.getenv('MINTER_ADDRESS')
    
    if not minter_address:
        raise ValueError("MINTER_ADDRESS environment variable is not set")
    
    # 确保地址是校验和格式
    checksum_address = w3.to_checksum_address(minter_address)
    nonce = w3.eth.get_transaction_count(checksum_address, 'pending')
    
    # 获取当前的 gas 价格
    try:
        gas_price = w3.eth.gas_price
        # 如果需要，可以稍微提高 gas 价格
        #gas_price = int(gas_price * 1.1)  # 提高 10%
    except Exception as e:
        print(f"无法获取 gas 价格: {e}")
        # 如果无法获取 gas 价格，使用一个默认值
        gas_price = w3.to_wei(20, 'gwei')  # 使用 20 Gwei 作为默认值

    txn = rod_contract.functions.freeMintRod(user_id).build_transaction({
        'chainId': int(os.getenv('CHAIN_ID')),  # 链ID，用于确定是主网还是测试网
        'gas': 2000000,  # 交易的最大 gas 限制
        'gasPrice': gas_price,  # 使用计算得到的 gas 价格
        'nonce': nonce,  # 发送者账户的交易计数
    })

    # 签名交易
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=os.getenv('MINTER_PRIVATE_KEY'))
    # 发送交易
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # 增加等待时间并添加重试逻辑
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            break
        except TimeExhausted:
            if attempt == max_attempts - 1:
                raise
            time.sleep(10)  # 等待10秒后重试
    # 获得监听免费mint鱼竿得到的参数
    tokenId, skinId = mint_rod(tx_hash)
    free_mint_record.rod_minted = True
    event_data = {'tokenId': tokenId, 'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{skinId}.png"}
            
    # 更新用户的owned_rod_nfts和current_rod_nft
    owned_nfts = rod_contract.functions.getOwnedNFTs(user_id).call()
    user.owned_rod_nfts = [{"tokenId": str(nft[0]), "skinId": nft[1]} for nft in owned_nfts]
    # 如果current_rod_nft为空，设置为最新铸造的NFT
    if user.current_rod_nft is None and user.owned_rod_nfts:
        user.current_rod_nft = user.owned_rod_nfts[-1]
    db.session.commit()
    owned_rod_nfts = [
            {
                'tokenId': nft['tokenId'],
                'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{nft['skinId']}.png"
            }
            for nft in user.owned_rod_nfts
        ]
    current_rod_nft = user.current_rod_nft
    if current_rod_nft and 'skinId' in current_rod_nft:
        current_rod_nft['skinId'] = f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{current_rod_nft['skinId']}.png"
    # 返回成功响应
    response_data = {
            'status': 1,
            'message': 'success',
            'data': {
                'rod_minted': int(free_mint_record.rod_minted),
                'event_data': event_data,
                'owned_rod_nfts': owned_rod_nfts,
                'current_rod_nft': current_rod_nft
            }
        }
    return jsonify(response_data)

#3.10 更换钓手NFT和鱼竿NFT界面状态接口函数
def change_nft_status(data):
    user_id = data.get('user_id')
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404
    # 更新用户的owned_avatar_nfts
    avatar_contract = ethereum_service.get_avatar_contract()
    owned_nfts = avatar_contract.functions.getOwnedNFTs(user_id).call()
    user.owned_avatar_nfts = [{"tokenId": str(nft[0]), "skinId": nft[1]} for nft in owned_nfts]
    #增加初始免费钓手
    user.owned_avatar_nfts.append({
        "tokenId": "666666",
        "skinId": "010101050408080108"
    })
    db.session.commit()
    # avatar_contract = ethereum_service.get_avatar_contract()
    # owned_nfts = avatar_contract.functions.getOwnedNFTs(user_id).call()
    # user.owned_avatar_nfts = [{"tokenId": str(nft)} for nft in owned_nfts]
    # db.session.commit()        
    # 如果current_avatar_nft为空，设置为最新铸造的NFT
    # if user.current_avatar_nft is None and user.owned_avatar_nfts:
    #     user.current_avatar_nft = user.owned_avatar_nfts[-1]
    
    # 更新用户的owned_rod_nfts
    rod_contract = ethereum_service.get_rod_contract()
    owned_nfts = rod_contract.functions.getOwnedNFTs(user_id).call()
    user.owned_rod_nfts = [{"tokenId": str(nft[0]), "skinId": nft[1]} for nft in owned_nfts]
    db.session.commit()        
    # # 如果current_rod_nft为空，设置为最新铸造的NFT
    # if user.current_rod_nft is None and user.owned_rod_nfts:
    #     user.current_rod_nft = user.owned_rod_nfts[-1]
    # db.session.commit()
    
    current_avatar_nft = user.current_avatar_nft
    if current_avatar_nft and 'skinId' in current_avatar_nft:
        current_avatar_nft['skinId'] = f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmezqXViXKGVJizodoVT88xJv7vw3kYVyj7hJnRC3cZ9K8/{current_avatar_nft['skinId']}.png" if current_avatar_nft['skinId'].startswith('01') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmVwfRBC7Pi2TMdWL1PDt7S5yPcL2uerTu5A5WYWretgrD/{current_avatar_nft['skinId']}.png" if current_avatar_nft['skinId'].startswith('02') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmUVWsU9gmfBjnzhxpXXLTEp9P7fgykCmydbetsACxuTgJ/{current_avatar_nft['skinId']}.png"
        
    current_rod_nft = user.current_rod_nft
    if current_rod_nft and 'skinId' in current_rod_nft:
        skinId = current_rod_nft['skinId']
        current_rod_nft['skinId'] = f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{skinId}.png"
    
    owned_avatar_nfts = [
            {
                'tokenId': nft['tokenId'],
                'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmezqXViXKGVJizodoVT88xJv7vw3kYVyj7hJnRC3cZ9K8/{nft['skinId']}.png" if nft['skinId'].startswith('01') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmVwfRBC7Pi2TMdWL1PDt7S5yPcL2uerTu5A5WYWretgrD/{nft['skinId']}.png" if nft['skinId'].startswith('02') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmUVWsU9gmfBjnzhxpXXLTEp9P7fgykCmydbetsACxuTgJ/{nft['skinId']}.png"
            }
            for nft in user.owned_avatar_nfts
        ]
        
    owned_rod_nfts = [
            {
                'tokenId': nft['tokenId'],
                'skinId': f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{nft['skinId']}.png"
            }
            for nft in user.owned_rod_nfts
        ]
    
    # 返回成功响应
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'current_avatar_nft': current_avatar_nft,
            'current_rod_nft': current_rod_nft,
            'owned_avatar_nfts': owned_avatar_nfts,
            'owned_rod_nfts': owned_rod_nfts
        }
    })

#3.11 更换钓手NFT和鱼竿NFT接口函数
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
    try:
        user_id = user_id.strip()
    except ValueError:
        return jsonify({'status': 0, 'message': 'Invalid user_id format'}), 400
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 0, 'message': 'User not found'}), 404

    # 验证NFT类型
    if nft_type not in ['avatar', 'rod']:
        return jsonify({'status': 0, 'message': 'Invalid NFT type'}), 400

    
    # 根据NFT类型选择相应的NFT列表
    nft_list = user.owned_avatar_nfts if nft_type == 'avatar' else user.owned_rod_nfts
    nft = next((item for item in nft_list if item['tokenId'] == nft_token), None)

    # 检查用户是否拥有该NFT
    if not nft:
        return jsonify({'status': 0, 'message': 'NFT not found'}), 404

    # 更新用户当前使用的NFT
    if nft_type == 'avatar':
        user.current_avatar_nft = nft
    else:
        user.current_rod_nft = nft

    # 提交更改到数据库
    db.session.commit()
    
    if nft_type == 'avatar':
        nft['skinId'] = f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmezqXViXKGVJizodoVT88xJv7vw3kYVyj7hJnRC3cZ9K8/{nft['skinId']}.png" if nft['skinId'].startswith('01') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmVwfRBC7Pi2TMdWL1PDt7S5yPcL2uerTu5A5WYWretgrD/{nft['skinId']}.png" if nft['skinId'].startswith('02') else f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmUVWsU9gmfBjnzhxpXXLTEp9P7fgykCmydbetsACxuTgJ/{nft['skinId']}.png"
    else:
        nft['skinId'] = f"https://magenta-adorable-stork-81.mypinata.cloud/ipfs/QmWCHJAeyjvDNPrP8U8CrnTwwvAgsMmhBGnyNo4R7g7mBh/{nft['skinId']}.png"

    # 返回成功响应
    return jsonify({
        'status': 1,
        'message': 'success',
        'data': {
            'type': nft_type,
            'current_nft': nft
        }
    })
