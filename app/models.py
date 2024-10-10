from app import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_level = db.Column(db.Integer, nullable=False, default=1)
    user_exp = db.Column(db.Integer, nullable=False, default=0)
    user_gmc = db.Column(db.Numeric(10, 4), nullable=False, default=0)
    user_baits = db.Column(db.Integer, nullable=False, default=0)
    current_avator_nft = db.Column(JSONB, nullable=True)
    current_rod_nft = db.Column(JSONB, nullable=True)
    owned_avator_nfts = db.Column(JSONB, nullable=False, default=lambda: [])
    owned_rod_nfts = db.Column(JSONB, nullable=False, default=lambda: [])
    fishing_count = db.Column(db.Integer, nullable=False, default=0)
    next_recovery_time = db.Column(db.DateTime(timezone=True), nullable=True)
    accessible_fishing_grounds = db.Column(db.ARRAY(db.Integer), nullable=False, default=lambda: [])
    current_fishing_ground = db.Column(db.Integer, nullable=True)
    remaining_qte_count = db.Column(db.Integer, nullable=False, default=0)
    accumulated_qte_score = db.Column(db.Integer, nullable=False, default=0)
    qte_hit_status_green = db.Column(db.Boolean, nullable=False, default=False)
    qte_hit_status_red = db.Column(db.Boolean, nullable=False, default=False)
    qte_hit_status_black = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# Add other models (LevelExperience, FishingRodConfig, etc.) here...
