from app import db
from datetime import datetime
from app.models import TransactionsBtcTest


def addtransaction(category, amount, user_id, comment, orderid, balance):
    """

    :param category:
    :param amount:
    :param user_id:
    :param comment:
    :param orderid:
    :param balance:
    :return:
    """
    try:
        now = datetime.utcnow()
        comment = str(comment)
        orderid = int(orderid)

        trans = TransactionsBtcTest(
            category=category,
            user_id=user_id,
            senderid=0,
            confirmations=0,
            confirmed=1,
            txid='',
            blockhash='',
            timeoft=0,
            timerecieved=0,
            otheraccount=0,
            address='',
            fee=0,
            created=now,
            commentbtc=comment,
            amount=amount,
            orderid=orderid,
            balance=balance,
            digital_currency=2,
            confirmed_fee=0
        )
        db.session.add(trans)
        db.session.commit()

    except Exception as e:
        print(str(e))
