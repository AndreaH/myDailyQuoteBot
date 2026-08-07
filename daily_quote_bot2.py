import os
import re
import io
import random
import asyncio
import textwrap

from google import genai
from telegram import Bot
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# 설정값 로드
# ---------------------------------------------------------------------------
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Gemini 모델 우선순위 (503 발생 시 다음 모델로 fallback)
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]

# ---------------------------------------------------------------------------
# 도서 목록 (하이쿠 카테고리 추가)
# ---------------------------------------------------------------------------
BOOKS = {
    "부동산 및 경제경영": [
        "나는 부동산과 맞벌이한다(너바나)", "월급쟁이 부자로 은퇴하라(너나위)", "결국엔 오르는 아파트",
        "월가의 영웅(피터 린치)", "자본주의(EBS)", "돈의 속성(김승호)", "부의 인문학(브라운스톤)",
        "부자 아빠 투자 가이드(로버트 기요사키)", "보도 섀퍼의 돈(보도 섀퍼)", "이웃집 백만장자",
        "전세가를 알면 부동산 투자가 보인다", "부동산 투자의 정석", "노후를 위해 집을 이용하라",
        "부동산 트렌드 2026", "부자는 왜 더 부자가 되는가(로버트 기요사키)", "부의 전략 수업",
        "현명한 투자자(벤저민 그레이엄)", "부의 추월차선(엠제이 드마코)", "투자에 대한 생각(하워드 막스)",
        "시골의사의 부자경제학(박경철)", "강남의 탄생", "머니트렌드 2026",
        "트렌드 코리아 2026(김난도 외)", "넥스트 패러다임: AI 시대의 투자 전략",
        "서울 부동산 5년 후 미래 지도", "위대한 투자의 원칙", "초격차 자산관리",
        "AI 빅뱅과 부의 대전환", "마켓 트렌드 2026", "부의 공식(스콧 갤러웨이)"
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
        "퓨처 셀프(벤저민 하디)", "프레임(최인철)", "에고라는 적(라이언 홀리데이)", "챔피언 마인드",
        "초집중(니르 에얄)", "뇌, 욕망의 비밀을 풀다", "넥스트 레벨(Next Level)",
        "원티드(Wanted)", "도파민 네이션(애나 렘키)", "마음챙김의 힘",
        "일하는 마음의 기술", "아침 5시의 기적"
    ],
    "인문 및 기타": [
        "불변의 법칙(모건 하우절)", "포노 사피엔스(최재붕)", "죽음의 수용소에서(빅터 프랭클)",
        "행복의 기원(서은국)", "최고의 휴식", "인생은 순간이다(김성근)", "일본전산 이야기(김성호)",
        "사피엔스(유발 하라리)", "생각에 관한 생각(다니엘 카너먼)", "공정하다는 착각(마이클 샌델)",
        "역사의 대전환", "마이클 샌델의 질문", "문명의 지혜"
    ],
    "삶의 통찰(하이쿠)": [
        "마쓰오 바쇼 하이쿠 선집", "고바야시 잇사 하이쿠 선집", "요사 부손 하이쿠 선집",
        "에도 시대 고전 하이쿠", "인생의 본질을 꿰뚫는 일본 명작 하이쿠"
    ]
}

# ---------------------------------------------------------------------------
# Telegram MarkdownV2 이스케이프
# ---------------------------------------------------------------------------
def escape_markdown_v2(text: str) -> str:
    """MarkdownV2에서 특수문자를 이스케이프합니다."""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)


# ---------------------------------------------------------------------------
# Gemini 호출 (Exponential Backoff + 모델 Fallback)
# ---------------------------------------------------------------------------
async def call_gemini_with_retry(client, prompt: str, max_retries: int = 3) -> str:
    """503 UNAVAILABLE 오류 시 재시도하고, 실패 시 다음 모델로 fallback합니다."""
    for model in GEMINI_MODELS:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                print(f"[Gemini] 모델: {model}, 시도: {attempt + 1}")
                return response.text.strip()
            except Exception as e:
                is_unavailable = "503" in str(e) or "UNAVAILABLE" in str(e)
                if is_unavailable and attempt < max_retries - 1:
                    wait_seconds = (2 ** attempt) + random.uniform(0, 1)
                    print(f"[Gemini] 503 오류 → {wait_seconds:.1f}초 후 재시도 ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_seconds)
                elif is_unavailable:
                    print(f"[Gemini] {model} 최대 재시도 초과 → 다음 모델로 전환")
                    break
                else:
                    raise

    raise RuntimeError("모든 Gemini 모델에서 응답을 받지 못했습니다.")


# ---------------------------------------------------------------------------
# 이미지 카드 생성
# ---------------------------------------------------------------------------
def create_image_card(quote: str, source: str) -> io.BytesIO:
    """명언과 출처를 받아 이미지 카드를 생성하고 BytesIO로 반환합니다."""
    width, height = 1200, 800

    # 배경 이미지 랜덤 선택 (스크립트 디렉토리 기준 절대 경로)
    bg_files = [
        f for f in os.listdir(BASE_DIR)
        if f.startswith("background") and f.endswith(".png")
    ]

    base_img = None
    if bg_files:
        selected_bg = os.path.join(BASE_DIR, random.choice(bg_files))
        try:
            base_img = Image.open(selected_bg).convert("RGBA").resize((width, height))
            print(f"[Image] 배경: {os.path.basename(selected_bg)}")
        except Exception as e:
            print(f"[Image] 배경 로드 실패 ({e}) → 기본 배경 사용")

    if base_img is None:
        base_img = Image.new("RGBA", (width, height), color=(35, 39, 46, 255))

    # 가독성 오버레이
    overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 175))
    base_img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(base_img)

    # 폰트 로드
    font_path = os.path.join(BASE_DIR, "font.ttf")
    try:
        font_quote = ImageFont.truetype(font_path, 52)
        font_info = ImageFont.truetype(font_path, 32)
    except OSError:
        font_quote = font_info = ImageFont.load_default()

    # 명언 중앙 배치
    wrapped_lines = textwrap.wrap(quote, width=22)
    line_spacing = 20
    total_h = (
        sum(draw.textbbox((0, 0), line, font=font_quote)[3] for line in wrapped_lines)
        + (len(wrapped_lines) - 1) * line_spacing
    )
    current_h = (height - total_h) / 2 - 30

    for line in wrapped_lines:
        w = draw.textlength(line, font=font_quote)
        draw.text(((width - w) / 2, current_h), line, font=font_quote, fill="#FFFFFF")
        current_h += draw.textbbox((0, 0), line, font=font_quote)[3] + line_spacing

    # 出처 하단 배치
    info_text = f"출처: {source}"
    info_w = draw.textlength(info_text, font=font_info)
    draw.text((width - info_w - 70, height - 100), info_text, font=font_info, fill="#CCCCCC")

    img_bytes = io.BytesIO()
    base_img.convert("RGB").save(img_bytes, format="JPEG", quality=95)
    img_bytes.seek(0)
    return img_bytes


# ---------------------------------------------------------------------------
# 응답 파싱
# ---------------------------------------------------------------------------
def parse_gemini_response(raw_text: str) -> dict:
    """Gemini 응답에서 [문구], [출처], [질문], [태그] 필드를 파싱합니다."""
    data = {"문구": "", "출처": "", "질문": "", "태그": ""}
    for line in raw_text.split("\n"):
        for key in data:
            prefix = f"[{key}]:"
            if line.strip().startswith(prefix):
                data[key] = line.strip()[len(prefix):].strip()
                break
    return data


# ---------------------------------------------------------------------------
# 메인 실행 함수
# ---------------------------------------------------------------------------
async def generate_and_send_quote():
    # 카테고리 먼저 무작위 선택 후 내부 도서 선택 (하이쿠가 배정될 확률 확보를 위함)
    selected_category = random.choice(list(BOOKS.keys()))
    selected_book = random.choice(BOOKS[selected_category])
    print(f"[Bot] 선택된 카테고리: {selected_category} -> 선택된 항목: {selected_book}")

    client = genai.Client(api_key=GENAI_API_KEY)

    # 하이쿠 카테고리인 경우 프롬프트 변경 (요청사항 반영)
    if selected_category == "삶의 통찰(하이쿠)":
        prompt = f"""
인생의 깊은 통찰과 깨달음이 담긴 유명한 하이쿠(Haiku) 한 편을 선정하고 분석을 작성해줘.
도서/주제 제안: {selected_book}

조건:
1. [문구]: 하이쿠의 번역본을 줄바꿈을 활용하여 아름답게 작성 (예: "달팽이야\n쉬엄쉬엄 올라라\n후지산이란다") (이미지 삽입용)
2. [출처]: 하이쿠 작가 이름 (예: 고바야시 잇사)
3. [질문]: (원문 / 번역문)을 서두에 보여주고, 이어서 이 하이쿠가 주는 삶의 숨은 의미와 통찰을 깊이 있게 해석하여 작성해줘. (텔레그램 캡션용)
   * 가독성을 위해 줄바꿈을 명확히 할 것.
4. [태그]: 내용과 어울리는 해시태그 3~5개 (예: #하이쿠 #인생문구 #마음챙김 #명상)

형식을 반드시 엄격히 지킬 것:
[문구]: 내용
[출처]: 내용
[질문]: 내용
[태그]: 내용
"""
    else:
        # 기존 도서 프롬프트 유지
        prompt = f"""
다음 도서에서 핵심 내용을 담은 문장을 작성해줘.
도서: {selected_book}

조건:
1. [문구]: 책의 핵심 내용을 담은 80자 이내의 문장 (이미지 삽입용)
2. [출처]: 책 제목 (p.페이지 번호 포함)
3. [질문]: 위 문구를 읽고 자신의 삶이나 투자에 적용해볼 수 있는 깊은 질문 (캡션용)
4. [태그]: 내용과 어울리는 해시태그 3~5개 (예: #부자아빠 #투자철학 #자기계발)

형식을 반드시 엄격히 지킬 것:
[문구]: 내용
[출처]: 내용
[질문]: 내용
[태그]: 내용
"""

    raw_text = await call_gemini_with_retry(client, prompt)
    data = parse_gemini_response(raw_text)

    if not data["문구"]:
        raise ValueError(f"Gemini 응답 파싱 실패.\n원본 응답:\n{raw_text}")

    if not data["태그"]:
        data["태그"] = "#독서 #인사이트 #자기계발"

    image_data = create_image_card(data["문구"], data["출처"])

    # Telegram MarkdownV2 이스케이프 적용
    source_escaped = escape_markdown_v2(data["출처"])
    question_escaped = escape_markdown_v2(data["질문"])
    tags_escaped = escape_markdown_v2(data["태그"])

    if selected_category == "삶의 통찰(하이쿠)":
        caption = (
            f"🌿 *오늘의 하이쿠*: {source_escaped}\n\n"
            f"💡 *원문/번역문 및 숨은 의미*\n"
            f"{question_escaped}\n\n"
            f"{tags_escaped}"
        )
    else:
        caption = (
            f"📚 *오늘의 도서*: {source_escaped}\n\n"
            f"💡 *성장을 위한 질문*\n"
            f"\"{question_escaped}\"\n\n"
            f"{tags_escaped}"
        )

    async with Bot(token=TELEGRAM_TOKEN) as bot:
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=image_data,
            caption=caption,
            parse_mode="MarkdownV2",
        )

    print(f"[Bot] 전송 완료: {data['출처']}")


if __name__ == "__main__":
    asyncio.run(generate_and_send_quote())
