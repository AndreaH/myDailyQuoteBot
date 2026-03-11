# 📚 AI Daily Book Quote Bot

> **Gemini 2.0 & Telegram 기반 지능형 독서 코치 자동화 시스템**

이 프로젝트는 사용자가 업로드한 도서 목록 이미지에서 인사이트를 추출하거나, 엄선된 명저 리스트를 바탕으로 **매일 아침 8시(KST)**에 통찰력 있는 문구를 텔레그램으로 배달해 주는 자동화 서비스입니다.

---

## 🚀 주요 기능

* **지능형 문구 추출:** Gemini 1.5/2.0 Flash 모델을 활용하여 도서의 핵심 철학을 반영한 50자 내외의 추천 문구 생성.
* **완전 자동화:** GitHub Actions 스케줄러를 이용하여 서버 비용 없이 매일 정해진 시간에 작동.
* **멀티모달 지원:** 도서 썸네일 이미지를 직접 분석하거나 텍스트 리스트를 기반으로 큐레이션 가능.
* **맞춤형 알림:** 텔레그램 봇을 통해 개인화된 메시지 수신.

---

## 🛠 Tech Stack

* **Language:** Python 3.11+
* **AI Model:** Google Gemini API (`google-genai`)
* **Automation:** GitHub Actions
* **Interface:** Telegram Bot API (`python-telegram-bot`)

---

## ⚙️ 설정 및 설치 (Setup)

### 1. 환경 변수 (Secrets) 설정

GitHub 리포지토리의 `Settings > Secrets and variables > Actions`에 아래 항목을 등록해야 합니다.

| Name | Description |
| --- | --- |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/)에서 발급받은 API 키 |
| `TELEGRAM_TOKEN` | [@BotFather](https://t.me/botfather)를 통해 발급받은 봇 토큰 |
| `CHAT_ID` | 메시지를 수신할 사용자의 텔레그램 ID |

### 2. 로컬 테스트

```bash
# 저장소 복제
git clone https://github.com/your-username/myDailyQuoteBot.git

# 의존성 설치
pip install google-genai python-telegram-bot

# 스크립트 실행
python daily_quote_bot.py

```

---

## 📅 실행 스케줄 (Cron)

본 프로젝트는 GitHub Actions를 통해 다음 스케줄로 작동합니다:

* **설정 시간:** 매일 23:00 UTC (한국 시간 기준 **오전 08:00**)
* **파일 위치:** `.github/workflows/daily_quote.yml`

---

## 📝 도서 리스트 (Dataset)

현재 프로젝트는 아래와 같은 명저들을 기반으로 문구를 생성합니다:

* 재테크: *돈의 속성, 부의 추월차선, 레버리지...*
* 자기계발: *원씽, 그릿, 아주 작은 습관의 힘...*
* 부동산: *월급쟁이 부자로 은퇴하라, 부동산 투자의 정석...*

---

## 🤝 기여 (Contribution)

새로운 도서를 리스트에 추가하고 싶거나 기능 개선 제안은 언제든지 **Pull Request** 또는 **Issue**를 통해 환영합니다.

---

### 💡 향후 로드맵

* [ ] 독서 기록 데이터베이스(Notion) 연동
* [ ] 요일별 특정 카테고리(부동산/마인드셋 등) 집중 큐레이션

---
* Telegram Channel : https://t.me/+v1Fzyca60u5jN2M1
