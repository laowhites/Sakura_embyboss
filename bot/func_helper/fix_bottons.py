from cacheout import Cache
from pykeyboard import InlineKeyboard, InlineButton
from pyrogram.types import InlineKeyboardMarkup
from pyromod.helpers import ikb, array_chunk
from bot import chanel, main_group, bot_name, tz_id, tz_ad, tz_api, _open, user_buy, sakura_b, \
    schedule, config
from bot.func_helper import nezha_res
from bot.func_helper.navid import navidService
from bot.func_helper.utils import judge_admins, members_info

cache = Cache()

"""start面板 ↓"""


def judge_start_ikb(uid: int) -> InlineKeyboardMarkup:
    """
    start面板按钮
    :param uid:
    :return:
    """
    d = [['️👥 用户功能', 'members'], ['🌐 服务器', 'server'], ['🎟️ 使用注册码', 'exchange']]
    if _open.checkin:
        d.append([f'🎯 签到', 'checkin'])
    # 暂不开放购买
    # if user_buy.stat:
    #     d.append(user_buy.button)
    lines = array_chunk(d, 2)
    if judge_admins(uid):
        lines.append([['👮🏻‍♂️ admin', 'manage']])
    keyword = ikb(lines)
    return keyword


# un_group_answer
group_f = ikb([[('点击我(●ˇ∀ˇ●)', f't.me/{bot_name}', 'url')]])
# un in group
judge_group_ikb = ikb([[('🌟 频道入口 ', f't.me/{chanel}', 'url'),
                        ('💫 群组入口', f't.me/{main_group}', 'url')],
                       [('❌ 关闭消息', 'close_it')]])

"""members ↓"""


def members_ikb(emby=False) -> InlineKeyboardMarkup:
    """
    判断用户面板
    :param emby:
    :return:
    """
    if emby:
        method = 'storeall' if not user_buy.stat else 'exchange'
        return ikb([[('🏪 兑换商店', method), ('🗑️ 删除账号', 'delme')],
                    [('⭕ 重置密码', 'reset')],
                    [('♻️ 主界面', 'back_start')]])
    else:
        return ikb(
            [[('👑 创建账户', 'create')], [('⭕ 换绑TG', 'changetg'), ('🔍 绑定TG', 'bindtg')],
             [('♻️ 主界面', 'back_start')]])


back_start_ikb = ikb([[('💫 回到首页', 'back_start')]])
back_members_ikb = ikb([[('💨 返回', 'members')]])
re_create_ikb = ikb([[('🍥 重新输入', 'create'), ('💫 用户主页', 'members')]])
re_changetg_ikb = ikb([[('✨ 换绑TG', 'changetg'), ('💫 用户主页', 'members')]])
re_bindtg_ikb = ikb([[('✨ 绑定TG', 'bindtg'), ('💫 用户主页', 'members')]])
re_delme_ikb = ikb([[('♻️ 重试', 'delme')], [('🔙 返回', 'members')]])
re_reset_ikb = ikb([[('♻️ 重试', 'reset')], [('🔙 返回', 'members')]])
re_exchange_b_ikb = ikb([[('♻️ 重试', 'exchange'), ('❌ 关闭', 'close_it')]])


def store_ikb():
    return ikb([[(f'♾️ 兑换白名单', 'store-whitelist')],
                [(f'🎟️ 兑换注册码', 'store-invite'), (f'🔍 查询注册码', 'store-query')], [(f'❌ 取消', 'members')]])


re_store_renew = ikb([[('✨ 重新输入', 'changetg'), ('💫 取消输入', 'storeall')]])


def del_me_ikb(tg, navid_id) -> InlineKeyboardMarkup:
    return ikb([[('🎯 确定', f'delete_navid/{tg}/{navid_id}')], [('🔙 取消', 'members')]])


"""server ↓"""


@cache.memoize(ttl=120)
async def cr_page_server():
    """
    翻页服务器面板
    :return:
    """
    sever = nezha_res.sever_info(tz_ad, tz_api, tz_id)
    if not sever:
        return ikb([[('🔙 - 用户', 'members'), ('❌ - 上一级', 'back_start')]]), None
    d = []
    for i in sever:
        d.append([i['name'], f'server:{i["id"]}'])
    lines = array_chunk(d, 3)
    lines.append([['🔙 - 用户', 'members'], ['❌ - 上一级', 'back_start']])
    # keyboard是键盘，a是sever
    return ikb(lines), sever


"""admins ↓"""

gm_ikb_content = ikb([[('⭕ 注册状态', 'open-menu'), ('🎟️ 生成注册', 'cr_link')],
                      [('💊 查询注册', 'ch_link'), ('🏬 兑换设置', 'set_renew')],
                      [('🌏 定时', 'schedule'), ('🕹️ 主界面', 'back_start'), ('其他 🪟', 'back_config')]])


def open_menu_ikb(openstats, timingstats) -> InlineKeyboardMarkup:
    return ikb([[(f'{openstats} 自由注册', 'open_stat'), (f'{timingstats} 定时注册', 'open_timing')],
                [('⭕ 注册限制', 'all_user_limit')], [('🌟 返回上一级', 'manage')]])


back_free_ikb = ikb([[('🔙 返回上一级', 'open-menu')]])
back_open_menu_ikb = ikb([[('🪪 重新定时', 'open_timing'), ('🔙 注册状态', 'open-menu')]])
re_cr_link_ikb = ikb([[('♻️ 继续创建', 'cr_link'), ('🎗️ 返回主页', 'manage')]])
close_it_ikb = ikb([[('❌ - Close', 'close_it')]])


def ch_link_ikb(ls: list) -> InlineKeyboardMarkup:
    lines = array_chunk(ls, 2)
    lines.append([["💫 回到首页", "manage"]])
    return ikb(lines)


def date_ikb(i) -> InlineKeyboardMarkup:
    return ikb([[('🌘 - 月', f'register_mon_{i}'), ('🌗 - 季', f'register_sea_{i}'),
                 ('🌖 - 半年', f'register_half_{i}')],
                [('🌕 - 年', f'register_year_{i}'), ('🎟️ - 已用', f'register_used_{i}')], [('🔙 - 返回', 'ch_link')]])


# 翻页按钮
async def cr_paginate(i, j, n) -> InlineKeyboardMarkup:
    """
    :param i: 总数
    :param j: 目前
    :param n: mode 可变项
    :return:
    """
    keyboard = InlineKeyboard()
    keyboard.paginate(i, j, 'pagination_keyboard:{number}' + f'-{n}')
    keyboard.row(
        InlineButton('❌ - Close', 'close_it')
    )
    return keyboard


async def users_iv_button(i, j, tg) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboard()
    keyboard.paginate(i, j, 'users_iv:{number}' + f'_{tg}')
    keyboard.row(
        InlineButton('❌ - Close', f'closeit_{tg}')
    )
    return keyboard


async def plays_list_button(i, j, days) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboard()
    keyboard.paginate(i, j, 'uranks:{number}' + f'_{days}')
    keyboard.row(
        InlineButton('❌ - Close', f'close_it')
    )
    return keyboard


async def user_query_page(i, j) -> InlineKeyboardMarkup:
    """
    member的注册码查询分页
    :param i: 总
    :param j: 当前
    :param tg: tg
    :return:
    """
    keyboard = InlineKeyboard()
    keyboard.paginate(i, j, 'store-query:{number}')
    keyboard.row(
        InlineButton('❌ Close', f'close_it'), InlineButton('🔙 Back', 'storeall')
    )
    return keyboard


def cr_renew_ikb():
    checkin = '✔' if _open.checkin else '❌'
    exchange = '✔️' if _open.exchange else '❌'
    whitelist = '✔️' if _open.whitelist else '❌'
    invite = '✔️' if _open.invite else '❌'
    keyboard = InlineKeyboard(row_width=2)
    keyboard.add(InlineButton(f'{checkin} 每日签到', f'set_renew-checkin'),
                 InlineButton(f'{exchange} 自动{sakura_b}续期', f'set_renew-exchange'),
                 InlineButton(f'{whitelist} 兑换白名单', f'set_renew-whitelist'),
                 InlineButton(f'{invite} 兑换邀请码', f'set_renew-invite'))
    keyboard.row(InlineButton(f'◀ 返回', 'manage'))
    return keyboard


""" config_panel ↓"""


def config_preparation() -> InlineKeyboardMarkup:
    code = '✅' if _open.allow_code else '❎'
    buy_stat = '✅' if user_buy.stat else '❎'
    leave_ban = '✅' if _open.leave_ban else '❎'
    uplays = '✅' if _open.uplays else '❎'
    fuxx_pitao = '✅' if config.fuxx_pitao else '❎'
    keyboard = ikb(
        [[('📄 导出日志', 'log_out'), ('📌 设置探针', 'set_tz')],
         [('💠 Navid线路', 'set_line'), ('🎬 显/隐指定库', 'set_block')],
         [(f'{code} 注册码续期', 'open_allow_code'), (f'{buy_stat} 开关购买', 'set_buy')],
         [(f'{leave_ban} 退群删号', 'leave_ban'), (f'{uplays} 自动看片结算', 'set_uplays')],
         [(f'设置赠送资格天数({config.kk_gift_days}天)', 'set_kk_gift_days'),
          (f'{fuxx_pitao} 皮套人过滤功能', 'set_fuxx_pitao')],
         [('🔙 返回', 'manage')]])
    return keyboard


back_config_p_ikb = ikb([[("🎮  ️返回主控", "back_config")]])


def back_set_ikb(method) -> InlineKeyboardMarkup:
    return ikb([[("♻️ 重新设置", f"{method}"), ("🔙 返回主页", "back_config")]])


def try_set_buy(ls: list) -> InlineKeyboardMarkup:
    d = [[ls], [["✅ 体验结束返回", "back_config"]]]
    return ikb(d)


""" other """
register_code_ikb = ikb([[('🎟️ 注册', 'create'), ('⭕ 取消', 'close_it')]])
dp_g_ikb = ikb([[("🈺 ╰(￣ω￣ｏ)", "t.me/Aaaaa_su", "url")]])


async def cr_kk_ikb(uid, first):
    text = ''
    text1 = ''
    keyboard = []
    data = await members_info(uid)
    if data is None:
        text += f'**· 🆔 TG** ：[{first}](tg://user?id={uid}) [`{uid}`]\n数据库中没有此ID。ta 还没有私聊过我'
    else:
        name, lv, ex, us, navid_id, pwd2 = data
        if name != '无账户信息':
            ban = "🌟 解除禁用" if lv == "**已禁用**" else '💢 禁用账户'
            keyboard = [['⚠️ 删除账户', f'close_navid/{uid}']]
            try:
                res = await navidService.query_user(navid_id=navid_id)
                text1 = f"**· 🔋 上次活动** | f'{res.json()['lastLoginAt']}'\n"
            except (TypeError, IndexError, ValueError):
                text1 = f"**· 📅 过去30天未有记录**"
        else:
            keyboard.append(['✨ 赠送资格', f'gift/{uid}'])
        text += f"**· 🍉 TG&名称** | [{first}](tg://user?id={uid})\n" \
                f"**· 🍒 识别のID** | `{uid}`\n" \
                f"**· 🍓 当前状态** | {lv}\n" \
                f"**· 🍥 积分{sakura_b}** | {us[0]} · {us[1]}\n" \
                f"**· 💠 账号名称** | {name}\n" \
                f"**· 🚨 到期时间** | **{ex}**\n"
        text += text1
        keyboard.extend([['🚫 踢出并删除', f'fuck_off/{uid}'], ['❌ 删除消息', f'close_it']])
        lines = array_chunk(keyboard, 2)
        keyboard = ikb(lines)
    return text, keyboard


def cv_user_ip(user_id):
    return ikb([[('❌ 关闭', 'close_it')]])


def gog_rester_ikb(link=None) -> InlineKeyboardMarkup:
    link_ikb = ikb([[('🎁 点击领取', link, 'url')]]) if link else ikb([[('👆🏻 点击注册', f't.me/{bot_name}', 'url')]])
    return link_ikb


""" sched_panel ↓"""


def sched_buttons():
    check_ex = '✅' if schedule.check_ex else '❎'
    low_activity = '✅' if schedule.low_activity else '❎'
    backup_db = '✅' if schedule.backup_db else '❎'
    keyboard = InlineKeyboard(row_width=2)
    keyboard.add(InlineButton(f'{check_ex} 到期保号', f'sched-check_ex'),
                 InlineButton(f'{low_activity} 活跃保号', f'sched-low_activity'),
                 InlineButton(f'{backup_db} 自动备份数据库', f'sched-backup_db'),
                 )
    keyboard.row(InlineButton(f'🫧 返回', 'manage'))
    return keyboard


""" checkin 按钮↓"""
