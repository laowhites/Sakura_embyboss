import asyncio
import random
from datetime import datetime, timezone, timedelta

from pyrogram import filters

from bot import bot, _open, sakura_b
from bot.func_helper.filters import user_in_group_on_filter
from bot.func_helper.msg_utils import callAnswer, sendMessage, deleteMessage
from bot.sql_helper.sql_navid import sql_get_navid, sql_update_navid, Navid


@bot.on_callback_query(filters.regex('checkin') & user_in_group_on_filter)
async def user_in_checkin(_, call):
    if _open.checkin:
        navid = sql_get_navid(call.from_user.id)
        now = datetime.now()
        if not navid:
            return await callAnswer(call, '🧮 未查询到数据库', True)
        elif not navid.ch or navid.ch.strftime("%Y-%m-%d") < now.strftime("%Y-%m-%d"):
            reward = random.randint(1, 10)
            s = navid.iv + reward
            # 正常状态用户签到生效
            ex = navid.ex
            ex_new = now + timedelta(days=_open.checkin_duration);
            if navid.lv == 'b' and ex_new > navid.ex:
                ex = ex_new
            sql_update_navid(Navid.tg == call.from_user.id, iv=s, ch=now, ex=ex)
            text = (f'🎉 **签到成功** | {reward} {sakura_b}\n'
                    f'💴 **当前状态** | {s} {sakura_b}\n'
                    f'💴 **有效期至** | {ex.strftime("%Y-%m-%d")}\n'
                    f'⏳ **签到日期** | {now.strftime("%Y-%m-%d")}')
            await asyncio.gather(deleteMessage(call), sendMessage(call, text=text))

        else:
            await callAnswer(call, '⭕ 您今天已经签到过了！签到是无聊的活动哦。', True)
    else:
        await callAnswer(call, '❌ 未开启签到系统，等待！', True)
