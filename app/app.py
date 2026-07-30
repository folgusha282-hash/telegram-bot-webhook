import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@shibaoma"   # замени на свой канал, если нужно
PDF_FILE = "guide.pdf"    # название файла в папке static

def check_subscription(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {"chat_id": CHANNEL_ID, "user_id": user_id}
    resp = requests.get(url, params=params).json()
    if resp.get("ok"):
        status = resp["result"]["status"]
        return status in ["member", "administrator", "creator"]
    return False

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]

    if intent == "Get Gift Callback":
        user_id = req["originalDetectIntentRequest"]["payload"]["data"]["callback_query"]["from"]["id"]

        if check_subscription(user_id):
            text_msg = {
                "payload": {
                    "telegram": {
                        "text": "Отлично!🤗 Лови подарки:\n📔ПОЛНЫЙ гайд по использованию частицы 了, который РАБОТАЕТ и объяснит до 90% всех употреблений",
                        "parse_mode": "HTML"
                    }
                }
            }
            # Формируем ссылку на PDF, который будет лежать рядом в папке static
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
            return jsonify({"fulfillmentMessages": [
                {"payload": {"telegram": {
                    "text": "Ты ещё не подписался на канал 😕\nПодпишись: https://t.me/shibaoma\nи нажми кнопку ещё раз."
                }}}
            ]})

    return jsonify({"fulfillmentText": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
