import os
import random
import asyncio
from google import genai 
from telegram import Bot
import asyncio

# 1. 설정값 로드
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 도서 리스트는 그대로 유지
BOOK_LIST = [
    "나는 부동산과 맞벌이한다(너나위)", "월급쟁이 부자로 은퇴하라(너나위)", "아기곰의 재테크 불변의 법칙(아기곰)",
    "대한민국 아파트 부의 지도(이상우)", "서울의 수도권 꼬마아파트(제네시스박)", "부동산 투자의 정석(김원철)",
    "부자 아빠 가난한 아빠(로버트 기요사키)", "돈의 속성(김승호)", "돈의 심리학(모건 하우절)",
    "부의 문장들(보도 섀퍼)", "레버리지(롭 무어)", "부의 추월차선(엠제이 드마코)",
    "원씽(게리 켈러)", "그릿(앤절라 더크워스)", "아주 작은 습관의 힘(제임스 클리어)",
    "타이탄의 도구들(팀 페리스)", "몰입(황농문)", "인간관계론(데일 카네기)",
    "현명한 투자자(벤저민 그레이엄)", "돈, 뜨겁게 사랑하고 차갑게 다스려라(앙드레 코스톨라니)"
]

async def generate_and_send_quotes():
    # 1. 랜덤 책 선정
    selected_books = random.sample(BOOK_LIST, 5)
    books_context = ", ".join(selected_books)
    
    # 2. 새로운 Gemini Client 설정 (Gemini 2.0 모델 사용 추천)
    client = Client(api_key=GENAI_API_KEY)
    
    prompt = f"""
    다음 도서 목록에서 각 권당 하나씩, 총 5개의 통찰력 있는 추천 문구를 작성해줘.
    도서 목록: [{books_context}]
    
    조건:
    1. 각 문구는 50자 이내로 작성할 것.
    2. 형식: [문구 (책 제목, p.임의의 페이지)]
    """
    
    # 3. 콘텐츠 생성 (모델명 확인: 'gemini-2.0-flash' 사용 추천)
    response = client.models.generate_content(
        model='gemini-2.0-flash', 
        contents=prompt
    )
    
    # 4. 텔레그램 발송
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=f"📚 오늘의 추천 문구입니다:\n\n{response.text}")

if __name__ == "__main__":
    asyncio.run(generate_and_send_quotes())
