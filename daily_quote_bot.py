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

BOOKS = {
    "부동산 및 경제경영": [
        "나는 부동산과 맞벌이한다(너바나)", "월급쟁이 부자로 은퇴하라(너나위)", "결국엔 오르는 아파트",
        "월가의 영웅(피터 린치)", "자본주의(EBS)", "돈의 속성(김승호)", "부의 인문학(브라운스톤)",
        "부자 아빠 투자 가이드(로버트 기요사키)", "보도 섀퍼의 돈(보도 섀퍼)", "이웃집 백만장자",
        "전세가를 알면 부동산 투자가 보인다", "부동산 투자의 정석", "노후를 위해 집을 이용하라",
        "부동산 트렌드 2026", "부자는 왜 더 부자가 되는가(로버트 기요사키)", "부의 전략 수업",
        "현명한 투자자(벤저민 그레이엄)", "부의 추월차선(엠제이 드마코)", "투자에 대한 생각(하워드 막스)",
        "시골의사의 부자경제학(박경철)", "강남의 탄생", "머니트렌드 2026"
    ],
    "자기계발 및 마인드셋": [
        "원씽(ONE THING)", "인생투자", "사장학개론(김승호)", "나의 스무 살을 가장 존중한다",
        "인간관계론(데일 카네기)", "일독(日讀)", "바인더의 힘(강규형)", "레버리지(롭 무어)",
        "생각하라 그리고 부자가 되어라(나폴레온 힐)", "시크릿(론다 번)", "몰입(황농문)",
        "돈의 심리학(모건 하우절)", "절제의 성공학(미즈노 남보쿠)", "자기관리론(데일 카네기)",
        "그릿(Grit)", "아주 작은 습관의 힘", "원칙(레이 달리오)", "생각의 비밀(김승호)",
        "아주 작은 반복의 힘", "미라클 모닝", "기브 앤 테이크(애덤 그랜트)", "딥마인드(김미경)",
        "워런 버핏 삶의 원칙", "Start with Why(사이먼 사이넥)", "부러지지 않는 마음",
        "마음의 기술", "5초의 법칙(멜 로빈스)", "설득의 심리학(로버트 치알디니)",
        "마인드셋(캐럴 드웩)", "아비투스(Habitus)", "성공하는 사람들의 7가지 습관",
        "후회의 재발견(다니엘 핑크)", "회복탄력성(김주환)", "고수의 생각법",
        "퓨처 셀프(벤저민 하디)", "프레임(최인철)", "에고라는 적(라이언 홀리데이)", "챔피언 마인드"
    ],
    "인문 및 기타": [
        "불변의 법칙(모건 하우절)", "포노 사피엔스(최재붕)", "죽음의 수용소에서(빅터 프랭클)",
        "행복의 기원(서은국)", "최고의 휴식", "인생은 순간이다(김성근)", "일본전산 이야기(김성호)"
    ]
}

# 모든 책을 하나의 리스트로 통합 (랜덤 추출용)
ALL_BOOKS = [book for sublist in BOOKS.values() for book in sublist]

def create_image_card(text, book_title, page_info):
    """텍스트와 책 제목을 받아 이미지 카드를 생성하고 바이트 데이터로 반환합니다."""
    width, height = 1200, 800
    
    # 1. 배경 이미지 랜덤 선택 로직
    # 현재 디렉토리에서 background로 시작하고 .png로 끝나는 파일 목록 추출
    bg_files = [f for f in os.listdir('.') if f.startswith('background') and f.endswith('.png')]

    selected_bg = None
    if bg_files:
        selected_bg = random.choice(bg_files)
        print(f"선택된 배경: {selected_bg}")
    
    try:
        if selected_bg and os.path.exists(selected_bg):
            base_img = Image.open(selected_bg).convert("RGBA").resize((width, height))
        else:
            # 배경 파일이 하나도 없을 경우 기본 짙은 회색 배경 사용
            base_img = Image.new('RGBA', (width, height), color=(35, 39, 46, 255))
    except Exception as e:
        print(f"배경 로드 중 오류(기본 배경 전환): {e}")
        base_img = Image.new('RGBA', (width, height), color=(35, 39, 46, 255))

    # 2. 가독성을 위한 오버레이 (텍스트가 잘 보이도록 반투명 검은색 추가)
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 175)) # 투명도 약간 강화
    base_img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(base_img)

    # 3. 폰트 로드 (font.ttf 파일 필수)
    try:
        font_quote = ImageFont.truetype("font.ttf", 55)
        font_info = ImageFont.truetype("font.ttf", 35)
        font_page = ImageFont.truetype("font.ttf", 28)
    except OSError:
        font_quote = font_info = font_page = ImageFont.load_default()

    # 4. 본문 문구 배치 (중앙 정렬)
    wrapped_lines = textwrap.wrap(text, width=22)
    line_spacing = 25
    total_h = sum([draw.textbbox((0, 0), l, font=font_quote)[3] for l in wrapped_lines]) + (len(wrapped_lines)-1)*line_spacing
    current_h = (height - total_h) / 2 - 40

    for line in wrapped_lines:
        w = draw.textlength(line, font=font_quote)
        draw.text(((width - w) / 2, current_h), line, font=font_quote, fill="#FFFFFF")
        current_h += draw.textbbox((0, 0), line, font=font_quote)[3] + line_spacing

    # 5. 하단 정보 배치 (출처 및 페이지)
    info_text = f"출처: {book_title}"
    info_w = draw.textlength(info_text, font=font_info)
    draw.text((width - info_w - 70, height - 130), info_text, font=font_info, fill="#E0E0E0")

    page_text = f"Page. {page_info}"
    page_w = draw.textlength(page_text, font=font_page)
    draw.text((width - page_w - 70, height - 80), page_text, font=font_page, fill="#AAAAAA")

    # 6. 바이트 변환 및 반환
    img_byte_arr = io.BytesIO()
    base_img.convert("RGB").save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    return img_byte_arr
    
async def generate_and_send_quotes():
    try:
        # 1. 랜덤 책 선정 (Gemini에게 명확한 가이드 제공)
        selected_books = random.sample(ALL_BOOKS, 3)
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
