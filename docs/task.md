- [X] 2.1增加当前和拥有nft信息
  - [X] 增加current_avatar_nft信息
  - [X] 增加current_rod_nft信息
  - [X] 增加owned_avatar_nfts信息
  - [X] 增加owned_rod_nfts信息
- [X] 3.1增加最大钓鱼次数
- [X] 3.1增加查询合约代码
```
owned_avatar_nfts---->FishermanNFT合约（4.getOwnedNFTs）
owned_rod_nfts---->FishingRodNFT合约（4.getOwnedNFTs）
user_gmc---->GMC合约（balanceOf）   
user_baits---->User合约（getBaitCount）
```
- [X] 3.4保留"action_type": 2，"action_type": 1合并到3.5"action_type": 0删除
- [X] 3.5初始化接口检查双NFT需要加上查询合约的代码
- [X] 3.8初始化合并到3.5
- [X] 3.10更换钓手NFT和鱼需要加上查询合约的代码
- [X] 错误响应统一不用data，以及换成英文
- [ ] 异步更新接口
- [X] 完善3.11更换钓手NFT和鱼竿NFT界面状态接口
- [X] 把user_id换成钱包地址    

