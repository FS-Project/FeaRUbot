# INFO : This is a copy of the source code from the One4ubot repo, and has the permission of the owner.
try:
    from fearubot.modules.sql_helper import SESSION, BASE
except ImportError:
    raise AttributeError
from sqlalchemy import Column, String


class PMPermit(BASE):
    __tablename__ = "pmpermit"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)  # ensure string


PMPermit.__table__.create(checkfirst=True)


def is_approved(chat_id):
    try:
        return SESSION.query(PMPermit).filter(
            PMPermit.chat_id == str(chat_id)).one()
    except BaseException:
        return None
    finally:
        SESSION.close()


def approve(chat_id):
    adder = PMPermit(str(chat_id))
    SESSION.add(adder)
    SESSION.commit()


def dissprove(chat_id):
    rem = SESSION.query(PMPermit).get(str(chat_id))
    if rem:
        SESSION.delete(rem)
        SESSION.commit()
