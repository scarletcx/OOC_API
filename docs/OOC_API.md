# OOC接口设计

[TOC]

## 1 设计说明

该文档是对钓鱼佬游戏的设计说明文档，需要根据钓鱼佬游戏的交互功能设计，提供对应后端服务功能。接口设计内容需要详细说明清楚相关接口所服务的游戏交互功能、方法、url、参数、消息示例等信息。
该文档将按照产品需求设计说明书，逐个说明界面相关的接口设计。

使用说明：
- 初始化---3.1 钓鱼准备界面状态接口
- 免费mint---2.1 免费mint记录&查询接口(无type参数，用作记录)（罗总说不存在没获得免费mint就进游戏的情况，所以该接口可能不需要，后面的查询调用在哪用我也就先不写了）
- 首页---3.2 游戏进入条件检查接口（检查是否有双NFT）
      ---3.3 钓鱼次数回复倒计时及钓鱼操作接口（action_type使用0进行钓鱼次数和倒计时查询，前端在首页每次倒计时归0时都要调用一次该接口更新次数和倒计时）
- 点击鱼饵袋子时---3.4 鱼饵购买界面状态接口
- 点击鱼饵购买按钮时---3.5 购买鱼饵接口
- 点击钓鱼按钮时---3.3 钓鱼次数回复倒计时及钓鱼操作接口（action_type使用1进行钓鱼操作）
- 每次QTE操作点击后---3.6 QTE剩余次数和分数接口（查询当前QTE剩余次数和累计分数）  
- 点击更换皮肤和鱼竿时---3.7 更换皮肤和鱼竿接口
- QTE剩余次数为0时---4.1 获鱼信息接口

## 2 引导界面

### 2.1 免费mint记录&查询接口

#### 2.1.1 功能说明

该接口用于记录和查询玩家是否已经进行过免费mint操作，即记录和查询玩家的avator和rod的mint状态。

#### 2.1.2 详细设计

- 接口概要

  | 接口名称 | 免费mint记录&查询接口              |
  | -------- | ----------------------------------- |
  | 方法     | POST                                |
  | URL      | http://[IP]:[Port]/app/v1/mint/free |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 是否必须 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 是       | 123e4567-e89b-12d3-a456-426614174000 |
  | 调用参数 | type       | 查询的NFT类型，avator或rod         | string   | 否       | "avator"                             |

- 响应参数

  | 参数名称       | 参数英文名 | 参数描述                     | 参数类型 | 参数示例 |
  | -------------- | ---------- | ---------------------------- | -------- | -------- |
  | avator免费mint记录 | avator_minted | 是否已进行过avator免费mint，1是0否 | integer  | 1        |
  | rod免费mint记录    | rod_minted    | 是否已进行过rod免费mint，1是0否    | integer  | 0        |

#### 2.1.3 消息示例

- 请求消息（指定type）

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "type": "avator"
  }
  ```

- 请求消息（查询）

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应（指定type）

    ```json
    {
        "status": 0,
        "message": "success"
    }
    ```

  - 成功响应（查询）

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "avator_minted": 1,
            "rod_minted": 0
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Failed to retrieve mint information."
    }
    ```

#### 2.1.4 功能逻辑

1. 接收玩家ID作为必须参数，type作为可选参数；
2. 如果提供了type参数：
   a. 在数据库中更新指定类型（avator或rod）的免费mint记录,即把免费Mint记录表 (free_mint_records) 中指定user_id的avator_minted或rod_minted记录更新为TRUE；
   b. 返回操作成功或失败的状态；
3. 如果没有提供type参数：
   a. 查询玩家的avator和rod的免费mint记录,即查询免费Mint记录表 (free_mint_records) 中指定user_id的avator_minted和rod_minted记录；
   b. 返回两种类型的mint状态；
4. 如果查询成功，返回相应的mint状态；
5. 如果查询失败，返回错误信息。

## 3 钓鱼准备界面

### 3.1 钓鱼准备界面状态（初始化）接口

#### 3.1.1 功能说明

进入钓鱼准备界面，查询界面中相应的信息，信息基本都与玩家属性、玩家钓鱼资产状态相关。获取的内容应当包括：

- GMC数量
- 鱼饵数量
- 玩家等级
- 玩家经验值
- 升级所需经验值
- 当前使用的钓手NFT
- 当前使用的鱼竿NFT
- 拥有的所有钓手NFT
- 拥有的所有鱼竿NFT
- 鱼竿Battle Skill
- 鱼竿QTE Skill
- 准入渔场列表
- 当前渔场

#### 3.1.2 详细设计

- 接口概要

  | 接口名称 | 钓鱼准备界面状态接口                          |
  | -------- | --------------------------------- |
  | 方法     | GET                               |
  | URL      | http://[IP]:[Port]/app/v1/fishing |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                                     |
  | -------- | ---------- | ---------------------------------- | -------- | -------------------------------------------- |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b<br>-12d3-a456-42<br>6614174000 |

- 响应参数

  | 参数名称 | 参数英文名 | 次级参数名称      | 次级参数英文名   | 参数描述                                                     | 参数类型 | 参数示例                                     |
  | -------- | ---------- | ----------------- | ---------------- | ------------------------------------------------------------ | -------- | -------------------------------------------- |
  | 返回码   | status     | -                 | -                | 0表示成功，其他表示失败                                      | int      | 0                                            |
  | 返回信息 | message    | -                 | -                | 成功时返回success，失败时返回失败原因                        | string   | success                                      |
  | 返回数据 | data       | 玩家ID            | user_id          | 玩家唯一ID                                                   | string   | 123e4567-e89b<br>-12d3-a456-42<br>6614174000 |
  | 返回数据 | data       | 玩家等级          | user_level       | 玩家当前等级                                                 | int      | 12                                           |
  | 返回数据 | data       | 玩家经验值        | user_exp         | 玩家当前经验值                                               | int      | 35                                           |
  | 返回数据 | data       | 升级所需经验值    | max_exp          | 当前等级升级所需经验值                                       | int      | 65                                           |
  | 返回数据 | data       | GMC数量           | user_gmc         | 玩家当前GMC数量                                              | float    | 520.1314                                     |
  | 返回数据 | data       | 鱼饵数量          | user_baits       | 玩家当前鱼饵数量                                             | int      | 80                                           |
  | 返回数据 | data       | 玩家使用的钓手NFT | current_avator_nft | 玩家当前使用的<br/>钓手nft信息                                | object   | {"tokenId": "NFT#23189", "avatorId": 1}      |
  | 返回数据 | data       | 玩家使用的鱼竿NFT | current_rod_nft  | 玩家当前使用的<br/>鱼竿NFT信息                                | object   | {"tokenId": "NFT#23189", "rodId": 1}         |
  | 返回数据 | data       | 拥有的所有钓手NFT | owned_avator_nfts | 玩家拥有的所有<br/>钓手NFT信息列表，<br/>未拥有则为空数组     | array    | [{"tokenId": "NFT#23189", "avatorId": 1}, {"tokenId": "NFT#23190", "avatorId": 2}] |
  | 返回数据 | data       | 拥有的所有鱼竿NFT | owned_rod_nfts   | 玩家拥有的所有<br/>鱼竿NFT信息列表，<br/>未拥有则为空数组    | array    | [{"tokenId": "NFT#23189", "rodId": 1}, {"tokenId": "NFT#23190", "rodId": 2}] |
  | 返回数据 | data       | 鱼竿Battle Skill  | battle_skill_desc_en | 鱼竿Battle Skill<br/>英文描述                                | string   | An ordinary fisherman,<br>diligently practicing. |
  | 返回数据 | data       | 鱼竿QTE Skill     | qte_skill_desc_en | 鱼竿QTE Skill<br/>英文描述                                   | string   | Plain Fishing Rod                            |
  | 返回数据 | data       | 准入渔场列表      | accessible_fishing_grounds | 玩家可进入的渔场ID列表                                      | array    | [1001, 1002, 1003]                           |
  | 返回数据 | data       | 当前渔场          | current_fishing_ground | 玩家当前所在的渔场ID                                        | integer  | 1001                                         |
#### 3.1.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "user_level": 12,
            "user_exp": 35,
            "max_exp": 65,
            "user_gmc": 520.1314,
            "user_baits": 80,
            "current_avator_nft": {"tokenId": "NFT#23189", "avatorId": 1},
            "current_rod_nft": {"tokenId": "NFT#23189", "rodId": 1},
            "owned_avator_nfts": [
                {"tokenId": "NFT#23189", "avatorId": 1},
                {"tokenId": "NFT#23190", "avatorId": 2}
            ],
            "owned_rod_nfts": [
                {"tokenId": "NFT#23189", "rodId": 1},
                {"tokenId": "NFT#23190", "rodId": 2}
            ],
            "battle_skill_desc_en": "An ordinary fisherman, diligently practicing.",
            "qte_skill_desc_en": "Plain Fishing Rod",
            "accessible_fishing_grounds": [1001, 1002, 1003],
            "current_fishing_ground": 1001
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Can't get user's information."
    }
    ```

#### 3.1.4 功能逻辑

1. 根据传入的user_id，从users表中获取玩家的基本信息，包括：
   - user_id（users表）
   - user_level（users表）
   - user_exp（users表）
   - user_gmc（users表）
   - user_baits（users表）
   - current_avator_nft（users表）
   - current_rod_nft（users表）
   - owned_avator_nfts（users表）
   - owned_rod_nfts（users表）

2. 从level_experience表中获取当前等级升级所需的经验值（max_exp）。

3. 根据current_rod_nft中的rodId，从fishing_rod_configs表中获取当前使用鱼竿的Battle Skill和QTE Skill：
   - battle_skill_desc_en（fishing_rod_configs表）
   - qte_skill_desc_en（fishing_rod_configs表）

4. 计算accessible_fishing_grounds：
   a. 从fishing_ground_configs表中查询所有enter_lv小于等于玩家当前等级（user_level）的渔场ID。
   b. 将查询结果作为accessible_fishing_grounds,并保存到users表中。

5. 处理current_fishing_ground：
   a. 如果users表中的current_fishing_ground为null或不在accessible_fishing_grounds列表中：
      - 将current_fishing_ground设置为accessible_fishing_grounds列表中的第一个渔场ID。
      - 更新users表中的current_fishing_ground字段。
   b. 否则，保持current_fishing_ground不变。
   c. 将current_fishing_ground作为返回数据的一部分。    

6. 如果获取信息成功，将所有数据组合成响应消息返回；如果获取过程中出现任何错误，返回相应的错误信息。

响应参数来源说明：

| 响应参数 | 来源表 | 说明 |
|----------|--------|------|
| user_id | users | 直接从users表获取 |
| user_level | users | 直接从users表获取 |
| user_exp | users | 直接从users表获取 |
| max_exp | level_experience | 根据user_level从level_experience表获取 |
| user_gmc | users | 直接从users表获取 |
| user_baits | users | 直接从users表获取 |
| current_avator_nft | users | 直接从users表获取，包含tokenId和avatorId |
| current_rod_nft | users | 直接从users表获取，包含tokenId和rodId |
| owned_avator_nfts | users | 直接从users表获取，是一个包含多个{tokenId, avatorId}对象的数组 |
| owned_rod_nfts | users | 直接从users表获取，是一个包含多个{tokenId, rodId}对象的数组 |
| battle_skill_desc_en | fishing_rod_configs | 根据current_rod_nft中的rodId从fishing_rod_configs表获取 |
| qte_skill_desc_en | fishing_rod_configs | 根据current_rod_nft中的rodId从fishing_rod_configs表获取 |
| accessible_fishing_grounds | fishing_ground_configs | 根据user_level从fishing_ground_configs表中查询得到 |
| current_fishing_ground | users | 直接从users表获取，但需要确保它在accessible_fishing_grounds中 |

注意：accessible_fishing_grounds是根据玩家当前等级动态计算的，而不是直接从users表获取。这个计算过程应该在每次调用此接口时执行，以确保返回最新的可进入渔场列表。current_fishing_ground仍然直接从users表获取，但应确保它始终是accessible_fishing_grounds中的一个有效值。
### 3.2 游戏进入条件检查接口

#### 3.2.1 功能说明

该接口用于检查玩家是否拥有当前使用的钓手NFT和鱼竿NFT，以确定玩家是否能够进入游戏。

#### 3.2.2 详细设计

- 接口概要

  | 接口名称 | 游戏进入条件检查接口                    |
  | -------- | --------------------------------------- |
  | 方法     | POST                                   |
  | URL      | http://[IP]:[Port]/app/v1/game/entercheck |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |

- 响应参数

  | 参数名称       | 参数英文名      | 参数描述                     | 参数类型 | 参数示例 |
  | -------------- | --------------- | ---------------------------- | -------- | -------- |
  | 是否可进入游戏 | can_enter_game | 是否可以进入游戏的标识       | boolean  | true     |
  | 钓手NFT       | avator          | 当前使用的钓手NFT token，缺失则为null | string   | NFT#23189 |
  | 鱼竿NFT       | rod             | 当前使用的鱼竿NFT token，缺失则为null | string   | NFT#23190 |

#### 3.2.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "can_enter_game": true,
            "avator": "NFT#23189",
            "rod": "NFT#23190"
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Missing avatar or fishing rod",
        "data": {
            "can_enter_game": false,
            "avator": null,
            "rod": "NFT#23190"
        }
    }
    ```

#### 3.2.4 功能逻辑

1. 接收玩家ID作为输入参数；
2. 查询数据库里的users表，获取玩家当前使用的钓手NFT和鱼竿NFT信息；
3. 检查玩家是否同时拥有当前使用的钓手NFT和鱼竿NFT：
   a. 如果两者都拥有，设置 can_enter_game 为 true，并在响应中包含两个NFT的token；
   b. 如果缺少任一NFT，设置 can_enter_game 为 false，在响应中包含存在的NFT token，缺失的显示为null；
4. 返回检查结果。

#### 3.2.5 注意事项

1. 即使玩家不能进入游戏（can_enter_game 为 false），也应返回玩家拥有的NFT信息。
2. 失败响应中的 message 统一为 "Missing avatar or fishing rod"，具体缺失情况可以从 data 中的 avator 和 rod 值判断。
3. 成功响应中也应包含 avator 和 rod 的具体 token 信息，以便客户端使用。

### 3.3 改变渔场接口

#### 3.3.1 功能说明

该接口用于更改玩家当前所在的渔场。接口会验证玩家是否有权限进入指定的渔场，如果有权限则更新玩家的当前渔场，否则返回错误信息。

#### 3.3.2 详细设计

- 接口概要

  | 接口名称 | 改变渔场接口                              |
  | -------- | ----------------------------------------- |
  | 方法     | POST                                      |
  | URL      | http://[IP]:[Port]/app/v1/player/change-fishing-ground |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |
  | 渔场ID   | ground_id  | 目标渔场的ID                       | integer  | 1001                                 |

- 响应参数

  | 参数名称 | 参数英文名 | 参数描述           | 参数类型 | 参数示例 |
  | -------- | ---------- | ------------------ | -------- | -------- |
  | 渔场ID   | ground_id  | 更新后的当前渔场ID | integer  | 1001     |

#### 3.3.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "ground_id": 1001
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "ground_id": 1001
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Player does not have access to this fishing ground",
        "data": null
    }
    ```

#### 3.3.4 功能逻辑

1. 接收玩家ID（user_id）和目标渔场ID（ground_id）作为输入参数。
2. 根据user_id从users表中查询玩家的accessible_fishing_grounds字段。
3. 检查传入的ground_id是否在accessible_fishing_grounds列表中：
   a. 如果在列表中：
      - 更新users表中对应玩家的current_fishing_ground字段为新的ground_id。
      - 返回成功响应，包含更新后的ground_id。
   b. 如果不在列表中：
      - 返回失败响应，说明玩家没有权限进入该渔场。
4. 如果在更新过程中发生错误，返回相应的错误信息。

#### 3.3.5 注意事项

1. 确保在更新current_fishing_ground字段时使用数据库事务，以保证数据一致性。
2. 考虑添加日志记录，记录玩家的渔场变更，这对于后续的数据分析和问题排查很有帮助。
3. 实现适当的错误处理，例如当数据库查询或更新失败时返回相应的错误信息。
4. 在高并发情况下，需要考虑使用适当的锁机制来避免数据竞争。
5. 可以考虑在更改渔场成功后，触发其他相关的游戏逻辑，如重置某些与渔场相关的状态。
6. 确保接口的安全性，添加适当的身份验证和授权机制。
7. 考虑添加接口限流措施，防止玩家频繁切换渔场对服务器造成压力。

### 3.4 钓鱼次数回复倒计时及钓鱼操作接口

#### 3.4.1 功能说明

该接口用于初始化获取玩家当前的钓鱼次数和下一次恢复时间，以及在前端钓鱼次数和恢复时间变化时更新数据库并返回验证。所有时间均使用UTC时间。

当action_type为1（钓鱼操作）时，需要进行钓鱼会话session验证，并在成功调用后将钓鱼次数扣除状态（fishing_count_deducted）的值设置为True。

钓鱼次数恢复逻辑如下：
- 玩家最多拥有系统配置的最大钓鱼次数
- 每个恢复间隔恢复1次钓鱼机会
- 恢复时间精确到秒
- 只有在钓鱼次数少于最大次数时才会开始恢复计时
- 当钓鱼次数达到最大次数时，停止恢复计时

#### 3.4.2 详细设计

- 接口概要

  | 接口名称 | 钓鱼次数回复倒计时及钓鱼操作接口        |
  | -------- | ----------------------------------------- |
  | 方法     | GET / POST                                |
  | URL      | http://[IP]:[Port]/app/v1/player/status   |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 是否必须 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 是       | 123e4567-e89b-12d3-a456-426614174000 |
  | 操作类型 | action_type | 0: 查询, 1: 钓鱼（次数减一）, 2: 次数加一 | integer  | 是       | 1                                    |
  | 会话ID   | session_id | 钓鱼会话的唯一ID（仅当action_type为1时需要） | string   | 否       | 789abcde-f012-34g5-h678-901234ijklmn |
                         
- 响应参数

  | 参数名称       | 参数英文名      | 参数描述                     | 参数类型 | 参数示例 |
  | -------------- | --------------- | ---------------------------- | -------- | -------- |
  | 钓鱼次数       | fishing_count    | 玩家当前的钓鱼次数           | integer  | 5        |
  | 下次恢复时间   | next_recovery_time    | 下次恢复时间的UTC时间戳（秒） | integer  | 1696358400 |

#### 3.4.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "action_type": 0
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "fishing_count": 5,
            "next_recovery_time": 1696358400
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Failed to retrieve or update player status."
    }
    ```

#### 3.4.4 功能逻辑

1. 接收玩家ID和操作类型（action_type）作为输入参数。
2. 从数据库users表中获取玩家当前的钓鱼次数（fishing_count）和下次恢复时间（next_recovery_time）。
3. 从系统配置表中获取钓鱼次数恢复间隔（fishing_recovery_interval）和最大钓鱼次数（max_fishing_count）。
4. 获取当前UTC时间戳。
5. 根据action_type执行相应操作：
   - 如果action_type为0（查询）：
     a. 如果当前时间大于或等于下次恢复时间：
        - 计算应该恢复的次数：(当前时间 - next_recovery_time) / fishing_recovery_interval + 1，向下取整。
        - 更新钓鱼次数：当前次数 + 恢复次数，但不超过最大次数（max_fishing_count）。
        - 如果更新后的钓鱼次数小于最大次数：
          * 计算新的下次恢复时间：next_recovery_time + (恢复次数 * fishing_recovery_interval)。
        - 否则：
          * 将下次恢复时间设置为null。
     b. 将更新后的钓鱼次数和下次恢复时间保存到数据库。
   - 如果action_type为1（钓鱼，次数减一）：
     a. 验证会话ID（session_id）对应的会话状态（session_status）是否为True，如果不是，返回错误响应。
     b. 检查钓鱼次数扣除状态（fishing_count_deducted）是否为False。如果已经是True，返回错误响应。
     c. 将fishing_count减1。
     d. 如果减1后next_recovery_time为null，设置next_recovery_time为当前时间加上fishing_recovery_interval，否则不更新。
     e. 将钓鱼次数扣除状态（fishing_count_deducted）设置为True。
   - 如果action_type为2（次数加一）：
     a. 如果当前时间大于或等于next_recovery_time：
        - 将fishing_count加1，但不超过max_fishing_count。
        - 更新next_recovery_time为当前的next_recovery_time加上fishing_recovery_interval。
        - 如果更新后的fishing_count等于max_fishing_count，将next_recovery_time设为null。
     b. 如果当前时间小于next_recovery_time：
        - 拒绝更新，返回错误信息。
6. 将更新后的fishing_count和next_recovery_time保存到数据库。
7. 返回更新后的fishing_count和next_recovery_time（UTC时间戳）给前端。

#### 3.4.5 注意事项

1. 确保在数据库中正确存储和更新玩家的钓鱼次数和下次恢复时间信息，使用UTC时间戳。
2. 实现适当的错误处理，例如无效的玩家ID或操作类型等情况。
3. 考虑使用数据库事务来确保数据更新的原子性。
4. 可以考虑添加缓存机制，减少数据库访问频率，提高接口响应速度。
5. 所有时间戳均使用UTC时间，确保在不同时区的一致性。
6. 在实现过程中，应该考虑并发情况。例如，如果多个请求同时到达，应确保钓鱼次数的计算和更新是正确的。
7. 定期检查系统配置表中的值是否有更新，以确保使用最新的配置参数。
8. 前端应确保发送准确的操作类型。建议前端在本地进行类似的计算，以确保与服务端的计算结果一致。
9. 考虑添加日志记录，以便于追踪钓鱼次数的变化和可能的异常情况。
10. 当action_type为1时，确保正确验证会话ID并更新钓鱼次数扣除状态。
11. 考虑添加机制以防止重复扣除钓鱼次数，例如在会话结束时重置钓鱼次数扣除状态。

### 3.5 钓鱼会话初始化接口

#### 3.5.1 功能说明

初始化钓鱼会话，检查玩家是否满足开始钓鱼的条件，并创建一个新的会话。

#### 3.5.2 详细设计

- 接口概要

  | 接口名称 | 钓鱼会话初始化接口                    |
  | -------- | --------------------------------------- |
  | 方法     | POST                                    |
  | URL      | http://[IP]:[Port]/app/v1/fishing/init  |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |

- 响应参数

  | 参数名称   | 参数英文名 | 参数描述         | 参数类型 | 参数示例 |
  | ---------- | ---------- | ---------------- | -------- | -------- |
  | 剩余鱼饵量 | user_baits | 玩家剩余的鱼饵量 | integer  | 95       |
  | 会话ID     | session_id | 钓鱼会话的唯一ID | string   | 789abcde-f012-34g5-h678-901234ijklmn |

#### 3.5.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "user_baits": 95,
            "session_id": "789abcde-f012-34g5-h678-901234ijklmn"
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Insufficient fishing count",
        "data": null
    }
    ```

#### 3.5.4 功能逻辑

1. 接收玩家ID作为输入参数。
2. 从数据库中获取玩家信息，包括当前使用的钓手NFT、鱼竿NFT、钓鱼次数（fishing_count）和鱼饵数量（user_baits）。
3. 从system_configs表中获取每次钓鱼所需的鱼饵数量（fishing_bait_cost）。
4. 进行以下检查：
   a. 检查玩家是否拥有当前使用的钓手NFT和鱼竿NFT。
   b. 检查玩家的fishing_count是否大于0。
   c. 检查玩家的user_baits是否大于等于fishing_bait_cost。
5. 如果以上任何一个检查失败，立即返回失败响应，并提供相应的错误信息。
6. 如果所有检查都通过：
   a. 更新数据库中玩家的user_baits，减去fishing_bait_cost。
   b. 生成一个唯一的会话ID（session_id）。
   c. 在数据库中创建一个新的钓鱼会话记录，包含以下信息：
      - user_id
      - session_id
      - 开始时间
      - 会话状态（session_status）：设置为true
      - 钓鱼次数扣除状态（fishing_count_deducted）：设置为false
   d. 返回成功响应，包含更新后的user_baits值和新生成的session_id。

#### 3.5.5 注意事项

1. 确保在更新鱼饵数量和创建会话记录时使用数据库事务，以保证数据一致性。
2. 实现适当的错误处理，对于每种可能的失败情况都返回明确的错误信息。
3. 考虑添加并发控制机制，防止玩家在短时间内多次启动钓鱼会话。
4. 记录日志，包括钓鱼会话的开始时间、玩家ID等信息，以便后续分析和问题排查。
5. 确保接口的安全性，例如添加适当的身份验证和授权机制。
6. 考虑设置会话的有效期，并在后续接口中验证会话的有效性。

#### 3.5.6 错误码

| 错误码 | 错误信息                           | 描述                       |
|--------|------------------------------------|-----------------------------|
| 1001   | Missing avatar NFT                 | 玩家没有当前使用的钓手NFT   |
| 1002   | Missing fishing rod NFT            | 玩家没有当前使用的鱼竿NFT   |
| 1003   | Insufficient fishing count         | 玩家的钓鱼次数不足          |
| 1004   | Insufficient bait                  | 玩家的鱼饵数量不足          |
| 1005   | Database update failed             | 数据库更新失败              |

### 3.6 鱼饵购买界面状态接口

#### 3.6.1 功能说明

获取鱼饵购买界面的状态信息，包括购买上限和鱼饵单价。

#### 3.6.2 详细设计

- 接口概要

  | 接口名称 | 鱼饵购买界面状态接口                    |
  | -------- | --------------------------------------- |
  | 方法     | GET                                     |
  | URL      | http://[IP]:[Port]/app/v1/bait/buystate |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                                     |
  | -------- | ---------- | ---------------------------------- | -------- | -------------------------------------------- |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000         |

- 响应参数

  | 参数名称 | 参数英文名 | 参数描述           | 参数类型 | 参数示例 |
  | -------- | ---------- | ------------------ | -------- | -------- |
  | 购买上限 | max_buy_bait    | 单次可购买的最大数量 | integer  | 100      |
  | 鱼饵单价 | bait_price | 每个鱼饵的价格     | float    | 10.5     |

#### 3.6.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "max_buy_bait": 100,
            "bait_price": 10.5
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Failed to retrieve bait purchase information."
    }
    ```

### 3.7 购买鱼饵接口

#### 3.7.1 功能说明

玩家购买鱼饵，更新玩家的鱼饵数量和GMC数量。

#### 3.7.2 详细设计

- 接口概要

  | 接口名称 | 购买鱼饵接口                        |
  | -------- | ----------------------------------- |
  | 方法     | POST                                |
  | URL      | http://[IP]:[Port]/app/v1/bait/buy  |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |
  | 购买数量 | buy_amount | 玩家要购买的鱼饵数量               | integer  | 50                                   |

- 响应参数

  | 参数名称           | 参数英文名    | 参数描述                 | 参数类型 | 参数示例 |
  | ------------------ | ------------- | ------------------------ | -------- | -------- |
  | 玩家当前鱼饵数量   | user_baits  | 购买后玩家拥有的鱼饵数量 | integer  | 130      |
  | 玩家当前GMC数量    | user_gmc   | 购买后玩家拥有的GMC数量  | float    | 989.5    |

#### 3.7.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "buy_amount": 50
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "user_baits": 130,
            "user_gmc": 989.5
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Insufficient GMC for purchase."
    }
    ```

#### 3.7.4 功能逻辑

1. 接收玩家ID和购买数量作为输入参数；
2. 从数据库获取玩家当前的GMC数量和鱼饵单价；
3. 计算购买总价（购买数量 * 鱼饵单价）；
4. 如果购买总价大于玩家当前GMC数量，返回失败响应；
5. 如果GMC足够，更新数据库中玩家的鱼饵数量（增加购买数量）和GMC数量（减少购买总价）；
6. 返回更新后的玩家当前鱼饵数量和GMC数量。

### 3.8 QTE初始化/QTE剩余次数和分数接口

#### 3.8.1 功能说明

该接口用于初始化QTE操作或进行QTE操作并获取QTE累计分数和剩余次数。初始化操作会重置QTE次数为当前鱼竿的最大次数，将累计QTE分数清零，并重置所有QTE命中状态为0。每次开始新的钓鱼会话时，应当调用此接口的初始化功能。

#### 3.8.2 详细设计

- 接口概要

  | 接口名称 | QTE初始化/QTE次数和分数接口           |
  | -------- | ------------------------------------- |
  | 方法     | POST                                  |
  | URL      | http://[IP]:[Port]/app/v1/fishing/qte |

- 请求参数

  | 参数名称   | 参数英文名  | 参数描述                           | 参数类型 | 是否必须 | 参数示例                             |
  | ---------- | ----------- | ---------------------------------- | -------- | -------- | ------------------------------------ |
  | 玩家ID     | user_id     | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 是       | 123e4567-e89b-12d3-a456-426614174000 |
  | 操作类型   | action_type | 0: 初始化, 1: QTE操作              | integer  | 是       | 0                                    |
  | QTE颜色    | qte_colour  | QTE操作的颜色（仅当action_type为1时需要） | string   | 否       | "red"                                |

- 响应参数

  | 参数名称     | 参数英文名        | 参数描述                     | 参数类型 | 参数示例 |
  | ------------ | ----------------- | ---------------------------- | -------- | -------- |
  | 剩余QTE次数  | remaining_qte_count | 剩余的QTE次数              | integer  | 3        |
  | 累计QTE分数  | accumulated_qte_score | 当前累计的QTE分数        | integer  | 150      |

#### 3.8.3 消息示例

- 请求消息（初始化）

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "action_type": 0
  }
  ```

- 请求消息（QTE操作）

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "action_type": 1,
      "qte_colour": "red"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "remaining_qte_count": 3,
            "accumulated_qte_score": 150
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "No remaining QTE attempts."
    }
    ```

#### 3.8.4 功能逻辑

1. 接收玩家ID和操作类型作为输入参数。
2. 如果操作类型为0（初始化）：
   a. 从users表中获取玩家当前使用的鱼竿信息（current_rod_nft）。
   b. 根据current_rod_nft中的rodId，从fishing_rod_configs表中获取对应的qte_count。
   c. 更新users表中的以下字段：
      - remaining_qte_count设置为qte_count
      - accumulated_qte_score设置为0
      - qte_hit_status_green设置为0
      - qte_hit_status_red设置为0
      - qte_hit_status_black设置为0
   d. 返回更新后的remaining_qte_count和accumulated_qte_score。
3. 如果操作类型为1（QTE操作）：
   a. 从users表中获取玩家当前的remaining_qte_count和accumulated_qte_score。
   b. 检查remaining_qte_count是否大于0，如果为0则返回失败响应。
   c. 验证qte_colour是否为有效值（red, green, black），如果无效则返回错误响应。
   d. 计算本次QTE得分：
      i. 从users表中获取current_rod_nft、qte_hit_status_green、qte_hit_status_red和qte_hit_status_black。
      ii. 根据current_rod_nft中的rodId，从fishing_rod_configs表中获取green_qte_progress、red_qte_progress、qte_progress_change、consecutive_hit_bonus和qte_count。
      iii. 判断remaining_qte_count是否等于qte_count：
          - 如果相等，accumulated_qte_score += qte_progress_change
          - 如果不相等，accumulated_qte_score保持不变
      iv. 计算连续命中奖励：
          accumulated_qte_score += qte_hit_status_green * consecutive_hit_bonus + qte_hit_status_red * consecutive_hit_bonus
      v. 根据qte_colour更新相应的命中状态：
          - 如果qte_colour为"green"，设置qte_hit_status_green = 1
          - 如果qte_colour为"red"，设置qte_hit_status_red = 1
          - 否则（qte_colour为"black"），设置qte_hit_status_black = 1
      vi. 计算颜色相关的得分：
          accumulated_qte_score += qte_hit_status_green * green_qte_progress + qte_hit_status_red * red_qte_progress
   e. 更新remaining_qte_count（减1）。
   f. 在users表中更新accumulated_qte_score、remaining_qte_count和相应的qte_hit_status字段。
   g. 返回更新后的remaining_qte_count和accumulated_qte_score。

#### 3.8.5 注意事项

1. 服务器需要维护每个玩家当前的剩余QTE次数、累计QTE分数和各颜色QTE的命中状态。
2. 每种鱼竿的QTE总次数、不同颜色的得分规则、进度变化和连续命中奖励需要在fishing_rod_configs表中配置。
3. 确保在玩家更换鱼竿时更新QTE相关信息。
4. 实现适当的错误处理，例如无效的QTE颜色输入。
5. 考虑使用数据库事务来确保数据更新的一致性，特别是在更新多个相关字段时。
6. 可以考虑添加日志记录，以便于追踪QTE操作和可能的异常情况。
7. 在高并发情况下，需要考虑使用适当的锁机制来避免数据竞争。
8. 初始化操作应该是原子的，确保所有相关字段都被正确重置。
9. 在计算QTE得分时，需要注意数值精度和可能的溢出问题。
10. 可以考虑在响应中包含更多信息，如当前的命中状态，以减少客户端的额外请求。
### 3.9 等级经验数据接口

#### 3.9.1 功能说明

该接口用于更新玩家的等级和经验值，并关闭钓鱼会话。在接收到玩家ID和会话ID后，它会验证会话状态，然后查询玩家当前的等级和经验值，计算新增经验后的结果，进行升级操作（如果需要），并最终关闭钓鱼会话。

#### 3.9.2 详细设计

- 接口概要

  | 接口名称 | 等级经验数据接口                        |
  | -------- | --------------------------------------- |
  | 方法     | POST                                    |
  | URL      | http://[IP]:[Port]/app/v1/player/exp    |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |
  | 会话ID   | session_id | 钓鱼会话的唯一ID                   | string   | 789abcde-f012-34g5-h678-901234ijklmn |

- 响应参数

  | 参数名称 | 参数英文名 | 参数描述         | 参数类型 | 参数示例 |
  | -------- | ---------- | ---------------- | -------- | -------- |
  | 玩家等级 | user_level | 更新后的玩家等级 | integer  | 13       |
  | 玩家经验 | user_exp   | 更新后的玩家经验 | integer  | 150      |

#### 3.9.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "session_id": "789abcde-f012-34g5-h678-901234ijklmn"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "user_level": 13,
            "user_exp": 150
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Invalid session or experience already added",
        "data": null
    }
    ```

#### 3.9.4 功能逻辑

1. 接收玩家ID和会话ID作为输入参数。
2. 验证会话状态：
   a. 从fishing_sessions表中查询对应的会话记录。
   b. 检查session_status是否为true（活跃状态）。
   c. 检查fishing_count_deducted是否为true（钓鱼次数已扣除）。
   d. 如果以上任一条件不满足，返回失败响应。
3. 从users表中查询玩家当前的等级（user_level）和经验值（user_exp）。
4. 根据user_level从level_experience表中查询当前等级对应的最大经验值（max_exp）。
5. 从system_configs表中获取每次钓鱼获得的经验值（fishing_exp）。
6. 计算新的经验值：new_exp = user_exp + fishing_exp
7. 判断new_exp的值：
   a. 如果new_exp < max_exp：
      - user_level保持不变
      - user_exp = new_exp
   b. 如果new_exp >= max_exp：
      - user_level += 1
      - user_exp = new_exp - max_exp
8. 将更新后的user_level和user_exp保存到数据库的users表中。
9. 关闭钓鱼会话：
   a. 更新fishing_sessions表中对应的会话记录：
      - 将session_status设置为false。
      - 将fishing_count_deducted设置为false。
      - 设置end_time为当前时间。
10. 返回更新后的user_level和user_exp给前端。

#### 3.9.5 注意事项

1. 确保在更新玩家等级、经验值和会话状态时使用数据库事务，以保证数据一致性。
2. 考虑添加日志记录，记录玩家的等级变化，特别是在升级时。
3. 实现适当的错误处理，例如当数据库查询或更新失败时返回相应的错误信息。
4. 考虑使用缓存机制来存储level_experience表和system_configs表的数据，以减少数据库查询次数，提高接口响应速度。
5. 在实际应用中，可能需要考虑多级升级的情况，即一次可能跨越多个等级。
6. 确保接口的安全性，添加适当的身份验证和授权机制。
7. 考虑在升级时触发其他相关的游戏逻辑，如解锁新的功能或奖励。
8. 在高并发情况下，需要考虑使用适当的锁机制来避免数据竞争。


### 3.10 更换钓手NFT和鱼竿NFT接口

#### 3.10.1 功能说明

该接口用于更换玩家当前使用的钓手NFT或鱼竿NFT。接口会先验证玩家是否拥有要更换的NFT，如果验证通过，则更新玩家当前使用的NFT信息。

#### 3.10.2 详细设计

- 接口概要

  | 接口名称 | 更换钓手NFT和鱼竿NFT接口              |
  | -------- | ------------------------------------- |
  | 方法     | POST                                  |
  | URL      | http://[IP]:[Port]/app/v1/nft/change  |

- 请求参数

  | 参数名称   | 参数英文名  | 参数描述                           | 参数类型 | 是否必须 | 参数示例                             |
  | ---------- | ----------- | ---------------------------------- | -------- | -------- | ------------------------------------ |
  | 玩家ID     | user_id     | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 是       | 123e4567-e89b-12d3-a456-426614174000 |
  | 更换类型   | type        | 更换的NFT类型：avator或rod         | string   | 是       | "avator"                             |
  | NFT Token  | nft_token   | 要更换的NFT的token                 | string   | 是       | "NFT#12345"                          |

- 响应参数

  | 参数名称   | 参数英文名    | 参数描述                     | 参数类型 | 参数示例    |
  | ---------- | ------------- | ---------------------------- | -------- | ----------- |
  | 更换类型   | type          | 更换的NFT类型：avator或rod   | string   | "avator"    |
  | 新NFT Token| new_nft_token | 更换后的NFT token            | string   | "NFT#12345" |

#### 3.10.3 消息示例

- 请求消息（更换钓手NFT）

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "type": "avator",
      "nft_token": "NFT#12345"
  }
  ```

- 请求消息（更换鱼竿NFT）

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "type": "rod",
      "nft_token": "NFT#67890"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "type": "avator",
            "new_nft_token": "NFT#12345"
        }
    }
    ```

  - 失败响应（NFT不存在）

    ```json
    {
        "status": 1,
        "message": "NFT not found",
        "data": {
            "error_code": 2001,
            "error_message": "The specified NFT does not belong to the user"
        }
    }
    ```

  - 失败响应（无效的更换类型）

    ```json
    {
        "status": 1,
        "message": "Invalid type",
        "data": {
            "error_code": 2002,
            "error_message": "Type must be either 'avator' or 'rod'"
        }
    }
    ```

#### 3.10.4 功能逻辑

1. 接收玩家ID、更换类型和NFT Token作为输入参数。
2. 验证更换类型是否为 "avator" 或 "rod"，如果不是，返回无效类型的错误响应。
3. 根据玩家ID和更换类型，从数据库中获取玩家拥有的所有相应类型的NFT列表。
4. 检查要更换的NFT Token是否在玩家拥有的NFT列表中：
   a. 如果不在列表中，返回NFT不存在的错误响应。
   b. 如果在列表中，继续下一步。
5. 更新数据库中玩家当前使用的NFT信息：
   a. 如果type为"avator"，更新玩家当前使用的钓手NFT。
   b. 如果type为"rod"，更新玩家当前使用的鱼竿NFT。
6. 返回成功响应，包含更新后的NFT信息。

#### 3.10.5 注意事项

1. 确保在更换鱼竿NFT时，同步更新与鱼竿相关的其他信息，如QTE总次数等。
2. 实现适当的错误处理，包括但不限于：无效的用户ID、无效的NFT Token格式等。
3. 考虑添加日志记录，以便于追踪NFT更换历史。
4. 在更新NFT信息时，确保使用数据库事务来保证数据一致性。
5. 可以考虑在成功响应中返回更多相关信息，如更换后的NFT属性等，以减少客户端的额外请求。

## 4 获鱼界面

### 4.1 获鱼信息接口

#### 4.1.1 功能说明

在钓鱼成功后，调用此接口获取钓到的鱼的相关信息。

#### 4.1.2 详细设计

- 接口概要

  | 接口名称 | 获鱼信息接口                        |
  | -------- | ----------------------------------- |
  | 方法     | POST                                |
  | URL      | http://[IP]:[Port]/app/v1/fish/info |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |
  | 会话ID   | session_id | 钓鱼会话的唯一ID                   | string   | 789abcde-f012-34g5-h678-901234ijklmn |

- 响应参数

  | 参数名称     | 参数英文名      | 参数描述                   | 参数类型 | 参数示例                        |
  | ------------ | --------------- | -------------------------- | -------- | ------------------------------- |
  | 鱼ID         | fish_id         | 钓到的鱼的唯一标识ID       | string   | "4035"                          |
  | 鱼名字       | fish_name       | 钓到的鱼的名称             | string   | "Blueberry"                     |
  | 鱼图片资源   | fish_picture_res| 钓到的鱼的图片资源路径     | string   | "fish/blueberry.png"            |
  | 稀有度ID     | rarity_id       | 钓到的鱼的稀有度等级       | integer  | 4                               |
  | 渔场ID       | fishing_ground_id| 钓到鱼的渔场ID            | integer  | 1001                            |
  | 渔场名字     | fishing_ground_name| 钓到鱼的渔场名称        | string   | "夏日海滩钓鱼场"                |
  | 鱼价         | price           | 钓到的鱼的价格             | integer  | 2000                            |
  | 每三小时产币 | output          | 钓到的鱼每三小时产生的币量 | integer  | 10                              |
  | 磅数         | weight          | 钓到的鱼的重量（磅）       | float    | 20.15                           |

#### 4.1.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "session_id": "789abcde-f012-34g5-h678-901234ijklmn"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "fish_id": "4035",
            "fish_name": "Blueberry",
            "fish_picture_res": "fish/blueberry.png",
            "rarity_id": 4,
            "fishing_ground_id": 1001,
            "fishing_ground_name": "夏日海滩钓鱼场",
            "price": 2000,
            "output": 10,
            "weight": 20.15
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Invalid session or session expired",
        "data": null
    }
    ```

#### 4.1.4 功能逻辑

1. 接收玩家ID和会话ID作为输入参数。

2. 验证会话ID的有效性：
   a. 在fishing_sessions表中查询对应的会话记录。
   b. 检查session_status是否为true（活跃状态）。
   c. 检查fishing_count_deducted是否为true（钓鱼次数已扣除）。
   d. 如果以上任一条件不满足，返回错误响应。

3. 获取玩家信息和QTE分数：
   a. 在users表中查询玩家记录，获取current_fishing_ground和accumulated_qte_score。

4. 确定鱼的稀有度：
   a. 在rarity_determination表中查询符合条件的记录：
      - fishing_ground_id = current_fishing_ground
      - `qte_min <= accumulated_qte_score <= qte_max`
   b. 从查询结果中获取possible_rarity_ids和appearance_probabilities。
   c. 使用概率算法，根据appearance_probabilities随机选择一个稀有度ID。

5. 选择具体的鱼：
   a. 在fish_configs表中查询符合条件的记录：
      - rarity_id = 选定的稀有度ID
      - fishing_ground_id = current_fishing_ground
   b. 从符合条件的记录中随机选择一条。

6. 生成鱼的详细信息：
   a. 从选定的鱼记录中获取：鱼ID、鱼名字、鱼图片资源、稀有度ID、渔场ID、渔场名字、鱼价和每三小时产币量。
   b. 根据min_weight和max_weight随机生成鱼的重量（磅）。

7. 记录钓鱼结果：
   a. 在fishing_records表中插入新记录，包含步骤6中获得的所有信息和当前时间戳。

8. 返回钓到的鱼的详细信息。

注意：
- 所有数据库操作应在一个事务中完成，以确保数据一致性。
- 实现适当的错误处理机制，对可能出现的异常情况进行处理。
- 考虑使用预编译语句和参数化查询，以提高安全性和性能。
- 在高并发情况下，需要考虑使用适当的锁机制来避免数据竞争。

#### 4.1.5 注意事项

1. 确保在记录钓鱼结果和关闭会话时使用数据库事务，以保证数据一致性。
2. 实现适当的错误处理，例如无效的会话ID、数据库操作失败等情况。
3. 考虑添加日志记录，以便于追踪每次钓鱼的结果和可能的异常情况。
4. 确保接口的安全性，验证用户身份和会话的有效性。
5. 可以考虑在响应中包含一些统计信息，如玩家的总钓鱼次数、当天钓鱼次数等。

## 5 鱼池界面

### 5.1 鱼池状态查询接口

#### 5.1.1 功能说明

该接口用于查询玩家鱼池的当前状态，包括各星级泡泡中的GMC数量、数量上限、各星级鱼的数量等信息。

#### 5.1.2 详细设计

- 接口概要

  | 接口名称 | 鱼池状态查询接口                      |
  | -------- | ------------------------------------- |
  | 方法     | GET                                   |
  | URL      | http://[IP]:[Port]/app/v1/fishpool/status |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |

- 响应参数

  | 参数名称         | 参数英文名       | 参数描述                   | 参数类型 | 参数示例 |
  | ---------------- | ---------------- | -------------------------- | -------- | -------- |
  | 1星泡泡GMC数量   | bubble_1_gmc     | 1星泡泡中的GMC数量         | float    | 100.5    |
  | 1星泡泡GMC上限   | bubble_1_max     | 1星泡泡的GMC数量上限       | float    | 1000.0   |
  | 2星泡泡GMC数量   | bubble_2_gmc     | 2星泡泡中的GMC数量         | float    | 200.5    |
  | 2星泡泡GMC上限   | bubble_2_max     | 2星泡泡的GMC数量上限       | float    | 2000.0   |
  | 3星泡泡GMC数量   | bubble_3_gmc     | 3星泡泡中的GMC数量         | float    | 300.5    |
  | 3星泡泡GMC上限   | bubble_3_max     | 3星泡泡的GMC数量上限       | float    | 3000.0   |
  | 4星泡泡GMC数量   | bubble_4_gmc     | 4星泡泡中的GMC数量         | float    | 400.5    |
  | 4星泡泡GMC上限   | bubble_4_max     | 4星泡泡的GMC数量上限       | float    | 4000.0   |
  | 5星泡泡GMC数量   | bubble_5_gmc     | 5星泡泡中的GMC数量         | float    | 500.5    |
  | 5星泡泡GMC上限   | bubble_5_max     | 5星泡泡的GMC数量上限       | float    | 5000.0   |
  | 6星泡泡GMC数量   | bubble_6_gmc     | 6星泡泡中的GMC数量         | float    | 600.5    |
  | 6星泡泡GMC上限   | bubble_6_max     | 6星泡泡的GMC数量上限       | float    | 6000.0   |
  | 1星鱼数量        | fish_count_1     | 玩家拥有的1星鱼数量        | integer  | 5        |
  | 2星鱼数量        | fish_count_2     | 玩家拥有的2星鱼数量        | integer  | 4        |
  | 3星鱼数量        | fish_count_3     | 玩家拥有的3星鱼数量        | integer  | 3        |
  | 4星鱼数量        | fish_count_4     | 玩家拥有的4星鱼数量        | integer  | 2        |
  | 5星鱼数量        | fish_count_5     | 玩家拥有的5星鱼数量        | integer  | 1        |
  | 6星鱼数量        | fish_count_6     | 玩家拥有的6星鱼数量        | integer  | 0        |
  | 钱袋子GMC数量    | wallet_gmc       | 钱袋子中已收集的GMC数量    | float    | 1000.5   |
  | 鱼池等级         | pool_level       | 当前鱼池等级               | integer  | 3        |
  | 利率             | interest_rate    | 当前鱼池利率               | float    | 0.05     |

#### 5.1.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "bubble_1_gmc": 100.5,
            "bubble_1_max": 1000.0,
            "bubble_2_gmc": 200.5,
            "bubble_2_max": 2000.0,
            "bubble_3_gmc": 300.5,
            "bubble_3_max": 3000.0,
            "bubble_4_gmc": 400.5,
            "bubble_4_max": 4000.0,
            "bubble_5_gmc": 500.5,
            "bubble_5_max": 5000.0,
            "bubble_6_gmc": 600.5,
            "bubble_6_max": 6000.0,
            "fish_count_1": 5,
            "fish_count_2": 4,
            "fish_count_3": 3,
            "fish_count_4": 2,
            "fish_count_5": 1,
            "fish_count_6": 0,
            "wallet_gmc": 1000.5,
            "pool_level": 3,
            "interest_rate": 0.05
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Failed to retrieve fish pool status",
        "data": null
    }
    ```

#### 5.1.4 功能逻辑

1. 接收玩家ID作为输入参数。
2. 从数据库中查询玩家的鱼池状态信息，包括：
   - 各星级泡泡中的GMC数量和上限
   - 各星级鱼的数量
   - 钱袋子中的GMC数量
   - 鱼池等级
   - 当前利率
3. 如果查询成功，返回所有查询到的信息。
4. 如果查询失败，返回错误信息。

#### 5.1.5 注意事项

1. 确保数据库查询的效率，可以考虑使用索引优化查询性能。
2. 实现适当的错误处理，例如无效的玩家ID、数据库查询失败等情况。
3. 考虑添加缓存机制，减少频繁的数据库查询。
4. 确保接口的安全性，验证用户身份。
5. 可以考虑在响应中包含一些额外的统计信息，如总GMC产出等。

### 5.2 GMC领取接口

#### 5.2.1 功能说明

该接口用于玩家从鱼池中领取（claim）GMC。操作包括销毁鱼、减少钱袋子中已收集的GMC数量、增加用户GMC数量。

#### 5.2.2 详细设计

- 接口概要

  | 接口名称 | GMC领取接口                           |
  | -------- | ------------------------------------- |
  | 方法     | POST                                  |
  | URL      | http://[IP]:[Port]/app/v1/fishpool/claim |

- 请求参数

  | 参数名称   | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | ---------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID     | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |
  | 领取数量   | claim_amount | 玩家要领取的GMC数量              | float    | 500.5                                |

- 响应参数

  | 参数名称         | 参数英文名       | 参数描述                   | 参数类型 | 参数示例 |
  | ---------------- | ---------------- | -------------------------- | -------- | -------- |
  | 领取数量         | claimed_amount   | 实际领取的GMC数量          | float    | 500.5    |
  | 剩余钱袋子GMC    | remaining_wallet_gmc | 领取后钱袋子中剩余的GMC数量 | float    | 500.0    |
  | 玩家当前GMC      | user_gmc         | 领取后玩家拥有的GMC数量    | float    | 1500.5   |

#### 5.2.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "claim_amount": 500.5
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "claimed_amount": 500.5,
            "remaining_wallet_gmc": 500.0,
            "user_gmc": 1500.5
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Insufficient GMC in wallet",
        "data": null
    }
    ```

#### 5.2.4 功能逻辑

1. 接收玩家ID和领取数量作为输入参数。
2. 验证玩家钱袋子中的GMC是否足够领取。
3. 如果GMC足够：
   a. 减少钱袋子中的GMC数量。
   b. 增加玩家的GMC数量。
   c. 更新数据库中的相关信息。
4. 如果GMC不足，返回错误信息。
5. 返回实际领取的GMC数量、领取后钱袋子中剩余的GMC数量和玩家当前的GMC数量。

#### 5.2.5 注意事项

1. 使用数据库事务确保GMC转移的原子性。
2. 实现适当的错误处理，例如insufficient funds、数据库操作失败等情况。
3. 考虑添加日志记录，以便于追踪GMC的流动。
4. 确保接口的安全性，验证用户身份和请求的合法性。
5. 考虑添加限制，如每日最大领取次数或最小领取数量。

### 5.3 鱼池升级接口

#### 5.3.1 功能说明

该接口用于升级玩家的鱼池。升级会消耗玩家的GMC，提升鱼池等级，增加鱼数量上限和利率。

#### 5.3.2 详细设计

- 接口概要

  | 接口名称 | 鱼池升级接口                           |
  | -------- | -------------------------------------- |
  | 方法     | POST                                   |
  | URL      | http://[IP]:[Port]/app/v1/fishpool/upgrade |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |

- 响应参数

  | 参数名称         | 参数英文名       | 参数描述                   | 参数类型 | 参数示例 |
  | ---------------- | ---------------- | -------------------------- | -------- | -------- |
  | 新鱼池等级       | new_pool_level   | 升级后的鱼池等级           | integer  | 4        |
  | 新利率           | new_interest_rate| 升级后的利率               | float    | 0.06     |
  | 新鱼数量上限     | new_fish_limit   | 升级后的鱼数量上限         | integer  | 50       |
  | 消耗的GMC        | consumed_gmc     | 升级消耗的GMC数量          | float    | 1000.0   |
  | 玩家剩余GMC      | remaining_gmc    | 升级后玩家剩余的GMC数量    | float    | 500.5    |

#### 5.3.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "new_pool_level": 4,
            "new_interest_rate": 0.06,
            "new_fish_limit": 50,
            "consumed_gmc": 1000.0,
            "remaining_gmc": 500.5
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Insufficient GMC for upgrade",
        "data": null
    }
    ```

#### 5.3.4 功能逻辑

1. 接收玩家ID作为输入参数。
2. 从数据库中获取玩家当前的鱼池等级、GMC数量和鱼池升级配置信息。
3. 检查玩家的GMC是否足够支付升级费用。
4. 如果GMC足够：
   a. 扣除玩家相应的GMC。
   b. 增加鱼池等级。
   c. 更新利率和鱼数量上限。
   d. 更新数据库中的相关信息。
5. 如果GMC不足，返回错误信息。
6. 返回升级后的鱼池等级、新利率、新鱼数量上限、消耗的GMC和玩家剩余的GMC数量。

#### 5.3.5 注意事项

1. 使用数据库事务确保升级操作的原子性。
2. 实现适当的错误处理，例如insufficient funds、数据库操作失败等情况。
3. 考虑添加日志记录，以便于追踪鱼池升级历史。
4. 确保接口的安全性，验证用户身份和请求的合法性。
5. 考虑添加冷却时间或每日升级次数限制，以防止频繁升级。

### 5.4 利息计算接口

#### 5.4.1 功能说明

该接口用于定时计算玩家鱼池中的利息。每天UTC+0时，系统会自动计算并增加鱼池中已收集的GMC数量。

#### 5.4.2 详细设计

- 接口概要

  | 接口名称 | 利息计算接口                           |
  | -------- | -------------------------------------- |
  | 方法     | POST                                   |
  | URL      | http://[IP]:[Port]/app/v1/fishpool/interest |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |

- 响应参数

  | 参数名称         | 参数英文名       | 参数描述                   | 参数类型 | 参数示例 |
  | ---------------- | ---------------- | -------------------------- | -------- | -------- |
  | 利息金额         | interest_amount  | 计算得到的利息金额         | float    | 50.5     |
  | 新的钱袋子GMC    | new_wallet_gmc   | 加上利息后钱袋子中的GMC数量| float    | 1050.5   |

#### 5.4.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "interest_amount": 50.5,
            "new_wallet_gmc": 1050.5
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Failed to calculate interest",
        "data": null
    }
    ```

#### 5.4.4 功能逻辑

1. 接收玩家ID作为输入参数。
2. 从数据库中获取玩家当前的钱袋子GMC数量和利率。
3. 计算利息：利息 = 钱袋子GMC * 利率
4. 更新钱袋子GMC数量：新钱袋子GMC = 原钱袋子GMC + 利息
5. 将新的钱袋子GMC数量更新到数据库。
6. 返回计算得到的利息金额和新的钱袋子GMC数量。

#### 5.4.5 注意事项

1. 这个接口应该被系统定时任务调用，而不是由客户端直接调用。
2. 使用数据库事务确保利息计算和更新操作的原子性。
3. 考虑添加日志记录，以便于追踪每日利息计算情况。
4. 确保接口的安全性，只允许系统内部调用。
5. 考虑添加重复计算检查，防止同一天多次计算利息。
6. 利息计算可能需要考虑精度问题，建议使用适当的数据类型和精度控制。

### 5.5 玩家鱼类状态查询接口

#### 5.5.1 功能说明

该接口用于查询玩家拥有的各星级鱼的数量。

#### 5.5.2 详细设计

- 接口概要

  | 接口名称 | 玩家鱼类状态查询接口                   |
  | -------- | -------------------------------------- |
  | 方法     | GET                                    |
  | URL      | http://[IP]:[Port]/app/v1/player/fish-status |

- 请求参数

  | 参数名称 | 参数英文名 | 参数描述                           | 参数类型 | 参数示例                             |
  | -------- | ---------- | ---------------------------------- | -------- | ------------------------------------ |
  | 玩家ID   | user_id    | 标识游戏玩家的唯一ID，为32位uuid号 | string   | 123e4567-e89b-12d3-a456-426614174000 |

- 响应参数

  | 参数名称   | 参数英文名 | 参数描述           | 参数类型 | 参数示例 |
  | ---------- | ---------- | ------------------ | -------- | -------- |
  | 1星鱼数量  | fish_count_1 | 玩家拥有的1星鱼数量 | integer  | 10       |
  | 2星鱼数量  | fish_count_2 | 玩家拥有的2星鱼数量 | integer  | 8        |
  | 3星鱼数量  | fish_count_3 | 玩家拥有的3星鱼数量 | integer  | 6        |
  | 4星鱼数量  | fish_count_4 | 玩家拥有的4星鱼数量 | integer  | 4        |
  | 5星鱼数量  | fish_count_5 | 玩家拥有的5星鱼数量 | integer  | 2        |
  | 6星鱼数量  | fish_count_6 | 玩家拥有的6星鱼数量 | integer  | 1        |

#### 5.5.3 消息示例

- 请求消息

  ```json
  {
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

- 响应消息

  - 成功响应

    ```json
    {
        "status": 0,
        "message": "success",
        "data": {
            "fish_count_1": 10,
            "fish_count_2": 8,
            "fish_count_3": 6,
            "fish_count_4": 4,
            "fish_count_5": 2,
            "fish_count_6": 1
        }
    }
    ```

  - 失败响应

    ```json
    {
        "status": 1,
        "message": "Failed to retrieve fish status",
        "data": null
    }
    ```

#### 5.5.4 功能逻辑

1. 接收玩家ID作为输入参数。
2. 从数据库中查询玩家拥有的各星级鱼的数量。
3. 返回查询结果，包括每个星级的鱼的数量。

#### 5.5.5 注意事项

1. 确保数据库查询的效率，可以考虑使用索引优化查询性能。
2. 实现适当的错误处理，例如无效的玩家ID、数据库查询失败等情况。
3. 考虑添加缓存机制，减少频繁的数据库查询。
4. 确保接口的安全性，验证用户身份。
5. 可以考虑在响应中包含一些额外的统计信息，如总鱼数量等。


