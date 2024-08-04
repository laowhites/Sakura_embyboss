#! /usr/bin/python3
# -*- coding:utf-8 -*-
"""
navid的api操作方法
"""
import logging
from datetime import datetime, timedelta

import requests as r

from bot import navid_url, navid_admin_name, navid_admin_password, _open, schedule, LOGGER
from bot.func_helper.utils import pwd_create, tem_decrease
from bot.sql_helper.sql_navid import sql_update_navid, sql_get_navid, Navid
from bot.sql_helper.sql_navid2 import sql_add_navid2, sql_delete_navid2


class NavidService:
    """
    初始化一个类，接收url和api_key，params作为参数
    计划是将所有关于navid api的使用方法放进来
    """

    def __init__(self):
        """
        必要参数
        :param url: 网址
        :param name: 管理员用户名
        :param password: 管理员密码
        """
        self.url = navid_url
        self.name = navid_admin_name
        self.password = navid_admin_password
        self.agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 '
            'Safari/537.36 Edg/114.0.1823.82')
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'User-Agent': self.agent
        }
        self.token_touch = datetime.now()
        self.fetch_token(self)
        self.headers["x-nd-client-unique-id"] = 'navid-admin';
        self.headers["x-nd-authorization"] = f'Bearer {self.token}';

    @staticmethod
    def fetch_token(self):
        name_data = ({"username": self.name, "password": self.password})
        login_res = r.post(f'{self.url}/auth/login',
                           headers=self.headers,
                           json=name_data)
        if login_res.status_code == 200:
            self.token = login_res.json()['token']
            return
        logging.error("管理员token获取失败")

    async def navid_create(self, tg: int, name, pwd2, us: int, stats):

        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        """
        创建账户
        :param tg: tg_id
        :param name: navid_name
        :param pwd2: pwd2 安全码
        :param us: us 积分
        :param stats: policy 策略
        :return: bool
        """
        if _open.tem >= _open.all_user:
            return 403
        ex = (datetime.now() + timedelta(days=us))
        pwd = await pwd_create(8) if stats != 'o' else 5210

        name_data = ({
            "isAdmin": False,
            "userName": name,
            "name": name,
            "password": pwd
        })
        new_user = r.post(f'{self.url}/api/user',
                          headers=self.headers,
                          json=name_data)
        if new_user.status_code == 200:
            id_: str = new_user.json()["id"]
            if stats == 'y':
                sql_update_navid(Navid.tg == tg, navid_id=id_, name=name, pwd=pwd, pwd2=pwd2, lv='b',
                                 cr=datetime.now(), ex=ex)
            elif stats == 'n':
                sql_update_navid(Navid.tg == tg, navid_id=id_, name=name, pwd=pwd, pwd2=pwd2, lv='b',
                                 cr=datetime.now(), ex=ex,
                                 us=0)
            elif stats == 'o':
                sql_add_navid2(navid_id=id_, name=name, cr=datetime.now(), ex=ex)

            if schedule.check_ex:
                ex = ex.strftime("%Y-%m-%d %H:%M:%S")
            elif schedule.low_activity:
                ex = '__若21天无观看将封禁__'
            else:
                ex = '__无需保号，放心食用__'
            return pwd, ex
        elif new_user.status_code == 400:
            error = new_user.json()["errors"]
            if error and error['userName'] == "ra.validation.unique":
                return 100
        return 400

    async def navid_del(self, tg, navid_id, unbound=False):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        """
        删除navid账户
        :param tg: tele id
        :param navid_id: navid_id
        :param unbound: 未绑定
        :return: bool
        """

        if navid_id:
            res = r.delete(f'{self.url}/api/user/{navid_id}', headers=self.headers)
            if res.status_code != 200:
                return False

        if not unbound:
            if sql_update_navid(Navid.tg == tg, navid_id=None, name=None, pwd=None, pwd2=None, lv='d',
                                cr=None,
                                ex=None):
                await tem_decrease()
                return True
        else:
            if sql_delete_navid2(navid_id=navid_id):
                await tem_decrease()
                return True
        return False

    async def navid_reset(self, id, new=None):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        """
        重置密码
        step：
        1.query info
        2.update with info
        :param id: navid_id
        :param new: new_pwd
        :return: bool
        """
        res = r.get(f'{self.url}/api/user/{id}', headers=self.headers)
        if res.status_code != 200:
            logging.error("管理员账户查询用户信息失败")
            return False
        info = res.json()
        info["password"] = new
        res = r.put(f'{self.url}/api/user/{id}', json=info, headers=self.headers)
        if res.status_code != 200:
            return False
        if sql_update_navid(Navid.navid_id == id, pwd=new) is True:
            return True

    async def authority_account(self, tg, username, password=None):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        data = ({"username": username, "password": password})
        res = r.post(f'{self.url}/auth/login',
                     headers=self.headers,
                     json=data)
        if res.status_code == 200:
            navid_id = res.json()["User"]["Id"]
            return True, navid_id
        return False, 0

    async def users(self):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        try:
            _url = f"{self.url}/api/user"
            resp = r.get(_url, headers=self.headers)
            if resp.status_code != 200:
                return False, {'error': "🤕navid 服务器连接失败!"}
            return True, resp.json()
        except Exception as e:
            return False, {'error': e}

    def user(self, navid_id):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            self.refresh_token()
        """
        通过id查看该账户配置信息
        :param navid_id:
        :return:
        """
        try:
            _url = f"{self.url}/emby/Users/{navid_id}"
            resp = r.get(_url, headers=self.headers)
            if resp.status_code != 204 and resp.status_code != 200:
                return False, {'error': "🤕Emby 服务器连接失败!"}
            return True, resp.json()
        except Exception as e:
            return False, {'error': e}

    """
    修改用户policy，本质修改服务端密码或复原原始密码
    """

    async def navid_change_policy(self, navid_id, active=False):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        if not active:
            pwd = await pwd_create(8)
            await self.navid_reset(navid_id, pwd)
        else:
            navid = sql_get_navid(navid_id)
            if not navid:
                logging.error("未查询到用户信息")
                return
            await self.navid_reset(navid_id, navid.pwd)

    """
    修改用户管理权限
    """

    async def navid_admin(self, navid_id, admin=False):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        navid = self.query_user(navid_id)
        if not navid:
            return False

        navid["isAdmin"] = admin
        res = r.put(f'{self.url}/api/user/{id}', json=navid, headers=self.headers)
        if res.status_code == 200:
            return True

        logging.error("查询navid失败 " + f'{navid_id}')
        return False;

    async def query_user(self, navid_id: str):
        if self.token_touch + timedelta(hours=12) < datetime.now():
            await self.refresh_token()
        """
        查询用户信息
       """
        res = r.get(f'{self.url}/auth/login/{navid_id}',
                    headers=self.headers)
        if res.status_code != 200:
            return res.json()
        return None

    async def refresh_token(self):
        self.fetch_token(self)


# 实例
navidService = NavidService()
