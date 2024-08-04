from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

from bot import bot, group, LOGGER, _open
from bot.sql_helper.sql_navid import sql_get_navid
from bot.func_helper.navid import navidService


@bot.on_chat_member_updated(filters.chat(group))
async def leave_del_navid(_, event: ChatMemberUpdated):
    if event.old_chat_member and not event.new_chat_member:
        if not event.old_chat_member.is_member and event.old_chat_member.user:
            user_id = event.old_chat_member.user.id
            user_first_name = event.old_chat_member.user.first_name
            try:
                navid = sql_get_navid(user_id)
                if navid is None or navid.navid_id is None:
                    return
                if await navidService.navid_del(tg=navid.tg, navid_id=navid.navid_id):
                    LOGGER.info(
                        f'【退群删号】- {user_first_name}-{user_id} 已经离开了群组，咕噜噜，ta的账户被吃掉啦！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'✅ [{user_first_name}](tg://user?id={user_id}) 已经离开了群组，咕噜噜，ta的账户被吃掉啦！')
                else:
                    LOGGER.error(
                        f'【退群删号】- {user_first_name}-{user_id} 已经离开了群组，但是没能吃掉ta的账户，请管理员检查！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'❎ [{user_first_name}](tg://user?id={user_id}) 已经离开了群组，但是没能吃掉ta的账户，请管理员检查！')
                if _open.leave_ban:
                    await bot.ban_chat_member(chat_id=event.chat.id, user_id=user_id)
            except Exception as navid:
                LOGGER.error(f"【退群删号】- {user_id}: {navid}")
            else:
                pass
    elif event.old_chat_member and event.new_chat_member:
        if event.new_chat_member.status is ChatMemberStatus.BANNED:
            user_id = event.new_chat_member.user.id
            user_first_name = event.new_chat_member.user.first_name
            try:
                navid = sql_get_navid(user_id)
                if navid is None or navid.navid_id is None:
                    return
                if await navidService.navid_del(tg=navid.tg, navid_id=navid.navid_id):
                    LOGGER.info(
                        f'【退群删号】- {user_first_name}-{user_id} 已经离开了群组，咕噜噜，ta的账户被吃掉啦！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'✅ [{user_first_name}](tg://user?id={user_id}) 已经离开了群组，咕噜噜，ta的账户被吃掉啦！')
                else:
                    LOGGER.error(
                        f'【退群删号】- {user_first_name}-{user_id} 已经离开了群组，但是没能吃掉ta的账户，请管理员检查！')
                    await bot.send_message(chat_id=event.chat.id,
                                           text=f'❎ [{user_first_name}](tg://user?id={user_id}) 已经离开了群组，但是没能吃掉ta的账户，请管理员检查！')
                if _open.leave_ban:
                    await bot.ban_chat_member(chat_id=event.chat.id, user_id=user_id)
            except Exception as navid:
                LOGGER.error(f"【退群删号】- {user_id}: {navid}")
            else:
                pass
