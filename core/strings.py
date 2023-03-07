"""
We store all strings for communication with users here
"""
from typing import List, Tuple


class Strings(object):
    """
    The class mostly consists of static fields
    """
    # strings related to testing process
    welcome = "Hey! Ahvollar qalay!"
    you_are_not_a_member = "Botdan foydalanish uchun asosiy guruh a'zosi bo'lishingiz kerak."

    # new member
    new_member = "Salom <a href=\"tg://user?id={uid}\">{name}</a>! Python guruhiga xush kelibsiz!\n\nSiz hozir " \
                 "guruhda faqat o'qiy olasiz. Yozish imkoniyatiga ega bo'lish uchun quyidagi tugmani bosing va " \
                 "qoidalarga roziligingizni bildiring"
    new_member_button_text = "Bu yerga bosing"
    new_member_old_comrade_back = 'Eski qadrdonimiz <a href="tg://user?id={uid}">{name}</a> safimizga qaytdi'
    new_member_already_restricted = '⚠️ <a href="tg://user?id={uid}">{name}</a> avvaldan ushbu guruhda mavjud bo\'lgan ' \
                                    'va guruh adminlari tomonidan cheklov olgan. Cheklovlarni chetlab o\'tish maqsadida' \
                                    'guruhga qayta kirishga urindi. Foydalanuvchi muddat tugashini kutishi kerak.' \
                                    '\n\n⏰ Cheklov {time} da olib tashlanadi.'
    new_member_not_agreed_yet = '⚠️ <a href="tg://user?id={uid}">{name}</a> qoidalarga shu paytgacha rozilik ' \
                                'bildirmagan ko\'rinadi. Iltimos, quyidagi tugmani bosing va so\'ralgan topshiriqni ' \
                                'bajaring. Undan keyin sizga shu guruhda yozish imkoniyatini beramiz;)'
    new_member_button_pressed_by_wrong_user = "Qo'lingiz bilmasdan boshqa joyga tegib ketdi ;)\nShoshmang," \
                                              " hali sizgayam boshqa biror tugma jo'natarmiz bosishga."
    new_member_rules = "Python guruhida ushbu qoidalarga qat'iy amal qiling:\n\n - botlar haqida gaplashish;\n - " \
                       "pythonga aloqasi bo'lmagan mavzularda gaplashish;\n - odob-axloq qoidalariga zid mazmundagi" \
                       " gap-so'zlar;\n - guruhga ruxsatsiz bot qo'shish;\n - guruhga kanal, guruh, bot yoki boshqa" \
                       " mahsulotlar reklamasini jo'natish;\n - xabar ustiga chiqib ketadigan darajadagi " \
                       "belgilarning nikingiz (Telegramdagi taxallusingiz) ga yozilishi taqiqlanadi (Bu guruhda " \
                       "o'qish samaradorligini oshirish uchun, iltimos, buni jiddiy qabul qiling).\nAgar shu " \
                       "qoidalarga rozi bo'lsangiz hoziroq {key} so'zini yozib jo'nating. Unutmang, qoidaga qarshi" \
                       " har qanday harakat jazoga olib kelishi mumkin."
    new_member_congrats = "Juda yaxshi!\nPythonchilar davrasiga xush kelibsiz :)\n\nYana bir bor eslatib o'tamiz: " \
                          "O'zingizni hurmat qiling va faqat Python haqida gaplashing!"
    new_member_welcome = "Safimizda yangi a'zo bor!\nHozirgina <a href=\"tg://user?id={uid}\">{name}</a> guruh" \
                         " qoidalariga rozilik bildirdi"
    new_member_wrong_key = "Demak, siz bizning qoidalarni yo oxirigacha o'qimadingiz, yo rozi emassiz. Qoidalarga" \
                           " rozi bo'lmaguncha guruhda yoza olmaysiz"
    new_member_already_agreed = "Qoidalarga allaqachon rozilik bildirgansiz"

    # test
    start_test = "Kayfiyatlar qalay ;)\nXo'sh, hozir siz bor yo'g'i {count} dona test ishlaysiz, lekin shuning " \
                 "o'zi yetarli bo'ladi. Demak, testni boshlashdan avval tanishib olsak. Ism va familiyangizni" \
                 " Ism Familiya shaklida yozib jo'nating. Masalan:\n  Eshmatjon Toshmatov\n\nIltimos, ma'lumotni" \
                 " to'g'ri kiriting, ism va familiyangiz sertifikatingizga yoziladi."
    test_start_inline_button_text = "Bu yerga bosing"
    test_should_start_for_certificate = "Guruhda kod yozishuchun sertifikat omabsizu!\nBu nari borsa 5 daqiqa vaqt " \
                                        "oladi, sertifikat olish uchun pastdagi tugmani bosing."
    test_start_button_clicked_by_wrong_user = "Bu tugmani sizga jo'natmagandim, anavi akaxonimizga aytib qo'ying, " \
                                              "tezroq harakatini qilsin. Baribir sertifikat omaguncha qo'ymayman!"
    test_question_template = "<b>{index}-savol</b>\n{question}"
    test_quizzes_not_found = "Bermoqchi bo'lgan savollarimni unutib qo'ydim... Kamina borib savollarni qidirib " \
                             "kelaman. Bu balki 1 soat olar, balki 1 oy, yil... Biroz vaqt o'tib yana qayta kelib " \
                             "tekshiring, balki o'shanda savollarni eslagan bo'larman."
    test_full_name_invalid = "Bu negadir odam bolasining ismiga o'xshamadi, qaytadan ismga o'xshaganroq ism kiritib " \
                             "ko'rarsiz balki..."
    test_quiz_not_found = "Qiziq, savolni unutib qo'ydim... Qanaqa savol edi u, koinot haqidami, baliqlar haqidami..." \
                          " balki hammasini boshidan boshlarmiz? /{command} buyrug'ini bering, savollarni qaytadan " \
                          "eslashga urinib ko'raman"
    test_quiz_option_not_found = "Xotiram pand berishni boshladi, hozirgina o'zim bergan variantni esdan chiqarib " \
                                 "qo'ydim. Endi uni qayta eslolmasligim aniq. Hammasini boshidan boshlarmiz balki? " \
                                 "/{command} buyrug'ini bering."
    test_result_failure = "Berilgan testning {} tasiga javob topa oldingiz. Bu kam, biroz tayyorlanib, qayta" \
                          " urinib ko'ring."
    test_result_success = "Tabriklayman!\n{class_name} darajali sertifikatga ega bo'ldingiz!\nSiz bir kunda {limit}" \
                          " tagacha kodni Python guruhida yozib jo'natishingiz mumkin!\n\nUNUTMANG: kodni guruhga " \
                          "jo'natishdan oldin o'zimga yozishingiz eng yaxshi usul. Bu orqali siz kunlik limitni " \
                          "saqlab qolasiz va guruhdagilarga xato kodni ko'rsatib qo'yishning oldini olasiz."
    test_calulating_the_result = "natijangizni hisoblayapman..."
    test_certificate_image_generation_failed = "Rassom ishni chala qildi, sertifikatni rasmini oxiriga " \
                                               "yetkazolmadik. Keyinroq tayyor bo'b qolsa sizga o'zim jo'natib " \
                                               "qo'yaman."
    test_class_not_found = "Test natijalarini hisoblashda nimadir xato ketdi. Katta ehtimol bilan, olgan ballingiz" \
                           " birorta darajaga mos kelmadi"

    # code running
    code_please_provide_input = "Yozgan kodingiz input talab qiladigan kodga o'xshadi. Uni ishlatishim uchun" \
                                " shu kodga reply qilib inputni yozing. Har bir qator bitta input uchun matn " \
                                "hisoblanadi. Kodingizda bir nechta input bo'lsa, bir necha qator matn bilan " \
                                "reply qilishingiz mumkin. \n\nInput berish quyidagicha:\n\n" \
                                "<code>{input_header}birinchi input\nikkinchi input\nuchinchi input...</code>"
    code_result_template = "<b>Natija</b>\n<code>{result}</code>"
    code_result_error_template = "<b>Xatolik</b>\n<code>{errors}</code>"
    code_result_errors_detected_tip = "Guruhda kod yozganingizda xatolik chiqmasligi uchun, avval kodni mana shu " \
                                      "yerda <b>o'zimga jo'nating</b>, xatolari bo'lsa ko'rib, tuzatvolib, keyin " \
                                      "guruhga jo'natasiz. \n<b>Bu orqali siz guruhdagi kunlik limitlaringizni saqlab" \
                                      " qolasiz, chunki o'zimga kod yozganingizda limitlaringiz kamaymaydi.</b>"
    code_limit_exceeded = "Bugungi kun uchun limitlaringiz tugab qoldi, ertaga yana kod yoa olasiz"
    code_response_too_long = "Natija hajmi juda katta, ruxsat etilgan hajm - {limit} ta belgi"
    code_server_fatal_error = "Nimadir sindi..."
    code_no_results_no_errors = "Hech qanday natija chiqmadi. Bu kod o'zi xato yozilganmidi yoki kamina adashdimi?"
    code_webview_button_text = "Kodni veb sahifada ko'rish & ulashish"

    # prohibited topics
    prohibited_topic_detected = "{user_name} [<code>{user_id}</code>] taqiqlangan mavzudagi gaplari uchun {date} " \
                                "gacha guruhda yozishdan cheklab qo'yildi. \nQuyidagi taqiqlangan mavzular " \
                                "aniqlandi: {topics}"
    prohibited_topic_template = "<b>{topic_name}</b> mavzusi bo'yicha: {words}\n\n{hint}"
    prohibited_topic_with_tip_template = "<b>{tip}</b>\n\n{description}"
    prohibited_topic_in_code_response = "Kod natijasida taqiqlangan mavzu aniqlandi"
    restricted_until_time = '%Y-yil, {day}-{month}, soat %H:%M'
    restrictions_lifted = "Oxirgi cheklov olib tashlandi"
    restriction_cant_lift_time_too_little = "Hey! Cheklov vaqti allaqachon judayam kichkina (balki 0 dan kichikroq), " \
                                            "boshqa cheklovni kamaytirolmaymiz"

    # admins
    admins_chaos_disorder = "Shovqin ko'tarildi! Trevoga: <a href=\"https://t.me/{chat_id}/{message_id}\">xabar</a>"
    admins_alerted_tip_for_user = "Hey! Kapitanlar xavfdan ogohlantirildi. Lekin bu rostanam hammani bezovta " \
                                  "qilishga arzirmidi? Har doim ogohlantirishdan avval shuni o'ylab ko'ring. " \
                                  "Xabarni kapitanlarimiz tekshirib chiqishadi, ogohlantirish uchun rahmat ✌️"
    admin_check_user_details_template = "<b>Sertifikat:</b> {certificate}\n" \
                                        "<b>Oxirgi cheklov:</b> {last_restriction}\n" \
                                        "<b>Kunlik limit:</b> {remaining_daily_limit}"

    # greed island strings, shortly gi

    gi_tag_changed_by_master = "♻️ Siz qo'shgan tag {old} o'zgardi, endi u {new}. " \
                               "Keyingi safar uni {new} holatida ishlatishingizni so'raymiz."
    gi_tag_removed_by_master = "❌ Siz qo'shgan tag {tag} o'chirib qo'yildi. Iltimos, uni boshqa " \
                               "ishlatmang. O'chirilishiga sabab quyidagilardan biri bo'lishi mumkin: " \
                               "\n - bunaqa mazmundagi tag allaqachon mavjud edi" \
                               "\n - bu tag guruh mavzusiga mos emas" \
                               "\n - tagda xatolik bor" \
                               "\n - tagda boshqa muammo bor"

    @property
    def gi_tag_format(self) -> str:
        return "#{tag}"

    gi_new_question_received = "Siz ulangan taglar ({tags}) bo'yicha yangi savol keldi.\n\n" \
                               "<i>{question}</i>\n\n" \
                               "📩 <a href=\"{link_to_message}\">Xabarga o'tish</a>  " \
                               "🕵️‍♂️ <a href=\"{thread_link}\">Muhokamaga o'tish</a>"
    gi_answer_accepted_by_questioner = "Siz bergan <a href=\"{link_to_answer_message}\">javob</a> savol bergan odam " \
                                       "tomonidan to'g'ri, deb qabul qilindi"
    gi_answer_accepted_by_admin = "Siz bergan <a href=\"{link_to_answer_message}\">javob</a> adminlar " \
                                  "tomonidan to'g'ri, deb qabul qilindi"

    @property
    def gi_tags_list(self) -> str:
        return f"Format: {self.gi_tag_format.format(tag='tag')} (a'zolar soni).\n\n" \
               "{tags_list}\n\n" \
               "⚠️ Yuqorida eng ko'pida 10 dona tag ko'rsatildi. Hamma taglarni ko'rish va taglarga a'zo bo'lish, " \
               "a'zolikni bekor qilish uchun <b>'Tag dashboard'</b>ga o'ting."

    gi_tag_dashboard_button_text = "Tag dashboard"
    gi_accept_answer_commands: List[str] = ["✅"]
    gi_question_tag = "savol"
    gi_answer_tag = "javob"
    gi_marked_as_question = "<a href=\"{msg_link}\">Xabar</a> savol qilib belgilandi va quyidagi taglar qo'shildi: " \
                            "{new_tags}\n\nJami taglar: {all_tags}"
    gi_tags_tutorial_link = "https://telegra.ph/Tags-tags-tags-08-17"

    @property
    def gi_marked_as_question_to_author(self):
        return "Sizning <a href=\"{msg_link}\">bu xabaringiz</a> adminlar tomonidan 'savol' qilib " \
               f"belgilab qo'yildi. Iltimos, keyingi safar savol berganda uni " \
               f"{self.gi_tag_format.format(tag=self.gi_question_tag)} tagi bilan qo'shib yozing.\n\n" \
               f"Buni to'liqroq o'rganishingiz uchun maqola: {self.gi_tags_tutorial_link}"

    gi_answer_marked_as_correct = "<a href=\"{msg_link}\">Javob</a> to'g'ri deb belgilab qo'yildi."

    @property
    def gi_answer_marked_as_correct_by_admin(self):
        return "<a href=\"{msg_link}\">Javob</a> adminlar tomonidan to'g'ri deb belgilab qo'yildi. Iltimos, keyingi " \
               "safar kimdir savolingizga to'g'ri javob bersa, o'sha xabarga javoban (reply qilib) quyidagilardan " \
               f"birini yozing: {', '.join(self.gi_accept_answer_commands)}\n" \
               f"Shunda javob to'g'ri deb belgilab qo'yiladi." \
               f"Buni batafsil o'rganishingiz uchun maqola: {self.gi_tags_tutorial_link}"

    gi_failed_to_mark_as_question = "<a href=\"{msg_link}\">Xabar</a>ni savol qilib belgilab bo'lmadi"

    gi_marked_as_answer = "<a href=\"{msg_link}\">Xabar</a> javob qilib belgilab qo'yildi"
    gi_failed_to_mark_as_answer = "<a href=\"{msg_link}\">Xabar</a>ni javob qilib belgilab bo'lmadi"
    gi_tag_removed_from_question = "<a href=\"{msg_link}\">Savol</a>dan mana bu taglar olib tashlandi: " \
                                   "{removed_tags}\n\nQuyidagi taglar qoldi: {remaining_tags}"

    @property
    def gi_marked_as_answer_to_author(self):
        return "Siz <a href=\"{msg_link}\">yozgan xabarni</a> adminlar 'javob' qilib belgilab qo'ydi. Iltimos, " \
               f"keyingi safar savolga javob berganingizda {self.gi_tag_format.format(tag=self.gi_answer_tag)} tagini" \
               f" qo'shib yozing. \n\nBuni to'liqroq o'rganishingiz uchun maqola: {self.gi_tags_tutorial_link}"

    # generally used strings
    cancelled = "Jarayon bekor qilindi"
    step_not_matched = "Nima?"
    empty = '-'

    keys = ["olma", "yo'lbars", "ruchka", "wifi", "kitob", "toshbaqa", "kaktus", "hamkorlik", "hayot", "kema",
            "televizor", "xanjar", "oyna", "bulut", "stul", "bayroq", "diplom", "tanga", "sirtlon", "tulpor", "tarmoq",
            "python", "monitor", "grafika", "choynak", "apelsin", "diplomat", "kelajak", "daraxt", "bolta", "tuxum",
            "xazina", "onajonim", "xalq", "bolalik", "jannat", "farishta", "tabassum"
            ]

    @staticmethod
    def clean_html(text: str) -> str:
        """
        To replace html chars with their equivalences
        :param text: input data
        :return: clean text
        """
        if not text:
            return text
        gt = (">", "&gt;")
        lt = ("<", "&lt;")
        amp = ("&", "&amp;")
        return text.replace(amp[0], amp[1]).replace(gt[0], gt[1]).replace(lt[0], lt[1])

    @staticmethod
    def resize(text, max_size: int, ellipsis_at_end: bool = False) -> str:
        if not text:
            return text
        # resize the string and return it
        if len(text) > max_size:
            if ellipsis_at_end:
                return f"{text[:max_size].strip()}..."
            return f"{text[:max_size // 2].strip()}...{text[-max_size // 2:].strip()}"
        return text

    @staticmethod
    def month_to_str(month):
        months = {
            1: 'yanvar',
            2: 'fevral',
            3: 'mart',
            4: 'aprel',
            5: 'may',
            6: 'iyun',
            7: 'iyul',
            8: 'avgust',
            9: 'sentabr',
            10: 'oktabr',
            11: 'noyabr',
            12: 'dekabr'
        }
        return months.get(month, '¯\_(ツ)_/¯')

    @staticmethod
    def clean_text(text: str, spoilers: List[Tuple[str]]) -> str:
        """
        To clean the text from redundant chars...
        :param text: incoming message text
        :param spoilers: spoiler words and their alternatives
        :return: clean text
        """
        # reveal spoilers in text
        for spoiler, alternative in spoilers:
            text = text.replace(spoiler, alternative)
        # get rid of non-numeric & non-alpha chars
        for char in text:
            if not char.isalnum() and char != " ":
                text = text.replace(char, "")
        # translate kirill text
        letters = {
            'а': 'a',
            'б': 'b',
            'д': 'd',
            'э': 'e',
            'ф': 'f',
            'г': 'g',
            'ҳ': 'h',
            'и': 'i',
            'ж': 'j',
            'к': 'k',
            'л': 'l',
            'м': 'm',
            'н': 'n',
            'о': 'o',
            'п': 'p',
            'қ': 'q',
            'р': 'r',
            'с': 's',
            'т': 't',
            'у': 'u',
            'в': 'b',
            'х': 'x',
            'й': 'y',
            'з': 'z',
            'ў': 'o\'',
            'ғ': 'g\'',
            'ш': 'sh',
            'ч': 'ch',
            'е': 'ye',
            'ё': 'yo',
            'ю': 'yu',
            'я': 'ya',
            'ъ': '\'',
            'ы': 'y'
        }
        for letter, translation in letters.items():
            text = text.replace(letter, translation)
        return text
