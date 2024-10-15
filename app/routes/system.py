from flask import render_template, request, jsonify
from app.routes import bp
from app.services.system_service import get_all_tables, get_table_data, update_table_data, delete_table_data, insert_table_data
import logging
from app import db

@bp.route('/system')
def system_management():
    tables = get_all_tables()
    return render_template('system_management.html', tables=tables)

@bp.route('/api/table_data/<table_name>')
def get_table_data_api(table_name):
    data = get_table_data(table_name)
    return jsonify(data)

@bp.route('/api/update_data/<table_name>', methods=['POST'])
def update_data_api(table_name):
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': '没有接收到数据'}), 400
        
        result = update_table_data(table_name, data)
        if not result['success']:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        logging.exception(f"Unexpected error in update_data_api: {str(e)}")
        return jsonify({'success': False, 'message': f'意外错误: {str(e)}'}), 500

@bp.route('/api/delete_data/<table_name>', methods=['POST'])
def delete_data_api(table_name):
    data = request.json
    result = delete_table_data(table_name, data)
    return jsonify(result)

@bp.route('/api/insert_data/<table_name>', methods=['POST'])
def insert_data_api(table_name):
    data = request.json
    result = insert_table_data(table_name, data)
    return jsonify(result)
