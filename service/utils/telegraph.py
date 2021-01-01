# TELEGRAPH.py - all the Telegraph stuff is handled here
# pages are created, edited... blah-blah-blah...
# Get out the file right now, there is nothing good to see

import json
from dreamgraph import LogIn
from service.files import File as f
from service.globals import *
from service.utils.tools import log


client = LogIn(telegraph_token)


def node(message):
    content = message.text
    msg = 'https://t.me/python_uz/{}'.format(message.message_id)
    return {str(message.message_id): [{'tag': 'p', 'children': [content]},
                                      {'tag': 'a', 'attrs': {'href': msg}, 'children': ['Xabarga o\'tish']}]
            }


def name(uid):
    user = bot.get_chat_member(python_uz, uid).user
    user_name = user.first_name
    if user.last_name:
        user_name += ' ' + user.last_name
    return user_name


def notify(message, mark=False):
    user = message.reply_to_message.from_user.id
    code_id = message.reply_to_message.message_id
    code = message.reply_to_message.text
    try:
        info = json.loads(f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'r').read())
    except:
        info = {
            'likes':
                {
                    'all': 0,
                    'clicked': []
                },
            'people': 0,
            'comments': 0,
            'code': code,
            'url': None,
            'notified': False
        }
        f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(info))
        info = json.loads(f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'r').read())
    if mark:
        info['notified'] = True
        f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(info))
    return info['notified']


def all_pages(uid):
    try:
        data = eval(f.open('./comments/{}/all.db'.format(uid), 'r').read())
        log(1, data)
    except:
        data = False

    if data:
        pages = data['all']
        log(3, pages)
        url = data['url']
        result = []
        stat = {'tag': 'b', 'children': ['{} ta kod uchun izohlar'.format(len(pages))]}
        result.append(stat)
        result.append({'tag': 'br'})
        if len(pages) > 0:
            for page in pages:
                result.append({'tag': 'a', 'attrs': {'href': page}, 'children': ['• {}\n'.format(page[18:])]})
        else:
            return False
        log(4, result)
        if url:
            log(5, url)
            try:
                page = client.edit_page(path=data['url'][18:], title='Barcha kod va izohlar', content=result[:-1],
                                        author_name='Hops', author_url='https://t.me/Hopsrobot')
            except Exception as e:
                log(7, e)
        else:
            log(6, 'started to create')
            page = client.create_page(title='Barcha kod va izohlar', content=result, author_name='Hops',
                                      author_url='https://t.me/Hopsrobot')
            data['url'] = page.url
            log(2, data)
            f.open('./comments/{}/all.db'.format(uid), 'w').write(str(data))
        return page.url


def update(message, is_code=False):
    if is_code:
        user = message.from_user.id
        code_id = message.message_id
        code = message.text
        try:
            info = json.loads(f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'r').read())
        except:
            info = {'likes': {'all': 0, 'clicked': []}, 'people': 0, 'comments': 0, 'code': code, 'url': None,
                    'notified': False}
            f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(info))
            info = json.loads(f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'r').read())
        info['code'] = code
        f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(info))
        return False, False

    user = message.reply_to_message.from_user.id
    code_id = message.reply_to_message.message_id
    commenter = message.from_user.id
    comment = message.text
    code = message.reply_to_message.text

    if not code.startswith('#p'):
        return False, False

    likes = ['👍', '❤️']
    icons = ['❤️', '👤', '✏️']

    try:
        info = json.loads(f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'r').read())
    except:
        info = {'likes': {'all': 0, 'clicked': []}, 'people': 0, 'comments': 0, 'code': code, 'url': None,
                'notified': False}
        f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(info))
        info = json.loads(f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'r').read())

    for i in likes:
        if comment.startswith(i):
            if not commenter in info['likes']['clicked']:
                info['likes']['clicked'].append(commenter)
                info['likes']['all'] += 1

    try:
        data = json.loads(f.open('./comments/{}/codes/{}/{}.db'.format(user, code_id, code_id), 'r').read())
    except:
        data = {'users': {}}
        f.open('./comments/{}/codes/{}/{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(data))
        data = json.loads(f.open('./comments/{}/codes/{}/{}.db'.format(user, code_id, code_id), 'r').read())

    if str(commenter) in data['users'].keys():
        if str(message.message_id) in data['users'][str(commenter)].keys():
            data['users'][str(commenter)][str(message.message_id)][0] = node(message)[str(message.message_id)][0]
        else:
            data['users'][str(commenter)][str(message.message_id)] = node(message)[str(message.message_id)]
    else:
        data['users'][str(commenter)] = node(message)

    result = list()
    result.append({'tag': 'pre', 'children': [code]})
    result.append({'tag': 'aside', 'children': ['❤️ {}'.format(info['likes']['all'])]})
    all_people = 0
    all_comments = 0
    if len(data['users'].keys()) > 0:
        for _user in data['users'].keys():
            all_people += 1
            result.append({'tag': 'pre', 'children': [name(int(_user))]})
            for comment in data['users'][_user].keys():
                all_comments += 1
                result.append(data['users'][_user][comment][0])
                result.append(data['users'][_user][comment][1])
                br = {'tag': 'br'}
                result.append(br)

    info['people'] = all_people
    info['comments'] = all_comments

    result[1]['children'] = [
        '{likes}  {like} {space} {peoples}  {people} {space} {comments}  {comment}'.format(like=icons[0],
                                                                                           likes=info['likes']['all'],
                                                                                           people=icons[1],
                                                                                           peoples=info['people'],
                                                                                           comment=icons[2],
                                                                                           comments=info['comments'],
                                                                                           space=" " * 10)]
    if info['url']:
        page = client.edit_page(path=info['url'][18:], title='Kod uchun izohlar', content=result, author_name='Hops',
                                author_url='https://t.me/Hopsrobot', return_content=True)
    else:
        page = client.create_page(title='Kod uchun izohlar', content=result, author_name='Hops',
                                  author_url='https://t.me/Hopsrobot')

    try:
        all_pages = json.loads(f.open('./comments/{}/all.db'.format(user), 'r').read())
    except:
        f.open('./comments/{}/all.db'.format(user), 'w').write(json.dumps({"all": [], "url": None}))
        all_pages = json.loads(f.open('./comments/{}/all.db'.format(user), 'r').read())

    if not page.url in all_pages['all']:
        all_pages['all'].append(page.url)
        f.open('./comments/{}/all.db'.format(user), 'w').write(json.dumps(all_pages))

    info['url'] = page.url

    f.open('./comments/{}/codes/{}/info_{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(info))
    f.open('./comments/{}/codes/{}/{}.db'.format(user, code_id, code_id), 'w').write(json.dumps(data))
    if user == commenter:
        return False, False
    return page.url, True
