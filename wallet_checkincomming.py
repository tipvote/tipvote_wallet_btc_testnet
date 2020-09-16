
import json
from decimal import Decimal
from sqlalchemy import or_
import requests
from app import db

from walletconfig import url, digital_currency

from app.common.functions import floating_decimals
from app.notification import add_new_notification

from app.models import \
    BtcWalletTest, \
    TransactionsBtcTest, \
    BtcUnconfirmedTest, \
    BtcTransOrphanTest

# this script nonstop.
# This cron job gets the user unconfirmed.
# It searches for incomming transactions.


def addtounconfirmed(amount, user_id, txid):
    """
    this function can track multiple incomming unconfirmed amounts
    :param amount:
    :param user_id:
    :param txid:
    :return:
    """

    # get unconfirmed transactions
    unconfirmedtable = BtcUnconfirmedTest.query.filter_by(user_id=user_id).first()

    # put to decimal
    decamount = floating_decimals(amount, 8)

    # if doesnt exist, create a new unconfirmed tranactions
    if unconfirmedtable is None:

        newunconfirmed = BtcUnconfirmedTest(
            user_id=user_id,
            unconfirmed1=0,
            unconfirmed2=0,
            unconfirmed3=0,
            unconfirmed4=0,
            unconfirmed5=0,

        )
        db.session.add(newunconfirmed)
    else:
        # find matching in unconfirmed table
        if unconfirmedtable.unconfirmed1 == 0:
            unconfirmedtable.unconfirmed1 = decamount
            unconfirmedtable.txid1 = txid
            db.session.add(unconfirmedtable)

        elif unconfirmedtable.unconfirmed2 == 0:
            unconfirmedtable.txid2 = txid
            unconfirmedtable.unconfirmed2 = decamount
            db.session.add(unconfirmedtable)

        elif unconfirmedtable.unconfirmed3 == 0:
            unconfirmedtable.txid3 = txid
            unconfirmedtable.unconfirmed3 = decamount
            db.session.add(unconfirmedtable)

        elif unconfirmedtable.unconfirmed4 == 0:
            unconfirmedtable.txid4 = txid
            unconfirmedtable.unconfirmed4 = decamount
            db.session.add(unconfirmedtable)

        elif unconfirmedtable.unconfirmed5 == 0:
            unconfirmedtable.unconfirmed5 = decamount
            unconfirmedtable.txid5 = txid
            db.session.add(unconfirmedtable)

        else:
            pass


def removeunconfirmed(user_id, txid):

    """
    this function removes the amount from unconfirmed
    """

    # get unconfirmed in database
    unconfirmeddelete = BtcUnconfirmedTest.query.filter_by(user_id=user_id).first()

    # find matching txid in table
    if unconfirmeddelete.txid1 == txid:
        unconfirmeddelete.txid1 = ''
        unconfirmeddelete.unconfirmed1 = 0
        db.session.add(unconfirmeddelete)

    elif unconfirmeddelete.txid2 == txid:
        unconfirmeddelete.txid2 = ''
        unconfirmeddelete.unconfirmed2 = 0
        db.session.add(unconfirmeddelete)

    elif unconfirmeddelete.txid3 == txid:
        unconfirmeddelete.txid3 = ''
        unconfirmeddelete.unconfirmed3 = 0
        db.session.add(unconfirmeddelete)

    elif unconfirmeddelete.txid4 == txid:
        unconfirmeddelete.txid4 = ''
        unconfirmeddelete.unconfirmed4 = 0
        db.session.add(unconfirmeddelete)

    elif unconfirmeddelete.txid5 == txid:
        unconfirmeddelete.txid5 = ''
        unconfirmeddelete.unconfirmed5 = 0
        db.session.add(unconfirmeddelete)

    else:
        pass


def getbalanceunconfirmed(user_id):
    """
    this function removes the amount from unconfirmed
    """
    unconfirmeddelete = BtcUnconfirmedTest.query.filter_by(user_id=user_id).first()
    a = Decimal(unconfirmeddelete.unconfirmed1)
    b = Decimal(unconfirmeddelete.unconfirmed2)
    c = Decimal(unconfirmeddelete.unconfirmed3)
    d = Decimal(unconfirmeddelete.unconfirmed4)
    e = Decimal(unconfirmeddelete.unconfirmed5)

    total = a + b + c + d + e

    wallet = BtcWalletTest.query.filter_by(user_id=user_id).first()
    totalchopped = floating_decimals(total, 8)
    wallet.unconfirmed = totalchopped
    db.session.add(wallet)


def orphan(txid, amount2, address):
    """
    this function is if they cant find a matching address
    """
    getorphan = BtcTransOrphanTest.query.filter_by(txid=txid).first()
    if getorphan:
        pass
    else:
        # orphan transaction..put in background.
        # they prolly sent to old address
        trans = BtcTransOrphanTest(
            btc=amount2,
            btcaddress=address,
            txid=txid,
        )
        db.session.add(trans)


def newincomming(userwallet, amount2, txid, howmanyconfs):
    """
    this function creates a new transaction for incomming coin
    """
    dcurrency = digital_currency

    # calculate balance of incomming and current
    currentamount = Decimal(userwallet.currentbalance)
    addcurrent = currentamount + amount2
    shortaddcurrent = floating_decimals(addcurrent, 8)

    # create and watch transaction
    trans = TransactionsBtcTest(
        category=3,
        user_id=userwallet.user_id,
        confirmations=howmanyconfs,
        txid=txid,
        amount=amount2,
        address='',
        blockhash='',
        timerecieved=0,
        timeoft=0,
        commentbtc='',
        otheraccount=0,
        balance=shortaddcurrent,
        fee=0,
        confirmed=0,
        orderid=0,
        senderid=0,
        digital_currency=dcurrency,
        confirmed_fee=0,
    )
    db.session.add(trans)

    # stats - the transaction account
    usertranscount = userwallet.transactioncount
    newcount = usertranscount + 1
    userwallet.transactioncount = newcount
    db.session.add(userwallet)

    # add total of incomming
    addtounconfirmed(amount=amount2,
                     user_id=userwallet.user_id,
                     txid=txid
                     )

    # get total unconfirmed balance
    getbalanceunconfirmed(userwallet.user_id)

    # notify user
    sendnotification(user_id=userwallet.user_id, notetype=105)


def updateincomming(howmanyconfs, transactions, userwallet, txid, amount2):
    if transactions.confirmed == 1:
        pass
    else:
        # if confirmations less than 12..update them ..else
        # check to see if in table and delete
        if 0 <= howmanyconfs <= 5:

            # set confirmation count in transaction
            transactions.confirmations = howmanyconfs
            db.session.add(transactions)

            # get total unconfirmed balance
            getbalanceunconfirmed(userwallet.user_id)

        elif 6 <= howmanyconfs <= 25:

            # remove from unconfirmed
            removeunconfirmed(user_id=userwallet.user_id, txid=txid)

            # get new address
            # getnewaddress(user_id=userwallet.user_id)

            # calculate balance
            bal = floating_decimals(userwallet.currentbalance, 8)
            addit = floating_decimals(bal, 8) + amount2
            addittotal = floating_decimals(addit, 8)

            # set balance in database
            userwallet.currentbalance = addittotal

            # updated transaction
            transactions.confirmations = howmanyconfs
            transactions.confirmed = 1
            transactions.balance = addittotal

            db.session.add(transactions)
            db.session.add(userwallet)

            # get total unconfirmed balance
            getbalanceunconfirmed(userwallet.user_id)

        else:
            pass


def sendnotification(user_id, notetype):
    """
    # This function send notifications
    """
    # Positive
    # 0 =  wallet sent

    # errors
    # 100 =  too litte or too much at withdrawl
    # 102 = wallet error
    # 103 = btc address error

    # btc address error
    add_new_notification(
        thetypeofnote=notetype,
        user_id=user_id,
    )


def addcoin():
    # get the json response
    response_json = getincommingcoin()

    # this is a complicated response
    # turns array of json object

    for i in (response_json['result']):

        address = i['address']
        print(("address: ", i['address']))
        amount = i['amount']
        print(("amount: ", i['amount']))
        txid = i['txid']
        print(("txid: ", i['txid']))
        confirmations = i['confirmations']
        print(("confirmations: ", i['confirmations']))
        print("*"*10)

        # get the decimal of amount
        amount2 = floating_decimals(amount, 8)

        # get confirmations
        howmanyconfs = int(confirmations)

        # find the wallet that matches the address
        userwallets = BtcWalletTest.query \
            .filter(or_(BtcWalletTest.address1 == address,
                        BtcWalletTest.address2 == address,
                        BtcWalletTest.address3 == address
                        )
                    ) \
            .first()

        # if wallet exists else oprphan
        if userwallets:

            # get the transactions
            transactions = TransactionsBtcTest.query\
                .filter(TransactionsBtcTest.txid == txid)\
                .first()

            # create in database a new transaction or watch it
            if transactions:

                # update if there is a transaction
                updateincomming(howmanyconfs,
                                transactions,
                                userwallets,
                                txid,
                                amount2)
            else:

                # create a transaction
                newincomming(userwallets, amount2, txid, howmanyconfs)

        # no address found..orphan
        else:
            orphan(txid=txid, amount2=amount2, address=address)

    db.session.commit()


def getincommingcoin():
    # standard json header
    headers = {'content-type': 'application/json'}

    # method and params
    rpc_input = {
        "method": "listunspent",
        "params":
            {
             "minconf": 0,
             "maxconf": 50,
             }
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "1.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
    )

    response_json = response.json()
    print(response_json)
    return response_json


if __name__ == '__main__':
    addcoin()
