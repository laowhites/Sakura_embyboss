# 使用支持 ARM64 的 Python 镜像
FROM python:3.10.11-alpine3.18 AS builder

WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf $(TZdata::zoneinfo/$TZ) /etc/localtime && echo $TZ > /etc/timezone

# 设置环境变量
ENV DOCKER_MODE=1

# 安装必要的软件包
COPY requirements.txt requirements.txt
RUN apk add --no-cache --update \
    build-base \
    libffi-dev \
    mysql-client \
    mariadb-connector-c \
    tzdata \
    && pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY bot ./bot
RUN mkdir ./log
COPY *.py ./

# 设置入口点
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]