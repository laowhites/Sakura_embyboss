"""
基本的sql操作
"""
from bot.sql_helper import Base, Session, engine
from sqlalchemy import Column, BigInteger, String, DateTime, Integer, case
from sqlalchemy import func
from sqlalchemy import or_
from bot import LOGGER


class Navid(Base):
    """
    navid表，tg主键，默认值lv，us，iv
    """
    __tablename__ = 'navid'
    tg = Column(BigInteger, primary_key=True, autoincrement=False)
    navid_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    pwd = Column(String(255), nullable=True)
    pwd2 = Column(String(255), nullable=True)
    lv = Column(String(1), default='d')
    # 创建时间
    cr = Column(DateTime, nullable=True)
    # 失效时间
    ex = Column(DateTime, nullable=True)
    # 注册码兑换天数
    us = Column(Integer, default=0)
    # 某种币币值
    iv = Column(Integer, default=0)
    # 签到时间
    ch = Column(DateTime, nullable=True)


Navid.__table__.create(bind=engine, checkfirst=True)


def sql_add_navid(tg: int):
    """
    添加一条navid记录，如果tg已存在则忽略
    """
    with Session() as session:
        try:
            navid = Navid(tg=tg)
            session.add(navid)
            session.commit()
        except:
            pass


def sql_delete_navid(tg=None, navid_id=None, name=None):
    """
    根据tg, navid_id或name删除一条navid记录
    """
    with Session() as session:
        try:
            # 构造一个or_条件，只要有一个参数不为None就可以匹配
            condition = or_(Navid.tg == tg, Navid.navid_id == navid_id, Navid.name == name)
            # 用filter来过滤，注意要加括号
            navid = session.query(Navid).filter(condition).with_for_update().first()
            if navid:
                session.delete(navid)
                session.commit()
                return True
            else:
                return None
        except:
            return False


def sql_update_navids(some_list: list, method=None):
    """ 根据list中的tg值批量更新一些值 ，此方法不可更新主键"""
    with Session() as session:
        if method == 'iv':
            try:
                mappings = [{"tg": c[0], "iv": c[1]} for c in some_list]
                session.bulk_update_mappings(Navid, mappings)
                session.commit()
                return True
            except:
                session.rollback()
                return False
        if method == 'ex':
            try:
                mappings = [{"tg": c[0], "ex": c[1]} for c in some_list]
                session.bulk_update_mappings(Navid, mappings)
                session.commit()
                return True
            except:
                session.rollback()
                return False
        if method == 'bind':
            try:
                # mappings = [{"name": c[0], "navid_id": c[1]} for c in some_list] 没有主键不能插入的这是navid表
                mappings = [{"tg": c[0], "name": c[1], "navid_id": c[2]} for c in some_list]
                session.bulk_update_mappings(Navid, mappings)
                session.commit()
                return True
            except Exception as e:
                print(e)
                session.rollback()
                return False


def sql_get_navid(identification):
    """
    查询一条emby记录，可以根据tg, embyid或者name来查询
    """
    with Session() as session:
        try:
            # 使用or_方法来表示或者的逻辑，如果有tg就用tg，如果有navid_id就用navid_id，如果有name就用name，如果都没有就返回None
            navid = session.query(Navid).filter(or_(Navid.tg == identification, Navid.name == identification,
                                                    Navid.navid_id == identification)).first()
            return navid
        except:
            return None


def get_all_navid(condition):
    """
    查询所有navid记录
    """
    with Session() as session:
        try:
            embies = session.query(Navid).filter(condition).all()
            return embies
        except:
            return None


def sql_update_navid(condition, **kwargs):
    """
    更新一条navid记录，根据condition来匹配，然后更新其他的字段
    """
    with Session() as session:
        try:
            # 用filter来过滤，注意要加括号
            navid = session.query(Navid).filter(condition).first()
            if navid is None:
                return False
            # 然后用setattr方法来更新其他的字段，如果有就更新，如果没有就保持原样
            for k, v in kwargs.items():
                setattr(navid, k, v)
            session.commit()
            return True
        except Exception as e:
            LOGGER.error(e)
            return False


def sql_count_navid():
    """
    # 检索有tg和navid_id的navid记录的数量，以及navid.lv =='a'条件下的数量
    # count = sql_count_navid()
    :return: int, int, int
    """
    with Session() as session:
        try:
            # 使用func.count来计算数量，使用filter来过滤条件
            count = session.query(
                func.count(Navid.tg).label("tg_count"),
                func.count(Navid.navid_id).label("navid_id_count"),
                func.count(case((Navid.lv == "a", 1))).label("lv_a_count")
            ).first()
        except Exception as e:
            # print(e)
            return None, None, None
        else:
            return count.tg_count, count.navid_id_count, count.lv_a_count
