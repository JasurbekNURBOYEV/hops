# coding:utf8
"""
Necessary tools
"""
import json
from datetime import *
import re
from files import File as f
from globals import bot, dev, should_log


def log(*data):
    if should_log:
        bot.send_message(dev, ', '.join([str(x) for x in data]), parse_mode='html')


def resizer(name):
    sizes = {
        '1': 100,
        '2': 92,
        '3': 82,
        '4': 79,
        '5': 71,
        '6': 70,
        '7': 65,
        '8': 60,
        '9': 58,
        '10': 55,
        '11': 52,
        '12': 50,
        '13': 45,
        '14': 43,
        '15': 41,
        '16': 40,
        '17': 40,
        '18': 38,
        '19': 37,
        '20': 36,
        '21': 34,
        '22': 33,
        '23': 32,
        '24': 31,
        '25': 30
    }
    if len(name) > 25:
        return [30, name[:24] + '...']
    return [sizes[str(len(name))], name]


def anti_spam(text):
    patterns = ['^[🤔?]*$']
    for pattern in patterns:
        if len(re.findall(pattern, text)) > 0:
            return True
    return False


url = "https://futuredreams.imgix.net/~text&test.jpg?&txt={text}&txtclr=fff&txtsize={size}&txtpad=39&txtalign=right,middle&txtclip=ellipsis,middle&fm=jpg&txtshad=15"

questions = {
    '1': {
        "question": "Python dasturlash tilining asoschisi kim?",
        "answers":
            [
                {"key": "Guido van Rossum", "isTrue": True},
                {"key": "Monty Python", "isTrue": False},
                {"key": "Stefen Houking", "isTrue": False},
                {"key": "Pavel Durov", "isTrue": False}
            ]
    },
    '2': {
        "question": "Quyidagilar qanday nomlanadi:<code>\n\n\t+, 0, 'Integer'</code>",
        "answers":
            [
                {"key": "Integer, operator, string", "isTrue": False},
                {"key": "String, operator, integer", "isTrue": False},
                {"key": "Operator, string, integer", "isTrue": False},
                {"key": "Operator, integer, string", "isTrue": True}
            ]
    },
    '3': {
        "question": "<b>input()</b> funksiyasi qanday turdagi qiymat qaytaradi?",
        "answers":
            [
                {"key": "List", "isTrue": False},
                {"key": "String", "isTrue": True},
                {"key": "Integer", "isTrue": False},
                {"key": "Qiymat qaytarmaydi", "isTrue": False}
            ]
    },
    '4': {
        "question": "Quyidagi \"figurali qavslar\" orqali qanday turdagi ma'lumotlar hosil qilish mumkin:\n\n\t{}",
        "answers": [{"key": "Set", "isTrue": False},
                    {"key": "Dict", "isTrue": False},
                    {"key": "List", "isTrue": False},
                    {"key": "Set yoki dict", "isTrue": True}
                    ]
    },
    '5': {
        "question": "for bu ...",
        "answers":
            [
                {"key": "Qiymat qaytaruvchi funksiya", "isTrue": False},
                {"key": "Sikl", "isTrue": True},
                {"key": "Qiymat qaytarmaydigan funksiya", "isTrue": False},
                {"key": "Operator", "isTrue": False}
            ]
    },
    '6': {
        "question": "Quyidagi kod qanday natija qaytaradi?<code>\n\n\ta = 5\n\tb = 2\n\tc = a % b\n\tprint(c)</code>",
        "answers":
            [
                {"key": "1", "isTrue": True},
                {"key": "2", "isTrue": False},
                {"key": "10", "isTrue": False},
                {"key": "25", "isTrue": False}
            ]
    },
    '7': {
        "question": "Quyidagi kod qanday natija qaytaradi?<code>"
                    "\n\n\ta = ['12', '21']\n\tb = '11' + a[1]\n\tprint(b)</code>",
        "answers":
            [
                {"key": "1112", "isTrue": False},
                {"key": "23", "isTrue": False},
                {"key": "1121", "isTrue": True},
                {"key": "32", "isTrue": False}]},
    '8': {
        "question": "Quyidagi kod qanday natija qaytaradi?<code>"
                    "\n\n\ta, b = 1, 2\n\tb = a\n\tx, y = b, a\n\tc = str(x) * y\n\tprint(c)</code>",
        "answers": [{"key": "1", "isTrue": True}, {"key": "2", "isTrue": False}, {"key": "11", "isTrue": False},
                    {"key": "21", "isTrue": False}]},
    '9': {
        "question": "Quyidagi kod qanday natija qaytaradi?<code>"
                    "\n\n\ta = 2\n\tb = -2\n\twhile a >= 0:\n\t\tb = b ** a\n\t\ta -= 1\n\tprint(b)</code>",
        "answers": [{"key": "4", "isTrue": False}, {"key": "-4", "isTrue": False}, {"key": "-5", "isTrue": False},
                    {"key": "1", "isTrue": True}]},
    '10': {"question": "Quyidagi kod qanday natija qaytaradi?<code>\n\n\tprint(4 + 5 = 9)</code>",
           "answers": [{"key": "Kod xato", "isTrue": True}, {"key": "1", "isTrue": False},
                       {"key": "True", "isTrue": False}, {"key": "18", "isTrue": False}]},
}


def btn_maker(ind, score=0):
    from telebot import types
    k = types.InlineKeyboardMarkup()
    question = questions[str(ind)]
    answers = question['answers']
    n = 0
    for i in answers:
        k.row(types.InlineKeyboardButton(
            text=i['key'],
            callback_data="test_{}_{}_{}_{}".format(ind, i['isTrue'], score, n))
        )
        n += 1
    return k


def check_name(name):
    class Name:
        def __init__(self, name):
            if len(name.split()) == 2:
                self.valid = True
            else:
                self.valid = False
            if self.valid:
                self.name = name.split()[0]
                self.surname = name.split()[1]
            else:
                self.name = None
                self.surname = None

    return Name(name)


def get_info(uid):

    class Result:
        def __init__(self, uid):
            self.expired = False
            try:
                data = json.loads(f.open('./user/{}/status.db'.format(uid), 'r').read())
                if data['score'] > 5:
                    self.cert = True
                else:
                    self.cert = False
            except:
                self.cert = False
            if self.cert:
                self.score = data['score']
                self.date = data['date']
                self.limit = data['limit']
            else:
                self.score = None
                self.date = None
                self.limit = None

            if self.limit <= 0:
                if self.date == datetime.now().strftime('%Y-%m-%d'):
                    self.expired = True
                else:
                    self.limit = self.score - 3 if self.score else None
                    self.date = datetime.now().strftime('%Y-%m-%d')
                    self.expired = False

        def reduce_limit(self):
            atm = (datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d')
            if self.date != atm:
                self.limit = self.score - 3 if self.score else None
                self.date = atm
            self.limit -= 1
            f.open('./user/{}/status.db'.format(uid), 'w').write(json.dumps(
                {
                    "score": self.score,
                    "limit": self.limit,
                    "date": self.date
                })
            )
    return Result(uid)


def translate(text):
    text = text.lower()
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
    for i in letters.keys():
        text = text.replace(i, letters[i])
    return text.replace(
        '🅱️', 'b').replace('🅾️', 'o') \
        .replace('⭕️', 'o') \
        .replace('✝️'.replace(u'\ufe0f', u''), 't') \
        .replace('🅱️'.replace(u'\ufe0f', u''), 'b') \
        .replace('🅾️'.replace(u'\ufe0f', u''), 'o') \
        .replace('✝️', '') \
        .replace('⭕️'.replace(u'\ufe0f', u''), '')


def scaner(text):
    text = text.replace('\n', ' ')
    low = translate(text.lower())
    low = low.replace("0", "o")
    lt = translate(text.lower().replace('\n', ' '))
    is_bad = False
    bad_words = ["bot"]
    good_words = ["botan", "botanik", "botqa", "hisobot", "astrobot", "yunusobot", "botiq", "botmon", "robotexnika",
                 "botma", "botanika", "botqo", "botgan", "botkan", "botib", "botir", "botak", "botmon", "razrabot",
                 "obrabot", "robot", "isbot", "rabot", "umrbot", "botstrap", "boot", "bootcamp"]
    redundant_chars = "~`!?@#$%^&*()_+=-0987654321][}{'\";:.,/\\|"

    for i in redundant_chars:
        low = low.replace(i, "")

    space_pattern = "\s{2,}"
    spaceoverflows = re.findall(space_pattern, low)
    for i in spaceoverflows:
        low = low.replace(i, ' ')
        lt = low

    for i in low.split():
        if len(i) == 1:
            if i != "b" or i != "o" or i != "t":
                low = low.replace(i, '')
        else:
            if 'b' not in i and 'o' not in i and 't' not in i:
                low = low.replace(i, '')

    low = low.replace(' o ', 'o').replace(' o', 'o').replace('o ', 'o')
    multi_o_pattern = "o{2,}"
    results = re.findall(multi_o_pattern, low)
    if len(results) > 0:
        for word in results:
            low = low.replace(word, 'o')

    low = low.replace('b ot', 'bot').replace('bo t', 'bot').replace('b o t', 'bot')

    for bad in bad_words:
        if bad in lt:
            is_bad = True

    if text.lower() == "/stat@combot":
        return False

    detected_words = []
    if len(low.replace(" ", "")) > 0:
        data = low.split()
        stats = []
        if "b o t" in low or low == "b o t":
            stats.append(True)
        for i in data:
            if "bot" in i:
                is_bad = True
                for b in good_words:
                    if b in i:
                        if len(i) <= 4:
                            return True
                        else:
                            is_bad = False
                if is_bad:
                    detected_words.append(i)
                stats.append(is_bad)

        if any(stats): is_bad = True

    return {"is_bad": is_bad, "words": detected_words}


def resize(data):
    if len(data) > 23:
        return data[:10] + '...' + data[-10:]
    else:
        return data


def encryptor(a):
    abc = "ABCDEFGHJK"
    a = str(a).replace('-', 'L')
    for num in a:
        try:
            a = a.replace(num, abc[int(num)])
        except:
            pass
    return a


def decryptor(a):
    abc = "ABCDEFGHJK"
    for letter in a:
        try:
            a = a.replace(letter, str(abc.index(letter)))
        except:
            pass
    return a.replace('L', '-')


def html_converter(a):
    try:
        return a.replace('&', '&amp;').replace('<', '&lt;').replace('/', '&#47;').replace('>', '&gt;')
    except:
        return "NOT_STRING"


def steper(point, full):
    step = ["⬜️", "⬛️️"]
    if full == point:
        return "\n💣 " + step[1] * point + step[0] * (full - point) + " " + "100%"
    else:
        return "\n💣 " + step[1] * point + step[0] * (full - point) + " " + str((100 // full) * point) + "%"


def return_month(month):
    months = {
        '01': 'yanvar',
        '02': 'fevral',
        '03': 'mart',
        '04': 'aprel',
        '05': 'may',
        '06': 'iyun',
        '07': 'iyul',
        '08': 'avgust',
        '09': 'sentabr',
        '10': 'oktabr',
        '11': 'noyabr',
        '12': 'dekabr'
    }
    return months['{}'.format(month)]
