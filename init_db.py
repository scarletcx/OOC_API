import logging
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app import create_app, db
from app.models import User, LevelExperience, FishingRodConfig, FishingGroundConfig, SystemConfig, RarityDetermination, Fish, PondConfig, Bubble
from config import Config

# 删除这行
# load_dotenv(override=True)

def init_db():
    app = create_app()
    with app.app_context():
        try:
            logger.info("开始初始化数据库")
            # 清空所有表
            db.drop_all()
            logger.info("所有表已删除")
           
            # 创建表
            db.create_all()
            logger.info("所有表已重新创建")
            
            print(f"当前配置：")
            print(f"MAX_FISHING_COUNT: {Config.MAX_FISHING_COUNT}")
            print(f"FISHING_RECOVERY_INTERVAL: {Config.FISHING_RECOVERY_INTERVAL}")
            print(f"FISHING_EXP: {Config.FISHING_EXP}")
            print(f"MAX_BUY_BAIT: {Config.MAX_BUY_BAIT}")
            print(f"BAIT_PRICE: {Config.BAIT_PRICE}")
            print(f"FISHING_BAIT_COST: {Config.FISHING_BAIT_COST}")
            print(f"DATABASE_URL: {Config.SQLALCHEMY_DATABASE_URI}")
            print(f"INITIAL_BAIT_COUNT: {Config.INITIAL_BAIT_COUNT}")
            print(f"INITIAL_FISHING_COUNT: {Config.INITIAL_FISHING_COUNT}")
            print(f"INITIAL_GMC: {Config.INITIAL_GMC}")
            # 初始化系统配置
            if SystemConfig.query.count() == 0:
                configs = [
                    SystemConfig(config_key='initial_fishing_count', config_value=str(Config.INITIAL_FISHING_COUNT), description='初始钓鱼次数'),
                    SystemConfig(config_key='max_fishing_count', config_value=str(Config.MAX_FISHING_COUNT), description='最大钓鱼次数'),
                    SystemConfig(config_key='fishing_recovery_interval', config_value=str(Config.FISHING_RECOVERY_INTERVAL), description='钓鱼次数恢复间隔（秒）'),
                    SystemConfig(config_key='fishing_exp', config_value=str(Config.FISHING_EXP), description='每次钓鱼获得的经验值'),
                    SystemConfig(config_key='initial_bait_count', config_value=str(Config.INITIAL_BAIT_COUNT), description='初始鱼饵数量'),
                    SystemConfig(config_key='max_buy_bait', config_value=str(Config.MAX_BUY_BAIT), description='单次最大购买鱼饵数量'),
                    SystemConfig(config_key='bait_price', config_value=str(Config.BAIT_PRICE), description='鱼饵单价'),
                    SystemConfig(config_key='fishing_bait_cost', config_value=str(Config.FISHING_BAIT_COST), description='单次钓鱼消耗鱼饵数量'),
                    SystemConfig(config_key='initial_gmc', config_value=str(Config.INITIAL_GMC), description='初始GMC数量')
                ]
                db.session.add_all(configs)
                logger.info("系统配置已初始化")

            # 初始化等级经验表
            if LevelExperience.query.count() == 0:
                levels = [
                    LevelExperience(user_level=1, max_exp=20),
                    LevelExperience(user_level=2, max_exp=20),
                    LevelExperience(user_level=3, max_exp=20),
                    LevelExperience(user_level=4, max_exp=20),
                    LevelExperience(user_level=5, max_exp=20),
                    LevelExperience(user_level=6, max_exp=20),
                    LevelExperience(user_level=7, max_exp=20),
                    
                    LevelExperience(user_level=8, max_exp=40),
                    LevelExperience(user_level=9, max_exp=40),
                    LevelExperience(user_level=10, max_exp=40),
                    LevelExperience(user_level=11, max_exp=40),
                    LevelExperience(user_level=12, max_exp=40),
                    LevelExperience(user_level=13, max_exp=40),
                    
                    LevelExperience(user_level=14, max_exp=60),
                    LevelExperience(user_level=15, max_exp=60),
                    LevelExperience(user_level=16, max_exp=60),
                    LevelExperience(user_level=17, max_exp=60),
                    
                    LevelExperience(user_level=18, max_exp=80),
                    LevelExperience(user_level=19, max_exp=80),
                    LevelExperience(user_level=20, max_exp=80),
                    LevelExperience(user_level=21, max_exp=80),
                    
                    LevelExperience(user_level=22, max_exp=100),
                    LevelExperience(user_level=23, max_exp=100),
                    LevelExperience(user_level=24, max_exp=100),
                    LevelExperience(user_level=25, max_exp=100),
                    
                    LevelExperience(user_level=26, max_exp=120),
                    LevelExperience(user_level=27, max_exp=120),
                    LevelExperience(user_level=28, max_exp=120),
                    LevelExperience(user_level=29, max_exp=120),
                    
                    LevelExperience(user_level=30, max_exp=140),
                    LevelExperience(user_level=31, max_exp=140),
                    LevelExperience(user_level=32, max_exp=140),
                    LevelExperience(user_level=33, max_exp=140),
                    
                    LevelExperience(user_level=34, max_exp=160),
                    LevelExperience(user_level=35, max_exp=160),
                    LevelExperience(user_level=36, max_exp=160),
                    
                    LevelExperience(user_level=37, max_exp=180),
                    LevelExperience(user_level=38, max_exp=180),
                    LevelExperience(user_level=39, max_exp=180),
                    
                    LevelExperience(user_level=40, max_exp=200),
                    LevelExperience(user_level=41, max_exp=200),
                    LevelExperience(user_level=42, max_exp=200),
                    
                    LevelExperience(user_level=43, max_exp=220),
                    LevelExperience(user_level=44, max_exp=220),
                    LevelExperience(user_level=45, max_exp=220),
                    
                    LevelExperience(user_level=46, max_exp=240),
                    LevelExperience(user_level=47, max_exp=240),
                    LevelExperience(user_level=48, max_exp=240),
                    
                    LevelExperience(user_level=49, max_exp=280),
                    LevelExperience(user_level=50, max_exp=280),
                    
                    LevelExperience(user_level=51, max_exp=320),
                    LevelExperience(user_level=52, max_exp=320),
                    
                    LevelExperience(user_level=53, max_exp=360),
                    LevelExperience(user_level=54, max_exp=360),
                    
                    LevelExperience(user_level=55, max_exp=400),
                    LevelExperience(user_level=56, max_exp=400),
                    LevelExperience(user_level=57, max_exp=400),
                    LevelExperience(user_level=58, max_exp=400),
                    LevelExperience(user_level=59, max_exp=400),
                ]
                db.session.add_all(levels)
                logger.info("等级经验表已初始化")

            # 初始化钓鱼场地
            if FishingGroundConfig.query.count() == 0:
                grounds = [
                    FishingGroundConfig(
                        id=1001, 
                        name_chinese='星空钓鱼场', 
                        name_english='Stellar Spot', 
                        res='Fishing_1', 
                        enter_lv=1,
                        passcard_appearance_rate=0.01,  # 1% PassCard出现概率
                        passcard_blue_rate=0.50,  # 50% 蓝色PassCard概率
                        passcard_purple_rate=0.30,  # 30% 紫色PassCard概率
                        passcard_gold_rate=0.20  # 20% 金色PassCard概率
                    ),
                    FishingGroundConfig(
                        id=1002, 
                        name_chinese='红日钓鱼场', 
                        name_english='Red Sun Spot', 
                        res='Fishing_2', 
                        enter_lv=12,
                        passcard_appearance_rate=0.02,  # 2% PassCard出现概率
                        passcard_blue_rate=0.50,  # 50% 蓝色PassCard概率
                        passcard_purple_rate=0.30,  # 30% 紫色PassCard概率
                        passcard_gold_rate=0.20  # 20% 金色PassCard概率
                    ),
                    FishingGroundConfig(
                        id=1003, 
                        name_chinese='遗迹钓鱼场', 
                        name_english='Ruins Spot', 
                        res='Fishing_3', 
                        enter_lv=20,
                        passcard_appearance_rate=0.05,  # 5% PassCard出现概率
                        passcard_blue_rate=0.50,  # 50% 蓝色PassCard概率
                        passcard_purple_rate=0.30,  # 30% 紫色PassCard概率
                        passcard_gold_rate=0.20  # 20% 金色PassCard概率
                    )
                ]
                db.session.add_all(grounds)
                logger.info("钓鱼场地配置已初始化")

            # 初始化鱼竿配置
            if FishingRodConfig.query.count() == 0:
                rods = [
                    FishingRodConfig(
                        id=1,
                        name_chinese='木纹经典鱼竿',
                        name_english='Classic Woodgrain',
                        image='Classic Woodgrain.png',
                        quality_name='白',
                        quality=1,
                        max_supply=8000,
                        battle_skill_desc_cn='普通的钓鱼佬，勤学苦练中',
                        battle_skill_desc_en='An ordinary fisherman, diligently practicing.',
                        qte_count=4,
                        green_qte_progress=20,
                        red_qte_progress=40,
                        qte_skill_desc_cn='QTE次数4;内外圈QTE值20,40;连击值0',
                        qte_skill_desc_en='QTE Attempts: 4; Inner and Outer QTE Values: 20, 40; Combo Value: 0',
                        qte_progress_change=0,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=2,
                        name_chinese='深海之歌鱼竿',
                        name_english='Deep Sea Song',
                        image='Deep Sea Song.png',
                        quality_name='绿',
                        quality=2,
                        max_supply=7000,
                        battle_skill_desc_cn='初始背包格子+1',
                        battle_skill_desc_en='Initial Backpack Slots +1',
                        qte_count=4,
                        green_qte_progress=25,
                        red_qte_progress=50,
                        qte_skill_desc_cn='QTE次数4;内外圈QTE值25,50;连击值0',
                        qte_skill_desc_en='QTE Attempts: 4; Inner and Outer QTE Values: 25, 50; Combo Value: 0',
                        qte_progress_change=0,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=3,
                        name_chinese='白银之翼鱼竿',
                        name_english='Silver Wing',
                        image='Silver Wing.png',
                        quality_name='蓝',
                        quality=3,
                        max_supply=6000,
                        battle_skill_desc_cn='宠物冷却降低2%',
                        battle_skill_desc_en='Pet Action Cooldown Reduced by 2%',
                        qte_count=5,
                        green_qte_progress=25,
                        red_qte_progress=50,
                        qte_skill_desc_cn='QTE次数5;内外圈QTE值25,50;连击值0',
                        qte_skill_desc_en='QTE Attempts: 5; Inner and Outer QTE Values: 25, 50; Combo Value: 0',
                        qte_progress_change=0,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=4,
                        name_chinese='翡翠之光鱼竿',
                        name_english='Emerald Light',
                        image='Emerald Light.png',
                        quality_name='紫',
                        quality=4,
                        max_supply=5000,
                        battle_skill_desc_cn='根据拥有宠物类型数量提高全体4%生命值和攻击力',
                        battle_skill_desc_en='Increase all 4% health and attack based on the number of pet types owned.',
                        qte_count=4,
                        green_qte_progress=35,
                        red_qte_progress=70,
                        qte_skill_desc_cn='QTE次数4;内外圈QTE值35,70;连击值0',
                        qte_skill_desc_en='QTE Attempts: 4; Inner and Outer QTE Values: 35, 70; Combo Value: 0',
                        qte_progress_change=0,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=5,
                        name_chinese='彩虹之舞鱼竿',
                        name_english='Rainbow Dance',
                        image='Rainbow Dance.png',
                        quality_name='橙',
                        quality=5,
                        max_supply=4000,
                        battle_skill_desc_cn='每溢出5%暴击率可以转化为5%暴击伤害',
                        battle_skill_desc_en='For every 5% critical rate overflow, you gain 5% critical damage.',
                        qte_count=3,
                        green_qte_progress=55,
                        red_qte_progress=110,
                        qte_skill_desc_cn='QTE次数3;内外圈QTE值55,110;连击值0',
                        qte_skill_desc_en='QTE Attempts: 3; Inner and Outer QTE Values: 55, 110; Combo Value: 0',
                        qte_progress_change=0,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=6,
                        name_chinese='烈焰之心鱼竿',
                        name_english='Flame Heart',
                        image='Flame Heart.png',
                        quality_name='彩',
                        quality=6,
                        max_supply=500,
                        battle_skill_desc_cn='战斗能量恢复速度提高100%',
                        battle_skill_desc_en='Master of the roulette wheel, gains 100% free spins per day.',
                        qte_count=4,
                        green_qte_progress=40,
                        red_qte_progress=80,
                        qte_skill_desc_cn='QTE次数4;内外圈QTE值40,80;连击值30',
                        qte_skill_desc_en='QTE Attempts: 4; Inner and Outer QTE Values: 40, 80; Combo Value: 30',
                        qte_progress_change=0,
                        consecutive_hit_bonus=30
                    )
                ]
                db.session.add_all(rods)
                logger.info("鱼竿配置已初始化")

            # 初始化稀有度决定表
            if RarityDetermination.query.count() == 0:
                rarity_determinations = [
                    RarityDetermination(fishing_ground_id=1001, qte_min=0, qte_max=160, possible_rarity_ids=[1, 2, 3], appearance_probabilities=[0.50, 0.45, 0.05]),
                    RarityDetermination(fishing_ground_id=1001, qte_min=161, qte_max=200, possible_rarity_ids=[1, 2, 3, 4], appearance_probabilities=[0.50, 0.35, 0.10, 0.05]),
                    RarityDetermination(fishing_ground_id=1001, qte_min=201, qte_max=250, possible_rarity_ids=[1, 2, 3, 4], appearance_probabilities=[0.40, 0.35, 0.15, 0.10]),
                    RarityDetermination(fishing_ground_id=1001, qte_min=251, qte_max=280, possible_rarity_ids=[1, 2, 3, 4, 5], appearance_probabilities=[0.40, 0.33, 0.15, 0.10, 0.02]),
                    RarityDetermination(fishing_ground_id=1001, qte_min=281, qte_max=330, possible_rarity_ids=[1, 2, 3, 4, 5], appearance_probabilities=[0.35, 0.31, 0.15, 0.15, 0.04]),
                    RarityDetermination(fishing_ground_id=1001, qte_min=331, qte_max=410, possible_rarity_ids=[1, 2, 3, 4, 5, 6], appearance_probabilities=[0.28, 0.25, 0.15, 0.15, 0.15, 0.02]),
                    
                    RarityDetermination(fishing_ground_id=1002, qte_min=0, qte_max=160, possible_rarity_ids=[1, 2, 3], appearance_probabilities=[0.50, 0.40, 0.10]),
                    RarityDetermination(fishing_ground_id=1002, qte_min=161, qte_max=200, possible_rarity_ids=[1, 2, 3, 4], appearance_probabilities=[0.45, 0.35, 0.10, 0.10]),
                    RarityDetermination(fishing_ground_id=1002, qte_min=201, qte_max=250, possible_rarity_ids=[1, 2, 3, 4], appearance_probabilities=[0.35, 0.35, 0.15, 0.15]),
                    RarityDetermination(fishing_ground_id=1002, qte_min=251, qte_max=280, possible_rarity_ids=[1, 2, 3, 4, 5], appearance_probabilities=[0.40, 0.30, 0.15, 0.10, 0.05]),
                    RarityDetermination(fishing_ground_id=1002, qte_min=281, qte_max=330, possible_rarity_ids=[1, 2, 3, 4, 5], appearance_probabilities=[0.35, 0.25, 0.15, 0.15, 0.10]),
                    RarityDetermination(fishing_ground_id=1002, qte_min=331, qte_max=410, possible_rarity_ids=[1, 2, 3, 4, 5, 6], appearance_probabilities=[0.25, 0.25, 0.15, 0.15, 0.15, 0.05]),
                    
                    RarityDetermination(fishing_ground_id=1003, qte_min=0, qte_max=160, possible_rarity_ids=[1, 2, 3], appearance_probabilities=[0.40, 0.30, 0.20]),
                    RarityDetermination(fishing_ground_id=1003, qte_min=161, qte_max=200, possible_rarity_ids=[1, 2, 3, 4], appearance_probabilities=[0.40, 0.30, 0.10, 0.15]),
                    RarityDetermination(fishing_ground_id=1003, qte_min=201, qte_max=250, possible_rarity_ids=[1, 2, 3, 4], appearance_probabilities=[0.35, 0.30, 0.15, 0.20]),
                    RarityDetermination(fishing_ground_id=1003, qte_min=251, qte_max=280, possible_rarity_ids=[1, 2, 3, 4, 5], appearance_probabilities=[0.35, 0.30, 0.15, 0.10, 0.10]),
                    RarityDetermination(fishing_ground_id=1003, qte_min=281, qte_max=330, possible_rarity_ids=[1, 2, 3, 4, 5], appearance_probabilities=[0.30, 0.30, 0.15, 0.10, 0.15]),
                    RarityDetermination(fishing_ground_id=1003, qte_min=331, qte_max=410, possible_rarity_ids=[1, 2, 3, 4, 5, 6], appearance_probabilities=[0.25, 0.20, 0.15, 0.15, 0.15, 0.10])
                ]
                db.session.add_all(rarity_determinations)
                logger.info("稀有度决定表已初始化")

            # 初始化鱼类表
            if Fish.query.count() == 0:
                fishes = [
                    Fish(fish_id='4001', fish_name='Bronzeblade', fish_picture_res='Bronzeblade', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4002', fish_name='Copperfin', fish_picture_res='Copperfin', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4003', fish_name='Emeraldeye', fish_picture_res='Emeraldeye', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4004', fish_name='Lavendergaze', fish_picture_res='Lavendergaze', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4005', fish_name='Magenta', fish_picture_res='Magenta', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4006', fish_name='Rainbowtail', fish_picture_res='Rainbowtail', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4007', fish_name='Rosegold', fish_picture_res='Rosegold', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4008', fish_name='Shadowfin', fish_picture_res='Shadowfin', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4009', fish_name='Sunsetglow', fish_picture_res='Sunsetglow', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    Fish(fish_id='4010', fish_name='Twilight', fish_picture_res='Twilight', rarity_id=1, price=8, output=1, min_weight=5.01, max_weight=20.01),
                    
                    Fish(fish_id='4011', fish_name='Cherrywave', fish_picture_res='Cherrywave', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4012', fish_name='Citrusfin', fish_picture_res='Citrusfin', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4013', fish_name='Cosmofish', fish_picture_res='Cosmofish', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4014', fish_name='Fireflash', fish_picture_res='Fireflash', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4015', fish_name='Flarefin', fish_picture_res='Flarefin', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4016', fish_name='Galaxyfin', fish_picture_res='Galaxyfin', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4017', fish_name='Lavender', fish_picture_res='Lavender', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4018', fish_name='Lemonwave', fish_picture_res='Lemonwave', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4019', fish_name='Pinkfrost', fish_picture_res='Pinkfrost', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4020', fish_name='Seagrass', fish_picture_res='Seagrass', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4021', fish_name='Starbloom', fish_picture_res='Starbloom', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4022', fish_name='Sunstripe', fish_picture_res='Sunstripe', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    Fish(fish_id='4023', fish_name='Violetwave', fish_picture_res='Violetwave', rarity_id=2, price=16, output=2, min_weight=8.01, max_weight=30.01),
                    
                    Fish(fish_id='4024', fish_name='Amberstripe', fish_picture_res='Amberstripe', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4025', fish_name='Amethyst', fish_picture_res='Amethyst', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4026', fish_name='Goldenrod', fish_picture_res='Goldenrod', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4027', fish_name='Lemonburst', fish_picture_res='Lemonburst', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4028', fish_name='Nebulafish', fish_picture_res='Nebulafish', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4029', fish_name='Pinkwave', fish_picture_res='Pinkwave', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4030', fish_name='Rosetide', fish_picture_res='Rosetide', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4031', fish_name='Solarfin', fish_picture_res='Solarfin', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4032', fish_name='Starlight', fish_picture_res='Starlight', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4033', fish_name='Sunbeam', fish_picture_res='Sunbeam', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    Fish(fish_id='4034', fish_name='Violetfin', fish_picture_res='Violetfin', rarity_id=3, price=32, output=4, min_weight=7.01, max_weight=40.01),
                    
                    Fish(fish_id='4035', fish_name='Blueberry', fish_picture_res='Blueberry', rarity_id=4, price=64, output=8, min_weight=20.01, max_weight=70.01),
                    Fish(fish_id='4036', fish_name='Candyfish', fish_picture_res='Candyfish', rarity_id=4, price=64, output=8, min_weight=20.01, max_weight=70.01),
                    Fish(fish_id='4037', fish_name='Confetti', fish_picture_res='Confetti', rarity_id=4, price=64, output=8, min_weight=20.01, max_weight=70.01),
                    Fish(fish_id='4038', fish_name='Marshmallow', fish_picture_res='Marshmallow', rarity_id=4, price=64, output=8, min_weight=20.01, max_weight=70.01),
                    Fish(fish_id='4039', fish_name='Pastelwave', fish_picture_res='Pastelwave', rarity_id=4, price=64, output=8, min_weight=20.01, max_weight=70.01),
                    Fish(fish_id='4040', fish_name='Purpleswirl', fish_picture_res='Purpleswirl', rarity_id=4, price=64, output=8, min_weight=20.01, max_weight=70.01),
                    Fish(fish_id='4041', fish_name='Tangerine', fish_picture_res='Tangerine', rarity_id=4, price=64, output=8, min_weight=20.01, max_weight=70.01),
                    
                    Fish(fish_id='4042', fish_name='Blushfin', fish_picture_res='Blushfin', rarity_id=5, price=96, output=12, min_weight=30.01, max_weight=90.01),
                    Fish(fish_id='4043', fish_name='Goldenscale', fish_picture_res='Goldenscale', rarity_id=5, price=96, output=12, min_weight=30.01, max_weight=90.01),
                    Fish(fish_id='4044', fish_name='Periwinkle', fish_picture_res='Periwinkle', rarity_id=5, price=96, output=12, min_weight=30.01, max_weight=90.01),
                    
                    Fish(fish_id='4045', fish_name='Aquaedge', fish_picture_res='Aquaedge', rarity_id=6, price=160, output=20, min_weight=50.01, max_weight=99.01),
                ]
                db.session.add_all(fishes)
                logger.info("鱼类表已初始化")
            
            # 初始化测试用户
            if User.query.count() == 0:
                test_users = [
                    User(
                        user_id="0x1945fE87f2Ed52bda68B4bC9D79Af2d9bd544597",
                        fishing_count=Config.MAX_FISHING_COUNT,
                        bubble_gmc={
                                    "gmc_star1": 0,
                                    "gmc_star2": 0,
                                    "gmc_star3": 0,
                                    "gmc_star4": 0,
                                    "gmc_star5": 0,
                                    "gmc_star6": 0
                                    }
                    ),
                    User(
                        user_id="0x7242010401413C20aF4d4Cd34449F6F1F0b81d32",
                        fishing_count=Config.MAX_FISHING_COUNT,
                        bubble_gmc={"gmc_star1": 0,
                                    "gmc_star2": 0,
                                    "gmc_star3": 0,
                                    "gmc_star4": 0,
                                    "gmc_star5": 0,
                                    "gmc_star6": 0
                                    }
                    ),
                    User(
                        user_id="0xE9d0AC3148B37d0841bf5F96bfdc49E87f7e73Ff",
                        fishing_count=Config.MAX_FISHING_COUNT,
                        bubble_gmc={"gmc_star1": 0,
                                    "gmc_star2": 0,
                                    "gmc_star3": 0,
                                    "gmc_star4": 0,
                                    "gmc_star5": 0,
                                    "gmc_star6": 0
                                    }
                    )
                ]
                db.session.add_all(test_users)
                logger.info("测试用户已初始化")

                # 打印测试用户的 user_id
                #for user in test_users:
                 #   logger.info(f"测试用户 ID: {user.user_id}")
           
            # 初始化鱼池配置表
            if PondConfig.query.count() == 0:
                pond_configs = [
                    PondConfig(pond_level=1, upgrade_cost=320, fishs_max=12, interest=0.0100),
                    PondConfig(pond_level=2, upgrade_cost=340, fishs_max=13, interest=0.0120),
                    PondConfig(pond_level=3, upgrade_cost=370, fishs_max=14, interest=0.0140),
                    PondConfig(pond_level=4, upgrade_cost=480, fishs_max=18, interest=0.0160),
                    PondConfig(pond_level=5, upgrade_cost=1070, fishs_max=20, interest=0.0180),
                    PondConfig(pond_level=6, upgrade_cost=1310, fishs_max=22, interest=0.0200),
                    PondConfig(pond_level=7, upgrade_cost=1580, fishs_max=24, interest=0.0220),
                    PondConfig(pond_level=8, upgrade_cost=1710, fishs_max=26, interest=0.0240),
                    PondConfig(pond_level=9, upgrade_cost=1840, fishs_max=28, interest=0.0260),
                    PondConfig(pond_level=10, upgrade_cost=1970, fishs_max=30, interest=0.0280),
                    PondConfig(pond_level=11, upgrade_cost=3160, fishs_max=32, interest=0.0300),
                    PondConfig(pond_level=12, upgrade_cost=3510, fishs_max=34, interest=0.0320),
                    PondConfig(pond_level=13, upgrade_cost=2900, fishs_max=36, interest=0.0340),
                    PondConfig(pond_level=14, upgrade_cost=5100, fishs_max=38, interest=0.0360),
                    PondConfig(pond_level=15, upgrade_cost=5370, fishs_max=40, interest=0.0380),
                    PondConfig(pond_level=16, upgrade_cost=5640, fishs_max=42, interest=0.0400),
                    PondConfig(pond_level=17, upgrade_cost=5910, fishs_max=44, interest=0.0420),
                    PondConfig(pond_level=18, upgrade_cost=6180, fishs_max=46, interest=0.0440),
                    PondConfig(pond_level=19, upgrade_cost=6450, fishs_max=48, interest=0.0460),
                    PondConfig(pond_level=20, upgrade_cost=6720, fishs_max=50, interest=0.0480),
                    PondConfig(pond_level=21, upgrade_cost=6720, fishs_max=52, interest=0.0500),
                    PondConfig(pond_level=22, upgrade_cost=6720, fishs_max=54, interest=0.0520),
                    PondConfig(pond_level=23, upgrade_cost=6720, fishs_max=56, interest=0.0540),
                    PondConfig(pond_level=24, upgrade_cost=6720, fishs_max=58, interest=0.0560),
                    PondConfig(pond_level=25, upgrade_cost=6720, fishs_max=60, interest=0.0580),
                    PondConfig(pond_level=26, upgrade_cost=6720, fishs_max=62, interest=0.0600),
                    PondConfig(pond_level=27, upgrade_cost=6720, fishs_max=64, interest=0.0620),
                    PondConfig(pond_level=28, upgrade_cost=6720, fishs_max=66, interest=0.0640),
                    PondConfig(pond_level=29, upgrade_cost=6720, fishs_max=68, interest=0.0660),
                    PondConfig(pond_level=30, upgrade_cost=6720, fishs_max=70, interest=0.0680),
                ]
                db.session.add_all(pond_configs)
                logger.info("鱼池配置表已初始化")
            
            #初始化bubble表：
            if Bubble.query.count() == 0:
                bubbles = [
                    Bubble(id=1, gmc_max=360),
                    Bubble(id=2, gmc_max=480),
                    Bubble(id=3, gmc_max=960),
                    Bubble(id=4, gmc_max=960),
                    Bubble(id=5, gmc_max=1440),
                    Bubble(id=6, gmc_max=2400),
                ]
                db.session.add_all(bubbles)
                logger.info("bubble数据已初始化")
            
            db.session.commit()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败：{str(e)}")
            db.session.rollback()
        finally:
            db.session.close()

if __name__ == '__main__':
    init_db()

