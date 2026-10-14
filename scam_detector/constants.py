from pathlib import Path

MODEL_FILE = Path(__file__).resolve().parent / 'model.pkl'

# messages with scam probability above this are reported to the board group
SCAM_PROBABILITY_THRESHOLD = 0.95

SCANNED_CHAT_TYPES = ('group', 'supergroup')

POTENTIAL_SCAM_REPORT = "⚠️ <b>Potensial scam xabar</b>\n\n" \
                        "Ehtimollik: <b>{probability:.1%}</b>\n" \
                        "Muallif: <a href=\"tg://user?id={user_id}\">{user_name}</a> (<code>{user_id}</code>)\n" \
                        "Xabar: <a href=\"https://t.me/{chat_identifier}/{message_id}\">havola</a>\n\n"
