# 重启
from bot import bot, LOGGER, schedule, save_config
from pyrogram.errors import BadRequest


# 定义一个检查函数
async def check_restart():
    if schedule.restart_chat_id != 0:
        chat_id, msg_id = schedule.restart_chat_id, schedule.restart_msg_id
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
        except BadRequest:
            await bot.send_message(chat_id=chat_id, text='Restarted Successfully!')
        LOGGER.info(f"目标：{chat_id} 消息id：{msg_id} 已提示重启成功")
        schedule.restart_chat_id = 0
        schedule.restart_msg_id = 0
        save_config()

    else:
        LOGGER.info("未检索到有重启指令，直接启动")
