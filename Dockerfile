# 使用官方Python运行时作为父镜像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口5000
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# 运行应用
CMD ["flask", "run"]