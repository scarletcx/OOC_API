from web3 import Web3
import os
import json
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv(override=True)
'''
# 配置代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'https://127.0.0.1:7890',
}

# 创建一个带有代理的会话
session = requests.Session()
session.proxies = proxies
'''

#print('连接前')
# 连接到以太坊测试网
# Connect to the Ethereum network 
print(os.getenv('ETHEREUM_TESTNET_URL'))
w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_TESTNET_URL')))
# Get block by number
'''
block_number = 123456  # Replace with the desired block number or use 'latest'
block = w3.eth.get_block(block_number)
print(block)
'''
#print('w3:',w3)
#print('Is connected:', w3.is_connected())
#print('连接后')
# 读取 ABI 文件
with open(os.getenv('AVATAR_CONTRACT_ABI_PATH')) as f:
    AVATAR_CONTRACT_ABI = json.load(f)

with open(os.getenv('ROD_CONTRACT_ABI_PATH')) as f:
    ROD_CONTRACT_ABI = json.load(f)

# 获取智能合约地址
AVATAR_CONTRACT_ADDRESS = os.getenv('AVATAR_CONTRACT_ADDRESS')
ROD_CONTRACT_ADDRESS = os.getenv('ROD_CONTRACT_ADDRESS')

# 合约实例
avatar_contract = w3.eth.contract(address=AVATAR_CONTRACT_ADDRESS, abi=AVATAR_CONTRACT_ABI)
rod_contract = w3.eth.contract(address=ROD_CONTRACT_ADDRESS, abi=ROD_CONTRACT_ABI)
#print('avatar_contract:')
#print(avatar_contract)
#print(rod_contract)

def get_w3():
    return w3

def get_avatar_contract():
    return avatar_contract

def get_rod_contract():
    return rod_contract
