"""
 admin 面板
 功能暂定 开关注册，生成注册码，查看注册码情况，邀请注册排名情况
"""
import asyncio

from pyrogram import filters
from pyrogram.errors import BadRequest

from bot import bot, _open, save_config, bot_photo, LOGGER, bot_name, admins, owner
from bot.func_helper.filters import admins_on_filter
from bot.schemas import ExDate
from bot.sql_helper.sql_code import sql_count_code, sql_count_p_code
from bot.sql_helper.sql_navid import sql_count_navid
from bot.func_helper.fix_bottons import gm_ikb_content, open_menu_ikb, gog_rester_ikb, back_open_menu_ikb, \
    back_free_ikb, \
    re_cr_link_ikb, close_it_ikb, ch_link_ikb, date_ikb, cr_paginate, cr_renew_ikb
from bot.func_helper.msg_utils import callAnswer, editMessage, sendPhoto, callListen, deleteMessage, sendMessage
from bot.func_helper.utils import open_check, cr_link_one


@bot.on_callback_query(filters.regex('manage') & admins_on_filter)
async def gm_ikb(_, call):
    await callAnswer(call, '✔️ manage面板')
    stat, all_user, tem, timing, allow_code = await open_check()
    stat = "True" if stat else "False"
    allow_code = 'True' if allow_code else 'False'
    timing = 'Turn off' if timing == 0 else str(timing) + ' min'
    tg, navid_count, white = sql_count_navid()
    gm_text = f'⚙️ 欢迎您，亲爱的管理员 {call.from_user.first_name}\n\n· ®️ 注册状态 | **{stat}**\n· ⏳ 定时注册 | **{timing}**\n' \
              f'· 🔖 注册码续期 | **{allow_code}**\n' \
              f'· 🎫 总注册限制 | **{all_user}**\n· 🎟️ 已注册人数 | **{navid_count}** • WL **{white}**\n· 🤖 bot使用人数 | {tg}'

    await editMessage(call, gm_text, buttons=gm_ikb_content)


# 开关注册
@bot.on_callback_query(filters.regex('open-menu') & admins_on_filter)
async def open_menu(_, call):
    await callAnswer(call, '®️ register面板')
    # [开关，注册总数，定时注册] 此间只对navid表中tg用户进行统计
    stat, all_user, tem, timing, allow_code = await open_check()
    tg, navid_count, white = sql_count_navid()
    openstats = '✅' if stat else '❎'  # 三元运算
    timingstats = '❎' if timing == 0 else '✅'
    text = f'⚙ **注册状态设置**：\n\n- 自由注册即定量方式，定时注册既定时又定量，将自动转发消息至群组，再次点击按钮可提前结束并报告。\n' \
           f'- **注册总人数限制 {all_user}**'
    await editMessage(call, text, buttons=open_menu_ikb(openstats, timingstats))
    if tem != navid_count:
        _open.tem = navid_count
        save_config()


@bot.on_callback_query(filters.regex('open_stat') & admins_on_filter)
async def open_stats(_, call):
    stat, all_user, tem, timing, allow_code = await open_check()
    if timing != 0:
        return await callAnswer(call, "🔴 目前正在运行定时注册。\n无法调用，请再次点击，【定时注册】关闭状态", True)

    tg, navid_count, white = sql_count_navid()
    if stat:
        _open.stat = False
        save_config()
        await callAnswer(call, "🟢【自由注册】\n\n已结束", True)
        sur = all_user - tem
        text = f'🫧 管理员 {call.from_user.first_name} 已关闭 **自由注册**\n\n' \
               f'🎫 总注册限制 | {all_user}\n🎟️ 已注册人数 | {tem}\n' \
               f'🎭 剩余可注册 | **{sur}**\n🤖 bot使用人数 | {tg}'
        await asyncio.gather(sendPhoto(call, photo=bot_photo, caption=text, send=True),
                             editMessage(call, text, buttons=back_free_ikb))
        # await open_menu(_, call)
        LOGGER.info(f"【admin】：管理员 {call.from_user.first_name} 关闭了自由注册")
    elif not stat:
        _open.stat = True
        save_config()
        await callAnswer(call, "🟡【自由注册】\n\n已开启", True)
        sur = all_user - tem  # for i in group可以多个群组用，但是现在不做
        text = f'🫧 管理员 {call.from_user.first_name} 已开启 **自由注册**\n\n' \
               f'🎫 总注册限制 | {all_user}\n🎟️ 已注册人数 | {tem}\n' \
               f'🎭 剩余可注册 | **{sur}**\n🤖 bot使用人数 | {tg}'
        await asyncio.gather(sendPhoto(call, photo=bot_photo, caption=text, buttons=gog_rester_ikb(), send=True),
                             editMessage(call, text=text, buttons=back_free_ikb))
        # await open_menu(_, call)
        LOGGER.info(f"【admin】：管理员 {call.from_user.first_name} 开启了自由注册，总人数限制 {all_user}")


change_for_timing_task = None


@bot.on_callback_query(filters.regex('open_timing') & admins_on_filter)
async def open_timing(_, call):
    global change_for_timing_task
    if _open.timing == 0:
        await callAnswer(call, '⭕ 定时设置')
        await editMessage(call,
                          "🦄【定时注册】 \n\n- 请在 120s 内发送 [定时时长] [总人数]\n"
                          "- 形如：`30 50` 即30min，总人数限制50\n"
                          "- 如需要关闭定时注册，再次点击【定时注册】\n"
                          "- 设置好之后将发送置顶消息注意权限\n- 退出 /cancel")

        txt = await callListen(call, 120, buttons=back_open_menu_ikb)
        if txt is False:
            return

        await txt.delete()
        if txt.text == '/cancel':
            return await open_menu(_, call)

        try:
            new_timing, new_all_user = txt.text.split()
            _open.timing = int(new_timing)
            _open.all_user = int(new_all_user)
            _open.stat = True
            save_config()
        except ValueError:
            await editMessage(call, "🚫 请检查数字填写是否正确。\n`[时长min] [总人数]`", buttons=back_open_menu_ikb)
        else:
            tg, navid_count, white = sql_count_navid()
            sur = _open.all_user - navid_count
            await asyncio.gather(sendPhoto(call, photo=bot_photo,
                                           caption=f'🫧 管理员 {call.from_user.first_name} 已开启 **定时注册**\n\n'
                                                   f'⏳ 可持续时间 | **{_open.timing}** min\n'
                                                   f'🎫 总注册限制 | {_open.all_user}\n🎟️ 已注册人数 | {navid_count}\n'
                                                   f'🎭 剩余可注册 | **{sur}**\n🤖 bot使用人数 | {tg}',
                                           buttons=gog_rester_ikb(), send=True),
                                 editMessage(call,
                                             f"®️ 好，已设置**定时注册 {_open.timing} min 总限额 {_open.all_user}**",
                                             buttons=back_free_ikb))
            LOGGER.info(
                f"【admin】-定时注册：管理员 {call.from_user.first_name} 开启了定时注册 {_open.timing} min，人数限制 {sur}")
            # 创建一个异步任务并保存为变量，并给它一个名字
            change_for_timing_task = asyncio.create_task(
                change_for_timing(_open.timing, call.from_user.id, call), name='change_for_timing')

    else:
        try:
            # 遍历所有的异步任务，找到'change_for_timing'，取消
            for task in asyncio.all_tasks():
                if task.get_name() == 'change_for_timing':
                    change_for_timing_task = task
                    break
            change_for_timing_task.cancel()
        except AttributeError:
            pass
        else:
            await callAnswer(call, "Ⓜ️【定时任务运行终止】\n\n**已为您停止**", True)
            await open_menu(_, call)


async def change_for_timing(timing, tgid, call):
    a = _open.tem
    timing = timing * 60
    try:
        await asyncio.sleep(timing)
    except asyncio.CancelledError:
        pass
    finally:
        _open.timing = 0
        _open.stat = False
        save_config()
        b = _open.tem - a
        s = _open.all_user - _open.tem
        text = f'⏳** 注册结束**：\n\n🍉 目前席位：{_open.tem}\n🥝 新增席位：{b}\n🍋 剩余席位：{s}'
        send = await sendPhoto(call, photo=bot_photo, caption=text, timer=300, send=True)
        send1 = await send.forward(tgid)
        LOGGER.info(f'【admin】-定时注册：运行结束，本次注册 目前席位：{_open.tem}  新增席位:{b}  剩余席位：{s}')
        await deleteMessage(send1, 30)


@bot.on_callback_query(filters.regex('all_user_limit') & admins_on_filter)
async def open_all_user_l(_, call):
    await callAnswer(call, '⭕ 限制人数')
    send = await call.message.edit(
        "🦄 请在 120s 内发送开注总人数，本次修改不会对注册状态改动，如需要开注册请点击打开自由注册\n**注**：总人数满自动关闭注册 取消 /cancel")
    if send is False:
        return

    txt = await callListen(call, 120, buttons=back_free_ikb)
    if txt is False:
        return
    elif txt.text == "/cancel":
        await txt.delete()
        return await open_menu(_, call)

    try:
        await txt.delete()
        a = int(txt.text)
    except ValueError:
        await editMessage(call, f"❌ 八嘎，请输入一个数字给我。", buttons=back_free_ikb)
    else:
        _open.all_user = a
        save_config()
        await editMessage(call, f"✔️ 成功，您已设置 **注册总人数 {a}**", buttons=back_free_ikb)
        LOGGER.info(f"【admin】：管理员 {call.from_user.first_name} 调整了总人数限制：{a}")


# 生成注册链接
@bot.on_callback_query(filters.regex('cr_link') & admins_on_filter)
async def cr_link(_, call):
    await callAnswer(call, '✔️ 创建注册码')
    send = await editMessage(call,
                             f'🎟️ 请回复创建 [类行] [数量] [模式]\n\n'
                             f'**类型**：1-天数，月-30，季-90，半年-180，年-365\n'
                             f'**模式**： link -深链接 | code -码\n'
                             f'**示例**：`3 20 code` 记作 20条3天卡注册码\n'
                             f'         `月 20 link` 记作 20条月卡注册链接\n'
                             f'__取消本次操作，请 /cancel__')
    if send is False:
        return

    content = await callListen(call, 120, buttons=re_cr_link_ikb)
    if content is False:
        return
    elif content.text == '/cancel':
        await content.delete()
        return await editMessage(call, '⭕ 您已经取消操作了。', buttons=re_cr_link_ikb)
    try:
        await content.delete()
        duration, count, method = content.text.split()

        try:
            duration_ = int(duration)
            duration = '天'
        except:
            if duration != '天' and duration != '月' and duration != '季' and duration != '半年' and duration != '年':
                return await editMessage(call, '⭕ 输入的[类型]参数有误', buttons=re_cr_link_ikb)
            if duration == '月':
                duration_ = 30
            elif duration == '季':
                duration_ = 90
            elif duration == '半年':
                duration_ = 180
            else:
                duration_ = 365
        try:
            count = int(count)
        except:
            return await editMessage(call, '⭕ 输入的[数量]参数有误', buttons=re_cr_link_ikb)

        if method != 'code' and method != 'link':
            return await editMessage(call, '⭕ 输入的[模式]参数有误', buttons=re_cr_link_ikb)
    except (ValueError, IndexError):
        return await editMessage(call, '⚠️ 检查输入，有误。', buttons=re_cr_link_ikb)
    else:
        links = await cr_link_one(call.from_user.id, duration_, count, method=method)
        if links is None:
            return await editMessage(call, '⚠️ 数据库插入失败，请检查数据库。', buttons=re_cr_link_ikb)
        links = f"🎯 {bot_name}已为您生成了 **{duration_}天 {duration}卡** 邀请连接 {count} 个\n\n" + links
        chunks = [links[i:i + 4096] for i in range(0, len(links), 4096)]
        for chunk in chunks:
            await sendMessage(content, chunk, buttons=close_it_ikb)
        await editMessage(call, f'📂 {bot_name}已为 您 生成了 {count} 个 {duration_}天 {duration}卡邀请码', buttons=re_cr_link_ikb)
        LOGGER.info(f"【admin】：{bot_name}已为 {content.from_user.id} 生成了 {count} 个 {duration_}天 {duration}卡邀请码")


# 检索
@bot.on_callback_query(filters.regex('ch_link') & admins_on_filter)
async def ch_link(_, call):
    await callAnswer(call, '🔍 查看管理们注册码...时长会久一点', True)
    a, b, c, d, f = sql_count_code()
    text = f'**🎫 常用code数据：\n• 已使用 - {a}\n• 月码 - {b}   | • 季码 - {c} \n• 半年码 - {d}  | • 年码 - {f}**'
    ls = []
    admins.append(owner)
    for i in admins:
        name = await bot.get_chat(i)
        a, b, c, d, f = sql_count_code(i)
        text += f'\n👮🏻`{name.first_name}`: 月/{b}，季/{c}，半年/{d}，年/{f}，已用/{a}'
        f = [f"🔎 {name.first_name}", f"ch_admin_link-{i}"]
        ls.append(f)
    admins.remove(owner)
    keyboard = ch_link_ikb(ls)
    text += '\n详情查询 👇'

    await editMessage(call, text, buttons=keyboard)


@bot.on_callback_query(filters.regex('ch_admin_link'))
async def ch_admin_link(client, call):
    i = int(call.data.split('-')[1])
    if call.from_user.id != owner and call.from_user.id != i:
        return await callAnswer(call, '🚫 你怎么偷窥别人呀! 你又不是owner', True)
    await callAnswer(call, f'💫 管理员 {i} 的注册码')
    a, b, c, d, f = sql_count_code(i)
    name = await client.get_chat(i)
    text = f'**🎫 [{name.first_name}-{i}](tg://user?id={i})：\n• 已使用 - {a}\n• 月码 - {b}   | • 季码 - {c} \n• 半年码 - {d}  | • 年码 - {f}**'
    await editMessage(call, text, date_ikb(i))


@bot.on_callback_query(
    filters.regex('register_mon') | filters.regex('register_sea')
    | filters.regex('register_half') | filters.regex('register_year') | filters.regex('register_used'))
async def buy_mon(_, call):
    await call.answer('✅ 显示注册码')
    cd, times, u = call.data.split('_')
    n = getattr(ExDate(), times)
    a, i = sql_count_p_code(u, n)
    if a is None:
        x = '**空**'
    else:
        x = a[0]
    first = await bot.get_chat(u)
    keyboard = await cr_paginate(i, 1, n)
    await sendMessage(call, f'🔎当前 {first.first_name} - **{n}**天，检索出以下 **{i}**页：\n\n{x}', keyboard)


# 检索翻页
@bot.on_callback_query(filters.regex('pagination_keyboard'))
async def paginate_keyboard(_, call):
    j, mode = map(int, call.data.split(":")[1].split('-'))
    await callAnswer(call, f'好的，将为您翻到第 {j} 页')
    a, b = sql_count_p_code(call.from_user.id, mode)
    keyboard = await cr_paginate(b, j, mode)
    text = a[j - 1]
    await editMessage(call, f'🔎当前模式- **{mode}**天，检索出以下 **{b}**页链接：\n\n{text}', keyboard)


@bot.on_callback_query(filters.regex('set_renew'))
async def set_renew(_, call):
    await callAnswer(call, '🚀 进入续期设置')
    try:
        method = call.data.split('-')[1]
        setattr(_open, method, not getattr(_open, method))
        save_config()
    except IndexError:
        pass
    finally:
        await editMessage(call, text='⭕ **关于用户组的续期功能**\n\n选择点击下方按钮开关任意兑换功能',
                          buttons=cr_renew_ikb())
