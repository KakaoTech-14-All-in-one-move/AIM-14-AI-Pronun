# pronun_model/routers/upload_video.py

import logging
import logging.config
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response, Request
from pronun_model.utils.convert_to_mp3 import convert_to_mp3
from pronun_model.utils.text_cleaning import clean_extracted_text
from pronun_model.schemas.feedback import UploadResponse
from pronun_model.config import UPLOAD_DIR, CONVERT_MP3_DIR, SCRIPTS_DIR
from typing import Optional, Union, Set
import os
import uuid
import logging
import shutil

router = APIRouter()

# JSON 기반 로깅 설정 적용
logging_config_path = Path(__file__).resolve().parent.parent.parent / "logging_config.json"  # 최상단 경로
with open(logging_config_path, "r") as f:
    logging_config = json.load(f)

logging.config.dictConfig(logging_config)
logger = logging.getLogger("main_logger")

@router.post("/upload-video-with-script/", response_model=UploadResponse)
async def upload_video_with_optional_script(
    request: Request,
    response: Response,
    video: UploadFile = File(...),
    script: Optional[Union[UploadFile, str]] = File(None)
):
    """
    비디오 파일을 업로드하고, MP3로 변환하여 저장한 후 video_id를 반환합니다.
    """
    # 응답 헤더에 CORS 설정 추가
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "False"

    logger.info("upload_video_with_optional_script 엔드포인트 호출됨")
    logger.info(f"수신된 비디오 파일: {video.filename}")

    # script 필드가 빈 문자열로 전송된 경우 처리
    if isinstance(script, str):
        if not script.strip():
            script = None
        else:
            raise HTTPException(status_code=400, detail="스크립트 파일 형식이 올바르지 않습니다.")

    # script 필드 처리
    if script is not None:
        logger.info(f"스크립트가 수신되었습니다: {script.filename}")
    else:
        logger.info("스크립트가 제공되지 않았습니다.")

    # 지원하는 영상 파일 형식 확인
    ALLOWED_EXTENSIONS: Set[str] = {
        "webm", "mov", "avi", "mkv", "flac", "m4a",
        "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav"
    }
    if '.' in video.filename:
        file_extension = video.filename.rsplit(".", 1)[-1].lower()
    else:
        file_extension = ""
    
    if file_extension not in ALLOWED_EXTENSIONS:
        logger.error(f"지원하지 않는 비디오 파일 형식: {file_extension}. 파일명: {video.filename}")
        raise HTTPException(status_code=400, detail="지원하지 않는 영상 파일 형식입니다. 허용된 형식: " + ", ".join(ALLOWED_EXTENSIONS))

    # 지원하는 스크립트 파일 형식 확인
    ALLOWED_SCRIPT_EXTENSIONS: Set[str] = {"docx", "txt", "pdf", "hwp", "hwpx"}
    if script:
        if '.' in script.filename:
            script_extension = script.filename.rsplit(".", 1)[-1].lower()
        else:
            script_extension = ""
        if script_extension not in ALLOWED_SCRIPT_EXTENSIONS:
            logger.error(f"지원하지 않는 스크립트 파일 형식: {script_extension}. 파일명: {script.filename}")
            raise HTTPException(status_code=400, detail="지원하지 않는 스크립트 파일 형식입니다. 허용된 형식: " + ", ".join(ALLOWED_SCRIPT_EXTENSIONS))

    # 고유한 video_id 생성
    video_id = uuid.uuid4().hex

    # 비디오 파일 저장 경로 설정
    video_path = UPLOAD_DIR / f"{video_id}.{file_extension}"

    # 비디오 파일 저장
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        logger.info(f"비디오 파일이 성공적으로 저장되었습니다: {video_path}")

        # 파일 저장 여부 확인
        if not os.path.exists(video_path):
            logger.error(f"비디오 파일이 저장되지 않았습니다: {video_path}")
            raise HTTPException(status_code=500, detail="비디오 파일 저장 실패")

        # MP3 변환
        try:
            mp3_path = convert_to_mp3(str(video_path), video_id)
            if not mp3_path or not os.path.exists(mp3_path):
                logger.error(f"MP3 변환 실패: video_path={video_path}, video_id={video_id}")
                raise HTTPException(status_code=500, detail="MP3 변환 실패: 파일 생성에 실패했습니다.")
            logger.info(f"MP3 변환이 성공했습니다: {mp3_path}")
        except Exception as e:
            logger.error(f"MP3 변환 중 오류 발생: {e}. video_path={video_path}, video_id={video_id}")
            raise HTTPException(status_code=500, detail="MP3 변환 중 알 수 없는 오류가 발생했습니다.")

        # 스크립트 저장 (선택적, File 형태로만 처리)
        if script:
            try:
                script_path = SCRIPTS_DIR / f"{video_id}.{script_extension}"
                with open(script_path, "wb") as buffer:
                    shutil.copyfileobj(script.file, buffer)
                logger.info(f"스크립트 파일이 성공적으로 저장되었습니다: {script_path}")
            except Exception as e:
                logger.error(f"스크립트 파일 저장 중 오류 발생. 경로: {script_path}, 오류: {e}")
                raise HTTPException(status_code=500, detail="스크립트 파일 저장 실패")
        else:
            logger.info("스크립트 파일이 제공되지 않았습니다. STT 및 LLM을 사용하여 스크립트를 생성합니다.")

        # 성공 응답
        return UploadResponse(
            video_id=video_id,
            message=f"비디오 업로드 및 MP3 변환 완료. 피드백 데이터를 받으려면 pronun/send-feedback/{video_id} 엔드포인트를 호출하세요."
        )

    except Exception as e:
        logger.error(f"알 수 없는 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="파일 처리 중 예기치 않은 오류 발생")
