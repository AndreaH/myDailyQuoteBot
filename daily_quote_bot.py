import os
import random
import asyncio
import re
import io
from google import genai 
from telegram import Bot
from PIL import Image, ImageDraw, ImageFont, ImageFilter  # Pillow 라이브러리
from telegram.ext import ApplicationBuilder
import asyncio
import textwrap


# 1. 설정값 로드
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 도서 리스트는 그대로 유지
BOOK_LIST = [
    "나는 부동산과 맞벌이한다(너바나)", "월급쟁이 부자로 은퇴하라(너나위)", "아기곰의 재테크 불변의 법칙(아기곰)",
    "대한민국 아파트 부의 지도(이상우)", "서울의 수도권 꼬마아파트(제네시스박)", "부동산 투자의 정석(김원철)",
    "부자 아빠 가난한 아빠(로버트 기요사키)", "돈의 속성(김승호)", "돈의 심리학(모건 하우절)",
    "부의 문장들(보도 섀퍼)", "레버리지(롭 무어)", "부의 추월차선(엠제이 드마코)",
    "원씽(게리 켈러)", "그릿(앤절라 더크워스)", "아주 작은 습관의 힘(제임스 클리어)",
    "타이탄의 도구들(팀 페리스)", "몰입(황농문)", "인간관계론(데일 카네기)",
    "현명한 투자자(벤저민 그레이엄)", "돈, 뜨겁게 사랑하고 차갑게 다스려라(앙드레 코스톨라니)"
]

def create_image_card(text, book_title):
    """
    텍스트와 책 제목을 받아 이미지 카드를 생성하고 바이트 데이터로 반환합니다.
    """
    # 1. 배경 이미지 로드 (로컬에 background.jpg 파일 필요)
    try:
        base_img = Image.open("background.png").convert("RGBA")
    except FileNotFoundError:
        # 배경 파일이 없을 경우 단색 배경 생성 (예비용)
        base_img = Image.new('RGBA', (1200, 800), color=(30, 30, 30, 255))

    width, height = base_img.size
    draw = ImageDraw.Draw(base_img)

    # 2. 가독성을 위한 오버레이(반투명 검은색) 추가
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 150))
    base_img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(base_img) # 다시 그리기 객체 생성

    # 3. 폰트 설정 (로컬에 font.ttf 파일 필요)
    # 가독성을 위해 본문과 제목 폰트 크기를 다르게 설정
    try:
        font_body = ImageFont.truetype("font.ttf", 60)
        font_title = ImageFont.truetype("font.ttf", 40)
    except OSError:
        # 폰트 파일이 없을 경우 기본 폰트 사용 (한글 깨짐 주의)
        font_body = font_title = ImageFont.load_default()

    # 4. 텍스트 자동 줄바꿈 처리 (가로폭의 80% 수준)
    lines = textwrap.wrap(text, width=25) # 한글 기준 적절한 길이 조정 필요
    current_h, pad = height * 0.3, 20
    
    # 5. 본문 텍스트 그리기 (중앙 정렬)
    for line in lines:
        w = draw.textlength(line, font=font_body)
        draw.text(((width - w) / 2, current_h), line, font=font_body, fill="white")
        current_h += font_body.getbbox(line)[3] + pad

    # 6. 책 제목 그리기 (우측 하단)
    title_text = f"- {book_title}"
    title_w = draw.textlength(title_text, font=font_title)
    draw.text((width - title_w - 50, height - 100), title_text, font=font_title, fill="#AAAAAA")

    # 7. 이미지를 바이트 데이터로 변환
    img_byte_arr = io.BytesIO()
    base_img.convert("RGB").save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr
    
async def generate_and_send_quotes():
    # 1. 랜덤 책 선정
    selected_books = random.sample(BOOK_LIST, 3)
    books_context = ", ".join(selected_books)
    
    # 2. 새로운 Gemini Client 설정 (Gemini 2.0 모델 사용 추천)
    client = genai.Client(api_key=GENAI_API_KEY)
    
    prompt = f"""
    다음 도서 목록에서 각 권당 하나씩, 총 3개의 통찰력 있는 추천 문장를을 작성해줘.
    도서 목록: [{books_context}]
    
    조건:
    1. 각 문장은 100자 이내로 작성할 것.
    2. 각 문장은 매일 중복되지 않게 선정하고, 작가가 중요하게 여기는 문장을 뽑아줄 것.
    3. 형식: [문구 (책 제목, p.임의의 페이지)]
    """
    
    # 3. 콘텐츠 생성 (모델명 확인: 'gemini-2.0-flash' 사용 추천)
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt
    )

    raw_text = response.text.strip()

    if match:
        quote_text = match.group(1)
        book_title = match.group(2)
    else:
        # 파싱 실패 시 대비책 (Fallback)
        quote_text = raw_text
        book_title = "오늘의 명언"
        
    # 4. 텔레그램 발송
    # try:
    #     async with Bot(token=TELEGRAM_TOKEN) as bot:
    #         await bot.send_message(chat_id=CHAT_ID, text=f"📚 오늘의 추천 문구입니다:\n\n{response.text}")
    # except Exception as e:
    #     print(f"텔레그램 전송 실패: {e}")
    # 3. 이미지 카드 생성 및 전송
    try:
        async with Bot(token=TELEGRAM_TOKEN) as bot:
            image_data = create_image_card(quote_text, book_title)
            await bot.send_photo(
                chat_id=CHAT_ID, 
                photo=image_data, 
                caption=f"📚 {book_title}\n\n{quote_text}"
            )
    except Exception as e:
        print(f"전송 단계 오류: {e}")
if __name__ == "__main__":
    asyncio.run(generate_and_send_quotes())
