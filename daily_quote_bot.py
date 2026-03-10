import os
import random
import asyncio
import re
import io
import textwrap
from google import genai 
from telegram import Bot
from PIL import Image, ImageDraw, ImageFont

# 1. 설정값 로드
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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
    """텍스트와 책 제목을 받아 이미지 카드를 생성하고 바이트 데이터로 반환합니다."""
    width, height = 1200, 800
    
    # 1. 배경 이미지 로드 (background.png 또는 background.jpg 확인)
    bg_path = "background.png" if os.path.exists("background.png") else "background.jpg"
    
    try:
        if os.path.exists(bg_path):
            base_img = Image.open(bg_path).convert("RGBA").resize((width, height))
        else:
            base_img = Image.new('RGBA', (width, height), color=(30, 30, 30, 255))
    except Exception:
        base_img = Image.new('RGBA', (width, height), color=(30, 30, 30, 255))

    # 2. 가독성을 위한 오버레이 추가
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 160))
    base_img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(base_img)

    # 3. 폰트 설정
    try:
        # 본문 폰트 크기를 약간 줄여 가독성 확보 (60 -> 50)
        font_body = ImageFont.truetype("font.ttf", 50)
        font_title = ImageFont.truetype("font.ttf", 35)
    except OSError:
        font_body = font_title = ImageFont.load_default()

    # 4. 텍스트 줄바꿈 및 중앙 정렬 배치
    wrapped_lines = textwrap.wrap(text, width=25)
    line_heights = [draw.textbbox((0, 0), line, font=font_body)[3] for line in wrapped_lines]
    total_text_height = sum(line_heights) + (len(wrapped_lines) - 1) * 20
    
    current_h = (height - total_text_height) / 2
    
    for line in wrapped_lines:
        w = draw.textlength(line, font=font_body)
        draw.text(((width - w) / 2, current_h), line, font=font_body, fill="white")
        current_h += draw.textbbox((0, 0), line, font=font_body)[3] + 20

    # 5. 책 제목 (우측 하단)
    title_text = f"- {book_title}"
    title_w = draw.textlength(title_text, font=font_title)
    draw.text((width - title_w - 60, height - 80), title_text, font=font_title, fill="#BBBBBB")

    # 6. 바이트 변환
    img_byte_arr = io.BytesIO()
    base_img.convert("RGB").save(img_byte_arr, format='JPEG', quality=90)
    img_byte_arr.seek(0)
    return img_byte_arr
    
async def generate_and_send_quotes():
    try:
        # 1. 랜덤 책 선정 (Gemini에게 명확한 가이드 제공)
        selected_books = random.sample(BOOK_LIST, 3)
        books_context = ", ".join(selected_books)
        
        client = genai.Client(api_key=GENAI_API_KEY)
        
        # 모델명을 정식 명칭인 'gemini-2.0-flash'로 수정 (2.5는 존재하지 않음)
        prompt = f"""
        다음 도서 목록 중 가장 통찰력 있는 '단 한 권'을 선택해서 명언 또는 문장을 작성해줘.
        도서 목록: [{books_context}]
        
        조건:
        1. 문장은 100자 이내로 작성할 것.
        2. 반드시 아래의 형식을 엄격히 지킬 것.
        3. 각 책마다 중요한 문장들을 찾아서 작성할 것.
        형식: [문구 (책 제목, p.페이지)]
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )

        raw_text = response.text.strip()

        # 2. 정규표현식 매칭 (NameError 방지를 위해 match 변수 먼저 생성)
        match = re.search(r'\[(.*?) \((.*?), p\.(.*?)\)\]', raw_text)

        if match:
            quote_text = match.group(1)
            book_title = match.group(2)
        else:
            # 매칭 실패 시 수동 파싱 시도
            quote_text = raw_text.replace('[', '').replace(']', '')
            book_title = selected_books[0] # 폴백용 제목
            
        # 3. 이미지 카드 생성 및 텔레그램 전송
        async with Bot(token=TELEGRAM_TOKEN) as bot:
            image_data = create_image_card(quote_text, book_title)
            await bot.send_photo(
                chat_id=CHAT_ID, 
                photo=image_data, 
                caption=f"📚 {book_title}\n\n{quote_text}"
            )
            print("성공적으로 전송되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(generate_and_send_quotes())
