# 빌드 스테이지
FROM python:3.12-slim as builder

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉터리 설정
WORKDIR /app

# Python 종속성 설치
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt -t /app/dependencies

# 런타임 스테이지
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉터리 설정
WORKDIR /app

# 런타임 시스템 종속성 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 설치한 Python 종속성 복사
COPY --from=builder /app/dependencies /usr/local/lib/python3.12/site-packages

# /app/logs 디렉토리 생성
RUN mkdir -p /app/logs

# 프로젝트 파일 복사
COPY . .

# Python bin 디렉토리 $PATH에 추가
ENV PATH="/usr/local/lib/python3.12/site-packages/bin:$PATH"

# PYTHONPATH 설정
ENV PYTHONPATH=/app

# FastAPI가 실행될 포트 개방
EXPOSE 8000

# 애플리케이션 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-config", "logging_config.json"]
