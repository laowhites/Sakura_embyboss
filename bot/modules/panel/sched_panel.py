import asyncio
import os

from pyrogram import filters

from bot import bot, sakura_b, schedule, save_config, prefixes, owner, LOGGER
from bot.func_helper.filters import admins_on_filter
from bot.func_helper.fix_bottons import sched_buttons
from bot.func_helper.msg_utils import callAnswer, editMessage, deleteMessage
from bot.func_helper.scheduler import Scheduler
from bot.scheduler import *

# 实例化
scheduler = Scheduler()

# 初始化命令 开机检查重启
loop = asyncio.get_event_loop()
loop.call_later(10, lambda: loop.create_task(BotCommands.set_commands(client=bot)))
loop.call_later(10, lambda: loop.create_task(check_restart()))

# 启动定时任务
auto_backup_db = DbBackupUtils.auto_backup_db

# 写优雅点
# 字典，method相应的操作函数
action_dict = {
    "check_ex": check_expired,
    "backup_db": auto_backup_db,
}
# 字典，对应的操作函数的参数和id
args_dict = {
    "check_ex": {'hour': 1, 'minute': 30, 'id': 'check_expired'},
    "backup_db": {'hour': 2, 'minute': 30, 'id': 'backup_db'},
}


def set_all_sche():
    for key, value in action_dict.items():
        if getattr(schedule, key):
            action = action_dict[key]
            args = args_dict[key]
            scheduler.add_job(action, 'cron', **args)


set_all_sche()


async def sched_panel(_, msg):
    # await deleteMessage(msg)
    await editMessage(msg,
                      text=f'🎮 **管理定时任务面板**\n\n默认关闭**看片榜单**，开启请在日与周中二选一，以免重复{sakura_b}的计算，谨慎',
                      buttons=sched_buttons())


@bot.on_callback_query(filters.regex('sched') & admins_on_filter)
async def sched_change_policy(_, call):
    try:
        method = call.data.split('-')[1]
        # 根据method的值来添加或移除相应的任务
        action = action_dict[method]
        args = args_dict[method]
        if getattr(schedule, method):
            scheduler.remove_job(job_id=args['id'], jobstore='default')
        else:
            scheduler.add_job(action, 'cron', **args)
        setattr(schedule, method, not getattr(schedule, method))
        save_config()
        await asyncio.gather(callAnswer(call, f'⭕️ {method} 更改成功'), sched_panel(_, call.message))
    except IndexError:
        await sched_panel(_, call.message)


@bot.on_message(filters.command('check_ex', prefixes) & admins_on_filter)
async def check_ex_admin(_, msg):
    send = await msg.reply("🍥 正在运行 【到期检测】。。。")
    await check_expired()
    await asyncio.gather(msg.delete(), send.edit("✅ 【到期检测结束】"))


# bot数据库手动备份
@bot.on_message(filters.command('backup_db', prefixes) & filters.user(owner))
async def manual_backup_db(_, msg):
    await asyncio.gather(deleteMessage(msg), auto_backup_db())


@bot.on_message(filters.command('low_activity', prefixes) & admins_on_filter)
async def run_low_ac(_, msg):
    await deleteMessage(msg)
    send = await msg.reply(f"⭕ 不活跃检测运行ing···")
    # await asyncio.gather(check_low_activity(), send.delete())


@bot.on_message(filters.command('restart', prefixes) & admins_on_filter)
async def restart_bot(_, msg):
    await deleteMessage(msg)
    send = await msg.reply("Restarting，等待几秒钟。")
    schedule.restart_chat_id = send.chat.id
    schedule.restart_msg_id = send.id
    save_config()
    try:
        # some code here
        LOGGER.info("重启")
        os.execl('/bin/systemctl', 'systemctl', 'restart', 'embyboss')  # 用当前进程执行systemctl命令，重启embyboss服务
    except FileNotFoundError:
        exit(1)
