from app.models import User, db

def get_user_info(user_id):
    user = User.query.get(user_id)
    if user:
        return {
            "user_id": str(user.user_id),
            "user_level": user.user_level,
            "user_exp": user.user_exp,
            "user_gmc": float(user.user_gmc),
            "user_baits": user.user_baits,
            "current_avator_nft": user.current_avator_nft,
            "current_rod_nft": user.current_rod_nft,
            "owned_avator_nfts": user.owned_avator_nfts,
            "owned_rod_nfts": user.owned_rod_nfts,
            # Add other fields as needed
        }
    return None

# Add other database operation functions here...
