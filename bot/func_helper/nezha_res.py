"""
根据哪吒探针项目修改，只是图服务器界面好看。
"""
import humanize as humanize
import requests as r


def sever_info(tz, tz_api, tz_id):
    if not tz or not tz_api or not tz_id: return None

    # 请求头
    tz_headers = {
        'Authorization': tz_api  # 后台右上角下拉菜单获取 API Token
    }
    b = []
    try:
        # 请求地址
        for x in tz_id:
            tz_url = f'{tz}/api/v1/server/details?id={x}'
            # 发送GET请求，获取服务器流量信息
            res = r.get(tz_url, headers=tz_headers).json()
            # print(res)
            detail = res["result"][0]
            """cpu"""
            uptime = f'{int(detail["status"]["Uptime"] / 86400)} 天' if detail["status"]["Uptime"] != 0 else '⚠️掉线辣'
            CPU = f"{detail['status']['CPU']:.2f}"
            """内存"""
            MemTotal = humanize.naturalsize(detail['host']['MemTotal'], gnu=True)
            MemUsed = humanize.naturalsize(detail['status']['MemUsed'], gnu=True)
            Mempercent = f"{(detail['status']['MemUsed'] / detail['host']['MemTotal']) * 100:.2f}" if detail['host'][
                                                                                                          'MemTotal'] != 0 else "0"
            """流量"""
            NetInTransfer = humanize.naturalsize(detail['status']['NetInTransfer'], gnu=True)
            NetOutTransfer = humanize.naturalsize(detail['status']['NetOutTransfer'], gnu=True)
            """网速"""
            NetInSpeed = humanize.naturalsize(detail['status']['NetInSpeed'], gnu=True)
            NetOutSpeed = humanize.naturalsize(detail['status']['NetOutSpeed'], gnu=True)

            status_msg = f"· 🌐 服务器 | {detail['name']} · {uptime}\n" \
                         f"· 💫 CPU | {CPU}% \n" \
                         f"· 🌩️ 内存 | {Mempercent}% [{MemUsed}/{MemTotal}]\n" \
                         f"· ⚡ 网速 | ↓{NetInSpeed}/s  ↑{NetOutSpeed}/s\n" \
                         f"· 🌊 流量 | ↓{NetInTransfer}  ↑{NetOutTransfer}\n"
            b.append(dict(name=f'{detail["name"]}', id=detail["id"], server=status_msg))
        return b
    except:
        return None
