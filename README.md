# AIM-14-AI-Pronun
KakaoTech - AI 기반 발표 피드백 서비스 플랫폼 "Pitching"의 음성 평가 및 분석 엔진 (Pronunciation Analysis Engine) Repo 입니다.

## 개요
음성 평가 및 분석 엔진은 발표 음성을 분석하여 **발음 정확도**, **음성 유사도**, **말하기 속도** 등 다양한 피드백을 제공합니다. Whisper 모델 기반의 STT(Speech-To-Text)와 TTS(Text-To-Speech)를 활용하며, 발표 연습 및 피드백을 위한 강력한 도구입니다.

Pitching의 음성 평가를 지원하기 위해 설계되었습니다.

---

## 주요 기능

### 1. 음성 처리 및 분석
- **STT (Speech-To-Text)**
  - Whisper 모델을 사용하여 음성을 텍스트로 변환합니다.
- **TTS (Text-To-Speech)**
  - Whisper 기반 TTS 모델로 기준 음성을 생성합니다.
- **발음 정확도 분석**
  - STT 결과와 스크립트를 비교하여 발음 정확도를 평가합니다.
- **음성 유사도 분석**
  - Librosa를 활용하여 사용자 음성과 TTS 음성 간의 유사도를 계산합니다.
- **말하기 속도 계산**
  - 단어 수와 오디오 길이를 기반으로 발표자의 말하기 속도를 분석합니다.

### 2. 유연한 스크립트 처리
- 사용자가 제공한 스크립트를 기준으로 분석을 수행합니다.
- 스크립트가 없을 경우 LLM(OpenAI API)을 사용하여 STT 결과를 보정 후 분석합니다.

### 3. 발음 피드백 및 점수 제공
- **JSON 형식의 피드백 제공**:
  - 발음 정확도, 음성 유사도, 말하기 속도, 구간별 분석 결과를 제공합니다.
- 구간별 발음 정확도와 WPM(Word Per Minute)을 포함한 상세 데이터를 출력합니다.

### 4. API 기반 클라이언트 통합
- FastAPI 기반 RESTful API로 클라이언트와 쉽게 연동 가능합니다.
  - **POST** `/upload-audio`: 음성 업로드 및 분석 요청.
  - **GET** `/get-analysis`: 분석 결과 반환.

---

## 설치 및 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. FastAPI 서버 실행
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-config logging_config.json
```

### 3. 테스트 실행
```bash
pytest --cov=pronun_model tests/
```

---

## 폴더 구조
```
├── pronun_model
│   ├── stt.py
│   ├── tts.py
│   ├── analyze_pronunciation_accuracy.py
│   ├── compare_audio_similarity.py
│   └── ...
├── storage
│   ├── convert_mp3
│   ├── convert_tts
│   ├── input_video
│   ├── scripts
├── tests
│   ├── test_stt.py
│   ├── test_tts.py
│   ├── test_analyze_pronunciation_accuracy.py
│   └── ...
├── requirements.txt
├── logging_config.json
├── main.py
└── README.md
```

---

## 의존성 라이브러리
- **음성 처리**
  - `openai`, `librosa`, `soundfile`, `pydub`
- **FastAPI 관련**
  - `fastapi`, `uvicorn`, `python-multipart`
- **데이터 처리**
  - `scikit-learn`, `fuzzywuzzy`, `python-docx`, `PyPDF2`, `striprtf`
- **로깅 및 모니터링**
  - `python-json-logger`, `colorlog`, `sentry-sdk[fastapi]`
- **테스트 도구**
  - `pytest`, `pytest-cov`, `pytest-mock`, `httpx`

---

## 사용 사례
- **발표 연습 피드백**
  - 발표자의 음성을 분석하여 발음 정확도, 말하기 속도, 음성 유사도에 대한 피드백 제공.
- **교육용 활용**
  - 영어 학습자나 발표 연습자가 자신의 음성을 분석하고 개선하는 데 사용 가능.

---

## API 예제

### 음성 업로드 요청 (POST `/upload-audio`)
```bash
curl -X POST "http://localhost:8000/upload-audio" \
-H "Content-Type: multipart/form-data" \
-F "audio_file=@example_audio.mp3"
```

### 분석 결과 요청 (GET `/get-analysis`)
```bash
curl -X GET "http://localhost:8000/get-analysis?audio_id=12345"
```

---

## 기여 방법
1. 본 레포지토리를 포크합니다.
2. 새로운 브랜치를 생성합니다: `git checkout -b feature-name`
3. 변경 사항을 커밋합니다: `git commit -m 'Add some feature'`
4. 브랜치에 푸시합니다: `git push origin feature-name`
5. Pull Request를 생성합니다.

---

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](./LICENSE)를 참조하세요.

