# BOOKS.py - to do all and all about books, our little library
# You are not gonna touch any bit of the code,
# otherwise you'll have to deal with tons of nightmares, trust me

from service.globals import *
import json
import time
from service.files import File as f
from datetime import datetime, timedelta
from dreamgraph import LogIn
from service.tools import log

client = LogIn('b3ece8779d454736c76d48b288028a250ec7bf5f25e75d897110826ade2d')


lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et' \
        ' dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ' \
        'ex ea commodo consequat.'

langs = {'uz': 'o\'zbek', 'en': 'ingliz', 'ru': 'rus'}

books = [
    
    {'type': 'pdf', 'download': 'https://t.me/HopsBooks/5', 'url': False, 'lang': 'en', 'size': '24.8', 'title':
        'Learning Python', 'author': 'Mark Lutz'}
    ]


def maker(book=None, ind=0, comments=False):
    
    if not comments:
        try:
            comments = json.loads(f.open('./books/comments/book_{}.db'.format(ind), 'r').read())
        except:
            f.open('./books/comments/book_{}.db'.format(ind), 'w').write(json.dumps({'all': 0}))
            comments = {'all': 0}
    if not book:
        all_books = start()
        book = all_books[ind]
    
    result = []
    br = {'tag': 'br'}
    result.append(br)
    result.append({'tag': 'b', 'children': ['Muallif: {}'.format(book['author'])]})
    result.append(br)
    result.append({'tag': 'b', 'children': ['Til: {}'.format(langs[book['lang']])]})
    result.append(br)
    result.append({'tag': 'b', 'children': ['Turi: {}'.format(book['type'].upper())]})    
    result.append(br)
    result.append({'tag': 'b', 'children': ['Hajmi: {} MB'.format(book['size'])]})
    result.append(br)
    result.append({'tag': 'a', 'attrs':{'href': book['download']}, 'children': ['⬇️YUKLAB OLISH']})
    
    result.append({'tag': 'br'})
    result.append({'tag': 'aside', 'children': ['Kitob haqida fikrlar']})
    if comments['all'] > 0:
        for person in sorted(list(comments.keys())):
            if person == 'all':
                continue
            log(0, person, comments)
            log(list(comments.keys()))
            log(comments[person])
            try:
                result.append({'tag': 'pre', 'children': [comments[person]['name']]})
            except Exception as e:
                return '1. ' + str(e)
            for post in comments[person]['posts']:
                try:
                    result.append({'tag': 'code', 'children': [post['date']]})
                    result.append({'tag': 'blockquote', 'children': [post['text']]})
                except Exception as e:
                    return '2. ' + str(e)
    else:
        result.append({'tag': 'i', 'children': ['Hozircha izohlar mavjud emas']})
    return result

    
def start():
    global books
    try:
        books = json.loads(f.open('./books/all.db', 'r').read())
    except:
        bot.send_message(dev, str(books))
        result = maker(book=books[0], ind=0)
        page = client.create_page(
            title=books[0]['title'],
            content=result,
            author_name='Hops',
            author_url='https://t.me/Hopsrobot'
        )
        books[0]['url'] = page.url
        f.open('./books/all.db', 'w').write(json.dumps(books))
    return books    

start()


def represent(book, ind=0):
    if book['url']:
        return book['url']
    else:
        result = maker(book)
        page = client.create_page(
            title=book['title'],
            author_name='Hops',
            author_url='https://t.me/Hopsrobot',
            content=result
        )
        return page.url
        

def books_in_keyboards(all_books, first=False, go=False, back=False, page_number=0):
    counter = page_number
    mark = telebot.types.InlineKeyboardMarkup()
    for i in range(page_number, page_number + 5):
        try:
            single = telebot.types.InlineKeyboardButton(
                text='{}. {}'.format(counter, all_books[i]['title']),
                url=all_books[i]['url']
            )
            mark.add(single)
            counter += 1
        except:
            pass
    if go:
        if len(all_books[page_number:]) > 5:
            go_button = telebot.types.InlineKeyboardButton('Keyingisi >',
                                                           callback_data='booknextpage_{}'.format(page_number + 5))
            back_button = telebot.types.InlineKeyboardButton('< Oldingisi',
                                                             callback_data='bookbackpage_{}'.format(page_number - 5))
            mark.row(back_button, go_button)
        else:
            back_button = telebot.types.InlineKeyboardButton('< Oldingisi',
                                                             callback_data='bookbackpage_{}'.format(page_number - 5))
            mark.row(back_button)
    elif back:
        if len(all_books[:page_number]) >= 5:
            go_button = telebot.types.InlineKeyboardButton('Keyingisi >',
                                                           callback_data='booknextpage_{}'.format(page_number + 5))
            back_button = telebot.types.InlineKeyboardButton('< Oldingisi',
                                                             callback_data='bookbackpage_{}'.format(page_number - 5))
            mark.row(back_button, go_button)
        else:
            go_button = telebot.types.InlineKeyboardButton('Keyingisi >',
                                                           callback_data='booknextpage_{}'.format(page_number + 5))
            mark.row(go_button)
    elif first:
        if len(all_books[page_number:]) > 5:
            go_button = telebot.types.InlineKeyboardButton('Keyingisi >',
                                                           callback_data='booknextpage_{}'.format(page_number + 5))
            mark.row(go_button)
    return mark
    

def add_comment(book_id, uid, text, name):
    all_books = json.loads(f.open('./books/all.db', 'r').read())
    atm = str(time.time()).split('.')[0]
    date = (datetime.now() + timedelta(hours=5)).strftime('%Y.%m.%d')
    user = '{}_{}'.format(atm, uid)
    try:
        comments = json.loads(f.open('./books/comments/book_{}.db'.format(book_id), 'r').read())
    except:
        f.open('./books/comments/book_{}.db'.format(book_id), 'w').write(json.dumps({'all': 0}))
        comments = {'all': 0}
    if comments['all'] > 0:
        recorded = False
        for key in list(comments.keys()):
            if str(uid) in key:
                comments[key]['posts'].append({'text': text, 'date': date})
                recorded = True
        if not recorded:
            comments[user] = {
                'name': name,
                'posts': [
                    {
                        'text': text,
                        'date': date
                    }
                ]
            }
    else:
        comments[user] = {
            'name': name,
            'posts': [
                {
                    'text': text,
                    'date': date
                 }
            ]
        }
    comments['all'] += 1        
    f.open('./books/comments/book_{}.db'.format(book_id), 'w').write(json.dumps(comments))
    result = maker(all_books[book_id], ind=book_id, comments=comments)
    if all_books[book_id]['url']:
        client.edit_page(
            path=all_books[book_id]['url'][18:],
            title=all_books[book_id]['title'],
            content=result,
            author_name='Hops',
            author_url='https://t.me/Hopsrobot'
        )
    else:
        page = client.create_page(
            title=all_books[book_id]['title'],
            content=result,
            author_name='Hops',
            author_url='https://t.me/Hopsrobot'
        )
        all_books[book_id]['url'] = page.url
        f.open('./books/all.db', 'w').write(json.dumps(all_books))


def add_book(data):
    data = data.split('\n')
    title = data[1]
    author = data[2]
    lang = data[3]
    tip = data[4]
    size = data[5]
    download = data[6]
    book_id = len(books)
    new_book = {
        'title': title,
        'author': author,
        'lang': lang,
        'type': tip,
        'size': size,
        'download': download
    }
    result = maker(book=new_book, ind=book_id)
    page = client.create_page(
        title=title,
        content=result,
        author_name='Hops',
        author_url='https://t.me/Hopsrobot'
    )
    new_book['url'] = page.url
    books.append(new_book)
    f.open('./books/all.db', 'w').write(json.dumps(books))
    
    
def del_book(book_id):
    all_books = start()
    books.pop(book_id)
    f.open('./books/all.db', 'w').write(json.dumps(all_books))
    

def del_comment(data):
    data = data.split('\n')
    book_id = int(data[1])
    starting_text = data[2]
    date = data[3]
    
    try:
        comments = json.loads(f.open('./books/comments/book_{}.db'.format(book_id), 'r').read())
    except:
        f.open('./books/comments/book_{}.db'.format(book_id), 'w').write(json.dumps({'all': 0}))
        comments = {'all': 0}
    for user in list(comments.keys()):
        if user == 'all':
            continue
        for post in comments[user]['posts']:
            if post['text'].lower().startswith(starting_text.lower()) and post['date'] == date:
                if len(comments[user]['posts']) > 1:
                    comments[user]['posts'].remove(post)
                else:
                    comments.pop(user)
                    comments['all'] -= 1

    result = maker(ind=book_id, comments=comments)
    all_books = start()
    client.edit_page(
        path=all_books[book_id]['url'][18:],
        title=all_books[book_id]['title'],
        content=result,
        author_name='Hops',
        author_url='https://t.me/Hopsrobot'
    )
    f.open('./books/comments/book_{}.db'.format(book_id), 'w').write(json.dumps(comments))

# The End
