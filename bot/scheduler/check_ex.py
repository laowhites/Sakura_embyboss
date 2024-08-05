"""
定时检测账户有无过期
"""
from datetime import timedelta, datetime

from pyrogram.errors import FloodWait
from sqlalchemy import and_
from asyncio import sleep
from bot import bot, group, LOGGER, _open
from bot.func_helper.navid import navidService
from bot.sql_helper.sql_navid import Navid, get_all_navid, sql_update_navid
from bot.sql_helper.sql_navid2 import get_all_navid2, Navid2, sql_update_navid2


async def check_expired():
    # 询问 到期时间的用户，判断有无积分，有则续期，无就禁用
    rst = get_all_navid(and_(Navid.ex < datetime.now(), Navid.lv == 'b'))
    if rst is None:
        return LOGGER.info('【到期检测】- 等级 b 无到期用户，跳过')
    dead_day = datetime.now() + timedelta(days=5)
    ext = (datetime.now() + timedelta(days=30))
    for r in rst:
        if r.us >= 30:
            b = r.us - 30
            if sql_update_navid(Navid.tg == r.tg, ex=ext, us=b):
                text = f'【到期检测】\n#id{r.tg} 续期账户 [{r.name}](tg://user?id={r.tg})\n' \
                       f'在当前时间自动续期30天\n' \
                       f'📅实时到期：{ext.strftime("%Y-%m-%d %H:%M:%S")}'
                LOGGER.info(text)
            else:
                text = f'【到期检测】\n#id{r.tg} 续期账户 [{r.name}](tg://user?id={r.tg})\n' \
                       f'自动续期失败，请联系闺蜜（管理）'
                LOGGER.error(text)
            try:
                await bot.send_message(r.tg, text)
            except FloodWait as f:
                LOGGER.warning(str(f))
                await sleep(f.value * 1.2)
                await bot.send_message(r.tg, text)
            except Exception as e:
                LOGGER.error(e)

        elif _open.exchange and r.iv >= _open.exchange_cost * 30:
            b = r.iv - _open.exchange_cost * 30
            if sql_update_navid(Navid.tg == r.tg, ex=ext, iv=b):
                text = f'【到期检测】\n#id{r.tg} 续期账户 [{r.name}](tg://user?id={r.tg})\n' \
                       f'在当前时间自动续期30天\n' \
                       f'📅实时到期: {ext.strftime("%Y-%m-%d %H:%M:%S")}'
                LOGGER.info(text)
            else:
                text = f'【到期检测】\n#id{r.tg} 续期账户 [{r.name}](tg://user?id={r.tg})\n续期失败，请联系闺蜜（管理）'
                LOGGER.error(text)
            try:
                await bot.send_message(r.tg, text)
            except FloodWait as f:
                LOGGER.warning(str(f))
                await sleep(f.value * 1.2)
                await bot.send_message(r.tg, text)
            except Exception as e:
                LOGGER.error(e)

        else:
            if await navidService.navid_change_policy(r.navid_id, active=False):
                if sql_update_navid(Navid.tg == r.tg, lv='c'):
                    text = (f'【到期检测】\n#id{r.tg} 到期禁用 [{r.name}](tg://user?id={r.tg})\n'
                            f'将为您封存至 {dead_day.strftime("%Y-%m-%d")}，请及时续期')
                    LOGGER.info(text)
                else:
                    text = f'【到期检测】\n#id{r.tg} 到期禁用 [{r.name}](tg://user?id={r.tg}) 已禁用，数据库写入失败'
                    LOGGER.warning(text)
            else:
                text = f'【到期检测】\n#id{r.tg} 到期禁用 [{r.name}](tg://user?id={r.tg}) embyapi操作失败'
                LOGGER.error(text)
            try:
                send = await bot.send_message(r.tg, text)
                await send.forward(group[0])
            except FloodWait as f:
                LOGGER.warning(str(f))
                await sleep(f.value * 1.2)
                send = await bot.send_message(r.tg, text)
                await send.forward(group[0])
            except Exception as e:
                LOGGER.error(e)

    rsc = get_all_navid(and_(Navid.ex < datetime.now(), Navid.lv == 'c'))
    if rsc is None:
        return LOGGER.info('【到期检测】- 等级 c 无到期用户，跳过')
    for c in rsc:
        if c.us >= 30:
            c_us = c.us - 30
            if await navidService.navid_change_policy(id=c.navid_id, active=True):
                if sql_update_navid(Navid.tg == c.tg, lv='b', ex=ext, us=c_us):
                    text = f'【到期检测】\n#id{c.tg} 解封账户 [{c.name}](tg://user?id={c.tg})\n' \
                           f'在当前时间自动续期30天\n📅实时到期: {ext.strftime("%Y-%m-%d %H:%M:%S")}'
                    LOGGER.info(text)
                else:
                    text = f'【到期检测】\n#id{c.tg} 解封账户 [{c.name}](tg://user?id={c.tg}) 数据库写入失败，请联系管理'
                    LOGGER.warning(text)
            else:
                text = f'【到期检测】\n#id{c.tg} 解封账户 [{c.name}](tg://user?id={c.tg}) embyapi操作失败'
                LOGGER.error(text)
            try:
                await bot.send_message(c.tg, text)
            except FloodWait as f:
                LOGGER.warning(str(f))
                await sleep(f.value * 1.2)
                await bot.send_message(c.tg, text)
            except Exception as e:
                LOGGER.error(e)

        elif _open.exchange and c.iv >= _open.exchange_cost * 30:
            c_iv = c.iv - _open.exchange_cost * 30
            if await navidService.navid_change_policy(id=c.navid_id, method=True):
                if sql_update_navid(Navid.tg == c.tg, lv='b', ex=ext, iv=c_iv):
                    text = (f'【到期检测】\n#id{c.tg} 解封账户 [{c.name}](tg://user?id={c.tg})\n'
                            f'在当前时间自动续期30天\n📅实时到期：{ext.strftime("%Y-%m-%d %H:%M:%S")}')
                    LOGGER.info(text)
                else:
                    text = f'【到期检测】\n#id{c.tg} 解封账户 [{c.name}](tg://user?id={c.tg}) 已禁用，数据库写入失败，请联系管理'
                    LOGGER.warning(text)
            else:
                text = f'【到期检测】\n#id{c.tg} 解封账户 [{c.name}](tg://user?id={c.tg}) embyapi操作失败，请联系管理'
                LOGGER.error(text)
            try:
                await bot.send_message(c.tg, text)
            except FloodWait as f:
                LOGGER.warning(str(f))
                await sleep(f.value * 1.2)
                await bot.send_message(c.tg.text)
            except Exception as e:
                LOGGER.error(e)

        else:
            delta = c.ex + timedelta(days=5)
            if datetime.now() < delta:
                continue
            if await navidService.navid_del(navid_id=c.navid_id):
                text = f'【到期检测】\n#id{c.tg} 删除账户 [{c.name}](tg://user?id={c.tg})\n已到期 5 天，执行清除任务。期待下次与你相遇'
                LOGGER.info(text)
            else:
                text = f'【到期检测】\n#id{c.tg} #删除账户 [{c.name}](tg://user?id={c.tg})\n到期删除失败，请检查以免无法进行后续使用'
                LOGGER.warning(text)
            try:
                send = await bot.send_message(c.tg, text)
                await send.forward(group[0])
            except FloodWait as f:
                LOGGER.warning(str(f))
                await sleep(f.value * 1.2)
                send = await bot.send_message(c.tg.text)
                await send.forward(group[0])
            except Exception as e:
                LOGGER.error(e)

    rseired = get_all_navid2(and_(Navid2.expired == 0, Navid2.ex < datetime.now()))
    if rseired is None:
        return LOGGER.info(f'【封禁检测】- navid2 无数据，跳过')
    for e in rseired:
        if await navidService.navid_del(navid_id=e.navid_id, unbound=True):
            if sql_update_navid2(Navid2.navid_id == e.navid_id, expired=1):
                text = f"【封禁检测】- 到期封印非TG账户 [{e.name}](google.com?q={e.navid_id}) Done！"
                LOGGER.info(text)
            else:
                text = f'【封禁检测】- 到期封印非TG账户：`{e.name}` 数据库更改失败'
        else:
            text = '【封禁检测】- 到期封印非TG账户：`{e.name}` navidapi操作失败，请手动'
        try:
            await bot.send_message(group[0], text)
        except FloodWait as f:
            LOGGER.warning(str(f))
            await sleep(f.value * 1.2)
            await bot.send_message(group[0].text)
        except Exception as e:
            LOGGER.error(e)
