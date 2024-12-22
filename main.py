# main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Response

from pronun_model.routers.upload_video import router as upload_video_router
from pronun_model.routers.send_feedback import router as send_feedback_router
from pronun_model.routers.delete_files import router as delete_files_router 
from pronun_model.config import UPLOAD_DIR, CONVERT_MP3_DIR, CONVERT_TTS_DIR, SCRIPTS_DIR
from pronun_model.exceptions import DocumentProcessingError, AudioProcessingError, AudioImportingError

from pathlib import Path
from dotenv import load_dotenv 
import json
import uvicorn
import logging
import logging.config
import uuid
import traceback
import os
import sentry_sdk

# Sentry Logging Integration
from sentry_sdk.integrations.logging import LoggingIntegration

# Context variables import
from pronun_model.context_var import request_id_ctx_var

# Middleware import
from pronun_model.middleware import RequestIDMiddleware

# 환경 변수 로드
load_dotenv()

# 환경 변수 가져오기
SENTRY_DSN = os.getenv("SENTRY_DSN")
TRACE_SAMPLE_RATE = float(os.getenv("TRACE_SAMPLE_RATE", 1.0))  # 기본값 1.0

# Sentry 로깅 통합 설정
sentry_logging = LoggingIntegration(
    level=logging.INFO,          # Sentry가 기록할 최소 로깅 레벨 (Breadcrumbs)
    event_level=logging.ERROR    # Sentry 이벤트로 기록할 최소 로깅 레벨
)

# Sentry 초기화
sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=TRACE_SAMPLE_RATE,
    integrations=[sentry_logging],
    _experiments={
        "continuous_profiling_auto_start": True,
    },
)

app = FastAPI()

# JSON 기반 로깅 설정 적용
logging_config_path = Path(__file__).resolve().parent / "logging_config.json"  # 프로젝트 루트에 위치한 파일 경로
with open(logging_config_path, "r") as f:
    logging_config = json.load(f)

# Sentry 핸들러 추가 대신 LoggingIntegration 사용
# 기존에 Sentry 핸들러가 있다면 제거
if "sentry" in logging_config["handlers"]:
    del logging_config["handlers"]["sentry"]
    for logger in logging_config["loggers"].values():
        if "sentry" in logger.get("handlers", []):
            logger["handlers"].remove("sentry")

logging.config.dictConfig(logging_config)
logger = logging.getLogger("pronun_model")

# 모든 출처를 허용하는 CORS 설정 (자격 증명 포함 불가)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,  # credentials를 반드시 False로 설정
)

# Request ID 미들웨어 추가
app.add_middleware(RequestIDMiddleware)

# 라우터 포함
app.include_router(upload_video_router, prefix="/api/pronun", tags=["Video Upload & Script"])
app.include_router(send_feedback_router, prefix="/api/pronun", tags=["Feedback Retrieval"])
app.include_router(delete_files_router, prefix="/api/pronun", tags=["File Deletion"])

# 루트 엔드포인트 (선택 사항)
@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello, Nina!"}

# 요청 로깅 미들웨어: 모든 요청과 응답을 로깅
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug("Request received")
    try:
        response = await call_next(request)
        # responseTime 계산: 요청 처리 시간
        # FastAPI 자체적으로 responseTime을 제공하지 않으므로, 직접 측정 필요
        # 여기서는 단순 예시로 timestamp 차이를 사용
        # 실제로는 start_time을 기록하고 response 후에 차이를 계산해야 함
        response_time = response.headers.get("X-Response-Time", "unknown")  # 필요 시 설정
        logger.info("Response sent", extra={
            "errorType": "",
            "error_message": ""
        })
        return response
    except Exception as e:
        # 예외 발생 위치 추출
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            filename, lineno, func, text = tb[-1]  # 가장 마지막 스택 프레임
        else:
            filename, lineno, func, text = "unknown", 0, "unknown", "unknown"
        
        logger.error("Error processing request", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise e

# 예외 처리 핸들러: DocumentProcessingError 발생 시
@app.exception_handler(DocumentProcessingError)
async def document_processing_exception_handler(request: Request, exc: DocumentProcessingError):
    """
    DocumentProcessingError 발생 시 500 Internal Server Error 응답을 반환합니다.
    """
    logger.error("Document exception", extra={
        "errorType": type(exc).__name__,
        "error_message": str(exc)
    })
    return JSONResponse(
        status_code=500,
        content={"detail": "script를 처리하는중 오류가 발생했습니다."},
    )

# 예외 처리 핸들러: AudioImportingError 발생 시
@app.exception_handler(AudioImportingError)
async def audio_importing_exception_handler(request: Request, exc: AudioImportingError):
    """
    AudioImportingError 발생 시 400 Bad Request 응답을 반환합니다.
    이는 클라이언트가 업로드한 오디오 파일이 유효하지 않음을 의미합니다.
    """
    logger.error("audio importing exception", extra={
        "errorType": type(exc).__name__,
        "error_message": str(exc)
    })
    return JSONResponse(
        status_code=400,
        content={"detail": "음성을 가져와서 변환하는중 오류가 발생했습니다."},
    )

# 예외 처리 핸들러: AudioProcessingError 발생 시
@app.exception_handler(AudioProcessingError)
async def audio_processing_exception_handler(request: Request, exc: AudioProcessingError):
    """
    AudioProcessingError 발생 시 400 Bad Request 응답을 반환합니다.
    이는 클라이언트가 업로드한 오디오 파일 처리 중 오류가 발생했음을 의미합니다.
    """
    logger.error("audio processing exception", extra={
        "errorType": type(exc).__name__,
        "error_message": str(exc)
    })
    return JSONResponse(
        status_code=400,
        content={"detail": "음성을 가져와서 처리하는중 오류가 발생했습니다."},
    )

# 예외 처리 핸들러: 일반 예외 발생 시
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    예상치 못한 예외 발생 시 500 Internal Server Error 응답을 반환합니다.
    """
    logger.error("Unhandled exception", extra={
        "errorType": type(exc).__name__,
        "error_message": str(exc)
    })
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다."},
    )
# Sentry 테스트 엔드포인트 추가
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

# 테스트 엔드포인트 추가
@app.get("/test-logging")
def test_logging():
    logger.debug("디버그 레벨 로그 테스트")
    logger.info("정보 레벨 로그 테스트")
    logger.error("오류 레벨 로그 테스트")
    return {"message": "로깅 테스트 완료"}

# 서버 실행 (uvicorn.run()에서 log_config 지정)
if __name__ == "__main__":
    # 현재 작업 디렉터리를 스크립트의 디렉터리로 설정
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_config="logging_config.json"  # 로깅 설정 파일 지정
    )

# uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-config logging_config.json