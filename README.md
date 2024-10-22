# 钓鱼佬游戏后端

这是钓鱼佬游戏的后端服务器项目。它使用 Flask 框架和 PostgreSQL 数据库构建。

## 项目设置

### 前提条件

- Python 3.9+
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

   如果依赖文件有更新，请执行以下命令更新依赖：
   ```
   pip install --upgrade -r requirements.txt
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
  - `templates/`: HTML 模板
- `config.py`: 配置文件
- `init_db.py`: 数据库初始化脚本
- `run.py`: 应用入口点

## 前端页面

项目现在包含一个系统管理前端页面，可以通过以下URL访问：

- 系统管理页面: `http://localhost:5000/system`

这个页面提供了以下功能：
- 显示所有数据库表的列表
- 查看选定表的数据
- 删除记录（其他功能如添加和编辑记录尚未实现）

## API 文档

API 文档可以在 `docs/OOC_API_9.30.md` 中找到。

## 数据库设计

数据库设计文档可以在 `docs/dataBase.md` 中找到。

## 开发

### 更新依赖

如果添加了新的依赖，请更新 `requirements.txt` 文件：

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

## docker部署

### 1.更新系统包
```
sudo apt update
sudo apt upgrade -y
```

### 2.安装必要的依赖
```
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
```

### 3.安装 Docker
```
# 添加 Docker 的官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 添加 Docker 仓库
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# 更新包索引
sudo apt update

# 安装 Docker
sudo apt install -y docker-ce

# 启动 Docker 服务
sudo systemctl start docker

# 设置 Docker 开机自启
sudo systemctl enable docker

# 将当前用户添加到 docker 组（这样就不用每次都 sudo 了）
sudo usermod -aG docker ${USER}
```

### 4.安装 Docker Compose
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 5.安装和配置 PostgreSQL

```
# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 启动 PostgreSQL 服务
sudo systemctl start postgresql

# 设置 PostgreSQL 开机自启
sudo systemctl enable postgresql

# 切换到 postgres 用户
sudo -i -u postgres

# 创建新的数据库用户（替换 your_username 为您想要的用户名）
createuser --interactive --pwprompt your_username

# 创建新的数据库（替换 your_database 为您想要的数据库名）
createdb your_database

# 退出 postgres 用户
exit

# 配置 PostgreSQL 允许远程连接（可选，如果您需要从其他机器连接）
sudo nano /etc/postgresql/12/main/postgresql.conf
# 将 listen_addresses 行改为：listen_addresses = '*'

sudo nano /etc/postgresql/12/main/pg_hba.conf
# 添加以下行：host all all 0.0.0.0/0 md5  # 允许所有来源的连接，使用 md5 加密
#其他机器的连接方法
# 1. 在服务器上创建一个用户，并授予连接权限
# 2. 在客户端机器上使用该用户进行连接

# 重启 PostgreSQL 服务
sudo systemctl restart postgresql
```

### 6.在服务器上创建项目目录
```
mkdir -p ~/ooc_api
cd ~/ooc_api
```

### 7.将项目文件传输到服务器

### 8.在服务器上构建和启动 Docker 容器
```
cd ~/ooc_api
docker-compose up -d
```

### 9.初始化数据库
首次运行时，你需要初始化数据库。进入 web 容器并运行初始化脚本：
```

```

### 10.验证部署访问接口
现在你的应用应该在服务器的 5000 端口上运行。你可以通过浏览器访问 http://your_server_ip:5000 来查看你的应用。


替换上述值为您实际的数据库配置。

## 贡献

请阅读 CONTRIBUTING.md 了解如何为这个项目做出贡献。

## 许可证

这个项目使用 [MIT 许可证](LICENSE)。

## Docker 部署更新代码

当您需要更新已部署的 Docker 环境中的代码时，请按照以下步骤操作：

### 1. 拉取最新代码

首先，确保您的本地代码库是最新的：

```
git pull origin main
```

### 2. 重新构建和启动 Docker 容器

```
cd ~/ooc_api
docker-compose up -d
```

### 3. 重新初始化数据库

```
docker-compose exec web python init_db.py
```
