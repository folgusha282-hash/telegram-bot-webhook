import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")   # Токен бота, задаётся в Render
CHANNEL_ID = "@shibaoma"             # Твой канал (замени, если нужно)
PDF_FILE = "guide.pdf"               # Имя файла в папке static

def check_subscription(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {"chat_id": CHANNEL_ID, "user_id": user_id}
    try:
        resp = requests.get(url, params=params).json()
        if resp.get("ok"):
            status = resp["result"]["status"]
            return status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
    return False

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]

    # Обрабатываем нажатие на кнопку "Готово! Получить🎁" (callback_data = get_gift)
    if intent == "Get Gift Callback":
        # Достаём user_id из callback_query
        callback_data = req["originalDetectIntentRequest"]["payload"]["data"]["callback_query"]
        user_id = callback_data["from"]["id"]

        if check_subscription(user_id):
            # 1. Текстовое сообщение
            text_msg = {
                "payload": {
                    "telegram": {
                        "text": "Отлично!🤗 Лови подарки:\n📔ПОЛНЫЙ гайд по использованию частицы 了, который РАБОТАЕТ и объяснит до 90% всех употреблений",
                        "parse_mode": "HTML"
                    }
                }
            }
            # 2. PDF-файл из папки static
            base_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
            pdf_url = f"{base_url}/static/{PDF_FILE}"
            file_msg = {
                "payload": {
                    "telegram": {
                        "document": pdf_url,
                        "caption": "Гайд по 了.pdf"
                    }
                }
            }
            return jsonify({"fulfillmentMessages": [text_msg, file_msg]})
        else:
            # Если не подписан – просим подписаться
            return jsonify({"fulfillmentMessages": [
                {"payload": {"telegram": {
                    "text": "Ты ещё не подписался на канал 😕\nПодпишись: https://t.me/shibaoma\nи нажми кнопку ещё раз."
                }}}
            ]})

    # Если интент не распознан – просто отвечаем "ок"
    return jsonify({"fulfillmentText": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
