# 钓鱼佬游戏后端

这是钓鱼佬游戏的后端服务器项目。它使用 Flask 框架和 PostgreSQL 数据库构建。

## 项目设置

### 前提条件

- Python 3.7+
- PostgreSQL

### 安装步骤

1. 克隆仓库：
   ```
   git clone https://github.com/scarletcx/OOC_API.git
   cd OOC_API
   ```

2. 创建并激活虚拟环境：
   ```
   python -m venv venv
   source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

4. 设置环境变量：
   根据环境更新`.env`中的值。

5. 初始化数据库：
   ```
   python init_db.py
   ```

## 运行项目

启动开发服务器：
```
python run.py
```

服务器将在 `http://localhost:5000` 上运行。

## 项目结构

- `app/`: 主应用目录
  - `models.py`: 数据库模型
  - `routes/`: 路由处理
  - `services/`: 业务逻辑
- `config.py`: 配置文件
- `init_db.py`: 数据库初始化脚本
- `run.py`: 应用入口点

## API 文档

API 文档可以在 `docs/OOC_API_9.30.md` 中找到。

## 数据库设计

数据库设计文档可以在 `docs/dataBase.md` 中找到。

## 开发

### 更新依赖

如果添加了新的依赖，请更新 `requirements.txt` 文件：
```
pip freeze > requirements.txt
```

### 运行测试

（如果有测试的话，在这里添加运行测试的说明）

## 贡献

请阅读 CONTRIBUTING.md 了解如何为这个项目做出贡献。

## 许可证

这个项目使用 [MIT 许可证](LICENSE)。