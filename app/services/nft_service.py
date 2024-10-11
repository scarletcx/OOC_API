from app.models import User, FreeMintRecord
from app import db
from flask import jsonify

def handle_free_mint(data):
    user_id = data.get('user_id')
    mint_type = data.get('type')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    free_mint_record = FreeMintRecord.query.get(user_id)
    if not free_mint_record:
        free_mint_record = FreeMintRecord(user_id=user_id)
        db.session.add(free_mint_record)

    if mint_type:
        if mint_type == 'avator':
            free_mint_record.avator_minted = True
        elif mint_type == 'rod':
            free_mint_record.rod_minted = True
        else:
            return jsonify({'status': 1, 'message': 'Invalid mint type'}), 400
        
        db.session.commit()
        return jsonify({'status': 0, 'message': 'success'})
    else:
        return jsonify({
            'status': 0,
            'message': 'success',
            'data': {
                'avator_minted': int(free_mint_record.avator_minted),
                'rod_minted': int(free_mint_record.rod_minted)
            }
        })

def change_nft(data):
    user_id = data.get('user_id')
    nft_type = data.get('type')
    nft_token = data.get('nft_token')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 1, 'message': 'User not found'}), 404

    if nft_type not in ['avator', 'rod']:
        return jsonify({'status': 1, 'message': 'Invalid type', 'data': {'error_code': 2002, 'error_message': "Type must be either 'avator' or 'rod'"}}), 400

    nft_list = user.owned_avator_nfts if nft_type == 'avator' else user.owned_rod_nfts
    nft = next((item for item in nft_list if item['tokenId'] == nft_token), None)

    if not nft:
        return jsonify({'status': 1, 'message': 'NFT not found', 'data': {'error_code': 2001, 'error_message': 'The specified NFT does not belong to the user'}}), 404

    if nft_type == 'avator':
        user.current_avator_nft = nft
    else:
        user.current_rod_nft = nft

    db.session.commit()

    return jsonify({
        'status': 0,
        'message': 'success',
        'data': {
            'type': nft_type,
            'new_nft_token': nft_token
        }
    })