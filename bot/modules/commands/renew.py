from datetime import timedelta, datetime

from pyrogram import filters
from pyrogram.errors import BadRequest

from bot import bot, prefixes, LOGGER
from bot.func_helper.navid import navidService
from bot.func_helper.filters import admins_on_filter
from bot.func_helper.msg_utils import deleteMessage, sendMessage
from bot.sql_helper.sql_navid import sql_get_navid, sql_update_navid, Navid
from bot.sql_helper.sql_navid2 import sql_get_navid2, sql_update_navid2, Navid2


async def get_user_input(msg):
    await deleteMessage(msg)
    gm_name = msg.sender_chat.title if msg.sender_chat else f'管理员 [{msg.from_user.first_name}]({msg.from_user.id})'
    if msg.reply_to_message is None:
        try:
            b = msg.command[1]  # name
            c = float(msg.command[2])  # 天数
        except (IndexError, KeyError, BadRequest, ValueError, AttributeError):
            return None, None, None, None
    else:
        try:
            b = msg.reply_to_message.from_user.id
            c = float(msg.command[1])
        except (IndexError, KeyError, BadRequest, ValueError, AttributeError):
            return None, None, None, None

    navid = sql_get_navid(b)
    unbound = False
    if not navid:
        navid = sql_get_navid2(name=b)
        if not navid:
            await sendMessage(msg, f"♻️ 未检索到navid {b}，请确认重试或手动检查。")
            return None, None, None, None
        unbound = True

    return c, navid, unbound, gm_name


@bot.on_message(filters.command('renew', prefixes) & admins_on_filter)
async def renew_user(_, msg):
    days, navid, unbound, gm_name = await get_user_input(msg)
    if not navid:
        return await sendMessage(msg,
                                 f"🔔 **使用格式：**\n\n/renew [navid账户名] [+/-天数]\n或回复某人 /renew [+/-天数]",
                                 timer=60)
    reply = await msg.reply(f"🍓 正在处理ing···/·")
    try:
        name = f'[{navid.name}]({navid.tg})' if navid.tg else navid.name
    except:
        name = navid.name
    # 时间是 utc 来算的
    Now = datetime.now()
    ex_new = Now + timedelta(days=days) if Now > navid.ex else navid.ex + timedelta(days=days)
    lv = navid.lv
    # 无脑 允许播放
    if ex_new > Now:
        lv = 'a' if navid.lv == 'a' else 'b'
        await navidService.navid_change_policy(navid.navid_id, active=True)

    # 没有白名单就寄
    elif ex_new < Now:
        if navid.lv == 'a':
            pass
        else:
            lv = 'c'
            await navidService.navid_change_policy(navid.navid_id, method=False)

    if unbound == 1:
        expired = 1 if lv == 'c' else 0
        sql_update_navid2(Navid2.navid_id == navid.navid_id, ex=ex_new, expired=expired)
    else:
        sql_update_navid(Navid.tg == navid.tg, ex=ex_new, lv=lv)

    i = await reply.edit(
        f'🍒 __ {gm_name} 已调整 navid 用户 {name} 到期时间 {days} 天 (以当前时间计)__'
        f'\n📅 实时到期：{ex_new.strftime("%Y-%m-%d %H:%M:%S")}')
    try:
        await i.forward(navid.tg)
    except:
        pass

    LOGGER.info(
        f"【admin】[renew]：{gm_name} 对 navid账户 {name} 调节 {days} 天，"
        f"实时到期：{ex_new.strftime('%Y-%m-%d %H:%M:%S')}")
