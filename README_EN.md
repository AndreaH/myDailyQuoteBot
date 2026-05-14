# 📚 AI Daily Book Quote Bot

> **Intelligent Reading Coach Automation System Powered by Gemini 2.0 & Telegram**

This project is an automated service that extracts insights from book list images or curated masterpiece lists, delivering insightful quotes via Telegram **every morning at 8:00 AM (KST)**.

---

## 🚀 Key Features

* **Intelligent Quote Extraction:** Leverages Gemini 1.5/2.0 Flash models to generate concise recommended quotes (~50 characters) that reflect the core philosophy of each book.
* **Full Automation:** Utilizes the GitHub Actions scheduler to operate daily at fixed times with zero server costs.
* **Multimodal Support:** Supports both direct analysis of book thumbnail images and curation based on text-based lists.
* **Customized Notifications:** Delivers personalized messages directly to users through a Telegram bot.

---

## 🛠 Tech Stack

* **Language:** Python 3.11+
* **AI Model:** Google Gemini API (`google-genai`)
* **Automation:** GitHub Actions
* **Interface:** Telegram Bot API (`python-telegram-bot`)

---

## ⚙️ Setup & Installation

### 1. Environment Variables (Secrets) Configuration

You must register the following items in your GitHub repository under `Settings > Secrets and variables > Actions`:

| Name | Description |
| --- | --- |
| `GEMINI_API_KEY` | API Key obtained from [Google AI Studio](https://aistudio.google.com/) |
| `TELEGRAM_TOKEN` | Bot token generated via [@BotFather](https://t.me/botfather) |
| `CHAT_ID` | Telegram ID of the user who will receive the messages |

### 2. Local Testing

```bash
# Clone the repository
git clone [https://github.com/your-username/myDailyQuoteBot.git](https://github.com/your-username/myDailyQuoteBot.git)

# Install dependencies
pip install google-genai python-telegram-bot

# Run the script
python daily_quote_bot.py

```

---


## 📅 Execution Schedule (Cron)

This project runs on the following schedule via GitHub Actions:

* **Scheduled Time:** 23:00 UTC daily (equivalent to **08:00 AM KST**)
* **Workflow File:** `.github/workflows/daily_quote.yml`

```yml
name: AI Daily Book Quote Bot

on:
  schedule:
    # 23:00 UTC is 08:00 AM KST
    - cron: '0 23 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install google-genai python-telegram-bot
      - name: Run Bot
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
        run: python daily_quote_bot.py
```
---

## 📝 Book List (Dataset)

Currently, the project generates quotes based on curated masterpieces such as:

* Finance: *he Property of Money, The Millionaire Fastlane, Leverage...*
* Self-Improvement: *The One Thing, Grit, Atomic Habits...*
* Real Estate: *Retire as a Salaried Rich Person, The Essence of Real Estate Investment....*

---

## 🤝 Contribution

Contributions to add new books to the list or suggestions for functional improvements are always welcome via **Pull Request** or **Issue**.

---

### 💡 Roadmap

* [ ] Integration with reading record databases (e.g., Notion)
* [ ] Daily-themed curation focusing on specific categories (Real Estate, Mindset, etc.)

---
* Telegram Channel : https://t.me/+v1Fzyca60u5jN2M1
