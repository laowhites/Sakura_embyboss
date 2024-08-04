import asyncio
from pyrogram import filters
from pyrogram.errors import BadRequest

from bot import bot, prefixes, LOGGER, navid_line, owner, bot_photo, schedule
from bot.func_helper.navid import navidService
from bot.func_helper.filters import admins_on_filter
from bot.func_helper.fix_bottons import cv_user_ip
from bot.func_helper.msg_utils import sendMessage, editMessage, callAnswer, sendPhoto
from bot.sql_helper.sql_navid import sql_get_navid
from bot.sql_helper.sql_navid2 import sql_get_navid2


@bot.on_message(filters.command('ucr', prefixes) & admins_on_filter & filters.private)
async def admin_create(_, msg):
    # await deleteMessage(msg)
    try:
        name = msg.command[1]
        days = int(msg.command[2])
    except (IndexError, ValueError, KeyError):
        return await sendMessage(msg, "🔍 **无效的值。\n\n正确用法:** `/ucr [用户名] [使用天数]`", timer=60)
    else:
        send = await msg.reply(
            f'🆗 收到设置\n\n用户名：**{name}**\n\n__正在为您初始化账户，更新用户策略__......')
        try:
            int(name)
        except ValueError:
            pass
        else:
            try:
                await bot.get_chat(name)
            except BadRequest:
                pass
            else:
                await send.edit("🚫 根据银河正义法，您创建的用户名不得与任何 tg_id 相同")
                return
        await asyncio.sleep(1)
        pwd1 = await navidService.navid_create(5210, name, 1234, days, 'o')
        if pwd1 == 100:
            await send.edit(
                '**❎ 已有此账户名，请重新输入注册**\n或 ❔ __navid服务器未知错误！！！请联系闺蜜（管理）__ **会话已结束！**')
            LOGGER.error("未知错误，检查数据库和navid状态")
        elif pwd1 == 403:
            await send.edit('**🚫 很抱歉，注册总数已达限制**\n【admin】——>【注册状态】中可调节')
        else:
            await send.edit(
                f'**🎉 成功创建有效期{days}天 #{name}\n\n• 用户名称 | `{name}`\n'
                f'• 用户密码 | `{pwd1[0]}`\n• 安全密码 | `{1234}`\n'
                f'• 当前线路 | \n{navid_line}\n\n• 到期时间 | {pwd1[1]}**')

            await bot.send_message(owner,
                                   f"®️ 您的管理员 {msg.from_user.first_name} - `{msg.from_user.id}` 已经创建了一个非tg绑定用户 #{name} 有效期**{days}**天")
            LOGGER.info(f"【创建tg外账户】：{msg.from_user.id} - 建立了账户 {name}，有效期{days}天 ")


# 删除指定用户名账号命令
@bot.on_message(filters.command('urm', prefixes) & admins_on_filter)
async def urm_user(_, msg):
    reply = await msg.reply("🍉 正在处理ing....")
    try:
        navid_name = msg.command[1]  # name
    except IndexError:
        return await asyncio.gather(editMessage(reply,
                                                "🔔 **使用格式：**/urm [navid用户名]，此命令用于删除指定用户名的用户"),
                                    msg.delete())
    navid = sql_get_navid(navid_name)
    unbound = False
    if not navid:
        e2 = sql_get_navid2(name=navid_name)
        if not e2:
            return await reply.edit(f"♻️ 没有检索到 {navid_name} 账户，请确认重试或手动检查。")
        navid = e2
        unbound = True

    if await navidService.navid_del(tg=navid.tg, navid_id=navid.navid_id, unbound=unbound):
        try:
            await reply.edit(
                f'🎯 done，管理员 [{msg.from_user.first_name}](tg://user?id={msg.from_user.id})\n'
                f'账户 {navidService.name} 已完成删除。')
        except:
            pass
        LOGGER.info(f"【admin】：管理员 {msg.from_user.first_name} 执行删除 navid账户 {navidService.name}")


@bot.on_message(filters.command('uinfo', prefixes) & admins_on_filter)
async def uun_info(_, msg):
    try:
        n = msg.command[1]
    except IndexError:
        return await asyncio.gather(msg.delete(), sendMessage(msg, "⭕ 用法：/uinfo + navid用户名"))
    else:
        text = ''
        navid = sql_get_navid(n)
        if not navid:
            e2 = sql_get_navid2(n)
            if not e2:
                return await sendMessage(msg, f'数据库中未查询到 {n}，请手动确认')
            navid = e2
    try:
        a = f'**· 🆔 查询 TG** | {navid.tg}\n'
    except AttributeError:
        a = ''

    text += f"▎ 查询返回\n" \
            f"**· 🍉 账户名称** | {navid.name}\n{a}" \
            f"**· 🍓 当前状态** | {navid.lv}\n" \
            f"**· 🍒 创建时间** | {navid.cr}\n" \
            f"**· 🚨 到期时间** | **{navid.ex}**\n"

    await asyncio.gather(sendPhoto(msg, photo=bot_photo, caption=text, buttons=cv_user_ip(navid.navid_id)),
                         msg.delete())
