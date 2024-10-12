from app import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_level = db.Column(db.Integer, nullable=False, default=1)
    user_exp = db.Column(db.Integer, nullable=False, default=0)
    user_gmc = db.Column(db.Numeric(20, 8), nullable=False, default=0)  # 修改为Numeric
    user_baits = db.Column(db.Integer, nullable=False, default=0)
    current_avator_nft = db.Column(JSONB, nullable=True)
    current_rod_nft = db.Column(JSONB, nullable=True)
    owned_avator_nfts = db.Column(JSONB, nullable=False, default=[])
    owned_rod_nfts = db.Column(JSONB, nullable=False, default=[])
    fishing_count = db.Column(db.Integer, nullable=False, default=0)
    next_recovery_time = db.Column(db.BigInteger, nullable=True)
    accessible_fishing_grounds = db.Column(db.ARRAY(db.Integer), nullable=True)
    current_fishing_ground = db.Column(db.Integer, nullable=True)
    remaining_qte_count = db.Column(db.Integer, nullable=False, default=0)
    accumulated_qte_score = db.Column(db.Integer, nullable=False, default=0)
    qte_hit_status_green = db.Column(db.Boolean, nullable=False, default=False)
    qte_hit_status_red = db.Column(db.Boolean, nullable=False, default=False)
    qte_hit_status_black = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class FishingSession(db.Model):
    __tablename__ = 'fishing_sessions'

    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    end_time = db.Column(db.DateTime(timezone=True), nullable=True)
    session_status = db.Column(db.Boolean, nullable=False, default=True)
    fishing_count_deducted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class LevelExperience(db.Model):
    __tablename__ = 'level_experience'

    user_level = db.Column(db.Integer, primary_key=True)
    max_exp = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class FishingRodConfig(db.Model):
    __tablename__ = 'fishing_rod_configs'

    id = db.Column(db.Integer, primary_key=True)
    name_chinese = db.Column(db.Text, nullable=False)
    name_english = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    quality_name = db.Column(db.Text, nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    max_supply = db.Column(db.Integer, nullable=False, default=0)
    battle_skill_desc_cn = db.Column(db.Text)
    battle_skill_desc_en = db.Column(db.Text)
    qte_count = db.Column(db.Integer, nullable=False, default=0)
    green_qte_progress = db.Column(db.Integer, nullable=False, default=0)
    red_qte_progress = db.Column(db.Integer, nullable=False, default=0)
    qte_skill_desc_cn = db.Column(db.Text)
    qte_skill_desc_en = db.Column(db.Text)
    qte_progress_change = db.Column(db.Integer, nullable=False, default=0)
    consecutive_hit_bonus = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class FishingGroundConfig(db.Model):
    __tablename__ = 'fishing_ground_configs'

    id = db.Column(db.Integer, primary_key=True)
    name_chinese = db.Column(db.Text, nullable=False)
    name_english = db.Column(db.Text, nullable=False)
    res = db.Column(db.Text, nullable=False)
    enter_lv = db.Column(db.Integer, nullable=False, default=1)
    passcard_appearance_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0.00)
    passcard_blue_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0.00)
    passcard_purple_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0.00)
    passcard_gold_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class Fish(db.Model):
    __tablename__ = 'fishes'

    fish_id = db.Column(db.Text, primary_key=True)
    fish_name = db.Column(db.Text, nullable=False)
    fish_picture_res = db.Column(db.Text, nullable=False)
    rarity_id = db.Column(db.Integer, nullable=False)
    fishing_ground_id = db.Column(db.Integer, db.ForeignKey('fishing_ground_configs.id'), nullable=False)
    fishing_ground_name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False, default=0)  # 修改为Numeric
    output = db.Column(db.Numeric(20, 8), nullable=False, default=0)  # 修改为Numeric
    min_weight = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)  # 修改为Numeric
    max_weight = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)  # 修改为Numeric
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class FishingRecord(db.Model):
    __tablename__ = 'fishing_records'

    record_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    fish_id = db.Column(db.Text, db.ForeignKey('fishes.fish_id'), nullable=False)
    fish_name = db.Column(db.Text, nullable=False)
    fish_picture_res = db.Column(db.Text, nullable=False)
    rarity_id = db.Column(db.Integer, nullable=False)
    fishing_ground_id = db.Column(db.Integer, db.ForeignKey('fishing_ground_configs.id'), nullable=False)
    fishing_ground_name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False, default=0)  # 修改为Numeric
    output = db.Column(db.Numeric(20, 8), nullable=False, default=0)  # 修改为Numeric
    weight = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)  # 修改为Numeric
    caught_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class FreeMintRecord(db.Model):
    __tablename__ = 'free_mint_records'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), primary_key=True)
    avator_minted = db.Column(db.Boolean, nullable=False, default=False)
    rod_minted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

class SystemConfig(db.Model):
    __tablename__ = 'system_configs'

    config_key = db.Column(db.Text, primary_key=True)
    config_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

class RarityDetermination(db.Model):
    __tablename__ = 'rarity_determination'

    id = db.Column(db.Integer, primary_key=True)
    fishing_ground_id = db.Column(db.Integer, db.ForeignKey('fishing_ground_configs.id'), nullable=False)
    qte_min = db.Column(db.Integer, nullable=False)
    qte_max = db.Column(db.Integer, nullable=False)
    possible_rarity_ids = db.Column(db.ARRAY(db.Integer), nullable=False)
    appearance_probabilities = db.Column(db.ARRAY(db.Numeric(5, 4)), nullable=False)  # 修改为Numeric
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# Add other models as needed
