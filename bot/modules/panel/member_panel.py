"""
用户区面板代码
先检测有无账户
无 -> 创建账户、换绑tg

有 -> 账户续期，重置密码，删除账户，显隐媒体库
"""
import asyncio
import datetime
import math
import random
from datetime import timedelta, datetime

from pyrogram.errors import BadRequest
from bot.schemas import ExDate, Yulv
from bot import bot, navid_line, LOGGER, _open, sakura_b, group, config, user_buy, bot_name
from pyrogram import filters
from bot.func_helper.navid import navidService
from bot.func_helper.filters import user_in_group_on_filter
from bot.func_helper.utils import members_info, tem_alluser, cr_link_one, open_check
from bot.func_helper.fix_bottons import members_ikb, back_members_ikb, re_create_ikb, del_me_ikb, re_delme_ikb, \
    re_reset_ikb, re_changetg_ikb, re_exchange_b_ikb, store_ikb, re_store_renew, re_bindtg_ikb, close_it_ikb, \
    user_query_page
from bot.func_helper.msg_utils import callAnswer, editMessage, callListen, sendMessage, ask_return, deleteMessage
from bot.modules.commands import p_start
from bot.modules.commands.exchange import rgs_code
from bot.sql_helper.sql_code import sql_count_c_code
from bot.sql_helper.sql_navid import sql_get_navid, sql_update_navid, Navid, sql_delete_navid
from bot.sql_helper.sql_navid2 import sql_get_navid2, sql_delete_navid2


# 创号函数
async def create_user(_, call, us, stats):
    same = await editMessage(call,
                             text='🤖**注意：您已进入注册状态:\n\n• 请在2min内输入 `[用户名][空格][安全码]`\n• '
                                  '举个例子🌰：`二狗 1234`**\n\n• 用户名中不限制中/英文/emoji，🚫**特殊字符**'
                                  '\n• 安全码为敏感操作时附加验证，请填入最熟悉的数字4~6位；退出请点 /cancel')
    if same is False:
        return

    txt = await callListen(call, 120, buttons=back_members_ikb)
    if txt is False:
        return

    elif txt.text == '/cancel':
        return await asyncio.gather(txt.delete(),
                                    editMessage(call, '__您已经取消输入__ **会话已结束！**', back_members_ikb))
    else:
        try:
            await txt.delete()
            navid_name, navid_pwd2 = txt.text.split()
        except (IndexError, ValueError):
            await editMessage(call, f'⚠️ 输入格式错误\n【`{txt.text}`】\n **会话已结束！**', re_create_ikb)
        else:
            await editMessage(call,
                              f'🆗 会话结束，收到设置\n\n用户名：**{navid_name}**  安全码：**{navid_pwd2}** \n\n__正在为您创建账户__......')
            try:
                x = int(navid_name)
            except ValueError:
                pass
            else:
                try:
                    await bot.get_chat(x)
                except BadRequest:
                    pass
                else:
                    return await editMessage(call, "🚫 根据银河正义法，您创建的用户名不得与任何 tg_id 相同",
                                             re_create_ikb)
            # await asyncio.sleep(1)
            # navid api操作
            pwd1 = await navidService.navid_create(call.from_user.id, navid_name, navid_pwd2, us, stats)
            if pwd1 == 403:
                await editMessage(call, '**🚫 很抱歉，注册总数已达限制。**', back_members_ikb)
            elif pwd1 == 100:
                await editMessage(call,
                                  '**- ❎ 已有此账户名，请重新输入注册\n- ❎ 或检查有无特殊字符\n- ❎ 或navid服务器连接不通，会话已结束！**',
                                  re_create_ikb)
                LOGGER.error("【创建账户】：重复账户 or 未知错误！")
            else:
                await editMessage(call,
                                  f'**▎创建用户成功🎉**\n\n'
                                  f'· 用户名称 | `{navid_name}`\n'
                                  f'· 用户密码 | `{pwd1[0]}`\n'
                                  f'· 安全密码 | `{navid_pwd2}`（仅发送一次）\n'
                                  f'· 到期时间 | `{pwd1[1]}`\n'
                                  f'· 当前线路：\n'
                                  f'{navid_line}\n\n'
                                  f'**·【服务器】 - 查看线路和密码**')
                if stats == 'y':
                    LOGGER.info(f"【创建账户】[开注状态]：{call.from_user.id} - 建立了 {navid_name} ")
                elif stats == 'n':
                    LOGGER.info(f"【创建账户】：{call.from_user.id} - 建立了 {navid_name} ")
                await tem_alluser()


# 键盘中转
@bot.on_callback_query(filters.regex('members') & user_in_group_on_filter)
async def members(_, call):
    data = await members_info(call.from_user.id)
    if not data:
        return await callAnswer(call, '⚠️ 数据库没有你，请重新 /start录入', True)
    await callAnswer(call, f"✅ 用户界面")
    stat, all_user, tem, timing, allow_code = await open_check()
    name, lv, ex, us, navid_id, pwd2 = data
    text = f"▎__欢迎进入用户面板！{call.from_user.first_name}__\n\n" \
           f"**· 🆔 用户のID** | `{call.from_user.id}`\n" \
           f"**· 📊 当前状态** | {lv}\n" \
           f"**· 🚗 剩余车位** | {all_user - tem}\n" \
           f"**· 🍒 积分{sakura_b}** | {us[0]} · {us[1]}\n" \
           f"**· 💠 账号名称** | [{name}](tg://user?id={call.from_user.id})\n" \
           f"**· 🚨 到期时间** | {ex}"
    if not navid_id:
        await editMessage(call, text, members_ikb(False))
    else:
        await editMessage(call, text, members_ikb(True))


# 创建账户
@bot.on_callback_query(filters.regex('create') & user_in_group_on_filter)
async def create(_, call):
    e = sql_get_navid(call.from_user.id)
    if not e:
        return await callAnswer(call, '⚠️ 数据库没有你，请重新 /start录入', True)

    if e.navid_id:
        await callAnswer(call, '💦 你已经有账户啦！请勿重复注册。', True)
    elif not _open.stat and int(e.us) <= 0:
        await callAnswer(call, f'🤖 自助注册已关闭，等待开启。', True)
    elif not _open.stat and int(e.us) > 0:
        send = await callAnswer(call, f'🪙 积分满足要求，请稍后。', True)
        if send is False:
            return
        else:
            await create_user(_, call, us=e.us, stats='n')
    elif _open.stat:
        send = await callAnswer(call, f"🪙 开放注册，免除积分要求。", True)
        if send is False:
            return
        else:
            await create_user(_, call, us=30, stats='y')


# 换绑tg
@bot.on_callback_query(filters.regex('changetg') & user_in_group_on_filter)
async def change_tg(_, call):
    d = sql_get_navid(call.from_user.id)
    if not d:
        return await callAnswer(call, '⚠️ 数据库没有你，请重新 /start录入', True)
    if d.navid_id:
        return await callAnswer(call, '⚖️ 您已经拥有账户，请不要钻空子', True)

    await callAnswer(call, '⚖️ 更换绑定的TG')
    send = await editMessage(call,
                             '🔰 **【更换绑定navid的tg】**\n'
                             '须知：\n'
                             '- **请确保您之前用其他tg账户注册过**\n'
                             '- **请确保您注册的其他tg账户呈已注销状态**\n'
                             '- **请确保输入正确的navid用户名，安全码/密码**\n\n'
                             '您有120s回复 `[navid用户名] [安全码/密码]`\n例如 `二狗 1234` ”，退出点 /cancel')
    if send is False:
        return

    m = await callListen(call, 120, buttons=back_members_ikb)
    if m is False:
        return

    elif m.text == '/cancel':
        await m.delete()
        await editMessage(call, '__您已经取消输入__ **会话已结束！**', back_members_ikb)
    else:
        try:
            await m.delete()
            navid_name, navid_pwd = m.text.split()
        except (IndexError, ValueError):
            return await editMessage(call, f'⚠️ 输入格式错误\n【`{m.text}`】\n **会话已结束！**', re_changetg_ikb)

        await editMessage(call,
                          f'✔️ 会话结束，收到设置\n\n用户名：**{navid_name}** 正在检查码 **{navid_pwd}**......')

        pwd = '空（直接回车）', 5210 if navid_pwd == 'None' else navid_pwd, navid_pwd
        e = sql_get_navid(navid_name)
        if e is None:
            # 在navid2中，验证安全码 或者密码
            e2 = sql_get_navid2(name=navid_name)
            if e2 is None:
                return await editMessage(call, f'❓ 未查询到bot数据中名为 {navid_name} 的账户，请使用 **绑定TG** 功能。',
                                         buttons=re_bindtg_ikb)
            if navid_pwd != e2.pwd2:
                success, navid_id = await navidService.authority_account(call.from_user.id, navid_name, navid_pwd)
                if not success:
                    return await editMessage(call,
                                             f'💢 安全码or密码验证错误，请检查输入\n{navid_name} {navid_pwd} 是否正确。',
                                             buttons=re_changetg_ikb)
                sql_update_navid(Navid.tg == call.from_user.id, navid_id=navid_id, name=e2.name, pwd=navid_pwd,
                                 pwd2=e2.pwd2, lv=e2.lv, cr=e2.cr, ex=e2.ex)
                sql_delete_navid2(navid_id=e2.navid_id)
                text = f'⭕ 账户 {navid_name} 的密码验证成功！\n\n' \
                       f'· 用户名称 | `{navid_name}`\n' \
                       f'· 用户密码 | `{pwd[0]}`\n' \
                       f'· 安全密码 | `{e2.pwd2}`（仅发送一次）\n' \
                       f'· 到期时间 | `{e2.ex}`\n\n' \
                       f'· 当前线路：\n{navid_line}\n\n' \
                       f'**·在【服务器】按钮 - 查看线路和密码**'
                await sendMessage(call,
                                  f'⭕#TG改绑 原navid账户 #{navid_name}\n\n'
                                  f'从navid2表绑定至 [{call.from_user.first_name}](tg://user?id={call.from_user.id}) - {call.from_user.id}',
                                  send=True)
                LOGGER.info(f'【TG改绑】 navid账户 {navid_name} 绑定至 {call.from_user.first_name}-{call.from_user.id}')
                await editMessage(call, text)

            elif navid_pwd == e2.pwd2:
                text = f'⭕ 账户 {navid_name} 的安全码验证成功！\n\n' \
                       f'· 用户名称 | `{navid_name}`\n' \
                       f'· 用户密码 | `{e2.pwd}`\n' \
                       f'· 安全密码 | `{pwd[1]}`（仅发送一次）\n' \
                       f'· 到期时间 | `{e2.ex}`\n\n' \
                       f'· 当前线路：\n{navid_line}\n\n' \
                       f'**·在【服务器】按钮 - 查看线路和密码**'
                sql_update_navid(Navid.tg == call.from_user.id, navid_id=e2.navid_id, name=e2.name, pwd=e2.pwd,
                                 pwd2=navid_pwd, lv=e2.lv, cr=e2.cr, ex=e2.ex)
                sql_delete_navid2(navid_id=e2.navid_id)
                await sendMessage(call,
                                  f'⭕#TG改绑 原navid账户 #{navid_name}\n\n'
                                  f'从navid2表绑定至 [{call.from_user.first_name}](tg://user?id={call.from_user.id}) - {call.from_user.id}',
                                  send=True)
                LOGGER.info(f'【TG改绑】 navid账户 {navid_name} 绑定至 {call.from_user.first_name}-{call.from_user.id}')
                await editMessage(call, text)

        else:
            if navid_pwd != e.pwd2:
                LOGGER.info(f'navid_pwd: {navid_pwd}, e.pwd2: {e.pwd2}')
                success, navid_id = await navidService.authority_account(call.from_user.id, navid_name, navid_pwd)
                if not success:
                    return await editMessage(call,
                                             f'💢 安全码or密码验证错误，请检查输入\n{navid_name} {navid_pwd} 是否正确。',
                                             buttons=re_changetg_ikb)
                text = f'⭕ 账户 {navid_name} 的密码验证成功！\n\n' \
                       f'· 用户名称 | `{navid_name}`\n' \
                       f'· 用户密码 | `{pwd[0]}`\n' \
                       f'· 安全密码 | `{e.pwd2}`（仅发送一次）\n' \
                       f'· 到期时间 | `{e.ex}`\n\n' \
                       f'· 当前线路：\n{navid_line}\n\n' \
                       f'**·在【服务器】按钮 - 查看线路和密码**'
            elif navid_pwd == e.pwd2:
                text = f'⭕ 账户 {navid_name} 的安全码验证成功！\n\n' \
                       f'· 用户名称 | `{navid_name}`\n' \
                       f'· 用户密码 | `{e.pwd}`\n' \
                       f'· 安全密码 | `{pwd[1]}`（仅发送一次）\n' \
                       f'· 到期时间 | `{e.ex}`\n\n' \
                       f'· 当前线路：\n{navid_line}\n\n' \
                       f'**·在【服务器】按钮 - 查看线路和密码**'
            f = None
            try:
                f = await bot.get_tele_users(user_ids=e.tg)
            except Exception as ex:
                LOGGER.error(f'【TG改绑】 navid账户{navid_name} 通过tg api获取{e.tg}用户失败，原因：{ex}')
            if f is not None and not f.is_deleted:
                await sendMessage(call,
                                  f'⭕#TG改绑 **用户 [{call.from_user.id}](tg://user?id={call.from_user.id}) '
                                  f'正在试图改绑一个状态正常的[tg用户](tg://user?id={e.tg}) - {e.name}\n\n请管理员检查。**',
                                  send=True)
                return await editMessage(call,
                                         f'⚠️ **你所要换绑的[tg](tg://user?id={e.tg}) - {e.tg}\n\n用户状态正常！无须换绑。**',
                                         buttons=back_members_ikb)
            if sql_update_navid(Navid.tg == call.from_user.id, navid_id=e.navid_id, name=e.name, pwd=e.pwd,
                                pwd2=e.pwd2, lv=e.lv, cr=e.cr, ex=e.ex, iv=e.iv):
                await sendMessage(call,
                                  f'⭕#TG改绑 原navid账户 #{navid_name} \n\n已绑定至 [{call.from_user.first_name}](tg://user?id={call.from_user.id}) - {call.from_user.id}',
                                  send=True)
                LOGGER.info(
                    f'【TG改绑】 navid账户 {navid_name} 绑定至 {call.from_user.first_name}-{call.from_user.id}')
                await editMessage(call, text)
            else:
                await editMessage(call, '🍰 **【TG改绑】数据库处理出错，请联系闺蜜（管理）！**', back_members_ikb)
                LOGGER.error(f"【TG改绑】 navid账户{navid_name} 绑定未知错误。")
            if sql_delete_navid(tg=e.tg):
                LOGGER.info(f'【TG改绑】删除原账户 id{e.tg}, Navid:{e.name} 成功...')
            else:
                await editMessage(call, "🍰 **⭕#TG改绑 原账户删除错误，请联系闺蜜（管理）！**", back_members_ikb)
                LOGGER.error(f"【TG改绑】删除原账户 id{e.tg}, Navid:{e.name} 失败...")


@bot.on_callback_query(filters.regex('bindtg') & user_in_group_on_filter)
async def bind_tg(_, call):
    d = sql_get_navid(call.from_user.id)
    if d.navid_id is not None:
        return await callAnswer(call, '⚖️ 您已经拥有账户，请不要钻空子', True)
    await callAnswer(call, '⚖️ 将账户绑定TG')
    send = await editMessage(call,
                             '🔰 **【已有navid绑定至tg】**\n'
                             '须知：\n'
                             '- **请确保您需绑定的账户不在bot中**\n'
                             '- **请确保您不是恶意绑定他人的账户**\n'
                             '- **请确保输入正确的navid用户名，密码**\n\n'
                             '您有120s回复 `[navid用户名] [密码]`\n例如 `二狗 1234` ，若密码为空则填写“None”，退出点 /cancel')
    if send is False:
        return

    m = await callListen(call, 120, buttons=back_members_ikb)
    if m is False:
        return

    elif m.text == '/cancel':
        await m.delete()
        await editMessage(call, '__您已经取消输入__ **会话已结束！**', back_members_ikb)
    else:
        try:
            await m.delete()
            navid_name, navid_pwd = m.text.split()
        except (IndexError, ValueError):
            return await editMessage(call, f'⚠️ 输入格式错误\n【`{m.text}`】\n **会话已结束！**', re_bindtg_ikb)
        await editMessage(call,
                          f'✔️ 会话结束，收到设置\n\n用户名：**{navid_name}** 正在检查密码 **{navid_pwd}**......')
        e = sql_get_navid(navid_name)
        if e is None:
            e2 = sql_get_navid2(name=navid_name)
            if e2 is None:
                success, navid_id = await navidService.authority_account(call.from_user.id, navid_name, navid_pwd)
                if not success:
                    return await editMessage(call,
                                             f'🍥 很遗憾绑定失败，您输入的账户密码不符（{navid_name} - {navid_pwd}），请仔细确认后再次尝试',
                                             buttons=re_bindtg_ikb)
                else:
                    pwd = ['空（直接回车）', 5210] if navid_pwd == 'None' else [navid_pwd, navid_pwd]
                    ex = (datetime.now() + timedelta(days=30))
                    text = f'✅ 账户 {navid_name} 成功绑定\n\n' \
                           f'· 用户名称 | `{navid_name}`\n' \
                           f'· 用户密码 | `{pwd[0]}`\n' \
                           f'· 安全密码 | `{pwd[1]}`（仅发送一次）\n' \
                           f'· 到期时间 | `{ex}`\n\n' \
                           f'· 当前线路：\n{navid_line}\n\n' \
                           f'· **在【服务器】按钮 - 查看线路和密码**'
                    sql_update_navid(Navid.tg == call.from_user.id, navid_id=navid_id, name=navid_name, pwd=navid_pwd,
                                     pwd2=navid_pwd, lv='b', cr=datetime.now(), ex=ex)
                    await editMessage(call, text)
                    await sendMessage(call,
                                      f'⭕#新TG绑定 原navid账户 #{navid_name} \n\n已绑定至 [{call.from_user.first_name}]'
                                      f'(tg://user?id={call.from_user.id}) - {call.from_user.id}',
                                      send=True)
                    LOGGER.info(
                        f'【新TG绑定】 navid账户 {navid_name} 绑定至 {call.from_user.first_name}-{call.from_user.id}')
            else:
                await editMessage(call, '🔍 数据库已有此账户，不可绑定，请使用 **换绑TG**', buttons=re_changetg_ikb)
        else:
            await editMessage(call, '🔍 数据库已有此账户，不可绑定，请使用 **换绑TG**', buttons=re_changetg_ikb)


# kill yourself
@bot.on_callback_query(filters.regex('delme') & user_in_group_on_filter)
async def del_me(_, call):
    e = sql_get_navid(call.from_user.id)
    if e is None:
        return await callAnswer(call, '⚠️ 数据库没有你，请重新 /start录入', True)
    else:
        if e.navid_id is None:
            return await callAnswer(call, '未查询到账户，不许乱点！💢', True)
        await callAnswer(call, "🔴 请先进行 安全码 验证")
        edt = await editMessage(call, '**🔰账户安全验证**：\n\n👮🏻验证是否本人进行敏感操作，请对我发送您设置的安全码。倒计时 120s\n'
                                      '🛑 **停止请点 /cancel**')
        if edt is False:
            return

        m = await callListen(call, 120)
        if m is False:
            return

        elif m.text == '/cancel':
            await m.delete()
            await editMessage(call, '__您已经取消输入__ **会话已结束！**', buttons=back_members_ikb)
        else:
            if m.text == e.pwd2:
                await m.delete()
                await editMessage(call, '**⚠️ 如果您的账户到期，我们将封存您的账户，但仍保留数据'
                                        '而如果您选择删除，这意味着服务器会将您此前的活动数据全部删除。\n**',
                                  buttons=del_me_ikb(e.tg, e.navid_id))
            else:
                await m.delete()
                await editMessage(call, '**💢 验证不通过，安全码错误。**', re_delme_ikb)


@bot.on_callback_query(filters.regex('delete_navid') & user_in_group_on_filter)
async def del_navid(_, call):
    send = await callAnswer(call, "🎯 get，正在删除ing。。。")
    if send is False:
        return

    tg = call.data.split('/')[1]
    navid_id = call.data.split('/')[2]
    if await navidService.navid_del(tg=tg, navid_id=navid_id):
        send1 = await editMessage(call, '🗑️ 好了，已经为您删除...\n愿来日各自安好，山高水长，我们有缘再见！',
                                  buttons=back_members_ikb)
        if send1 is False:
            return

        LOGGER.info(f"【删除账号】：{call.from_user.id} 已删除！")
    else:
        await editMessage(call, '🥧 蛋糕辣~ 好像哪里出问题了，请向管理反应', buttons=back_members_ikb)
        LOGGER.error(f"【删除账号】：{call.from_user.id} 失败！")


# 重置密码为空密码
@bot.on_callback_query(filters.regex('reset') & user_in_group_on_filter)
async def reset(_, call):
    e = sql_get_navid(call.from_user.id)
    if e is None:
        return await callAnswer(call, '⚠️ 数据库没有你，请重新 /start录入', True)
    if e.navid_id is None:
        return await bot.answer_callback_query(call.id, '未查询到账户，不许乱点！💢', show_alert=True)
    else:
        await callAnswer(call, "🔴 请先进行 安全码 验证")
        send = await editMessage(call, '**🔰账户安全验证**：\n\n 👮🏻验证是否本人进行敏感操作，请对我发送您设置的安全码。倒计时 120 s\n'
                                       '🛑 **停止请点 /cancel**')
        if send is False:
            return

        m = await callListen(call, 120, buttons=back_members_ikb)
        if m is False:
            return

        elif m.text == '/cancel':
            await m.delete()
            await editMessage(call, '__您已经取消输入__ **会话已结束！**', buttons=back_members_ikb)
        else:
            if m.text != e.pwd2:
                await m.delete()
                await editMessage(call, f'**💢 验证不通过，{m.text} 安全码错误。**', buttons=re_reset_ikb)
            else:
                await m.delete()
                await editMessage(call, '🎯 请在 120s内 输入你要更新的密码,不限制中英文，emoji。特殊字符部分支持，其他概不负责。\n\n'
                                        '点击 /cancel 将重置为空密码并退出。 无更改退出状态请等待120s')
                mima = await callListen(call, 120, buttons=back_members_ikb)
                if mima is False:
                    return

                elif mima.text == '/cancel':
                    await mima.delete()
                    await editMessage(call, '**🎯 收到，正在重置ing。。。**')
                    if await navidService.navid_reset(id=e.navid_id) is True:
                        await editMessage(call, '🕶️ 操作完成！已为您重置密码为 空。', buttons=back_members_ikb)
                        LOGGER.info(f"【重置密码】：{call.from_user.id} 成功重置了空密码！")
                    else:
                        await editMessage(call, '🫥 重置密码操作失败！请联系管理员。')
                        LOGGER.error(f"【重置密码】：{call.from_user.id} 重置密码失败 ！")

                else:
                    await mima.delete()
                    await editMessage(call, '**🎯 收到，正在重置ing。。。**')
                    if await navidService.navid_reset(id=e.navid_id, new=mima.text) is True:
                        await editMessage(call, f'🕶️ 操作完成！已为您重置密码为 `{mima.text}`。',
                                          buttons=back_members_ikb)
                        LOGGER.info(f"【重置密码】：{call.from_user.id} 成功重置了密码为 {mima.text} ！")
                    else:
                        await editMessage(call, '🫥 操作失败！请联系管理员。', buttons=back_members_ikb)
                        LOGGER.error(f"【重置密码】：{call.from_user.id} 重置密码失败 ！")


@bot.on_callback_query(filters.regex('exchange') & user_in_group_on_filter)
async def call_exchange(_, call):
    await asyncio.gather(callAnswer(call, '🔋 使用注册码'), deleteMessage(call))
    msg = await ask_return(call, text='🔋 **【使用注册码】**：\n\n'
                                      f'- 请在120s内对我发送你的注册码，形如\n Navid-xx-xxxx\n退出点 /cancel',
                           button=re_exchange_b_ikb)
    if msg is False:
        return
    elif msg.text == '/cancel':
        await asyncio.gather(msg.delete(), p_start(_, msg))
    else:
        await rgs_code(_, msg, register_code=msg.text)


@bot.on_callback_query(filters.regex('storeall') & user_in_group_on_filter)
async def do_store(_, call):
    if user_buy.stat:
        # return await callAnswer(call, '🌏 Sorry，此功能仅服务于公益服，其他请点击 【使用注册码】 续期', True) # 公费直接转兑换码
        return await call_exchange(_, call)
    await asyncio.gather(callAnswer(call, '✔️ 欢迎进入兑换商店'),
                         editMessage(call,
                                     f'**🏪 请选择想要使用的服务：**\n\n🤖 自动{sakura_b}续期：{_open.exchange} {_open.exchange_cost * 30}/月',
                                     buttons=store_ikb()))


@bot.on_callback_query(filters.regex('store-whitelist') & user_in_group_on_filter)
async def do_store_whitelist(_, call):
    if _open.whitelist:
        e = sql_get_navid(call.from_user.id)
        if e is None:
            return
        if e.iv < _open.whitelist_cost or e.lv == 'a':
            return await callAnswer(call,
                                    f'🏪 兑换规则：\n当前兑换白名单需要 {_open.whitelist_cost} {sakura_b}，已有白名单无法再次消费。勉励',
                                    True)
        await callAnswer(call, f'🏪 您已满足 {_open.whitelist_cost} {sakura_b}要求', True)
        sql_update_navid(Navid.tg == call.from_user.id, lv='a', iv=e.iv - _open.whitelist_cost)
        send = await call.message.edit(f'**{random.choice(Yulv.load_yulv().wh_msg)}**\n\n'
                                       f'🎉 恭喜[{call.from_user.first_name}](tg://user?id={call.from_user.id}) '
                                       f'今日晋升，Navid白名单')
        await send.forward(group[0])
        LOGGER.info(f'【兑换白名单】- {call.from_user.id} 已花费 9999{sakura_b}，晋升白名单')
    else:
        await callAnswer(call, '❌ 管理员未开启此兑换', True)


@bot.on_callback_query(filters.regex('store-invite') & user_in_group_on_filter)
async def do_store_invite(_, call):
    if _open.invite:
        e = sql_get_navid(call.from_user.id)
        if not e or not e.navid_id:
            return callAnswer(call, '❌ 仅持有账户可兑换此选项', True)
        if e.iv < _open.invite_cost:
            return await callAnswer(call,
                                    f'🏪 兑换规则：\n当前兑换邀请码至少需要 {_open.invite_cost} {sakura_b}。勉励',
                                    True)
        await editMessage(call,
                          f'🎟️ 请回复创建 [类型] [数量] [模式]\n\n'
                          f'**类型**：月mon，季sea，半年half，年year\n'
                          f'**模式**： link -深链接 | code -码\n'
                          f'**示例**：`sea 1 link` 记作 1条 季度注册码链接\n'
                          f'**注意**：兑率 30天 = {_open.invite_cost}{sakura_b}\n'
                          f'__取消本次操作，请 /cancel__')
        content = await callListen(call, 120)
        if content is False:
            return await do_store(_, call)

        elif content.text == '/cancel':
            return await asyncio.gather(content.delete(), do_store(_, call))
        try:
            times, count, method = content.text.split()
            days = getattr(ExDate(), times)
            count = int(count)
            cost = math.floor((days * count / 30) * _open.invite_cost)
            if e.iv < cost:
                return await asyncio.gather(content.delete(),
                                            sendMessage(call,
                                                        f'您只有 {e.iv}{sakura_b}，而您需要花费 {cost}，超前消费是不可取的哦！？',
                                                        timer=10),
                                            do_store(_, call))
            method = getattr(ExDate(), method)
        except (AttributeError, ValueError, IndexError):
            return await asyncio.gather(sendMessage(call, f'⚠️ 检查输入，格式似乎有误\n{content.text}', timer=10),
                                        do_store(_, call),
                                        content.delete())
        else:
            sql_update_navid(Navid.tg == call.from_user.id, iv=e.iv - cost)
            links = await cr_link_one(call.from_user.id, days, count, days, method)
            if links is None:
                return await editMessage(call, '⚠️ 数据库插入失败，请检查数据库')
            links = f"🎯 {bot_name}已为您生成了 **{days}天** 邀请码 {count} 个\n\n" + links
            chunks = [links[i:i + 4096] for i in range(0, len(links), 4096)]
            for chunk in chunks:
                await sendMessage(content, chunk)
            LOGGER.info(f"【注册码兑换】：{bot_name}已为 {content.from_user.id} 生成了 {count} 个 {days} 天邀请码")

    else:
        await callAnswer(call, '❌ 管理员未开启此兑换', True)


@bot.on_callback_query(filters.regex('store-query') & user_in_group_on_filter)
async def do_store_query(_, call):
    a, b = sql_count_c_code(tg_id=call.from_user.id)
    if not a:
        return await callAnswer(call, '❌ 空', True)
    try:
        number = int(call.data.split(':')[1])
    except (IndexError, KeyError, ValueError):
        number = 1
    await callAnswer(call, '📜 正在翻页')
    await editMessage(call, text=a[number - 1], buttons=await user_query_page(b, number))
