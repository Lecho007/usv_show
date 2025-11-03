# 基础镜像
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目
COPY . .

# 容器启动命令
CMD ["python", "app.py"]