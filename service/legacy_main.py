# MAIN.py - major process is handled here
# Once you face with damn lines which were written with one eye closed,
# don't think about who wrote those shits
# just skip those lines, and you are good
# whenever you have questions, don't ask,
# you are the one who should realize and do "bumbala bum" magics to understand this whole headache
# there are no comments, no explanations, no, no and no.
# anyway, good luck if you are gonna read the code
# just understand: you are alone, no one is gonna explain you the code
# last advice: do not read the code.

from time import sleep
from telebot import types
import random
from service.utils.rex import run
from service.utils.tools import *
from service.utils import telegraph, book, tools
from service.files import File as f
from service.strings import get_string
from service.globals import *


def is_restricted(cid, uid):
    return bot.get_chat_member(cid, uid).can_send_messages is False


def get_restrict_time(cid, uid):
    until_date = bot.get_chat_member(cid, uid).until_date
    log("UNTIL DATE: ", until_date)
    try:
        a = datetime.fromtimestamp(until_date)
        b = datetime.now()
        if a < b and until_date:
            return 'forever'
        month = (datetime.fromtimestamp(until_date) + timedelta(hours=5)).strftime('%m')
        day = int((datetime.fromtimestamp(until_date) + timedelta(hours=5)).strftime('%d'))
        return (datetime.fromtimestamp(until_date) + timedelta(hours=5)).strftime('%Y-yilning {}-{} kuni soat %H:%M'.format(day, return_month(month)))
    except:
        return 'forever'


def stranger(cid):
    if cid in allowed_groups:
        return False
    else:
        return True


def hops(m, words):
    if len(words) > 1:
        words = ", ".join(words)
    else:
        words = words[0]
    words = html_converter(words)
    uid = m.from_user.id
    cid = m.chat.id
    name = m.from_user.first_name
    if m.from_user.last_name:
        name += " " + m.from_user.last_name
    name = resize(name)    
    name = html_converter(name)
    stat = bot.get_chat_member(cid, uid).status
    if stat != 'creator' and stat != 'administrator':
        if uid not in verified:
            try:
                import time
                try:
                    data = json.loads(f.open('./restricted/user_{}.json'.format(uid), 'r').read())
                except Exception as e:
                    log("Yangi fayl ochildi: {}".format(e))
                    f.open('./restricted/user_{}.json'.format(uid), 'w').write('{"times": 0}')
                    data = json.loads(f.open('./restricted/user_{}.json'.format(uid), 'r').read())
                times = data['times']
                if is_restricted(cid, uid):
                    times += (times + 1)
                else:
                    times += 1
                data = {"times": times}
                f.open('./restricted/user_{}.json'.format(uid), 'w').write(json.dumps(data))    
                atm = datetime.now()
                result = atm + timedelta(hours=times)
                overall = time.mktime(result.timetuple())
                if times >= 720:
                    bot.restrict_chat_member(
                        cid,
                        uid,
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                        until_date=overall
                    )
                    bot.kick_chat_member(cid, uid)
                else:    
                    bot.restrict_chat_member(cid, uid, can_send_messages=False, until_date=overall)
                
            except Exception as e:
                log("Error while restricting: {}".format(e))
            msg = bot.send_message(
                cid,
                get_string('warn') + steper(0, 7),
                parse_mode='HTML',
                reply_to_message_id=m.message_id
            )
            for i in range(1, 8):
                sleep(3)
                try:
                    bot.edit_message_text(
                        chat_id=cid,
                        message_id=msg.message_id,
                        text=get_string('warn') + steper(i, 7),
                        parse_mode='HTML'
                    )
                except:
                    break
            sleep(1)
            try:
                bot.delete_message(cid, m.message_id)
            except:
                bot.send_chat_action(cid, 'typing')
            bot.delete_message(cid, msg.message_id)
            until_date = get_restrict_time(cid, uid)
            if until_date == 'forever':
                bot.send_message(
                    cid,
                    get_string('banned').format(name, times, uid=uid, words=words),
                    parse_mode='HTML'
                )
            else:
                bot.send_message(
                    cid,
                    get_string('restricted').format(name, times, until_date, uid=uid, words=words),
                    parse_mode='HTML'
                )


def sign(m):
    text = m.text
    uid = m.from_user.id
    cid = m.chat.id
    lowmsg = str(text).lower()
    try:
        data = json.loads(f.open('./agreed/users.json', 'r').read())
    except Exception as e:
        log("agreed/users -> {}".format(e))
        f.open('./agreed/users.json', 'w').write('{"all": []}')
        data = json.loads(f.open('./agreed/users.json', 'r').read())
    users = data['all']  
    try:
        info = json.loads(f.open('./users/{}_rules.json'.format(uid), 'r').read())
    except Exception as e:
        log("Error in f.opening users/rules -> {}".format(e))
        bot.send_message(cid, get_string('fatal_error'))
        info = {}
    chat_id = int(info['cid'])
    key_in = int(info['key_in'])
    if lowmsg == get_string('keys')[key_in]:
        try:
            try:
                bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=uid,
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            except Exception as e:
                log("Rest: " + str(e))
            name = m.from_user.first_name
            if m.from_user.last_name:
                name += " " + m.from_user.last_name
            name = resize(name)    
            name = html_converter(name)
            
            try:
                msg_id_of_sent_rules_in_group = int(f.open('./msg_ids/{}.txt'.format(uid), 'r').read())
            except:
                msg_id_of_sent_rules_in_group = 0
            
            last_message_in_group = msg_id()
            if int(last_message_in_group) == int(msg_id_of_sent_rules_in_group):
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=last_message_in_group,
                    text=get_string('new_agreement_in_group').format(
                        uid, resize(name)
                    ),
                    parse_mode='HTML'
                )
            else:    
                bot.send_message(
                    chat_id,
                    get_string('new_agreement_in_group').format(
                        uid, resize(name)
                    ),
                    parse_mode='HTML'
                )
            
            bot.send_message(uid, get_string('congrats'), parse_mode='HTML')
            bot.send_message(uid, get_string('manual'), parse_mode='html')
            
            users.append(uid)
            data = {"all": users}
            f.open('./agreed/users.json', 'w').write(json.dumps(data))
        except Exception as e:
            log("RestOver: " + str(e))
    else:
        if text.startswith('/'):
            bot.send_chat_action(cid, 'typing')
        else:
            bot.send_message(uid, get_string('no_agreement'))


def modify_the_code(data):
    changed = False
    human = get_string('zen')
    odamgarchilik = get_string('zen_uz')
    patterns = ['import\s+human', 'import\s+odamgarchilik']
    origin_code = [human, odamgarchilik]
    
    for pattern in patterns:
        found = re.findall(pattern, data)
        for i in found:
            changed = True
            data = data.replace(i, 'print("""{}""")'.format(origin_code[patterns.index(pattern)]))
    return data, changed


def runner(m, lang):
    uid = m.from_user.id
    cid = m.chat.id
    langs = {
        '#py': 24,
        '#py2': 5,
        '#php': 8
    }
    available = True

    if m.chat.type != 'private':
        status = bot.get_chat_member(cid, uid).status
        if status != 'administrator' and status != 'creator':
            user = get_info(uid)
            if user.cert:
                if user.expired:
                    available = False
                else:
                    user.reduce_limit()
            else:
                available = False
                k = types.InlineKeyboardMarkup()
                b = types.InlineKeyboardButton(text=get_string('get_cert_button'), callback_data='cert_{}'.format(uid))
                k.row(b)
                bot.send_message(cid, get_string('get_cert'), reply_markup=k, reply_to_message_id=m.message_id)
            
    if available:        
        try:
            bot.send_chat_action(cid, 'typing')
            code = m.text.replace('{}\n'.format(lang), '', 1)
            modified = modify_the_code(code)
            code = modified[0]
            changed = modified[1]
            request_id = m.message_id
            compiled = run(langs[lang], code)
            k = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton(text="Info", callback_data="info_{}/{}/{}".format(cid, uid, request_id))
            k.add(b)
            if len(str(compiled.result)) <= 3000:
                if compiled.success:
                    check = scaner(compiled.result) if m.chat.type != 'private' else {'is_bad': False}
                    if check['is_bad'] and (not changed):
                        bot.send_message(
                            cid,
                            get_string('bad_word_in_output'),
                            parse_mode='html',
                            reply_to_message_id=m.message_id
                        )
                        hops(m, check['words'])
                        return
                    response = bot.send_message(
                        cid,
                        get_string('output').format(
                            html_converter(compiled.result)
                        ),
                        reply_to_message_id=m.message_id,
                        parse_mode='html',
                        reply_markup=k
                    )
                else:
                    response = bot.send_message(
                        cid,
                        get_string('output_error').format(
                            html_converter(compiled.errors)
                        ),
                        reply_to_message_id=m.message_id,
                        parse_mode='html',
                        reply_markup=k
                    )
            else:
                response = bot.send_message(
                    cid,
                    get_string('output_too_large'),
                    reply_to_message_id=m.message_id,
                    parse_mode='html'
                )
            response_id = response.message_id
            data = {"response_id": response_id, "stats": compiled.stats, "lang": langs[lang]}
            f.open('./codes/{}/{}/{}_code.json'.format(cid, uid, request_id), 'w').write(json.dumps(data))    

        except Exception as e:
            log(e)
            bot.send_message(cid, get_string('fatal_error'), reply_to_message_id=m.message_id)
    
    
def editor(m):
    try:
        langs = {
            '24': '#py',
            '5' : '#py2',
            '8' : '#php'
        }

        uid = m.from_user.id
        cid = m.chat.id
        request_id = m.message_id
        data = json.loads(f.open('./codes/{}/{}/{}_code.json'.format(cid, uid, request_id), 'r').read())
        lang = data['lang']
        response_id = data['response_id']
        code = m.text.replace('{}\n'.format(langs[str(lang)]), '', 1)
        modified = modify_the_code(code)
        code = modified[0]
        k = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton(text="Info", callback_data="info_{}/{}/{}".format(cid, uid, request_id))
        k.add(b)
        try:
            bot.send_chat_action(cid, 'typing')
            compiled = run(lang, code)
            if len(str(compiled.result)) <= 3000:
                if compiled.success:
                    bot.edit_message_text(
                        chat_id=cid,
                        message_id=response_id,
                        text=get_string('output').format(
                            html_converter(compiled.result)
                        ),
                        parse_mode='html',
                        reply_markup=k
                    )
                else:
                    bot.edit_message_text(
                        chat_id=cid,
                        message_id=response_id,
                        text=get_string('output_error').format(
                            html_converter(compiled.errors)
                        ), parse_mode='html',
                        reply_markup=k
                    )
            else:
                bot.edit_message_text(
                    chat_id=cid,
                    message_id=response_id,
                    text=get_string('output_too_large'),
                    parse_mode='html',
                    reply_markup=k
                )
            data = {"response_id": response_id, "stats": compiled.stats, "lang": lang}
            f.open('./codes/{}/{}/{}_code.json'.format(cid, uid, request_id), 'w').write(json.dumps(data))        
        except Exception as e:
            log(e)
    except Exception as e:
        log(e)
    
    
def splitter(data):
    pattern = "\d{1,}[,\.]?\d{1,}"
    digits = re.findall(pattern, data)
    for i in digits:
        data = data.replace(i, i.replace(',', '.'))
    return "⏰ " + "\n🔹 ".join([x for x in data.split(',')])    
    
    
def begin_test(m):
    text = m.text
    uid = m.from_user.id
    if text.startswith('/'):
        if text == '/cancel':
                bot.send_message(uid, get_string('test_cancelled'))
        else:
            bot.send_chat_action(uid, 'typing')
    else:
        qtns = tools.questions
        data = tools.check_name(text)
        if data.valid:
            info = {"name": data.name, "surname": data.surname}
            status = {"score": 0, "limit": 0, "date": None}
            f.open('./user/{}/info.json'.format(uid), 'w').write(json.dumps(info))
            f.open('./user/{}/status.json'.format(uid), 'w').write(json.dumps(status))
            k = tools.btn_maker(1)
            bot.send_message(uid, text="<b>{}-savol</b>\n{}".format(1, qtns['1']['question']), reply_markup=k, parse_mode='html')
        else:
            if text == '/cancel':
                bot.send_message(uid, get_string('test_cancelled'))
            else:
                a = bot.send_message(uid, get_string('test_invalid_credentials'))
                bot.register_next_step_handler(a, begin_test)
                
                
def get_user_data(forwarded_message):
    user = forwarded_message.forward_from.id
    a = bot.get_chat_member(python_uz, user)
    if a.status == 'left':
        return False
    data = tools.get_info(user)
    try:
        ban_info = json.loads(f.open('./restricted/user_{}.json'.format(user), 'r').read())['times']
    except:
        ban_info = 0
    result = get_string('user_info')
    rest = is_restricted(python_uz, user)
    rest_date = get_string('user_info_date').format(get_restrict_time(python_uz, user)) if rest else ''
    rest = '{} {}'.format(get_string('yes'), rest_date) if rest else get_string('no')
    certified = get_string('yes') if data.cert else get_string('no')
    limit = data.limit if data.limit else '0'
    score = data.score if data.score else '0'
    result = result.format(
        rest,
        ban_info,
        certified,
        get_string('user_info_scores').format(
            score,
            limit
        ) if data.cert else ''
    )
    return result


def get_comment(m):
    text = m.text
    uid = m.from_user.id
    cid = m.chat.id
    if text == '/cancel':
        bot.send_message(cid, get_string('book_comment_cancelled'))
        return
    else:
        name = m.from_user.first_name
        if m.from_user.last_name:
            name += " " + m.from_user.last_name
        name = resize(name)
        book_steps = json.loads(f.open('./books/steps.json', 'r').read())
        book_id = book_steps['{}'.format(uid)]
        try:
            books = json.loads(f.open('./books/all.json', 'r').read())
            try:
                books[int(book_id)]
            except Exception as e:
                bot.send_message(uid, get_string('error_in_comment'))
                log('XATOLIK: comment => {}'.format(e))
        except:
            book.start()
        book.add_comment(book_id=book_id, uid=uid, text=text, name=name)
        bot.send_message(cid, get_string('book_comment_saved'))


def msg_id(mid=False):
    try:
        data = f.open('./mid.txt', 'r').read()
    except:
        data = '0'
        f.open('./mid.txt', 'w').write(data)
    
    if mid:
        f.open('./mid.txt', 'w').write(str(mid))
    else:
        return int(data)


@bot.message_handler(content_types=['sticker', 'video', 'photo', 'audio', 'gif', 'voice', 'document', 'text'])
def main(m):
    text = m.text
    uid = m.from_user.id
    cid = m.chat.id
    lowmsg = text.lower()
    name = m.from_user.first_name
    stat = bot.get_chat_member(python_uz, uid).status
    allowed = ['administrator', 'creator']
    if m.reply_to_message:
        if m.reply_to_message:
            if m.reply_to_message.text:
                if m.reply_to_message.text.startswith('#py\n') \
                        or m.reply_to_message.text.startswith('#py2\n') \
                        or m.reply_to_message.text.startswith('#php\n'):
                    coder = m.reply_to_message.from_user.id
                    page = telegraph.update(m)
                    if page[0]:
                        notify = telegraph.notify(m)
                        if page[1]:
                            if not notify:
                                bot.send_message(
                                    coder,
                                    get_string('you_have_new_comment').format(page[0]),
                                    parse_mode='html'
                                )
                                telegraph.notify(m, True)
                        else:
                            if not notify:
                                bot.send_message(
                                    coder,
                                    get_string('somebody_liked_your_code').format(page[0]),
                                    parse_mode='html'
                                )
                                telegraph.notify(m, True)

    if m.from_user.last_name:
        name += " " + m.from_user.last_name
    name = resize(name)
    if lowmsg == 'order_101':
        bot.send_message(
            cid,
            'Privacy and policy requirements [ordered by 101]\n\n{}'.format(get_string('new_member_rules'))
        )
    
    if lowmsg == 'order_102':
        bot.send_message(
            cid,
            'Manual for beginners [ordered by 102]\n\n{}'.format(get_string('manual')),
            parse_mode='html'
        )
    if lowmsg == 'yordam' and m.chat.type == 'private':
        bot.send_message(cid, get_string('manual'), parse_mode='html')
    if cid in allowed_groups:
        police = scaner(lowmsg)
        is_bad = police['is_bad']
        if is_bad:
            hops(m, police['words'])
        if m.photo or m.video or m.audio or m.voice or m.document:
            police = scaner(lowmsg)
            is_bad = police['is_bad']
            if is_bad:
                hops(m, police['words'])
            else:
                if anti_spam(text):
                    bot.delete_message(cid, m.message_id)
    elif stranger(cid) and m.chat.type != 'private':
        log(cid)
        bot.leave_chat(cid)
    
    elif m.chat.type == 'private':
        if text.startswith('/start'):
            if text == '/start start_test':
                a = bot.send_message(cid, get_string('start_test'))
                bot.register_next_step_handler(a, begin_test)
            
            elif text.startswith('/start bookcomment_'):
                a = bot.send_message(cid, get_string('book_send_comment'))
                book_id = int(text.split('_')[1])
                try:
                    book_steps = json.loads(f.open('./books/steps.json', 'r').read())
                    book_steps['{}'.format(uid)] = book_id
                    f.open('./books/steps.json', 'w').write(json.dumps(book_steps))
                except:
                    f.open('./books/steps.json', 'w').write(json.dumps({'ok': True, '{}'.format(uid): book_id}))
                bot.register_next_step_handler(a, get_comment)
            
            else:    
                try:
                    try:
                        data = json.loads(f.open('./members.json', 'r').read())
                    except:
                        f.open('./members.json', 'w').write('{"all":[]}')  
                        data = json.loads(f.open('./members.json', 'r').read())
                    if uid in data['all']:
                        pass
                    else:
                        data['all'].append(uid)
                    text = text.replace('/start ', '', 1)
                    if text.startswith('rules_'):
                        try:
                            data = json.loads(f.open('./agreed/users.json', 'r').read())
                        except Exception as e:
                            log("agreed/users -> {}".format(e))
                            f.open('./agreed/users.json', 'w').write('{"all": []}')
                            data = json.loads(f.open('./agreed/users.json', 'r').read())
                        users = data['all']    
                        if uid in users:
                            bot.send_message(cid, get_string('agreed_already'))
                        else:
                            datas = text.replace('rules_', '', 1).split('_')
                            user = int(decryptor(datas[0]))
                            chat_id = decryptor(datas[1])
                            key_in = int(decryptor(datas[2]))
                            if uid == user:
                                msg = bot.send_message(
                                    uid,
                                    get_string('new_member_rules').format(
                                        key=get_string('keys')[key_in]),
                                    parse_mode='HTML'
                                )
                                info = {"cid": chat_id, "key_in": key_in}
                                f.open('./users/{}_rules.json'.format(uid), 'w').write(json.dumps(info))
                                bot.register_next_step_handler(msg, sign)
                            else:
                                bot.send_message(cid, get_string('rules_taken_by_wrong_user'))
                    f.open('./members.json', 'w').write(json.dumps(data))
                except Exception as e:
                    log("""Common Rule: {}\n\n{}\n<a href="tg://user?id={}">{}</a>""".format(
                                                                                                html_converter(str(e)),
                                                                                                html_converter(str(m)),
                                                                                                uid,
                                                                                                html_converter(name)),
                        )
    else:
        pass
    if lowmsg == '#stat':
        if m.chat.type == 'private':
            try:
                data = json.loads(f.open('./restricted/user_{}.json'.format(uid), 'r').read())
            except:
                data = {"times":0}
            times = int(data['times'])
            if times > 0:
                bot.send_message(cid, get_string('stat_restricted').format(times), reply_to_message_id=m.message_id)
            else:
                bot.send_message(cid, get_string('stat_good'), reply_to_message_id=m.message_id)
        else:
            bot.send_chat_action(cid, "typing")
    if lowmsg == '#comments':
        if m.chat.type == 'private':
            data = telegraph.all_pages(uid)
            if data:
                msg = get_string('comments_all').format(data)
            else:
                msg = get_string('comments_not_found')
            bot.send_message(uid, msg, parse_mode='html')
    if text.startswith('#py\n'):
        telegraph.update(m, True)
        runner(m, '#py')
    if text.startswith('#py2\n'):
        telegraph.update(m, True)
        runner(m, '#py2')
    if text.startswith('#php\n'):
        telegraph.update(m, True)
        runner(m, '#php')
    if text == '/test':
        if m.chat.type == 'private':
            try:
                qtns = questions
                json.loads(f.open('./user/{}/info.json'.format(uid), 'r').read())
                k = btn_maker(1)
                bot.send_message(
                    uid,
                    text=get_string('test_question').format(1, qtns['1']['question']),
                    reply_markup=k,
                    parse_mode='html'
                )
            except:
                a = bot.send_message(cid, get_string('start_test'))
                bot.register_next_step_handler(a, begin_test)
                
    if text == '#books':
        if m.chat.type == 'private':
            books = book.start()
            mark = book.books_in_keyboards(all_books=books, first=True)
            bot.send_message(cid, get_string('book_choose'), reply_markup=mark)

    if uid == dev or stat in allowed:
        if text.startswith("#reo "):
            data = text.replace("#reo ", "", 1).split()
            user = int(data[0])
            amount = int(data[1])
            try:
                data = json.loads(f.open('./restricted/user_{}.json'.format(user), 'r').read())
            except:
                data = {"times":0}
            times = int(data['times'])
            data = {"times": amount}
            f.open('./restricted/user_{}.json'.format(user), 'w').write(json.dumps(data))
            bot.send_message(
                cid,
                get_string('reo').format(
                    user,
                    get_string('user'),
                    times,
                    amount),
                reply_to_message_id=m.message_id,
                parse_mode='HTML'
            )
        
        elif text.startswith('#add_book\n'):
            book.add_book(text)
            bot.send_message(cid, "Kitob qo'shildi")
        
        elif text.startswith('#del_book '):
            book_id = int(text.split()[1])
            book.del_book(book_id)
            log("O'chirildi")
            
        elif text.startswith('#del_comment\n'):
            book.del_comment(text)
            bot.send_message(cid, "O'chirildi")
            
        elif text.startswith('#send '):
            text = text.replace('#send ', '', 1)
            try:
                cid = int(text.split()[0])
            except:
                if text.split()[0] == 'py':
                    text = text.replace('py', '', 1)
                    cid = python_uz
                else:
                    log("Xatolik kelib chiqdi")    
            text = text.replace(str(cid), '', 1)
            try:
                bot.send_message(cid, text, parse_mode='markdown', disable_web_page_preview=True)
                log("Jo'natildi")
            except:
                log("Markdownda xato")
        
        elif text.startswith("#check "):
            data = text.replace("#check ", "", 1).split()
            user = int(data[0])
            try:
                data = json.loads(f.open('./restricted/user_{}.json'.format(user), 'r').read())
            except Exception as e:
                data = {"times":0}
            times = int(data['times'])
            bot.send_message(
                cid,
                "<a href=\"tg://user?id={}\">Vaqt</a>: {}".format(user, times),
                reply_to_message_id=m.message_id,
                parse_mode='html'
            )
        
        elif m.forward_from:
            if stat == 'administrator' or stat == 'creator':
                if m.chat.type == 'private':
                    data = get_user_data(m)
                    if data:
                        bot.send_message(uid, data, parse_mode='html')
                    else:
                        bot.send_message(uid, get_string('user_info_not_a_member'))
    if cid == python_uz:
        msg_id(m.message_id)
    
    
@bot.message_handler(content_types=['new_chat_member', 'new_chat_members'])
def new_chat_member(message):
    chat_id = message.chat.id
    key = random.choice(get_string('keys'))
    key_in = get_string('keys').index(key)
    try:
        data = json.loads(f.open('./agreed/users.json', 'r').read())
    except Exception as e:
        log("agreed/users -> {}".format(e))
        f.open('./agreed/users.json', 'w').write('{"all": []}')
        data = json.loads(f.open('./agreed/users.json', 'r').read())
    users = data['all']
    
    for i in message.new_chat_members:
        if i.id == bot_id:
            if stranger(chat_id) and message.chat.type != 'private':
                bot.leave_chat(chat_id)
        else:
            if not i.is_bot:
                name = i.first_name
                if i.last_name:
                    name += " " + i.last_name
                name = resize(name)
                name = html_converter(name)
                try:
                    data = json.loads(f.open('./restricted/user_{}.json'.format(i.id), 'r').read())
                except Exception as e:
                    log("Yangi fayl ochildi: {}".format(e))
                    f.open('./restricted/user_{}.json'.format(i.id), 'w').write('{"times": 0}')
                    data = json.loads(f.open('./restricted/user_{}.json'.format(i.id), 'r').read())
                times = data['times']
                if is_restricted(chat_id, i.id):
                    until_date = get_restrict_time(chat_id, i.id)
                    if times >= 720:
                        bot.kick_chat_member(chat_id, i.id)
                        bot.send_message(
                            chat_id,
                            get_string('banned_in_entrance').format(uid=i.id, name=name),
                            parse_mode='html'
                        )
                    else:
                        try:
                            if until_date == 'forever':
                                k = types.InlineKeyboardMarkup()
                                b = types.InlineKeyboardButton(
                                    text=get_string('click_the_button'),
                                    callback_data="done_{}|{}_{}_{}".format(i.id,
                                                                            encryptor(i.id),
                                                                            encryptor(chat_id),
                                                                            encryptor(key_in)
                                                                            )
                                )
                                k.row(b)
                                bot.send_message(
                                    chat_id,
                                    get_string('restricted_user_rules').format(i.id, name),
                                    parse_mode='HTML',
                                    reply_markup=k
                                )
                            else:
                                bot.send_message(
                                    chat_id,
                                    get_string('restricted_user').format(i.id, name, until_date),
                                    parse_mode='HTML'
                                )
                        except Exception as e:
                            log("Trying again: {}".format(e))
                elif i.id in users and not is_restricted(chat_id, i.id):
                    if times >= 720:
                        bot.kick_chat_member(chat_id, i.id)
                        bot.send_message(
                            chat_id,
                            get_string('banned_in_entrance').format(uid=i.id, name=name),
                            parse_mode='html'
                        )
                    else:
                        bot.send_message(chat_id, get_string('old_member').format(i.id, name), parse_mode='HTML')
                else:
                    user = "{}_{}_{}".format(encryptor(i.id), encryptor(chat_id), encryptor(key_in))
                    try:
                        bot.restrict_chat_member(chat_id, i.id, can_send_messages=False)
                        msg = bot.send_message(
                            chat_id,
                            get_string('new_member').format(name=resize(name), user=user),
                            parse_mode='HTML'
                        )
                        f.open('./msg_ids/{}.txt'.format(i.id), 'w').write(str(msg.message_id))
                        msg_id(msg.message_id)
                    except Exception as e:
                        log("Restrictda xato: " + str(e))


@bot.edited_message_handler(content_types=['sticker', 'gif', 'video', 'photo', 'voice', 'document', 'audio', 'text'])
def edited(m):
    text = m.text
    cid = m.chat.id
    lowmsg = text.lower()
    if cid in allowed_groups:
        police = scaner(lowmsg)
        is_bad = police['is_bad']
        if is_bad:
            hops(m, police['words'])
        elif m.photo or m.video or m.audio or m.voice or m.document:
            police = scaner(m.caption.lower())
            is_bad = police['is_bad']
            if is_bad:
                hops(m, police['words'])
    if stranger(cid) and m.chat.type != 'private':
        bot.leave_chat(cid)
    if text.startswith('#py\n'):
        telegraph.update(m, True)
        editor(m)
    elif text.startswith('#py2\n'):
        telegraph.update(m, True)
        editor(m)
    elif text.startswith('#php\n'):
        telegraph.update(m, True)
        editor(m)
    if m.reply_to_message:
        if m.reply_to_message.text:
            if m.reply_to_message.text.startswith('#py\n') \
                    or m.reply_to_message.text.startswith('#py2\n') \
                    or m.reply_to_message.text.startswith('#php\n'):
                telegraph.update(m)

        
@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    user = call.from_user.id
    cid = call.message.chat.id
    if call.data.startswith('done_'):
        dat = call.data.replace('done_', '', 1).split('|')
        uid = int(dat[0])
        http = dat[1]
        if user == uid:
            bot.answer_callback_query(
                call.id,
                text=get_string('new_member_rules_prepare'), url="https://t.me/{}?start=rules_{}".format(botlink, http),
                show_alert=True
            )
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, text=get_string('new_member_rules_taken_by_wrong_user'), show_alert=True)
    if call.data.startswith('info_'):
        path = call.data.replace('info_', '', 1)
        data = json.loads(f.open('./codes/{}_code.json'.format(path), 'r').read())
        info = splitter(data['stats'])
        bot.answer_callback_query(callback_query_id=call.id, text=info, show_alert=True)
    if call.data.startswith('test_'):
        data = call.data.replace('test_', '', 1).split('_')
        ind = int(data[0]) + 1
        answer = data[1]
        score = int(data[2])
        scores = {'6': [3, 'E'], '7': [4, 'D'], '8': [5, 'C'], '9': [6, 'B'], '10': [7, 'A']}
        if answer == 'True':
            score += 1
        if ind == 11:
            if score >= 6:
                user_data = tools.get_info(user)
                data = json.loads(f.open('./user/{}/status.json'.format(user), 'r').read())
                data['score'] = score
                if user_data.cert:
                    data['limit'] = user_data.limit
                else:    
                    data['limit'] = scores[str(score)][0]
                data['date'] = datetime.now().strftime('%Y-%m-%d')
                number = "#{}{}".format(scores[str(score)][1], str(user)[-5:])
                data['cert'] = number
                f.open('./user/{}/status.json'.format(user), 'w').write(json.dumps(data))
                bot.edit_message_text(
                    chat_id=cid,
                    message_id=call.message.message_id,
                    text=get_string('get_cert_completed_success').format(scores[str(score)][1], scores[str(score)][0])
                )
                try:
                    data = json.loads(f.open('./certificates/users.json', 'r').read())
                except:
                    f.open('./certificates/users.json', 'w').write('{"all": []}')
                    data = json.loads(f.open('./certificates/users.json', 'r').read())
                data['all'].append(user)    
                f.open('./certificates/users.json', 'w').write(json.dumps(data))
            else:
                bot.edit_message_text(
                    chat_id=cid,
                    message_id=call.message.message_id,
                    text=get_string('get_cert_completed_fail').format(score)
                )
        else:
            k = tools.btn_maker(ind, score)
            bot.edit_message_text(
                chat_id=cid,
                message_id=call.message.message_id,
                text="<b>{}-savol</b>\n{}".format(
                    ind,
                    tools.questions[str(ind)]['question']),
                parse_mode='html',
                reply_markup=k
            )
 
    if call.data.startswith('cert_'):
        uid = int(call.data.replace('cert_', '', 1))
        if user == uid:
            bot.delete_message(cid, call.message.message_id)
            bot.answer_callback_query(call.id, url='https://t.me/{}?start=start_test'.format(botlink))
        else:
            bot.answer_callback_query(call.id, text=get_string("get_cert_button_taken_by_wrong_user"), show_alert=True)
    if call.data.startswith('booknextpage_'):
        page_number = int(call.data.split('_')[1])
        books = book.start()
        mark = book.books_in_keyboards(all_books=books, go=True, page_number=page_number)
        bot.edit_message_text(
            chat_id=cid,
            message_id=call.message.message_id,
            text=get_string('book_choose'),
            reply_markup=mark
        )
    
    if call.data.startswith('bookbackpage_'):
        page_number = int(call.data.split('_')[1])
        books = book.start()
        mark = book.books_in_keyboards(all_books=books, back=True, page_number=page_number)
        bot.edit_message_text(
            chat_id=cid,
            message_id=call.message.message_id,
            text=get_string('book_choose'),
            reply_markup=mark
        )

# I hope you just skipped all lines and headed to the end
# Anyway, you are at the end of the file

# This is a sample repo, it DOES DEMONSTRATE how Hops works
# I just used polling method to utilize updates
# But you aren't limited to this functionality only, and you can and you should move to webhook before production
# By running this project you get the taste of Hops, but not the whole maintainable application
# You should implement your own webhook handlers, and server stuff yourself or just copy/paste from somewhere else
# Here, I'm jus gonna use polling, it gets updates and works on 'em
# BUT, again, this is not for production purposes
bot.infinity_polling()
