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
