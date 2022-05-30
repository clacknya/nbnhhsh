#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import aiohttp

from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.util import escape

sv = Service('能不能好好说话？', help_='''
[.guess 缩写] 查询
'''.strip())

async def query(text: str) -> str:
    if len(text) > 50:
        return '太、太长了8…'
    if not re.match(r'^[a-zA-Z0-9]+$', text):
        return '只能包含字母'
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.post('https://lab.magiconch.com/api/nbnhhsh/guess', data={'text': text}) as resp:
            ret = await resp.json()
    result = []
    for item in ret:
        prefix = '[%s]: ' % item.get('name')
        trans = item.get('trans')
        if trans == None:
            inputting = ', '.join(item.get('inputting', []))
            if inputting == '':
                ans = '优质解答：我不知道'
            else:
                ans = '有可能是：' + inputting
        else:
            ans = ', '.join(trans)
        result.append(prefix + ans)
    return '\n'.join(result)

@sv.on_prefix('.guess')
async def guess(bot, ev: CQEvent):
    s = escape(ev.message.extract_plain_text().strip())
    msg = await query(s)
    if msg:
        await bot.send(ev, msg, at_sender=True)

@sv.on_rex(re.compile(r'^\s*(?P<text>[a-zA-Z0-9]+)是(什么|甚么|啥|？|\?)'))
async def guess_re(bot, ev: CQEvent):
    match = ev['match']
    msg = await query(match.group('text'))
    if msg:
        await bot.send(ev, msg, at_sender=True)
