#后端调用模板
'''
# 获取Web3实例以连接以太坊网络
    w3 = ethereum_service.get_w3()
    user_contract = ethereum_service.get_user_contract()
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

    txn = user_contract.functions.buyBaitsAdmin(user_id, buy_amount).build_transaction({
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
    #从合约更新user_gmc
    gmc_contract = ethereum_service.get_gmc_contract()
    user.user_gmc = gmc_contract.functions.balanceOf(user_id).call() * (10 ** -18)  # .call() 用于在本地执行合约函数，不会发起链上交易
    #从合约更新鱼饵数量
    user.user_baits = user_contract.functions.getBaitCount(user_id).call()
    db.session.commit()
    '''