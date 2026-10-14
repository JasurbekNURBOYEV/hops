from pathlib import Path

MODEL_FILE = Path(__file__).resolve().parent / 'model.pkl'

# messages with scam probability above this are reported to the board group
SCAM_PROBABILITY_THRESHOLD = 0.95

SCANNED_CHAT_TYPES = ('group', 'supergroup')

# on-demand check: the first line is the command, the rest is the text to score
SCAM_CHECK_COMMAND = '!isscam'

SCAM_CHECK_USAGE = "Foydalanish: birinchi qatorga <code>!isscam</code>, keyingi qatorlarga " \
                   "tekshiriladigan matnni yozing."

SCAM_CHECK_RESULT = "{verdict}\n\nScam ehtimolligi: <b>{probability:.1%}</b>"
SCAM_CHECK_VERDICT_SCAM = "⚠️ <b>Scam bo'lishi ehtimoli yuqori</b>"
SCAM_CHECK_VERDICT_NOT_SCAM = "✅ <b>Scamga o'xshamaydi</b>"

POTENTIAL_SCAM_REPORT = "⚠️ <b>Potensial scam xabar</b>\n\n" \
                        "Ehtimollik: <b>{probability:.1%}</b>\n" \
                        "Muallif: <a href=\"tg://user?id={user_id}\">{user_name}</a> (<code>{user_id}</code>)\n" \
                        "Xabar: <a href=\"https://t.me/{chat_identifier}/{message_id}\">havola</a>\n\n"
