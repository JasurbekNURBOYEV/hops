"""
We store all strings for communication with users here
"""


class Strings(object):
    """
    The class mostly consists of static fields
    """
    # strings related to testing process
    start_test = "Kayfiyatlar qalay ;)\nXo'sh, hozir siz bor yo'g'i 10 dona test ishlaysiz, lekin shuning " \
                 "o'zi yetarli bo'ladi. Demak, testni boshlashdan avval tanishib olsak. Ism va familiyangizni" \
                 " Ism Familiya shaklida yozib jo'nating. Masalan:\n  Eshmatjon Toshmatov\n\nIltimos, ma'lumotni" \
                 " to'g'ri kiriting, ism va familiyangiz sertifikatingizga yoziladi."
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
    # generally used strings
    cancelled = "Jarayon bekor qilindi"
    step_not_matched = "Nima?"

