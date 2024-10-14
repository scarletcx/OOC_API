# Add any system-related services here if needed
from app import db
from sqlalchemy import inspect
from flask import jsonify

def get_table_info(table_name):
    """获取指定表的所有数据，包括字段、字段类型和每条记录"""
    try:
        # 获取表的模型类
        table_class = db.Model._decl_class_registry.get(table_name)
        if table_class is None:
            return jsonify({'status': 1, 'message': f'Table {table_name} not found'}), 404

        # 获取表的字段信息
        inspector = inspect(table_class)
        columns = [{
            'name': column.key,
            'type': str(column.type)
        } for column in inspector.columns]

        # 获取表的所有记录
        records = table_class.query.all()
        data = [{column['name']: getattr(record, column['name']) for column in columns} for record in records]

        return jsonify({
            'status': 0,
            'message': 'success',
            'data': {
                'columns': columns,
                'records': data
            }
        })
    except Exception as e:
        return jsonify({'status': 1, 'message': str(e)}), 500

def create_record(table_name, data):
    """在指定表中创建新记录"""
    try:
        table_class = db.Model._decl_class_registry.get(table_name)
        if table_class is None:
            return jsonify({'status': 1, 'message': f'Table {table_name} not found'}), 404

        new_record = table_class(**data)
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'status': 0, 'message': 'Record created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 1, 'message': str(e)}), 500

def update_record(table_name, record_id, data):
    """更新指定表中的记录"""
    try:
        table_class = db.Model._decl_class_registry.get(table_name)
        if table_class is None:
            return jsonify({'status': 1, 'message': f'Table {table_name} not found'}), 404

        record = table_class.query.get(record_id)
        if record is None:
            return jsonify({'status': 1, 'message': 'Record not found'}), 404

        for key, value in data.items():
            setattr(record, key, value)
        db.session.commit()
        return jsonify({'status': 0, 'message': 'Record updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 1, 'message': str(e)}), 500

def delete_record(table_name, record_id):
    """删除指定表中的记录"""
    try:
        table_class = db.Model._decl_class_registry.get(table_name)
        if table_class is None:
            return jsonify({'status': 1, 'message': f'Table {table_name} not found'}), 404

        record = table_class.query.get(record_id)
        if record is None:
            return jsonify({'status': 1, 'message': 'Record not found'}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({'status': 0, 'message': 'Record deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 1, 'message': str(e)}), 500
