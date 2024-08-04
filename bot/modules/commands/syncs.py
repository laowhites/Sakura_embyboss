"""
Syncs 功能

1.sync——groupm 群组成员同步任务，遍历数据库中等级 b 账户，tgapi检测是否仍在群组，否->封禁

2.sync——unbound 绑定同步任务，遍历服务器中users，未在数据表中找到同名数据的即 删除

3. 小功能 - 给admin的账号开管理员后台，但是会被续期覆盖

"""
import time
from datetime import datetime, timedelta
from asyncio import sleep
from pyrogram import filters
from pyrogram.errors import FloodWait
from bot import bot, prefixes, bot_photo, LOGGER, owner, group
from bot.func_helper.navid import navidService
from bot.func_helper.filters import admins_on_filter
from bot.sql_helper.sql_navid import get_all_navid, Navid, sql_get_navid, sql_update_navids, sql_delete_navid
from bot.func_helper.msg_utils import deleteMessage, sendMessage, sendPhoto
from bot.sql_helper.sql_navid2 import sql_get_navid2


@bot.on_message(filters.command('syncgroupm', prefixes) & admins_on_filter)
async def sync_navid_group(_, msg):
    await deleteMessage(msg)
    send = await sendPhoto(msg, photo=bot_photo, caption="⚡群组成员同步任务\n  **正在开启中...消灭未在群组的账户**",
                           send=True)
    LOGGER.info(
        f"【群组成员同步任务开启】 - {msg.from_user.first_name} - {msg.from_user.id}")
    # 减少api调用
    members = [member.user.id async for member in bot.get_chat_members(group[0])]
    r = get_all_navid(Navid.lv == 'b')
    if not r:
        return await send.edit("⚡群组同步任务\n\n结束！搞毛，没有人。")
    a = b = 0
    text = ''
    start = time.perf_counter()
    for navid in r:
        b += 1
        if navid.tg not in members:
            if await navidService.navid_del(navid.tg, navid.navid_id):
                a += 1
                reply_text = f'{b}. #id{navid.tg} - [{navid.name}](tg://user?id={navid.tg}) 删除\n'
                LOGGER.info(reply_text)
                sql_delete_navid(tg=navid.tg)
            else:
                reply_text = f'{b}. #id{navid.tg} - [{navid.name}](tg://user?id={navid.tg}) 删除错误\n'
                LOGGER.error(reply_text)
            text += reply_text
            try:
                await bot.send_message(navid.tg, reply_text)
            except FloodWait as f:
                LOGGER.warning(str(f))
                await sleep(f.value * 1.2)
                await bot.send_message(navid.tg, reply_text)
            except Exception as e:
                LOGGER.error(e)

    # 防止触发 MESSAGE_TOO_LONG 异常，text可以是4096，caption为1024，取小会使界面好看些
    n = 1000
    chunks = [text[i:i + n] for i in range(0, len(text), n)]
    for c in chunks:
        await sendMessage(msg, c + f'\n🔈 当前时间：{datetime.now().strftime("%Y-%m-%d")}')
    end = time.perf_counter()
    times = end - start
    if a != 0:
        await sendMessage(msg,
                          text=f"**⚡群组成员同步任务 结束！**\n  共检索出 {b} 个账户，处刑 {a} 个账户，耗时：{times:.3f}s")
    else:
        await sendMessage(msg, text="** 群组成员同步任务 结束！没人偷跑~**")
    LOGGER.info(f"【群组同步任务结束】 - {msg.from_user.id} 共检索出 {b} 个账户，处刑 {a} 个账户，耗时：{times:.3f}s")


@bot.on_message(filters.command('sync_unbound', prefixes) & admins_on_filter)
async def sync_navid_unbound(_, msg):
    await deleteMessage(msg)
    send = await sendPhoto(msg, photo=bot_photo, caption="⚡绑定同步任务\n  **正在开启中...消灭未绑定bot的navid账户**",
                           send=True)
    LOGGER.info(
        f"【绑定同步任务开启 - 消灭未绑定bot的navid账户】 - {msg.from_user.first_name} - {msg.from_user.id}")
    a = b = 0
    text = ''
    start = time.perf_counter()
    success, server_navids = await navidService.users()
    if not success or server_navids is None:
        return await send.edit("⚡绑定同步任务\n\n结束！搞毛，没有人。")

    if success:
        for server_navid in server_navids:
            b += 1
            try:
                # 消灭不是管理员的账号
                if not server_navid['isAdmin']:
                    navid_id = server_navid['id']
                    # 查询无异常，并且无sql记录
                    navid = sql_get_navid(navid_id)
                    if navid is None:
                        navid2 = sql_get_navid2(name=server_navid)
                        if navid2 is not None:
                            a += 1
                            await navidService.navid_del(navid_id=server_navid, unbound=True)
                            text += f"🎯 #{server_navid['userName']} 未绑定bot，删除\n"
            except Exception as navid:
                LOGGER.warning(navid)
        # 防止触发 MESSAGE_TOO_LONG 异常
        n = 1000
        chunks = [text[i:i + n] for i in range(0, len(text), n)]
        for c in chunks:
            await sendMessage(msg, c + f'\n**{datetime.now().strftime("%Y-%m-%d")}**')
    end = time.perf_counter()
    times = end - start
    if a != 0:
        await sendMessage(msg, text=f"⚡绑定同步任务 done\n  共检索出 {b} 个账户，删除 {a}个，耗时：{times:.3f}s")
    else:
        await sendMessage(msg, text=f"**绑定同步任务 结束！搞毛，没有人被干掉。**")
    LOGGER.info(f"【绑定同步任务结束】 - {msg.from_user.id} 共检索出 {b} 个账户，删除 {a}个，耗时：{times:.3f}s")


@bot.on_message(filters.command('navid_admin', prefixes) & admins_on_filter)
async def reload_admins(_, msg):
    await deleteMessage(msg)
    e = sql_get_navid(msg.from_user.id)
    if e.navid_id is not None:
        await navidService.navid_admin(id=e.navid_id, admin=True)
        LOGGER.info(f"{msg.from_user.first_name} - {msg.from_user.id} 开启了 navid 后台")
        await sendMessage(msg, "👮🏻 授权完成。已开启navid后台", timer=60)
    else:
        LOGGER.info(f"{msg.from_user.first_name} - {msg.from_user.id} 开启 navid 后台失败")
        await sendMessage(msg, "👮🏻 授权失败。未查询到绑定账户", timer=60)


@bot.on_message(filters.command('kick_not_navid', prefixes) & admins_on_filter & filters.group)
async def kick_not_navid(_, msg):
    await deleteMessage(msg)
    try:
        open_kick = msg.command[1]
    except:
        return await sendMessage(msg,
                                 '注意: 此操作会将 当前群组中无navid账户的选手kick, 如确定使用请输入 `/kick_not_navid true`')
    if open_kick == 'true':
        LOGGER.info(f"{msg.from_user.first_name} - {msg.from_user.id} 执行了踢出非navid用户的操作")
        navid_users = get_all_navid(Navid.navid_id is not None and Navid.navid_id != '')
        # get tgid
        navid_tags = []
        if navid_users:
            navid_tags = [i.tg for i in navid_users]
        chat_members = [member.user.id async for member in bot.get_chat_members(chat_id=msg.chat.id)]
        until_date = datetime.now() + timedelta(minutes=1)
        for cmember in chat_members:
            if cmember not in navid_tags:
                try:
                    await msg.chat.ban_member(cmember, until_date=until_date)
                    await sendMessage(msg, f'{cmember} 已踢出', send=True)
                    LOGGER.info(f"{cmember} 已踢出")
                except Exception as e:
                    LOGGER.info(f"踢出 {cmember} 失败，原因: {e}")
                    pass
