import re
import json

from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.util import escape
from hoshino.aiorequests import post

sv = Service('能不能好好说话？', help_='''
[.guess 缩写] 查询
'''.strip())

async def query(text: str) -> str:
    if len(text) > 50:
        return '太、太长了8…'
    if not re.match(r'^[a-zA-Z0-9]+$', text):
        return '只能包含字母'
    rsp = await post(
        'https://lab.magiconch.com/api/nbnhhsh/guess',
        headers={'content-type': 'application/json'},
        data=json.dumps({'text': text}),
    )
    rsp = await rsp.json()
    rsp = rsp[0]
    trans = rsp.get('trans')
    if trans == None:
        result = ', '.join(rsp.get('inputting', []))
        if result == '':
            result = '最佳答案：我不知道'
        else:
            result = '有可能是：' + result
    else:
        result = ', '.join(trans)
    return result

@sv.on_prefix('.guess')
async def guess(bot, ev: CQEvent):
    s = escape(ev.message.extract_plain_text().strip())
    msg = await query(s)
    await bot.send(ev, msg, at_sender=True)

@sv.on_rex(re.compile(r'^\s*(?P<text>[a-zA-Z0-9]+)是(什么|甚么|啥|？|\?)'))
async def guess_re(bot, ev: CQEvent):
    match = ev['match']
    msg = await query(match.group('text'))
    await bot.send(ev, msg, at_sender=True)
