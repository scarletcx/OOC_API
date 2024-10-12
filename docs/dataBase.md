# 钓鱼佬游戏数据库设计文档 (PostgreSQL版)

## 1. 用户表 (users)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| user_id | UUID | 否 | gen_random_uuid() | 主键，用户唯一标识符 |
| user_level | INTEGER | 否 | 1 | 用户等级 |
| user_exp | INTEGER | 否 | 0 | 用户当前经验值 |
| user_gmc | NUMERIC(20,8) | 否 | 0 | 用户GMC数量 |
| user_baits | INTEGER | 否 | 0 | 用户鱼饵数量 |
| current_avator_nft | JSONB | 是 | NULL | 当前使用的钓手NFT信息 |
| current_rod_nft | JSONB | 是 | NULL | 当前使用的鱼竿NFT信息 |
| owned_avator_nfts | JSONB | 否 | '[]' | 拥有的所有钓手NFT信息列表 |
| owned_rod_nfts | JSONB | 否 | '[]' | 拥有的所有鱼竿NFT信息列表 |
| fishing_count | INTEGER | 否 | 0 | 当前可用钓鱼次数 |
| next_recovery_time | BIGINT | 是 | NULL | 下次钓鱼次数恢复时间（Unix时间戳） |
| accessible_fishing_grounds | INTEGER[] | 是 | NULL | 可进入的渔场ID列表 |
| current_fishing_ground | INTEGER | 是 | NULL | 当前所在渔场ID |
| remaining_qte_count | INTEGER | 否 | 0 | 剩余QTE次数 |
| accumulated_qte_score | INTEGER | 否 | 0 | 累计QTE分数 |
| qte_hit_status_green | BOOLEAN | 否 | FALSE | 绿色QTE命中状态 |
| qte_hit_status_red | BOOLEAN | 否 | FALSE | 红色QTE命中状态 |
| qte_hit_status_black | BOOLEAN | 否 | FALSE | 黑色QTE命中状态 |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

### 字段说明

1. current_avator_nft：JSON格式，存储结构为 `{"tokenId": "NFT#XXXXX", "avatorId": X}`
   - tokenId: 字符串，表示NFT的唯一标识符
   - avatorId: 整数，表示钓手的ID

2. current_rod_nft：JSON格式，存储结构为 `{"tokenId": "NFT#XXXXX", "rodId": X}`
   - tokenId: 字符串，表示NFT的唯一标识符
   - rodId: 整数，表示鱼竿的ID

3. owned_avator_nfts：JSON数组格式，每个元素的结构为 `{"tokenId": "NFT#XXXXX", "avatorId": X}`
   - 存储用户拥有的所有钓手NFT信息
   - 如果用户没有钓手NFT，则为空数组 `[]`

4. owned_rod_nfts：JSON数组格式，每个元素的结构为 `{"tokenId": "NFT#XXXXX", "rodId": X}`
   - 存储用户拥有的所有鱼竿NFT信息
   - 如果用户没有鱼竿NFT，则为空数组 `[]`

5. accessible_fishing_grounds：INTEGER数组类型，允许为空
   - 表示用户可以进入的渔场ID列表
   - 如果为空，表示用户可以进入所有等级小于等于其当前等级的渔场
   - 例如：`[1001, 1002, 1003]` 或 `NULL`

6. qte_hit_status_green：存储最近一次绿色QTE的命中状态
   - 0表示未命中，1表示命中
   - 每次进行绿色QTE操作后更新此字段

7. qte_hit_status_red：存储最近一次红色QTE的命中状态
   - 0表示未命中，1表示命中
   - 每次进行红色QTE操作后更新此字段

8. qte_hit_status_black：存储最近一次黑色QTE的命中状态
   - 0表示未命中，1表示命中
   - 每次进行黑色QTE操作后更新此字段

9. current_fishing_ground：存储用户当前所在的渔场ID
   - 允许为null，表示用户当前不在任何渔场中
   - 当用户进入一个新的渔场时更新此字段
   - 当用户退出渔场时将此字段设置为null

### 注意事项

1. 使用JSON类型存储NFT和渔场信息可以提供灵活性，但在查询和索引时可能会影响性能。根据实际需求，可能需要考虑优化策略。

2. 在应用层面，应确保JSON数据的完整性和有效性。

3. 对于frequently_used_avator_nfts和frequently_used_rod_nfts字段，可以考虑在应用层面实现，而不是在数据库中存储，除非有特定的性能需求。

4. next_recovery_time字段使用BIGINT类型存储Unix时间戳，表示下次钓鱼次数恢复的时间。在应用层面应使用UTC时间进行操作。

5. 可以考虑为user_id, user_level, user_gmc等频繁查询的字段创建索引，以提高查询性能。

6. 根据实际需求，可能需要为某些JSON字段创建函数索引，以优化特定查询的性能。

7. qte_hit_status_green、qte_hit_status_red和qte_hit_status_black字段的更新应与remaining_qte_count和accumulated_qte_score的更新同步进行。

8. 可以考虑为current_fishing_ground字段创建索引，以优化基于当前渔场的查询操作。

9. 在更新current_fishing_ground字段时，应确保该渔场ID存在于accessible_fishing_grounds列表中。

10. 在应用层面，当用户切换渔场时，需要同时更新current_fishing_ground字段和相关的游戏状态（如果有的话）。

11. 当 accessible_fishing_grounds 为 NULL 时，应用程序应该动态计算用户可进入的渔场，基于用户的当前等级和渔场的进入等级要求。

12. next_recovery_time字段存储的是Unix时间戳，在进行时间比较和计算时，需要注意将其转换为适当的时间格式。

## 2. 等级经验表 (level_experience)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| user_level | INTEGER | 否 | - | 主键，等级 |
| max_exp | INTEGER | 否 | - | 升级所需的最大经验值 |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

## 3. 鱼竿配置表 (fishing_rod_configs)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| id | SERIAL | 否 | - | 主键，序号 |
| name_chinese | TEXT | 否 | - | 鱼竿中文名字 |
| name_english | TEXT | 否 | - | 鱼竿英文名字 |
| image | TEXT | 否 | - | 鱼竿形象 |
| quality_name | TEXT | 否 | - | 品质名称 |
| quality | INTEGER | 否 | - | 品质等级 |
| max_supply | INTEGER | 否 | 0 | 最大供应数量 |
| battle_skill_desc_cn | TEXT | 是 | NULL | fishing_battle_skill中文描述 |
| battle_skill_desc_en | TEXT | 是 | NULL | fishing_battle_skill英文描述 |
| qte_count | INTEGER | 否 | 0 | QTE次数 |
| green_qte_progress | INTEGER | 否 | 0 | 绿圈QTE进度 |
| red_qte_progress | INTEGER | 否 | 0 | 红圈QTE进度 |
| qte_skill_desc_cn | TEXT | 是 | NULL | fishing_qte_skill中文描述 |
| qte_skill_desc_en | TEXT | 是 | NULL | fishing_qte_skill英文描述 |
| qte_progress_change | INTEGER | 否 | 0 | QTE进度值增减属性 |
| consecutive_hit_bonus | INTEGER | 否 | 0 | 连续命中QTE进度值增加属性 |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

## 4. 渔场配置表 (fishing_ground_configs)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| id | INTEGER | 否 | - | 主键，渔场ID |
| name_chinese | TEXT | 否 | - | 渔场中文名称 |
| name_english | TEXT | 否 | - | 渔场英文名称 |
| res | TEXT | 否 | - | 图片资源路径 |
| enter_lv | INTEGER | 否 | 1 | 进入所需等级 |
| passcard_appearance_rate | NUMERIC(5,2) | 否 | 0.00 | PassCard出现概率 (%) |
| passcard_blue_rate | NUMERIC(5,2) | 否 | 0.00 | 蓝色PassCard出现概率 (%) |
| passcard_purple_rate | NUMERIC(5,2) | 否 | 0.00 | 紫色PassCard出现概率 (%) |
| passcard_gold_rate | NUMERIC(5,2) | 否 | 0.00 | 金色PassCard出现概率 (%) |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

## 5. 鱼类表 (fishes)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| fish_id | TEXT | 否 | - | 主键，鱼ID |
| fish_name | TEXT | 否 | - | 鱼名称 |
| fish_picture_res | TEXT | 否 | - | 鱼图片资源路径 |
| rarity_id | INTEGER | 否 | - | 稀有度ID |
| fishing_ground_id | INTEGER | 否 | - | 外键，关联fishing_ground_configs表的id |
| fishing_ground_name | TEXT | 否 | - | 渔场名称 |
| price | NUMERIC(20,8) | 否 | 0 | 鱼价 |
| output | NUMERIC(20,8) | 否 | 0 | 每三小时产币量 |
| min_weight | NUMERIC(10,2) | 否 | 0.0 | 最小重量（磅） |
| max_weight | NUMERIC(10,2) | 否 | 0.0 | 最大重量（磅） |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

注意事项：
1. 新增了 fishing_ground_name 字段，类型为 TEXT，不允许为空。
2. fishing_ground_id 仍然保持外键约束，关联到 fishing_ground_configs 表的 id 字段。
3. fishing_ground_name 字段可能会与 fishing_ground_configs 表中的名称字段存在数据冗余，需要注意保持一致性。

示例触发器（用于保持 fishing_ground_name 与 fishing_ground_configs 表一致）：
```sql
CREATE OR REPLACE FUNCTION update_fishing_ground_name()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fishing_ground_name = (SELECT name_chinese FROM fishing_ground_configs WHERE id = NEW.fishing_ground_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fishing_ground_name
BEFORE INSERT OR UPDATE OF fishing_ground_id ON fishes
FOR EACH ROW
EXECUTE FUNCTION update_fishing_ground_name();
```

这个触发器会在插入新记录或更新 fishing_ground_id 时自动更新 fishing_ground_name 字段，确保其与 fishing_ground_configs 表中的名称保持一致。

添加 fishing_ground_name 字段可能会导致数据冗余，但它可以提高查询性能，减少联表查询的需求。在决定是否保留这个字段时，需要权衡数据一致性维护的复杂性和查询性能的提升。

## 6. 钓鱼记录表 (fishing_records)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| record_id | BIGSERIAL | 否 | - | 主键，自增 |
| user_id | UUID | 否 | - | 外键，关联users表 |
| fish_id | TEXT | 否 | - | 外键，关联fishes表 |
| fish_name | TEXT | 否 | - | 钓到的鱼的名称 |
| fish_picture_res | TEXT | 否 | - | 钓到的鱼的图片资源路径 |
| rarity_id | INTEGER | 否 | - | 钓到的鱼的稀有度等级 |
| fishing_ground_id | INTEGER | 否 | - | 外键，关联fishing_ground_configs表 |
| fishing_ground_name | TEXT | 否 | - | 钓到鱼的渔场名称 |
| price | NUMERIC(20,8) | 否 | 0 | 钓到的鱼的价格 |
| output | NUMERIC(20,8) | 否 | 0 | 钓到的鱼每三小时产生的币量 |
| weight | NUMERIC(10,2) | 否 | 0.0 | 钓到的鱼的重量（磅） |
| caught_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 钓到鱼的时间 |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

注意事项：
1. user_id、fish_id、fishing_ground_id 应该建立外键约束，分别关联到相应的表。
2. 可以为 user_id、fish_id、fishing_ground_id 创建索引，以优化查询性能。
3. caught_at 字段用于记录实际钓到鱼的时间，而 created_at 则是记录插入数据库的时间。
4. 考虑添加触发器来自动更新 updated_at 字段。

示例索引：
```sql
CREATE INDEX idx_fishing_records_user_id ON fishing_records(user_id);
CREATE INDEX idx_fishing_records_fish_id ON fishing_records(fish_id);
CREATE INDEX idx_fishing_records_fishing_ground_id ON fishing_records(fishing_ground_id);
```

示例触发器（用于更新 updated_at 字段）：
```sql
CREATE OR REPLACE FUNCTION update_fishing_records_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fishing_records_updated_at
BEFORE UPDATE ON fishing_records
FOR EACH ROW
EXECUTE FUNCTION update_fishing_records_updated_at();
```

## 7. 免费Mint记录表 (free_mint_records)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| user_id | UUID | 否 | - | 主键，外键，关联users表 |
| avator_minted | BOOLEAN | 否 | FALSE | 是否已进行过avator免费mint |
| rod_minted | BOOLEAN | 否 | FALSE | 是否已进行过rod免费mint |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |

## 8. 系统配置表 (system_configs)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| config_key | TEXT | 否 | - | 主键，配置键 |
| config_value | TEXT | 否 | - | 配置值 |
| description | TEXT | 是 | NULL | 配置项描述 |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

示例配置项：
1. fishing_recovery_interval: 钓鱼次数恢复间隔（秒）
2. max_fishing_count: 最大钓鱼次数
3. bait_price: 鱼饵价
4. max_buy_bait: 单次可购买的最大鱼饵数量
5. fishing_bait_cost: 单次钓鱼消耗鱼饵数量
6. fishing_exp: 单次钓鱼增加的经验值

## 9. 钓鱼会话表 (fishing_sessions)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| session_id | UUID | 否 | gen_random_uuid() | 主键，会话唯一标识符 |
| user_id | UUID | 否 | - | 外键，关联users表 |
| start_time | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 会话开始时间 |
| end_time | TIMESTAMP WITH TIME ZONE | 是 | NULL | 会话结束时间 |
| session_status | BOOLEAN | 否 | TRUE | 会话状态（true为活跃，false为已结束） |
| fishing_count_deducted | BOOLEAN | 否 | FALSE | 钓鱼次数是否已扣除 |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

注意事项：
1. 使用UUID作为session_id，可以通过PostgreSQL的gen_random_uuid()函数自动生成。
2. user_id字段应该建立外键约束，关联到users表的user_id字段。
3. session_status字段用于标识会话是否仍然活跃。
4. fishing_count_deducted字段用于标识是否已经扣除了钓鱼次数，防止重复扣除。
5. 可以为user_id和session_status字段创建索引，以优化查询性能。
6. 考虑添加触发器来自动更新updated_at字段。

示例索引：
```sql
CREATE INDEX idx_fishing_sessions_user_id ON fishing_sessions(user_id);
CREATE INDEX idx_fishing_sessions_status ON fishing_sessions(session_status);
```

示例触发器：
```sql
CREATE OR REPLACE FUNCTION update_fishing_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fishing_sessions_updated_at
BEFORE UPDATE ON fishing_sessions
FOR EACH ROW
EXECUTE FUNCTION update_fishing_sessions_updated_at();
```

## 10. 稀有度决定表 (rarity_determination)

| 字段名 | 类型 | 允许空 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| id | SERIAL | 否 | - | 主键，自增ID |
| fishing_ground_id | INTEGER | 否 | - | 外键，关联fishing_ground_configs表的id |
| qte_min | INTEGER | 否 | - | QTE最小值 |
| qte_max | INTEGER | 否 | - | QTE最大值 |
| possible_rarity_ids | INTEGER[] | 否 | - | 可能钓到的鱼的稀有度ID数组 |
| appearance_probabilities | NUMERIC(5,4)[] | 否 | - | 对应的出现概率数组 |
| created_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | 否 | CURRENT_TIMESTAMP | 记录更新时间 |

注意事项：
1. fishing_ground_id 字段应该建立外键约束，关联到 fishing_ground_configs 表的 id 字段。
2. possible_rarity_ids 和 appearance_probabilities 使用数组类型来存储多个值，这两个数组的长度应该始终保持一致。
3. appearance_probabilities 数组中的值应该是百分比，总和应该等于100。
4. 可以为 fishing_ground_id 和 qte_min, qte_max 创建复合索引，以优化查询性能。

示例索引：
```sql
CREATE INDEX idx_rarity_determination_fishing_ground_qte ON rarity_determination(fishing_ground_id, qte_min, qte_max);
```

示例触发器（用于更新 updated_at 字段）：
```sql
CREATE OR REPLACE FUNCTION update_rarity_determination_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_rarity_determination_updated_at
BEFORE UPDATE ON rarity_determination
FOR EACH ROW
EXECUTE FUNCTION update_rarity_determination_updated_at();
```

这个表设计允许你存储图片中显示的所有信息，并且使用了PostgreSQL的数组类型来存储多个稀有度ID和对应的概率。这种设计既保持了数据的完整性，又提供了良好的查询性能。