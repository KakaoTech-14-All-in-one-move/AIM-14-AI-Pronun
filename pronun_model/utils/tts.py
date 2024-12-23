# pronun_model/utils/tts.py

from fastapi import HTTPException
from pydub import AudioSegment
import math
import os
import uuid
from openai import OpenAI
from openai import (
    AuthenticationError,
    APIError,
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    BadRequestError,
    OpenAIError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    UnprocessableEntityError
)
from ..openai_config import OPENAI_API_KEY
from ..config import CONVERT_TTS_DIR
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

client = OpenAI(api_key=OPENAI_API_KEY)

def TTS(script, video_id: str, output_path=None, speed=1.0):
    """
    텍스트를 음성으로 변환(TTS)합니다. 스크립트가 4000자 이상일 경우, 분할하여 여러 개의 음성 파일을 생성한 후 결합합니다.

    Args:
        script (str): 입력 텍스트.
        output_path (str): 생성될 음성 파일 경로.
        video_id (str): video_id 
        speed (float): 음성 속도 조절 (0.5 ~ 4.0).

    Returns:
        str: 생성된 음성 파일 경로.
        None: 변환 실패 시.
    """
    try:
        if output_path is None:
            # 고유한 파일 이름 생성
            filename = f"{video_id}_TTS_{uuid.uuid4()}.mp3"
            output_path = CONVERT_TTS_DIR / filename
        else:
            output_path = Path(output_path)
            if not output_path.is_absolute():
                output_path = CONVERT_TTS_DIR / output_path

        num = math.ceil(len(script) / 4000)

        if num == 1:
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=script,
                speed=speed
            )
            with open(output_path, 'wb') as f:
                f.write(response.content)  # 수정된 부분
        else:
            tts_files = []
            for i in range(num):
                segment = script[4000 * i : 4000 * (i + 1)]
                segment_filename = f"{video_id}_TTS_{i}_{uuid.uuid4()}.mp3"
                tts_segment_path = CONVERT_TTS_DIR / segment_filename

                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=segment,
                    speed=speed
                )
                with open(tts_segment_path, 'wb') as f:
                    f.write(response.content)  # 수정된 부분
                logger.debug(f"TTS segment {i+1} saved at {tts_segment_path}")
                tts_files.append(tts_segment_path)

            # 여러 개의 TTS 파일을 결합
            combined_audio = AudioSegment.empty()
            for tts_file in tts_files:
                audio_segment = AudioSegment.from_mp3(tts_file)
                combined_audio += audio_segment
                os.remove(tts_file)  # 임시 파일 삭제
                logger.debug(f"Combined and removed segment file {tts_file}")

            # 결합된 오디오 저장
            combined_audio.export(output_path, format="mp3")

        logging.info(f"TTS 생성 완료: {output_path}")
        return str(output_path.resolve())

    except AuthenticationError as e:
        logger.error(f"TTS 변환 중 인증 오류 발생: {e}", extra={
            "errorType": "AuthenticationError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=401, detail="인증 오류: API 키를 확인해주세요.") from e

    except PermissionDeniedError as e:
        logger.error(f"TTS 변환 중 권한 오류 발생: {e}", extra={
            "errorType": "PermissionDeniedError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=403, detail="권한 오류: API 사용 권한을 확인해주세요.") from e

    except RateLimitError as e:
        logger.error(f"TTS 변환 중 Rate Limit 초과: {e}", extra={
            "errorType": "RateLimitError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=429, detail="요청 제한 초과: 요청 속도를 줄여주세요.") from e

    except BadRequestError as e:
        logger.error(f"TTS 변환 중 잘못된 요청 오류 발생: {e}", extra={
            "errorType": "BadRequestError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=400, detail="잘못된 요청: 요청 데이터를 확인해주세요.") from e

    except ConflictError as e:
        logger.error(f"TTS 변환 중 충돌 오류 발생: {e}", extra={
            "errorType": "ConflictError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=409, detail="충돌 오류: 요청을 다시 시도해주세요.") from e

    except InternalServerError as e:
        logger.error(f"TTS 변환 중 내부 서버 오류 발생: {e}", extra={
            "errorType": "InternalServerError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=502, detail="내부 서버 오류: 나중에 다시 시도해주세요.") from e

    except NotFoundError as e:
        logger.error(f"TTS 변환 중 자원 미존재 오류 발생: {e}", extra={
            "errorType": "NotFoundError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=404, detail="자원이 존재하지 않습니다.") from e

    except UnprocessableEntityError as e:
        logger.error(f"TTS 변환 중 처리 불가능한 엔티티 오류 발생: {e}", extra={
            "errorType": "UnprocessableEntityError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=422, detail="처리 불가능한 데이터입니다.") from e

    except APIError as e:
        logger.error(f"TTS 변환 중 API 오류 발생: {e}", extra={
            "errorType": "APIError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=502, detail="서버 오류: 나중에 다시 시도해주세요.") from e

    except APITimeoutError as e:
        logger.error(f"TTS 변환 중 API 타임아웃 오류 발생: {e}", extra={
            "errorType": "APITimeoutError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=504, detail="서버 응답 지연: 나중에 다시 시도해주세요.") from e

    except APIConnectionError as e:
        logger.error(f"TTS 변환 중 API 연결 오류 발생: {e}", extra={
            "errorType": "APIConnectionError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=503, detail="연결 오류: 네트워크 상태를 확인해주세요.") from e

    except OpenAIError as e:
        logger.error(f"TTS 변환 중 OpenAI 라이브러리 오류 발생: {e}", extra={
            "errorType": "OpenAIError",
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="OpenAI 처리 중 알 수 없는 오류가 발생했습니다.") from e

    except Exception as e:
        logger.error(f"TTS 변환 오류: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail="TTS 변환 중 오류 발생.") from e