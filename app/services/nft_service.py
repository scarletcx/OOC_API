from app.models import User, FreeMintRecord
from app import db
from flask import jsonify
import uuid
from app.services import ethereum_service
import os
from dotenv import load_dotenv
from web3.exceptions import Web3Exception

# 加载环境变量
load_dotenv()

#2.1 免费mint&记录接口函数
def handle_free_mint(user_id, mint_type, wallet_address):
    """
    处理免费NFT铸造请求
    
    此函数处理用户的免费NFT铸造请求，包括在以太坊测试网上的铸造操作。
    
    参数:
    - user_id: 用户ID (UUID格式的字符串)
    - mint_type: 铸造类型，可选值为 'avatar' 或 'rod'
    - wallet_address: 玩家的以太坊钱包地址
    
    返回:
    - 包含操作结果的JSON响应
    """
    try:
        # 将字符串形式的user_id转换为UUID对象
        user_id = uuid.UUID(user_id)
    except ValueError:
        # 如果user_id格式无效，返回错误响应
        return jsonify({'status': 1, 'message': '无效的user_id格式'}), 400

    # 查询用户信息
    user = User.query.get(user_id)
    if not user:
        # 如果用户不存在，返回错误响应
        return jsonify({'status': 1, 'message': '未找到用户'}), 404

    # 获取或创建用户的免费铸造记录
    free_mint_record = FreeMintRecord.query.get(user_id)
    if not free_mint_record:
        # 如果记录不存在，创建新记录
        free_mint_record = FreeMintRecord(user_id=user_id, avatar_minted=False, rod_minted=False)
        db.session.add(free_mint_record)

    # 验证铸造类型
    if mint_type not in ['avatar', 'rod']:
        # 如果铸造类型无效，返回错误响应
        return jsonify({'status': 1, 'message': '无效的铸造类型'}), 400
    
    # 检查是否已经铸造过该类型的NFT
    if mint_type == 'avatar' and free_mint_record.avatar_minted:
        return jsonify({'status': 1, 'message': '钓手NFT已经铸造过了'}), 400
    
    if mint_type == 'rod' and free_mint_record.rod_minted:
        return jsonify({'status': 1, 'message': '鱼竿NFT已经铸造过了'}), 400
    
    # 执行铸造操作
    #try:
    if mint_type == 'avatar':
        # 铸造钓手NFT
        tx_hash = mint_avatar(wallet_address)
        free_mint_record.avatar_minted = True
    else:
        # 铸造鱼竿NFT
        tx_hash = mint_rod(wallet_address)
        free_mint_record.rod_minted = True
    
    # 提交数据库更改
    db.session.commit()
    
    # 回回成功响应，包含铸造状态和交易哈希
    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'avatar_minted': int(free_mint_record.avatar_minted),
            'rod_minted': int(free_mint_record.rod_minted),
            'tx_hash': tx_hash
        }
    })
    # except Exception as e:
    #     # 如果铸造过程中出现异常，回滚数据库更改
    #     db.session.rollback()
    #     # 返回错误响应
    #     return jsonify({'status': 1, 'message': f'铸造失败: {str(e)}'}), 500

def mint_avatar(wallet_address):
    """
    在以太坊测试网上铸造钓手NFT
    
    参数:
    - wallet_address: 玩家的以太坊钱包地址
    
    返回:
    - 交易哈希
    """
    print('调用mint_avatar')
    # 获取Web3实例以连接以太坊网络
    w3 = ethereum_service.get_w3()
    
    avatar_contract = ethereum_service.get_avatar_contract()
    print('avatar_contract:',avatar_contract)
    # try:
    minter_address = os.getenv('MINTER_ADDRESS')
    print('minter_address:',minter_address)
    if not minter_address:
        raise ValueError("MINTER_ADDRESS environment variable is not set")
    
    # 确保地址是校验和格式
    checksum_address = w3.to_checksum_address(minter_address)
    
    # 获取 nonce
    # 获取账户的交易计数（nonce）
    # checksum_address: 发送交易的账户地址（校验和格式）
    # 'pending': 包括待处理的交易在内的nonce值
    print(checksum_address)
    
    # 检查网络连接
    if not w3.is_connected():
        raise ConnectionError("无法连接到以太坊网络")
    
    # 获取当前区块号，以验证连接
    latest_block = w3.eth.get_block('latest')
    print(f"最新区块号: {latest_block['number']}")
    
    nonce = w3.eth.get_transaction_count(checksum_address, 'pending')
    print('nonce:',nonce)
    # except Web3Exception as e:
    #     print(f"Web3 error occurred: {e}")
    #     # 处理错误...
    # except ValueError as e:
    #     print(f"Value error: ")
    #     # 处理错误...
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    #     # 处理错误...
 
    # 构建交易
    # .build_transaction() 是 Web3.py 库中的一个方法，用于构建以太坊交易
    # 它接受一个字典作为参数，包含交易的各种参数
    # 这个方法会返回一个完整的交易对象，但还未签名
    print('freeMintFisherman前')
    txn = avatar_contract.functions.freeMintFisherman(wallet_address).build_transaction({
        'chainId': int(os.getenv('CHAIN_ID')),  # 链ID，用于确定是主网还是测试网
        'gas': 2000000,  # 交易的最大 gas 限制
        'gasPrice': w3.eth.gas_price,  # 当前网络的 gas 价格
        'nonce': nonce,  # 发送者账户的交易计数
    })
 
    print('freeMintFisherman后')
    # 这个构建好的交易对象后续会被签名并发送到网络
    
    # 签名交易
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=os.getenv('MINTER_PRIVATE_KEY'))
    # 发送交易
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # 返回交易哈希
    return w3.to_hex(tx_hash)

def mint_rod(wallet_address):
    """
    在以太坊测试网上铸造鱼竿NFT
    
    参数:
    - wallet_address: 玩家的以太坊钱包地址
    
    返回:
    - 交易哈希
    """
    w3 = ethereum_service.get_w3()
    rod_contract = ethereum_service.get_rod_contract()
    
    try:
        minter_address = os.getenv('MINTER_ADDRESS')
        if not minter_address:
            raise ValueError("MINTER_ADDRESS environment variable is not set")
        
        # 确保地址是校验和格式
        checksum_address = w3.to_checksum_address(minter_address)
        
        # 获取 nonce
        nonce = w3.eth.get_transaction_count(checksum_address, 'pending')
    except Web3Exception as e:
        print(f"Web3 error occurred: {e}")
        # 处理错误...
    except ValueError as e:
        print(f"Value error: {e}")
        # 处理错误...
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # 处理错误...
    
    # 构建交易
    txn = rod_contract.functions.freeMintRod(wallet_address).build_transaction({
        'chainId': int(os.getenv('CHAIN_ID')),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })
    # 签名交易
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=os.getenv('MINTER_PRIVATE_KEY'))
    # 发送交易
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # 返回交易哈希
    return w3.to_hex(tx_hash)
