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

def create_image_card(text, book_title, page_info):
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

    # 2. 오버레이 (텍스트 가독성 향상)
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 170))
    base_img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(base_img)

    # 3. 폰트 설정
    try:
        # 본문 폰트 크기를 약간 줄여 가독성 확보 (60 -> 50)
        font_quote = ImageFont.truetype("font.ttf", 60)   # 본문 문구
        font_info = ImageFont.truetype("font.ttf", 35)    # 책 제목 및 작가
        font_page = ImageFont.truetype("font.ttf", 28)    # 페이지 수
    except OSError:
        font_quote = font_info = font_page = ImageFont.load_default()

    # 4. 본문 문구 배치 (중앙 정렬)
    wrapped_lines = textwrap.wrap(text, width=22)
    line_spacing = 25
    
    # 전체 텍스트 높이 계산
    total_text_height = sum([draw.textbbox((0, 0), line, font=font_quote)[3] for line in wrapped_lines]) + (len(wrapped_lines)-1) * line_spacing
    current_h = (height - total_text_height) / 2 - 40 # 약간 위쪽으로 배치
    
    for line in wrapped_lines:
        w = draw.textlength(line, font=font_quote)
        draw.text(((width - w) / 2, current_h), line, font=font_quote, fill="#FFFFFF")
        current_h += draw.textbbox((0, 0), line, font=font_quote)[3] + line_spacing
    
# 5. 책 정보 및 페이지 배치 (우측 하단)
    # 제목(작가) 정보
    info_text = f"출처: {book_title}"
    info_w = draw.textlength(info_text, font=font_info)
    draw.text((width - info_w - 70, height - 130), info_text, font=font_info, fill="#E0E0E0")

    # 페이지 정보 (더 작고 연한 색으로)
    page_text = f"Page. {page_info}"
    page_w = draw.textlength(page_text, font=font_page)
    draw.text((width - page_w - 70, height - 80), page_text, font=font_page, fill="#AAAAAA")

    # 6. 바이트 변환
    img_byte_arr = io.BytesIO()
    base_img.convert("RGB").save(img_byte_arr, format='JPEG', quality=95)
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
        도서 목록: [{selected_books}]
        
        조건:
        1. 문장은 200자 이내로 작성할 것.
        2. 반드시 아래의 형식을 엄격히 지킬 것.
        3. 각 책마다 중요한 문장들을 찾아서 작성할 것.
        형식: [문구 (책 제목, p.페이지)]
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )

        raw_text = response.text.strip()

        # 정규표현식으로 문구, 제목(작가), 페이지 추출
        match = re.search(r'\[(.*?) \((.*?), p\.(.*?)\)\]', raw_text)

        if match:
            quote_text = match.group(1)
            book_info = match.group(2) # "제목(작가)" 형태
            page_info = match.group(3) # "00" 형태
        else:
            quote_text = raw_text
            book_info = selected_book
            page_info = "미상"
            
        # 이미지 생성 시 모든 정보 전달
        image_data = create_image_card(quote_text, book_info, page_info)
        
        async with Bot(token=TELEGRAM_TOKEN) as bot:
            await bot.send_photo(
                chat_id=CHAT_ID, 
                photo=image_data, 
                caption=f"📚 {book_info}\n📄 {page_info}페이지\n\n{quote_text}"
                )
    
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(generate_and_send_quotes())
