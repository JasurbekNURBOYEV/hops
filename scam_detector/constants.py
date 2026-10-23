from pathlib import Path

MODEL_FILE = Path(__file__).resolve().parent / 'model.pkl'

# messages with scam probability above this are reported to the board group, which decides what to do
SCAM_REPORT_THRESHOLD = 0.80
# above this we are confident enough to delete the message ourselves (the board group still gets a report)
SCAM_REMOVE_THRESHOLD = 0.95

SCANNED_CHAT_TYPES = ('group', 'supergroup')

# on-demand check: the first line is the command, the rest is the text to score
SCAM_CHECK_COMMAND = '!isscam'

SCAM_CHECK_USAGE = "Foydalanish: birinchi qatorga <code>!isscam</code>, keyingi qatorlarga " \
                   "tekshiriladigan matnni yozing."

SCAM_CHECK_RESULT = "{verdict}\n\nScam ehtimolligi: <b>{probability:.1%}</b>"
SCAM_CHECK_VERDICT_SCAM = "⚠️ <b>Scam bo'lishi ehtimoli yuqori</b>"
SCAM_CHECK_VERDICT_SUSPICIOUS = "❔ <b>Scam bo'lishi mumkin</b>"
SCAM_CHECK_VERDICT_NOT_SCAM = "✅ <b>Scamga o'xshamaydi</b>"

POTENTIAL_SCAM_REPORT = "⚠️ <b>Potensial scam xabar</b>\n\n" \
                        "Ehtimollik: <b>{probability:.1%}</b>\n" \
                        "Muallif: <a href=\"tg://user?id={user_id}\">{user_name}</a> (<code>{user_id}</code>)\n" \
                        "Xabar: <a href=\"https://t.me/{chat_identifier}/{message_id}\">havola</a>\n\n"

# remove button on the report: deletes the reported message from its group
CALLBACK_DATA_HEADER_REMOVE = 'scamremove'
CALLBACK_DATA_REMOVE_TEMPLATE = CALLBACK_DATA_HEADER_REMOVE + '_{chat_id}|{message_id}'
REMOVE_BUTTON_TEXT = "🗑 F"
REMOVE_FAILED = "Xabarni o'chirib bo'lmadi (allaqachon o'chirilgan yoki botda huquq yo'q)."
REMOVED_BY = "🗑 <a href=\"tg://user?id={user_id}\">{user_name}</a> tomonidan o'chirildi"
REMOVED_AUTOMATICALLY = "🗑 Avtomatik o'chirildi"
