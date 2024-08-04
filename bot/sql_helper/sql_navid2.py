from bot.sql_helper import Base, Session, engine
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy import or_


class Navid2(Base):
    """
    无tag绑定账号
    navid表，navid_id主键，默认值lv，us，iv
    """
    __tablename__ = 'navid2'
    navid_id = Column(String(255), primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=True)
    pwd = Column(String(255), nullable=True)
    pwd2 = Column(String(255), nullable=True)
    #
    lv = Column(String(1), default='d')
    cr = Column(DateTime, nullable=True)
    ex = Column(DateTime, nullable=True)
    expired = Column(Integer, nullable=True)


Navid2.__table__.create(bind=engine, checkfirst=True)


def sql_add_navid2(navid_id, name, cr, ex, pwd='5210', pwd2='1234', lv='b', expired=0):
    """
    添加一条navid记录，如果tg已存在则忽略
    """
    with Session() as session:
        try:
            navid = Navid2(navid_id=navid_id, name=name, pwd=pwd, pwd2=pwd2, lv=lv, cr=cr, ex=ex, expired=expired)
            session.add(navid)
            session.commit()
        except:
            pass


def sql_get_navid2(name):
    """
    查询一条navid记录，可以根据, navid_id或者name来查询
    """
    with Session() as session:
        try:
            # 使用or_方法来表示或者的逻辑，如果有tg就用tg，如果有navid_id就用navid_id，如果有name就用name，如果都没有就返回None
            navid = session.query(Navid2).filter(or_(Navid2.name == name, Navid2.navid_id == name)).first()
            return navid
        except:
            return None


def get_all_navid2(condition):
    """
    查询所有navid记录
    """
    with Session() as session:
        try:
            embies = session.query(Navid2).filter(condition).all()
            return embies
        except:
            return None


def sql_update_navid2(condition, **kwargs):
    """
    更新一条navid记录，根据condition来匹配，然后更新其他的字段
    """
    with Session() as session:
        try:
            # 用filter来过滤，注意要加括号
            navid = session.query(Navid2).filter(condition).first()
            if navid is None:
                return False
            # 然后用setattr方法来更新其他的字段，如果有就更新，如果没有就保持原样
            for k, v in kwargs.items():
                setattr(navid, k, v)
            session.commit()
            return True
        except:
            return False


def sql_delete_navid2(navid_id):
    """
    根据tg删除一条navid记录
    """
    with Session() as session:
        try:
            navid = session.query(Navid2).filter_by(navid_id=navid_id).first()
            if navid:
                session.delete(navid)
                try:
                    session.commit()
                    return True
                except Exception as e:
                    # 记录错误信息
                    print(e)
                    # 回滚事务
                    session.rollback()
                    return False
            else:
                return None
        except Exception as e:
            # 记录错误信息
            print(e)
            return False
