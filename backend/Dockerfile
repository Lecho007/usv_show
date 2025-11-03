# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 拷贝 requirements.txt
COPY requirements.txt ./

# 安装依赖，包括 cryptography
RUN pip install --no-cache-dir -r requirements.txt cryptography pymysql -i https://mirrors.aliyun.com/pypi/simple/


# 拷贝代码
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]