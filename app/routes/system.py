from app.routes import bp
from flask import jsonify, request
from app.services import system_service

# Add any system-related routes here if needed

@bp.route('/system/table/<table_name>', methods=['GET'])
def get_table_data(table_name):
    return system_service.get_table_info(table_name)

@bp.route('/system/table/<table_name>', methods=['POST'])
def create_table_record(table_name):
    data = request.json
    return system_service.create_record(table_name, data)

@bp.route('/system/table/<table_name>/<record_id>', methods=['PUT'])
def update_table_record(table_name, record_id):
    data = request.json
    return system_service.update_record(table_name, record_id, data)

@bp.route('/system/table/<table_name>/<record_id>', methods=['DELETE'])
def delete_table_record(table_name, record_id):
    return system_service.delete_record(table_name, record_id)
