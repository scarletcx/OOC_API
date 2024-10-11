from app import create_app, db
from app.models import User, LevelExperience, FishingRodConfig, FishingGroundConfig, SystemConfig
from config import Config

def init_db():
    app = create_app()
    with app.app_context():
        # 创建表
        db.create_all()

        # 初始化系统配置
        if SystemConfig.query.count() == 0:
            configs = [
                SystemConfig(config_key='max_fishing_count', config_value=str(Config.MAX_FISHING_COUNT), description='最大钓鱼次数'),
                SystemConfig(config_key='fishing_recovery_interval', config_value=str(Config.FISHING_RECOVERY_INTERVAL), description='钓鱼次数恢复间隔（秒）'),
                SystemConfig(config_key='fishing_exp', config_value=str(Config.FISHING_EXP), description='每次钓鱼获得的经验值'),
                SystemConfig(config_key='max_buy_bait', config_value=str(Config.MAX_BUY_BAIT), description='单次最大购买鱼饵数量'),
                SystemConfig(config_key='bait_price', config_value=str(Config.BAIT_PRICE), description='鱼饵单价')
            ]
            db.session.add_all(configs)

        # 初始化等级经验表
        if LevelExperience.query.count() == 0:
            levels = [LevelExperience(user_level=i, max_exp=i*100) for i in range(1, 101)]
            db.session.add_all(levels)

        # 初始化钓鱼场地
        if FishingGroundConfig.query.count() == 0:
            grounds = [
                FishingGroundConfig(id=1001, name_chinese='新手池塘', name_english='Novice Pond', res='novice_pond.png', enter_lv=1),
                FishingGroundConfig(id=1002, name_chinese='中级湖泊', name_english='Intermediate Lake', res='intermediate_lake.png', enter_lv=10),
                FishingGroundConfig(id=1003, name_chinese='高级海洋', name_english='Advanced Ocean', res='advanced_ocean.png', enter_lv=20)
            ]
            db.session.add_all(grounds)

        # 初始化鱼竿配置
        if FishingRodConfig.query.count() == 0:
            rods = [
                FishingRodConfig(id=1, name_chinese='初级鱼竿', name_english='Beginner Rod', image='beginner_rod.png', rarity='Common', qte_count=3),
                FishingRodConfig(id=2, name_chinese='中级鱼竿', name_english='Intermediate Rod', image='intermediate_rod.png', rarity='Rare', qte_count=4),
                FishingRodConfig(id=3, name_chinese='高级鱼竿', name_english='Advanced Rod', image='advanced_rod.png', rarity='Epic', qte_count=5)
            ]
            db.session.add_all(rods)

        db.session.commit()

if __name__ == '__main__':
    init_db()