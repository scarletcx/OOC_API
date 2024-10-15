from app import db
from sqlalchemy import inspect, text, JSON, ARRAY
from app.models import *
import json
import logging
from datetime import datetime
from uuid import UUID

def get_all_tables():
    inspector = inspect(db.engine)
    return inspector.get_table_names()

def get_table_data(table_name):
    table = db.metadata.tables[table_name]
    columns = [column.name for column in table.columns]
    column_types = [str(column.type) for column in table.columns]
    
    query = text(f"SELECT * FROM {table_name}")
    result = db.session.execute(query)
    data = []
    for row in result:
        formatted_row = {}
        for col, value in zip(columns, row):
            formatted_row[col] = format_value_for_json(value)
        data.append(formatted_row)
    
    return {
        'columns': columns,
        'column_types': column_types,
        'data': data
    }

def format_value_for_json(value):
    if isinstance(value, (datetime, UUID)):
        return str(value)
    elif isinstance(value, (list, dict)):
        return json.dumps(value)
    return value

def parse_value_from_json(value, column_type):
    if value is None:
        return None
    if isinstance(column_type, (ARRAY, JSON)):
        return json.loads(value) if isinstance(value, str) else value
    elif isinstance(column_type, db.DateTime):
        return datetime.fromisoformat(value) if value else None
    elif isinstance(column_type, db.Boolean):
        return value if isinstance(value, bool) else value.lower() in ('true', '1', 'yes', 'on')
    elif isinstance(column_type, db.Integer):
        return int(value)
    elif isinstance(column_type, (db.Float, db.Numeric)):
        return float(value)
    elif isinstance(column_type, db.UUID):
        return UUID(value) if value else None
    return value

def update_table_data(table_name, data):
    table = db.metadata.tables[table_name]
    primary_key = table.primary_key.columns.keys()[0]
    
    if primary_key not in data:
        return {'success': False, 'message': f'缺少主键 {primary_key}'}
    
    update_stmt = f"UPDATE {table_name} SET "
    update_parts = []
    params = {}
    
    for key, value in data.items():
        if key != primary_key and key in table.columns:
            column = table.columns[key]
            try:
                params[key] = parse_value_from_json(value, column.type)
                update_parts.append(f"{key} = :{key}")
            except Exception as e:
                logging.error(f"Error processing column {key}: {str(e)}")
                return {'success': False, 'message': f'处理列 {key} 时出错: {str(e)}'}
    
    if not update_parts:
        return {'success': False, 'message': '没有需要更新的数据'}
    
    update_stmt += ", ".join(update_parts)
    update_stmt += f" WHERE {primary_key} = :{primary_key}"
    params[primary_key] = parse_value_from_json(data[primary_key], table.columns[primary_key].type)
    
    try:
        db.session.execute(text(update_stmt), params)
        db.session.commit()
        
        # 获取更新后的数据
        updated_data = db.session.execute(text(f"SELECT * FROM {table_name} WHERE {primary_key} = :pk"), {'pk': params[primary_key]}).fetchone()
        updated_dict = {col: format_value_for_json(val) for col, val in zip(table.columns.keys(), updated_data)}
        
        return {'success': True, 'message': '数据更新成功', 'updatedData': updated_dict}
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating data: {str(e)}")
        return {'success': False, 'message': f'更新失败: {str(e)}'}

def delete_table_data(table_name, data):
    table = db.metadata.tables[table_name]
    primary_key = table.primary_key.columns.keys()[0]
    
    delete_stmt = f"DELETE FROM {table_name} WHERE {primary_key} = :{primary_key}"
    
    try:
        db.session.execute(text(delete_stmt), {primary_key: data[primary_key]})
        db.session.commit()
        return {'success': True, 'message': '数据删除成功'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'删除失败: {str(e)}'}

def insert_table_data(table_name, data):
    table = db.metadata.tables[table_name]
    
    insert_stmt = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join([f':{key}' for key in data.keys()])})"
    
    try:
        db.session.execute(text(insert_stmt), data)
        db.session.commit()
        return {'success': True, 'message': '数据插入成功'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'插入失败: {str(e)}'}
