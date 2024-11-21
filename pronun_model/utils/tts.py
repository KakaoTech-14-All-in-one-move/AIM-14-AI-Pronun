# pronun_model/utils/tts.py

from pydub import AudioSegment
import math
import os
import uuid
from openai import OpenAI
from ..config import OPENAI_API_KEY, CONVERT_TTS_DIR
import logging

client = OpenAI(api_key=OPENAI_API_KEY)

def TTS(script, output_path=None, speed=1.0):
    """
    텍스트를 음성으로 변환(TTS)합니다. 스크립트가 4000자 이상일 경우, 분할하여 여러 개의 음성 파일을 생성한 후 결합합니다.

    Args:
        script (str): 입력 텍스트.
        output_path (str): 생성될 음성 파일 경로.
        speed (float): 음성 속도 조절 (0.5 ~ 4.0).

    Returns:
        str: 생성된 음성 파일 경로.
        None: 변환 실패 시.
    """
    try:
        if output_path is None:
            # 고유한 파일 이름 생성
            filename = f"TTS_{uuid.uuid4()}.mp3"
            output_path = os.path.join(CONVERT_TTS_DIR, filename)
        else:
            # output_path가 디렉토리를 포함하지 않으면 CONVERT_TTS_DIR을 포함하도록 수정
            if not os.path.isabs(output_path):
                output_path = os.path.join(CONVERT_TTS_DIR, output_path)

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
                tts_segment_path = os.path.join(CONVERT_TTS_DIR, f"TTS_{i}_{uuid.uuid4()}.mp3")
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=segment,
                    speed=speed
                )
                with open(tts_segment_path, 'wb') as f:
                    f.write(response.content)  # 수정된 부분
                tts_files.append(tts_segment_path)

            # 여러 개의 TTS 파일을 결합
            combined_audio = AudioSegment.empty()
            for tts_file in tts_files:
                audio_segment = AudioSegment.from_mp3(tts_file)
                combined_audio += audio_segment
                os.remove(tts_file)  # 임시 파일 삭제

            combined_audio.export(output_path, format="mp3")

        logging.info(f"TTS 생성 완료: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"TTS 변환 오류: {e}")
        return None