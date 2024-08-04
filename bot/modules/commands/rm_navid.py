from pyrogram import filters

from bot import bot, prefixes, LOGGER
from bot.func_helper.navid import navidService
from bot.func_helper.filters import admins_on_filter
from bot.func_helper.msg_utils import deleteMessage, editMessage
from bot.sql_helper.sql_navid import sql_get_navid


# 删除账号命令
@bot.on_message(filters.command('rm_navid', prefixes) & admins_on_filter)
async def rm_navid_user(_, msg):
    await deleteMessage(msg)
    reply = await msg.reply("🍉 正在处理ing....")
    if msg.reply_to_message is None:
        try:
            tag = msg.command[1]  # name
        except (IndexError, KeyError, ValueError):
            return await editMessage(reply,
                                     "🔔 **使用格式：**/rm_navid tg_id或回复某人 \n/rm_navid 亦可]")
        navid = sql_get_navid(tag)
    else:
        tag = msg.reply_to_message.from_user.id
        navid = sql_get_navid(tag)

    if navid is None:
        return await reply.edit(f"♻️ 没有检索到 {tag} 账户，请确认重试或手动检查。")

    if navid.navid_id is not None:
        first = await bot.get_chat(navid.tg)
        if await navidService.navid_del(tg=navid.tg, navid_id=navid.navid_id):
            try:
                await reply.edit(
                    f'🎯 done，管理员 [{msg.from_user.first_name}](tg://user?id={msg.from_user.id})\n[{first.first_name}]'
                    f'(tg://user?id={navid.tg}) 账户 {navid.name} '
                    f'已完成删除。')
                await bot.send_message(navid.tg,
                                       f'🎯 done，管理员 [{msg.from_user.first_name}](tg://user?id={msg.from_user.id})'
                                       f' 已将 您的账户 {navid.name} 删除。')
            except:
                pass
            LOGGER.info(
                f"【admin】：管理员 {msg.from_user.first_name} 执行删除 {first.first_name}-{navid.tg} 账户 {navid.name}")
    else:
        await reply.edit(f"💢 [ta](tg://user?id={tag}) 还没有注册账户呢")
