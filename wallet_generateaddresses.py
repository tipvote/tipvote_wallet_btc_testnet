
from app import db
import requests
import json
from walletconfig import url

from app.models import BtcWalletAddressesTest


def callforaddress():

    # standard json header
    headers = {'content-type': 'application/json'}

    # the method/params
    rpc_input = {
        "method": "getnewaddress",
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "1.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
    )

    # print response
    print(response.url)

    # the response in json format
    response_json = response.json()

    return response_json


def generate_addresses():

    # query amount addresses that are not uses
    get_available_addresses = BtcWalletAddressesTest.query\
        .filter(BtcWalletAddressesTest.status == 0)\
        .count()

    # see if less than 50
    if get_available_addresses <= 50:

        # make a 100 new addresses
        for f in range(100):

            # call the rpc
            newwalletaddress = callforaddress()

            # get the new address
            the_address = newwalletaddress["address"]

            # add to db addresses
            walletadd = BtcWalletAddressesTest(
                btcaddress=the_address,
                status=0,
                 )

            db.session.add(walletadd)

        db.session.commit()
    else:
        print(f"We have {get_available_addresses} addresses available still.  No need to run")


if __name__ == '__main__':
    generate_addresses()