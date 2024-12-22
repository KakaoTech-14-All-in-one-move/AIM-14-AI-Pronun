# AIM-14-AI-Pronun (Pitching 음성 처리 엔진)

Pronun (움성 처리 서버)는 "Pitching" 플랫폼의 인공지능 모델을 활용하여 음성 분석을 수행하고 발표에 대한 피드백을 제공하는 시스템입니다. **FastAPI**와 **Swagger UI**를 사용하여 음성 처리 서버를 구축하였으며, 이를 **AWS EC2**에 **Docker**로 배포하여 **프론트엔드(FE)** 애플리케이션과 연동합니다. 서버는 음성 업로드를 처리하고, 피드백 데이터를 생성하여 프론트엔드에 제공합니다. 또한, **librosa**, **opeani**, **fuzzywuzzy**를 활용하여 음성 코덱 변환, 음성 길이 계산, 그리고 발음 정확도 분석 등의 기능을 포함하고 있습니다.

---

## 목차

- [사전 요구사항](#사전-요구사항)
  - [Swagger UI 테스트용 요구사항](#swagger-ui-테스트용-요구사항)
  - [배포 (CI/CD)용 요구사항](#배포-cicd용-요구사항)
- [디렉토리 구조](#디렉토리-구조)
- [설치 및 배포](#설치-및-배포)
  - [1. 리포지토리 클론](#1-리포지토리-클론)
  - [2. 환경 변수 설정](#2-환경-변수-설정)
  - [3. Docker 이미지 빌드](#3-docker-이미지-빌드)
  - [4. Docker 컨테이너 실행](#4-docker-컨테이너-실행)
  - [5. 로컬 테스트](#5-로컬-테스트)
    - [5.1 사전 요구사항](#51-사전-요구사항)
    - [5.2 의존성 설치](#52-의존성-설치)
    - [5.3 환경 변수 설정](#53-환경-변수-설정)
    - [5.4 FastAPI 서버 실행](#54-fastapi-서버-실행)
    - [5.5 실행 확인](#55-실행-확인)
  - [6 API 테스트](#6-api-테스트)
- [CORS 설정](#cors-설정)
  - [발생한 이슈](#발생한-이슈)
  - [해결 방법](#해결-방법)
- [음성 처리](#음성-처리)
  - [1. 음성 길이 계산](#1-음성-길이-계산)
  - [2. 코덱 변환 (기본 형식 → MP3)](#2-코덱-변환-기본-형식--mp3)
  - [3. 발음 정확도 분석 (Pronun)](#3-발음-정확도-분석-pronun)
- [음성 처리 오류 처리](#음성-처리-오류-처리)
- [사용법](#사용법)
  - [1. 음성 업로드](#1-음성-업로드)
  - [2. 피드백 조회](#2-피드백-조회)
- [추가 자료](#추가-자료)
- [.dockerignore](#dockerignore)
- [requirements.txt](#requirementstxt)
- [Dockerfile](#dockerfile)

---

## 사전 요구사항

### Swagger UI 테스트용 요구사항

- **FastAPI**: 백엔드 프레임워크.
- **Swagger UI**: API 문서화 및 테스트 도구.
- **librosa**: 오디오 코덱 변환 및 정보 추출 도구.
- **opeani**: 오디오 처리 및 분석 라이브러리.
- **fuzzywuzzy**: 발음 및 음성 분석 라이브러리.
- **requirements.txt**: 라이브러리 설치 파일.

---

### 배포 (CI/CD)용 요구사항

- **프론트엔드 애플리케이션**: 백엔드 서버와 연동하는 클라이언트 애플리케이션.
- **AWS EC2 인스턴스**: FastAPI의 경우 8001번 포트 등 필요한 포트가 허용되도록 보안 그룹 설정.
- **Docker**: EC2 인스턴스에 설치 필요.

---

## 디렉토리 구조

프로젝트의 디렉토리 구조는 다음과 같습니다:

```
.
├── LICENSE
├── README.md
├── Research
├── dockerfile
├── fonts
│   └── NotoSans-VariableFont_wdth,wght.ttf
├── logging_config.json
├── logs
│   ├── README.md
│   ├── access.log
│   ├── app.log
│   └── error.log
├── main.py
├── pronun_model
│   ├── __init__.py
│   ├── config.py
│   ├── context_var.py
│   ├── exceptions.py
│   ├── logging_filter.py
│   ├── middleware.py
│   ├── openai_config.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── delete_files.py
│   │   ├── send_feedback.py
│   │   └── upload_video.py
│   ├── schemas
│   │   ├── __init__.py
│   │   └── feedback.py
│   └── utils
│       ├── __init__.py
│       ├── adjust_audio_length.py
│       ├── analyze_low_accuracy.py
│       ├── analyze_pronunciation_accuracy.py
│       ├── calculate_audio_duration.py
│       ├── calculate_presentation_score.py
│       ├── calculate_speed.py
│       ├── compare_audio_similarity.py
│       ├── convert_to_mp3.py
│       ├── correct_text_with_llm.py
│       ├── count_words.py
│       ├── document_extract
│       │   ├── __init__.py
│       │   ├── docx_text_extraction.py
│       │   ├── hwpx_text_extraction.py
│       │   ├── pdf_text_extraction.py
│       │   ├── rtf_text_extraction.py
│       │   └── txt_text_extraction.py
│       ├── preprocess_text.py
│       ├── stt.py
│       ├── text_cleaning.py
│       ├── text_extraction.py
│       └── tts.py
├── pytest.ini
├── requirements.txt
├── setup.py
├── storage
│   ├── convert_mp3
│   ├── convert_tts
│   ├── input_video
│   └── scripts
├── prompt.txt
├── requirements.txt
├── setup.py
├── storage
│   ├── convert_mp3
│   ├── convert_tts
│   ├── input_video
│   └── scripts
└── tests
    ├── conftest.py
    ├── pronun_model
    │   ├── test_routers
    │   │   ├── test_delete_files.py
    │   │   ├── test_send_feedback.py
    │   │   └── test_upload_video.py
    │   └── test_utils
    │       ├── test_adjust_audio_length.py
    │       ├── test_analyze_low_accuracy.py
    │       ├── test_analyze_pronunciation_accuracy.py
    │       ├── test_calculate_audio_duration.py
    │       ├── test_calculate_presentation_score.py
    │       ├── test_calculate_speed.py
    │       ├── test_compare_audio_similarity.py
    │       ├── test_convert_to_mp3.py
    │       ├── test_correct_text_with_llm.py
    │       ├── test_count_words.py
    │       ├── test_document_extract
    │       │   ├── __pycache__
    │       │   ├── test_docx_text_extraction.py
    │       │   ├── test_hwpx_text_extraction.py
    │       │   ├── test_pdf_text_extraction.py
    │       │   ├── test_rtf_text_extraction.py
    │       │   └── test_txt_text_extraction.py
    │       ├── test_preprocess_text.py
    │       ├── test_stt.py
    │       ├── test_text_cleaning.py
    │       ├── test_text_extraction.py
    │       └── test_tts.py
    └── test_main.py
```

### 주요 디렉토리 및 파일 설명

- **Research/**: 연구 및 테스트용 Jupyter Notebook 파일들이 위치합니다.
  - **model_test/**: 다양한 Pronun 모델 테스트 노트북.
  - **script_extract_text/**: 텍스트 추출을 위한 스크립트 및 노트북.
  
- **fonts/**: 프로젝트에서 사용하는 폰트 파일들.
  
- **logs/**: 애플리케이션 로그 파일들.
  
- **storage/**: 입력 음성 및 변환된 파일들을 저장하는 디렉토리.
  
- **pronun_model/**: 주요 애플리케이션 코드가 위치하는 디렉토리.
  - **routers/**: FastAPI 라우터 모듈.
  - **schemas/**: 데이터 스키마 정의.
  - **utils/**: 유틸리티 함수 모듈.
  
- **main.py**: FastAPI 애플리케이션의 진입점.
  
- **dockerfile**: Docker 이미지 빌드를 위한 설정 파일.
  
- **requirements.txt**: Python 의존성 목록.
  
- **setup.py**: 패키지 설정 파일.
  
- **logging_config.json**: 로깅 설정 파일.

---

# 설치 및 배포 가이드

## 1. 리포지토리 클론

먼저 프로젝트 리포지토리를 클론합니다.

```bash
git clone https://github.com/KakaoTech-14-All-in-one-move/AIM-14-AI-Pronun.git
```

---

## 2. 환경 변수 설정

`.env` 파일을 생성하고 필요한 환경 변수를 설정합니다. 예시:

```bash
OPENAI_API_KEY=your api key
CHUNK_SIZE=60
AVERAGE_WPM=100
ENABLE_PLOTTING=False # 또는 True (활성화 하면 파형 그림 생성)
UPLOAD_DIR=storage/input_video
CONVERT_MP3_DIR=storage/convert_mp3
CONVERT_TTS_DIR=storage/convert_tts
SCRIPTS_DIR=storage/scripts
SENTRY_DSN=your sentry key
TRACE_SAMPLE_RATE=1.0
```

> **참고**: 위에서 설정한 디렉토리(`UPLOAD_DIR`, `CONVERT_MP3_DIR` 등)는 배포 중 자동으로 생성됩니다.

---

## 3. Docker 이미지 빌드

프로젝트의 **Dockerfile**을 확인하고 이미지 빌드를 진행합니다.

### Dockerfile 예시

```dockerfile
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
```

### Docker 이미지 빌드

```bash
docker build -t pronun-audio-processing .
```

---

## 4. Docker 컨테이너 실행

```bash
docker run -d -p 8001:8001 --name pronun-container pronun-audio-processing
```

> **주의**: EC2 또는 다른 서버를 사용하는 경우, 포트 `8001`로의 인바운드 트래픽을 허용해야 합니다.

---

## 5. 로컬 테스트

### 5.1. 사전 요구사항
- Python 3.9 이상
- FFmpeg 설치 (위 설치 단계 참고)
- `requirements.txt` 파일의 의존성 설치

### 5.2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 5.3. 환경 변수 설정

로컬 환경에서 필요한 디렉토리를 설정합니다. `.env` 파일을 만들어 아래 내용을 추가하세요.

```bash
UPLOAD_DIR=storage/input_video
FEEDBACK_DIR=storage/output_feedback_frame
```

설정된 디렉토리는 자동으로 생성됩니다.

### 5.4. FastAPI 서버 실행

FastAPI 서버를 실행합니다. `main.py` 파일이 FastAPI 애플리케이션의 엔트리 포인트라고 가정합니다.

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-config logging_config.json
```

- **--host 0.0.0.0**: 로컬 네트워크에서도 접근 가능
- **--port 8001**: 기본 포트 설정
- **--reload**: 개발 환경에서 코드 변경 시 서버 자동 재시작

### 5.5. 실행 확인

서버가 성공적으로 실행되면 다음과 같은 메시지가 출력됩니다:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using watchgod
INFO:     Started server process [12347]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

로컬 브라우저에서 [http://localhost:8001](http://localhost:8001)에 접속하여 API 문서를 확인할 수 있습니다.

---

이제 설치와 배포가 완료되었습니다. 성공적으로 설정이 완료되었는지 확인하고, 필요한 경우 추가 테스트를 진행하세요.

## 6. API 테스트

서버가 실행 중이면 [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)로 이동하여 Swagger UI에서 API를 테스트할 수 있습니다.

---

## CORS 설정

### 발생한 이슈

FastAPI 서버를 AWS EC2에 Docker로 배포한 후 프론트엔드와 연결할 때 **CORS (Cross-Origin Resource Sharing)** 이슈가 발생할 수 있습니다.

**오류 예시:**

```
CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 해결 방법

FastAPI에서 CORS 이슈를 해결하기 위해 **`CORSMiddleware`**를 사용하여 미들웨어를 설정할 수 있습니다.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 도메인 또는 IP로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- **운영 환경**에서는 보안을 위해 특정 출처만 허용하도록 설정하는 것이 권장됩니다.

---

## 음성 처리

### 1. 음성 길이 계산

음성 파일의 길이를 초 단위로 계산하기 위해 **librosa**와 **soundfile**을 활용합니다.

### 2. 코덱 변환 (기본 형식 → MP3)

기본 형식의 오디오 파일을 MP3로 변환하기 위해 **pydub**를 사용합니다.


### 3. 발음 정확도 분석 (Pronun)

발표자의 발음을 분석하여 피드백을 제공하기 위해 **Pronun** 모듈을 사용합니다.

---

## 음성 처리 오류 처리

다양한 오류 상황을 대비하여 아래와 같은 예외 처리를 추가했습니다:

- **파일 없음**: `HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")`
- **지원되지 않는 형식**: 허용된 파일 형식을 안내하는 응답 반환.
- **FFmpeg 또는 코덱 문제**: `HTTPException(status_code=500, detail="코덱 변환 실패")`
- **발음 정확도 분석 실패**: `HTTPException(status_code=500, detail="발음 정확도 분석 실패")`

---

## 사용법

### 음성 업로드

**엔드포인트:**

```
POST /api/pronun/upload-video-with-script
```

### 피드백 조회

**엔드포인트:**

```
GET /api/pronun/send-feedback/{video_id}
```

---

## 추가 자료

- **FastAPI 문서**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Docker 문서**: [https://docs.docker.com/](https://docs.docker.com/)
- **Openai Audio API 문서**: [https://platform.openai.com/docs/guides/audio/](https://platform.openai.com/docs/guides/audio)
- **FastAPI CORS 미들웨어**: [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)

---

## .dockerignore

```dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.env
.git
.gitignore
*.md
*.ipynb
storage/
logs/
fonts/
htmlcov/
```

- **Python 캐시 파일:** `__pycache__`, `.pyc`, `.pyo`, `.pyd`
- **환경 파일:** `.env`
- **Git 관련 파일:** `.git`, `.gitignore`
- **문서 파일:** `*.md`, `*.ipynb`
- **데이터 및 로그 디렉토리:** `storage/`, `logs/`
- **기타:** `fonts/`, `htmlcov/`

---

## requirements.txt

```plaintext
python-dotenv
pydub
jiwer
fuzzywuzzy[speedup]
openai
librosa
soundfile
scikit-learn
fastapi
uvicorn
olefile
python-docx
PyPDF2
python-multipart
python-json-logger
colorlog
striprtf
sentry-sdk[fastapi]
pytest
pytest-cov
pytest-mock
httpx
```

---

## Dockerfile

- **베이스 이미지 선택**
    - `python:3.12-slim`: 가벼운 Python 3.12 이미지를 사용하여 최종 이미지 크기를 최소화합니다.
- **환경 변수 설정**
    - `PYTHONDONTWRITEBYTECODE=1`: Python이 `.pyc` 파일을 생성하지 않도록 설정.
    - `PYTHONUNBUFFERED=1`: Python 출력이 버퍼링되지 않고 즉시 터미널에 출력되도록 설정.
- **작업 디렉터리 설정**
    - `/app` 디렉터리를 작업 디렉터리로 설정합니다.
- **시스템 종속성 설치**
    - `build-essential`, `libffi-dev`, `libssl-dev`, `ffmpeg`, `libsndfile1` 등을 설치합니다.
    - `ffmpeg`: 오디오 및 비디오 처리에 필요합니다.
    - `libsndfile1`: 오디오 파일 처리를 위한 라이브러리입니다.
- **Python 종속성 설치**
    - `requirements.txt` 파일을 복사한 후, `pip`을 업그레이드하고 필요한 Python 패키지를 설치합니다.
- **프로젝트 파일 복사**
    - 현재 디렉터리의 모든 파일을 컨테이너의 `/app` 디렉터리로 복사합니다.

---
