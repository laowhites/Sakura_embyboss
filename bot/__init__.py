#! /usr/bin/python3
# -*- coding: utf-8 -*-
from .func_helper.logger_config import logu, Now
from pyrogram import enums
from pyromod import Client
from .schemas import Config
from pyrogram.types import BotCommand

LOGGER = logu(__name__)

config = Config.load_config()


def save_config():
    config.save_config()


'''从config对象中获取属性值'''
# bot
bot_name = config.bot_name
bot_token = config.bot_token
owner_api = config.owner_api
owner_hash = config.owner_hash
owner = config.owner
group = config.group
main_group = config.main_group
chanel = config.chanel
bot_photo = config.bot_photo
user_buy = config.user_buy
_open = config.open
admins = config.admins
invite = config.invite
sakura_b = config.money
prefixes = ['/', '!', '.', '，', '。']
schedule = config.schedule
# navid设置
navid_admin_name = config.navid_admin_name
navid_admin_password = config.navid_admin_password
navid_url = config.navid_url
navid_line = config.navid_line
another_line = config.another_line
# # 数据库
db_host = config.db_host
db_user = config.db_user
db_pwd = config.db_pwd
db_name = config.db_name
db_port = config.db_port
db_is_docker = config.db_is_docker
db_docker_name = config.db_docker_name
db_backup_dir = config.db_backup_dir
db_backup_maxcount = config.db_backup_max_count
# 探针
tz_ad = config.tz_ad
tz_api = config.tz_api
tz_id = config.tz_id

w_anti_channel_ids = config.w_anti_channel_ids
kk_gift_days = config.kk_gift_days
fuxx_pitao = config.fuxx_pitao

save_config()

LOGGER.info("配置文件加载完毕")

'''定义不同等级的人使用不同命令'''
user_p = [
    BotCommand("start", "[私聊] 开启用户面板"),
    BotCommand("my_info", "[用户] 查看状态"),
]
if not user_buy.stat:
    user_p += [BotCommand("red", "[用户/禁言] 发红包"),
               BotCommand("srank", "[用户/禁言] 查看计分")]
# 取消 BotCommand("exchange", "[私聊] 使用注册码")
admin_p = user_p + [
    BotCommand("kk", "管理用户 [管理]"),
    BotCommand("score", "加/减积分 [管理]"),
    BotCommand("coins", f"加/减{sakura_b} [管理]"),
    BotCommand("kick_not_navid", f"踢出当前群内无号崽 [管理]"),
    BotCommand("renew", "调整到期时间 [管理]"),
    BotCommand("rm_navid", "删除用户[包括非tg] [管理]"),
    BotCommand("prouser", "增加白名单 [管理]"),
    BotCommand("revuser", "减少白名单 [管理]"),
    BotCommand("rev_white_channel", "移除皮套人白名单 [管理]"),
    BotCommand("white_channel", "添加皮套人白名单 [管理]"),
    BotCommand("unban_channel", "解封皮套人 [管理]"),
    BotCommand("syncgroupm", "消灭不在群的人 [管理]"),
    BotCommand("sync_unbound", "消灭未绑定bot的emby账户 [管理]"),
    BotCommand("low_activity", "手动运行活跃检测 [管理]"),
    BotCommand("check_ex", "手动到期检测 [管理]"),
    BotCommand("navid_admin", "开启navid控制台权限 [管理]"),
    BotCommand("ucr", "私聊创建非tg的navid用户 [管理]"),
    BotCommand("uinfo", "查询指定用户名 [管理]"),
    BotCommand("urm", "删除指定用户名 [管理]"),
    BotCommand("restart", "重启bot [owner]"),
]

owner_p = admin_p + [
    BotCommand("proadmin", "添加bot管理 [owner]"),
    BotCommand("revadmin", "移除bot管理 [owner]"),
    BotCommand("renewall", "一键派送天数给所有未封禁的用户 [owner]"),
    BotCommand("coinsall", "一键派送币币给所有未封禁的用户 [owner]"),
    BotCommand("callall", "群发消息给每个人 [owner]"),
    BotCommand("backup_db", "手动备份数据库[owner]"),
    BotCommand("config", "开启bot高级控制面板 [owner]")
]

proxy = {} if not config.proxy.scheme else config.proxy.dict()

bot = Client(bot_name, api_id=owner_api, api_hash=owner_hash, bot_token=bot_token, proxy=proxy,
             workers=300,
             max_concurrent_transmissions=1000, parse_mode=enums.ParseMode.MARKDOWN)

LOGGER.info("client 客户端准备")
