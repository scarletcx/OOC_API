import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app import create_app, db
from app.models import User, LevelExperience, FishingRodConfig, FishingGroundConfig, SystemConfig
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

            # 初始化系统配置
            if SystemConfig.query.count() == 0:
                configs = [
                    SystemConfig(config_key='max_fishing_count', config_value=str(Config.MAX_FISHING_COUNT), description='最大钓鱼次数'),
                    SystemConfig(config_key='fishing_recovery_interval', config_value=str(Config.FISHING_RECOVERY_INTERVAL), description='钓鱼次数恢复间隔（秒）'),
                    SystemConfig(config_key='fishing_exp', config_value=str(Config.FISHING_EXP), description='每次钓鱼获得的经验值'),
                    SystemConfig(config_key='max_buy_bait', config_value=str(Config.MAX_BUY_BAIT), description='单次最大购买鱼饵数量'),
                    SystemConfig(config_key='bait_price', config_value=str(Config.BAIT_PRICE), description='鱼饵单价'),
                    SystemConfig(config_key='fishing_bait_cost', config_value=str(Config.FISHING_BAIT_COST), description='单次钓鱼消耗鱼饵数量')
                ]
                db.session.add_all(configs)
                logger.info("系统配置已初始化")

            # 初始化等级经验表
            if LevelExperience.query.count() == 0:
                levels = [
                    LevelExperience(user_level=1, max_exp=10),
                    LevelExperience(user_level=2, max_exp=15),
                    LevelExperience(user_level=3, max_exp=20),
                    LevelExperience(user_level=4, max_exp=25),
                    LevelExperience(user_level=5, max_exp=30),
                    LevelExperience(user_level=6, max_exp=35),
                    LevelExperience(user_level=7, max_exp=40),
                    LevelExperience(user_level=8, max_exp=45),
                    LevelExperience(user_level=9, max_exp=50),
                    LevelExperience(user_level=10, max_exp=55),
                    LevelExperience(user_level=11, max_exp=60),
                    LevelExperience(user_level=12, max_exp=65),
                    LevelExperience(user_level=13, max_exp=70),
                    LevelExperience(user_level=14, max_exp=75),
                    LevelExperience(user_level=15, max_exp=80),
                    LevelExperience(user_level=16, max_exp=85),
                    LevelExperience(user_level=17, max_exp=90),
                    LevelExperience(user_level=18, max_exp=95),
                    LevelExperience(user_level=19, max_exp=100),
                    LevelExperience(user_level=20, max_exp=105),
                    LevelExperience(user_level=21, max_exp=110),
                    LevelExperience(user_level=22, max_exp=115),
                    LevelExperience(user_level=23, max_exp=120),
                    LevelExperience(user_level=24, max_exp=125),
                    LevelExperience(user_level=25, max_exp=130),
                    LevelExperience(user_level=26, max_exp=135),
                    LevelExperience(user_level=27, max_exp=140),
                    LevelExperience(user_level=28, max_exp=145),
                    LevelExperience(user_level=29, max_exp=150),
                    LevelExperience(user_level=30, max_exp=155),
                    LevelExperience(user_level=31, max_exp=160),
                    LevelExperience(user_level=32, max_exp=165),
                    LevelExperience(user_level=33, max_exp=170),
                    LevelExperience(user_level=34, max_exp=175),
                    LevelExperience(user_level=35, max_exp=180),
                    LevelExperience(user_level=36, max_exp=185),
                    LevelExperience(user_level=37, max_exp=190),
                    LevelExperience(user_level=38, max_exp=195),
                    LevelExperience(user_level=39, max_exp=200),
                    LevelExperience(user_level=40, max_exp=205),
                    LevelExperience(user_level=41, max_exp=210),
                    LevelExperience(user_level=42, max_exp=215),
                    LevelExperience(user_level=43, max_exp=220),
                    LevelExperience(user_level=44, max_exp=225),
                    LevelExperience(user_level=45, max_exp=230),
                    LevelExperience(user_level=46, max_exp=235),
                    LevelExperience(user_level=47, max_exp=240),
                    LevelExperience(user_level=48, max_exp=245),
                    LevelExperience(user_level=49, max_exp=250),
                    LevelExperience(user_level=50, max_exp=255),
                ]
                db.session.add_all(levels)
                logger.info("等级经验表已初始化")

            # 初始化钓鱼场地
            if FishingGroundConfig.query.count() == 0:
                grounds = [
                    FishingGroundConfig(
                        id=1001, 
                        name_chinese='夏日钓鱼场', 
                        name_english='Summer Fishing Spot', 
                        res='Fishing 1', 
                        enter_lv=1,
                        passcard_appearance_rate=0.01,  # 1% PassCard出现概率
                        passcard_blue_rate=0.50,  # 50% 蓝色PassCard概率
                        passcard_purple_rate=0.30,  # 30% 紫色PassCard概率
                        passcard_gold_rate=0.20  # 20% 金色PassCard概率
                    ),
                    FishingGroundConfig(
                        id=1002, 
                        name_chinese='赛博朋克钓鱼场', 
                        name_english='Cyberpunk Fishing Spot', 
                        res='Fishing 2', 
                        enter_lv=10,
                        passcard_appearance_rate=0.02,  # 2% PassCard出现概率
                        passcard_blue_rate=0.50,  # 50% 蓝色PassCard概率
                        passcard_purple_rate=0.30,  # 30% 紫色PassCard概率
                        passcard_gold_rate=0.20  # 20% 金色PassCard概率
                    ),
                    FishingGroundConfig(
                        id=1003, 
                        name_chinese='克苏鲁钓鱼场', 
                        name_english='Cthulhu Fishing Spot', 
                        res='Fishing 3', 
                        enter_lv=30,
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
                        name_chinese='Classic Woodgrain', 
                        name_english='Classic Woodgrain', 
                        image='Classic Woodgrain.png', 
                        quality_name='白', 
                        quality=1,
                        max_supply=8000,
                        battle_skill_desc_cn='普通的钓鱼佬，勤学苦练中',
                        battle_skill_desc_en='An ordinary fisherman, diligently practicing.',
                        qte_count=4,
                        green_qte_progress=20,
                        red_qte_progress=20,
                        qte_skill_desc_cn='平平无奇的普通',
                        qte_skill_desc_en='Plain Fishing Rod',
                        qte_progress_change=0,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=2, 
                        name_chinese='Deep Sea Song', 
                        name_english='Deep Sea Song', 
                        image='Deep Sea Song.png', 
                        quality_name='蓝', 
                        quality=2,
                        max_supply=7000,
                        battle_skill_desc_cn='初阶钓鱼佬才有',
                        battle_skill_desc_en='Initial backpack skill',
                        qte_count=4,
                        green_qte_progress=20,
                        red_qte_progress=20,
                        qte_skill_desc_cn='平平无奇的普通',
                        qte_skill_desc_en='Plain Fishing Rod',
                        qte_progress_change=0,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=3, 
                        name_chinese='Alien White', 
                        name_english='Alien White', 
                        image='Alien White.png', 
                        quality_name='紫', 
                        quality=3,
                        max_supply=6000,
                        battle_skill_desc_cn='高阶钓鱼佬的标配',
                        battle_skill_desc_en='Hot Action Goldfish: Heal and attack based on the number of pet types owned.',
                        qte_count=4,
                        green_qte_progress=30,
                        red_qte_progress=30,
                        qte_skill_desc_cn='qte命中率+15%',
                        qte_skill_desc_en='QTE Accuracy Bonus +15%',
                        qte_progress_change=15,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=4, 
                        name_chinese='Emerald Light', 
                        name_english='Emerald Light', 
                        image='Emerald Light.png', 
                        quality_name='金', 
                        quality=4,
                        max_supply=5000,
                        battle_skill_desc_cn='高阶钓鱼佬的标配',
                        battle_skill_desc_en='Hot Action Goldfish: Heal and attack based on the number of pet types owned.',
                        qte_count=4,
                        green_qte_progress=35,
                        red_qte_progress=35,
                        qte_skill_desc_cn='qte命中率+15%',
                        qte_skill_desc_en='QTE Accuracy Bonus +15%',
                        qte_progress_change=15,
                        consecutive_hit_bonus=0
                    ),
                    FishingRodConfig(
                        id=5, 
                        name_chinese='Rainbow Dance', 
                        name_english='Rainbow Dance', 
                        image='Rainbow Dance.png', 
                        quality_name='彩', 
                        quality=5,
                        max_supply=1000,
                        battle_skill_desc_cn='高阶钓鱼佬的标配，暴击率溢出20%转化为暴击伤害',
                        battle_skill_desc_en='Advanced fisherman\'s standard, 20% crit rate overflow converted to crit damage',
                        qte_count=4,
                        green_qte_progress=60,
                        red_qte_progress=60,
                        qte_skill_desc_cn='qte连续命中进度值+40，暴击伤害+40%',
                        qte_skill_desc_en='QTE Consecutive Hit Progress +40, Critical Damage +40%',
                        qte_progress_change=0,
                        consecutive_hit_bonus=40
                    ),
                    FishingRodConfig(
                        id=6, 
                        name_chinese='Flame Heart', 
                        name_english='Flame Heart', 
                        image='Flame Heart.png', 
                        quality_name='彩', 
                        quality=6,
                        max_supply=500,
                        battle_skill_desc_cn='品质最高的钓鱼佬装备，暴击率100%',
                        battle_skill_desc_en='Master of the roulette wheel, gains 100% free spin per day.',
                        qte_count=4,
                        green_qte_progress=20,
                        red_qte_progress=20,
                        qte_skill_desc_cn='qte连续命中进度值+40',
                        qte_skill_desc_en='QTE Combo Progress +40',
                        qte_progress_change=0,
                        consecutive_hit_bonus=40
                    )
                ]
                db.session.add_all(rods)
                logger.info("鱼竿配置已初始化")

            db.session.commit()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败：{str(e)}")
            db.session.rollback()
        finally:
            db.session.close()

if __name__ == '__main__':
    init_db()