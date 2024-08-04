"""
kk - 纯装x
赠与账户，禁用，删除
"""
import pyrogram
from pyrogram import filters
from pyrogram.errors import BadRequest
from bot import bot, prefixes, owner, admins, LOGGER, config
from bot.func_helper.navid import navidService
from bot.func_helper.filters import admins_on_filter
from bot.func_helper.fix_bottons import cr_kk_ikb, gog_rester_ikb
from bot.func_helper.msg_utils import deleteMessage, sendMessage, editMessage
from bot.func_helper.utils import judge_admins, cr_link_two
from bot.sql_helper.sql_navid import sql_add_navid, sql_get_navid


# 管理用户
@bot.on_message(filters.command('kk', prefixes) & admins_on_filter)
async def user_info(_, msg):
    await deleteMessage(msg)
    if msg.reply_to_message is None:
        try:
            uid = int(msg.command[1])
            if not msg.sender_chat:
                if msg.from_user.id != owner and uid == owner:
                    return await sendMessage(msg,
                                             f"⭕ [{msg.from_user.first_name}](tg://user?id={msg.from_user.id})！不可以偷窥主人",
                                             timer=60)
            else:
                pass
            first = await bot.get_chat(uid)
        except (IndexError, KeyError, ValueError):
            return await sendMessage(msg, '**请先给我一个tg_id！**\n\n用法：/kk [tg_id]\n或者对某人回复kk', timer=60)
        except BadRequest:
            return await sendMessage(msg, f'{msg.command[1]} - 🎂抱歉，此id未登记bot，或者id错误', timer=60)
        except AttributeError:
            pass
        else:
            sql_add_navid(uid)
            text, keyboard = await cr_kk_ikb(uid, first.first_name)
            await sendMessage(msg, text=text, buttons=keyboard)  # protect_content=True 移除禁止复制

    else:
        uid = msg.reply_to_message.from_user.id
        try:
            if msg.from_user.id != owner and uid == owner:
                return await msg.reply(
                    f"⭕ [{msg.from_user.first_name}](tg://user?id={msg.from_user.id})！不可以偷窥主人")
        except AttributeError:
            pass

        sql_add_navid(uid)
        text, keyboard = await cr_kk_ikb(uid, msg.reply_to_message.from_user.first_name)
        await sendMessage(msg, text=text, buttons=keyboard)


# 赠送资格
@bot.on_callback_query(filters.regex('gift'))
async def gift(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("请不要以下犯上 ok？", show_alert=True)

    await call.answer("✅ ok")
    b = int(call.data.split("/")[1])
    if b in admins and b != call.from_user.id:
        return await editMessage(call,
                                 f"⚠️ 打咩，no，机器人不可以对bot管理员出手喔，请[自己](tg://user?id={call.from_user.id})解决")

    first = await bot.get_chat(b)
    e = sql_get_navid(b)
    if e.navid_id is None:
        link = await cr_link_two(call.from_user.id, for_tg=b, days=config.kk_gift_days)
        await editMessage(call, f"🌟 好的，管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n"
                                f'已为 [{first.first_name}](tg://user?id={b}) 赠予资格。前往bot进行下一步操作：',
                          buttons=gog_rester_ikb(link))
        LOGGER.info(f"【admin】：{call.from_user.id} 已发送 注册资格 {first.first_name} - {b} ")
    else:
        await editMessage(call, f'💢 [ta](tg://user?id={b}) 已注册账户。')


# 删除账户
@bot.on_callback_query(filters.regex('close_navid'))
async def close_emby(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("请不要以下犯上 ok？", show_alert=True)

    await call.answer("✅ ok")
    b = int(call.data.split("/")[1])
    if b in admins and b != call.from_user.id:
        return await editMessage(call,
                                 f"⚠️ 打咩，no，机器人不可以对bot管理员出手喔，请[自己](tg://user?id={call.from_user.id})解决",
                                 timer=60)

    first = await bot.get_chat(b)
    navid = sql_get_navid(b)
    if navid.navid_id is None:
        return await editMessage(call, f'💢 ta 还没有注册账户。', timer=60)

    if await navidService.navid_del(tg=navid.tg, navid_id=navid.navid_id):
        await editMessage(call,
                          f'🎯 done，管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id})\n等级：{navid.lv} - [{first.first_name}](tg://user?id={b}) '
                          f'账户 {navid.name} 已完成删除。')
        await bot.send_message(b,
                               f"🎯 管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id}) 已删除 您 的账户 {navid.name}")
        LOGGER.info(f"【admin】：{call.from_user.id} 完成删除 {b} 的账户 {navid.name}")
    else:
        await editMessage(call, f'🎯 done，等级：{navid.lv} - {first.first_name}的账户 {navid.name} 删除失败。')
        LOGGER.info(f"【admin】：{call.from_user.id} 对 {b} 的账户 {navid.name} 删除失败 ")


@bot.on_callback_query(filters.regex('fuck_off'))
async def fuck_off_m(_, call):
    if not judge_admins(call.from_user.id):
        return await call.answer("请不要以下犯上 ok？", show_alert=True)

    await call.answer("✅ ok")
    tg = int(call.data.split("/")[1])
    if tg in admins and tg != call.from_user.id:
        return await editMessage(call,
                                 f"⚠️ 打咩，no，机器人不可以对bot管理员出手喔，请[自己](tg://user?id={call.from_user.id})解决",
                                 timer=60)
    try:
        first = await bot.get_chat(tg)
        await bot.ban_chat_member(call.message.chat.id, tg)
        navid = await sql_get_navid(tg)
        if navid:
            await navidService.navid_del(tg=tg, navid_id=navid.navid_id)
        await editMessage(call,
                          f'🎯 done，管理员 [{call.from_user.first_name}](tg://user?id={call.from_user.id}) 已移除 {first.first_name}')
        LOGGER.info(
            f"【admin】：{call.from_user.id} 已从群组 {call.message.chat.id} 封禁 {first.first_name} - {tg}")
    except pyrogram.errors.ChatAdminRequired:
        await editMessage(call,
                          f"⚠️ 请赋予我踢出成员的权限 [{call.from_user.first_name}](tg://user?id={call.from_user.id})")
    except pyrogram.errors.UserAdminInvalid:
        await editMessage(call,
                          f"⚠️ 打咩，no，机器人不可以对群组管理员出手喔，请[自己](tg://user?id={call.from_user.id})解决")
