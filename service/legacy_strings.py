# STRINGS.py - it is just legacy_strings.py
# this file is the most ugly one, it is highly recommended to close this file right now
# thanks

from service.globals import botlink

source = {
    "keys": ["olma", "yo'lbars", "ruchka", "wifi", "kitob", "toshbaqa", "kaktus", "hamkorlik", "hayot", "kema",
             "televizor", "xanjar", "oyna", "bulut", "stul", "bayroq", "diplom", "tanga", "sirtlon", "tulpor", "tarmoq",
             "python", "monitor", "grafika", "choynak", "apelsin", "diplomat", "kelajak", "daraxt", "bolta", "tuxum",
             "xazina", "onajonim", "xalq", "bolalik", "jannat", "farishta", "tabassum"],
    "warn": "⚠️<b> Guruhda botlar haqida gaplashish taqiqlanadi!</b>\n\n 🍀 Agar bu mavzuga qiziqsangiz, quyidagi "
            "guruhlardan birida fikrlaringizni yozib qoldiring: \n🔹 @botlarhaqida\n🔹 @python_uz_offtopic",
    "new_member": "Salom {name}! Python guruhiga xush kelibsiz!\n\nSiz hozir guruhda faqat o'qiy olasiz. Yozish "
                  "imkoniyatiga ega bo'lish uchun quyidagi link orqali o'ting va qoidalarga roziligingizni "
                  "bildiring: <a href=\"https://t.me/" + botlink + "?start=rules_{user}\">→nazoratchi @"
                  + botlink + " qoidalari←</a>",
    "new_member_rules": "Python guruhida ushbu qoidalarga qat'iy amal qiling:\n\n - botlar haqida gaplashish;\n - "
                        "pythonga aloqasi bo'lmagan mavzularda gaplashish;\n - odob-axloq qoidalariga zid mazmundagi"
                        " gap-so'zlar;\n - guruhga ruxsatsiz bot qo'shish;\n - guruhga kanal, guruh, bot yoki boshqa"
                        " mahsulotlar reklamasini jo'natish;\n - xabar ustiga chiqib ketadigan darajadagi "
                        "belgilarning nikingiz (Telegramdagi taxallusingiz) ga yozilishi taqiqlanadi (Bu guruhda "
                        "o'qish samaradorligini oshirish uchun, iltimos, buni jiddiy qabul qiling).\nAgar shu "
                        "qoidalarga rozi bo'lsangiz hoziroq {key} so'zini yozib jo'nating. Unutmang, qoidaga qarshi"
                        " har qanday harakat jazoga olib kelishi mumkin.",
    "manual": """
Xo'sh, boshladik!
Hozir siz bilan qiloladigan ishlariz haqida gaplashvosak.
(agar rostanam shu hammasini o'qimoqchi bo'sez, rostanam erinmagan banda ekansiz)

⭕️ #books - mana shu heshtegni jo'nating, kamina esa sizga kutubxonamizni ko'rsatadi.
Unda ajoyib (balki g'aroyib) kitoblarni topasiz (o'qishizga kafolat yo'q lekin, ochig'ini aytavering, sizam manga
 o'xshagan bir dangasasiz!).
Kutubxonamiz guruh a'zolari taklif qilgan kitoblar asosida barpo etilgan, dangasalikni yengib o'tolgan kuniz ulani
 o'qib ko'rishiz mumkin ;)
Aytgancha, bu komanda guruhda ishlamaydi, kitob kerak bo'b qosa o'zimga aytaverasiz.

⭕️ /test - mana bu daxshatli komanda! Bosgan zahotiz so'roqqa tutishni boshlayman!
Agar bergan savollarimdan (10 ta) kamida 6 tasiga to'g'ri javob berolsangiz, sizga maxsus 'Shon-sharaf' medali
o'rniga kamtarona sertifikat beramiz.
U medaldan ko'ra ko'proq narsa beradi sizga. Uni olgach guruhimizda Pythonda yozgan kodingizni boshqalarga namoyish
 qilib berishingiz mumkin bo'ladi.
Ochig'ini ayting, baloniyam tushunmadiz! Keling tushuntiraman. Siz guruhda shunchaki kodni jo'natishdan tashqari uni
 ishlatib, natijani olishingiz ham mumkin. Siz kod jo'natasiz, man uni ishga tushirib, natijasini guruhdagilarga
 ko'rsataman.
Faqta shu hadeb 'Hello World' kodlarini tashamang (hazillashmayapman, adminlarimiz ozroq ishkalchiroq, guruhni
chiqish eshigini ko'rsatvorishlari mumkin).
Bu hunarimdan faqat biror jiddiy kodingizni (avval sinab, rostanam ishlashiga ishonch hosil qilib) guruhdagilarga
 jonli namoyish qilish uchun foydalaning.
Bu komandamizam guruhda ishlamaydi, to'g'ri o'zimga yozaverasiz.

⭕️ #py yoki #py2 - mana shu kodingizni ishga tushirish uchun komandalar. #py orqali Python3, #py2 orqali esa
Python2 da yozilgan kodlarni ishga tushira olasiz.
Masalan, <code>print('Hello World!')</code> ni ishlatmoqchisiz deylik, bunday yozasiz:

#py
print('Hello World!')

Unutmang, #py dan keyin probel qo'shmasdan yangi qatorga o'tib kod yozaverasiz.
#py2 bilan ham xuddi shunday ish qilasiz.
Bu ikkala komanda guruhda ham, o'zim bilan chatda ham ishlayveradi. Kodni avval o'zimga yozing, o'xshasa, keyin
 guruhga otvorasiz!

⭕️ comments - xo'sh, nima desam ekan... bu komanda hozir ishlamayapti (oldin ishlardi, dangasa developerimiz
tuzatishga hech qunt qilmadida), bu orqali.. ha mayli, bu shartmas!

Adashmasam, mana shular sizga hozircha yetarli. Qogan narsalani guruhimizda sekin-asta o'rganib boraverasiz.
Kaminani hazillaridan tashqari jiddiy jazolariyam bor, qoidalarga rioya qilsangiz, ishonavering, sizga 3-4 so'm
bermaymizu, lekin tinchgina yurasiz :)
(Mani guruhda Hops deb chaqiring, bot demang, hazillashmadim shu joyida!)
""",
    "congrats": "Juda yaxshi!\nPythonchilar davrasiga xush kelibsiz :)\n\nYana bir bor eslatib o'tamiz: O'zingizni"
                " hurmat qiling va faqat Python haqida gaplashing!",
    "restricted": """⚠️ <a href="tg://user?id={uid}">{}</a> [<code>{uid}</code>] <b>{}</b> soatga "read-only"
     rejimiga tushirildi.\n<b>Sabab:</b> taqiqlangan mavzu ko'tarildi: <i>{words}</i>\n\n⏰ Cheklov {} da olib
      tashlanadi.""",
    "restricted_user": """⚠️ <a href="tg://user?id={}">{}</a> avvaldan ushbu guruhda mavjud bo'lgan va guruh
    adminlari tomonidan cheklov olgan. Cheklovlarni chetlab o'tish maqsadida guruhga qayta kirishga urindi.
    Foydalanuvchi muddat tugashini kutishi kerak.\n\n⏰ Cheklov {} da olib tashlanadi.""",
    "restricted_user_rules": """⚠️ <a href="tg://user?id={}">{}</a> qoidalarga shu paytgacha rozilik bildirmagan
    ko'rinadi. Iltimos, quyidagi tugmani bosing va so'ralgan topshiriqni bajaring. Undan keyin sizga shu guruhda
    yozish imkoniyatini beramiz ;)""",
    "banned": """⚠️ <a href="tg://user?id={uid}">{}</a> [<code>{uid}</code>] <b>{}</b> soatga "read-only" (bu
     muddat juda uzoq, balki bu shunchaki read-only emasdir...) rejimiga tushirildi.\n<b>Sabab:</b> taqiqlangan
      mavzu ko'tarildi: <i>{words}</i>\n\n 🚨 <b>Foydalanuvchi guruhdan haydaldi!</b>""",
    "old_member": """Eski qadrdonimiz <a href="tg://user?id={}">{}</a> safimizga qaytdi""",
    "agreed_already": "Qoidalarga allaqachon rozilik bildirgansiz",
    "stat_good": """Hujjatlar sizni "oppog'oy" ekanligingizni ko'rsatyapti, bir soat ham "o'tirib chiqmagan"
    ekansiza shu paytgacha! Shunday davom eting!""",
    "stat_restricted": "Xo'sh... ancha sho'xlik qb qo'yganakansiz. Naqd {} soatga mehmon bo'bsiz biz tarafda."
                       "\n Kaminani bot emas, Hops deb chaqiring!\n Qoidalarga amal qiling, qat'iy amal qiling"
                       " (hazillashmayapman)!",
    "reo": """<a href="tg://user?id={}">{}</a> vaqti {} soatdan {} soatga o'zgartirildi""",
    "get_cert": "Guruhda kod yozishuchun sertifikat omabsizu!\nBu nari borsa 5 daqiqa vaqt oladi, sertifikat olish"
                " uchun pastdagi tugmani bosing.",
    "get_cert_button": "Sertifikat olish",
    "you_have_new_comment": "<b>📩 Yozgan kodingiz uchun guruhda munosabat bildirildi.</b>\nBarcha izohlarni "
                            "<a href=\"{}\">yagona sahifa</a>da o'qishingiz mumkin.",
    "somebody_liked_your_code": "<b>❤️ Kodingiz guruhimizda kimgadir yoqdi.</b>\nBarcha izohlarni <a href=\"{}\">"
                                "yagona sahifa</a>da o'qishingiz mumkin.",
    "banned_in_entrance": """🚨 <a href="tg://user?id={uid}">{name}</a> <b>guruhdan haydaldi.</b>\n\n⚠️
    Foydalanuvchimiz oxirgi marta guruhdan chiqib ketishidan avval hamma yoqni rasvosini chiqargan ekan. Guruh
    boshqaruvchilari foydalanuvchining cheklov muddatini kamaytirmaguncha u guruhga qaytib kira olmaydi.""",
    "error_in_comment": "Kutilmagan xatolik kelib chiqdi, iltimos bu haqda guruh boshqaruvchilariga xabar bering "
                        "va xatolik tuzalguncha kuting...",
    "book_send_comment": "Ushbu kitob haqidagi fikrlaringizni yozib jo'nating. Qoldirgan izohingiz sizdan keyingi"
                         " o'quvchilar uchun juda foydali bo'lishi mumkin, iltimos, shuni hisobga olgan holda yozing"
                         " izohni.\n\nBekor qilish uchun /cancel buyrug'ini jo'nating.",
    "book_comment_saved": "Izohingiz qo'shib qo'yildi, fikrlar uchun rahmat!",
    "book_choose": "Quyida kitoblar ro'yxati, kitobni yuklab olmoqchi bo'lsangiz, tugma ustiga bosing va kitob "
                   "uchun ajratilgan sahifadan uni yuklab oling",
    "zen": """The Zen of Python UZBEKISTAN Chat
(Inspired by "The Zen of Python, by Tim Peters")

- Short introduction of yourself is better than "hello".
- Link to gist is better than source paste.
- One long message is better than many short.
- Editing the message is better than correcting via another one.
- Staying on topic is better than offtopic.
- Good topic is worth discussing though.
- Unless it is started by a link to Habrahabr.
- Politeness counts.
- Bad mood is not a good reason to break the rules.
- Don't ask to ask just ask.
- Text message is better than voice message.
- Unless it is voice conference.
- Git repos are one honking great idea — let's do more of those!""",
    "zen_uz": """Python UZBEKISTAN guruhining 'The Zen' maslahatlar to'plami
(Tim Peters'ning 'The Zen of Python' qoidalar to'plamidan ilhomlanib yozilgan)

- O'zingiz haqingizdagi qisqa tanishtiruv 'salom' dan yaxshi.
- Kodga link berish uni guruhga tashlashdan yaxshi.
- Bitta uzun xabar bo'laklab jo'natilgan xabarlardan yaxshi.
- Xabarni tuzatish uchun tahrirlab qo'yish yana boshqa bir xabar jo'natishdan yaxshiroq.
- Mavzu haqida gaplashish undan chetlashishdan yaxshi.
- Lekin yaxshi mavzuda gaplashish bu vaqt ajratishga arziydigan hol.
- Faqat u habrahabr ga link berish bilan boshlanmagan bo'lsa.
- Xushmuomalalik ahamiyatga ega.
- Kayfiyatning yomonligi qoidalarni buzishga arzirli sabab bo'lolmaydi.
- So'rash uchun so'ramang, shunchaki savolning o'zini yozing.
- Matnli xabar ovozlisidan yaxshi.
- Faqat agar bu ovozli konferensiya bo'lmasa.
- Botlar haqida alohida guruhlarda gaplashish ularni shu guruhda muhokama qilishdan yaxshiroq.
- Savolni avval Googlega yozish uni o'sha zahoti guruhga jo'natishdan yaxshi.
- Qoidalarga amal qilish adminlarning (ayniqsa Hops) nazariga tushishdan yaxshiroq.
- Uxlashdan oldin tishni yuvib yotish sog'liqqa foydali.""",
    "no_agreement": "Demak, siz bizning qoidalarni yo oxirigacha o'qimadingiz, yo rozi emassiz. Qoidalarga"
                    " rozi bo'lmaguncha guruhda yoza olmaysiz",
    "new_agreement_in_group": """Safimizda yangi a'zo bor!\nHozirgina <a href="tg://user?id={}">{}</a>
    guruh qoidalariga rozilik bildirdi""",
    "bad_word_in_output": "<b>Natijada taqiqlangan mavzu aniqlandi</b>",
    "output": "<b>Natija:</b>\n<code>{}</code>",
    "output_error": "<b>Xatoliklar topildi:</b>\n<code>{}</code>",
    "output_too_large": "<b>Cheklov:</b>\n<code>Natija hajmi juda katta, ruxsat etilgan hajm - 3000 ta belgi</code>",
    "fatal_error": "Kutilmagan xatolik yuz berdi, iltimos, ushbu xabarni @FutureDreams'ga jo'nating",
    "test_cancelled": "Mayli, shu joyida tugatamiz.",
    "test_invalid_cedentials": "Ma'lumotni noto'g'ri kiritdingiz, qayta urinib ko'ring. Testni bekor qilish"
                               " uchun /cancel buyrug'idan foydalaning",
    "user_info": """<b>Cheklovlar:</b>
      - ayni paytda cheklanganmi: {}
      - jami olingan cheklovlar: {} soat
<b>Sertifikat:</b>
      - sertifikat olinganmi: {}
      {}""",
    "user_info_date": "\n\t\t\t\t\t\t- muddat: {} gacha",
    "user_info_scores": """- to'g'ri javoblar soni: {}
      - bugun uchun qolgan limit: {}""",
    "book_comment_cancelled": "Izoh qoldirish bekor qilindi, boshqa safar yozarsiz.",
    "start_test": "Kayfiyatlar qalay ;)\nXo'sh, hozir siz bor yo'g'i 10 dona test ishlaysiz, lekin shuning "
                  "o'zi yetarli bo'ladi. Demak, testni boshlashdan avval tanishib olsak. Ism va familiyangizni"
                  " Ism Familiya shaklida yozib jo'nating. Masalan:\n  Eshmatjon Toshmatov\n\nIltimos, ma'lumotni"
                  " to'g'ri kiriting, ism va familiyangiz sertifikatingizga yoziladi.",
    "rules_taken_by_wrong_user": "Qadrdonim, qoidalarni sizga jo'natmagandim. Ko'k yozuvakan deb bosaverasizmi ;)",
    "comments_all": "<b>Barcha kodlaringiz va izohlar:</b> <a href=\"{}\">bu yerga bosing</a>",
    "comments_not_found": "Hozircha izohlar mavjud emas",
    "test_question": "<b>{}-savol</b>\n{}",
    "user": "Foydalanuvchi",
    "user_info_not_a_member": "Ayni paytda Python guruhi a\'zosi emas",
    "click_the_button": "Mana shu tugmani bosing",
    "new_member_rules_prepare": "Juda yaxshi, hozir siz manga start berasiz, sizni qoidalar bilan "
                                "tanishtirib chiqaman.",
    "new_member_rules_taken_by_wrong_user": "Qo'lingiz bilmasdan boshqa joyga tegib ketdi ;)\nShoshmang,"
                                            " hali sizgayam boshqa biror tugma jo'natarmiz bosishga.",
    "get_cert_completed_success": "Tabriklayman!\n{} darajali sertifikatga ega bo'ldingiz!\nSiz bir kunda {} tagacha"
                                  " kodni Python guruhida yozib jo'natishingiz mumkin!",
    "get_cert_completed_fail": "Berilgan testning {} tasiga javob topa oldingiz. Bu kam, biroz tayyorlanib, qayta"
                               " urinib ko'ring.",
    "get_cert_button_taken_by_wrong_user": "Bu tugmani sizga jo'natmagandim, anavi akaxonimizga aytib qo'ying, "
                                           "tezroq harakatini qilsin. Baribir sertifikat omaguncha qo'ymayman!",

}


def get_string(key=None):
    if str(key) in source.keys():
        return source.get(str(key))
    else:
        return 'STR_NOT_FOUND'
