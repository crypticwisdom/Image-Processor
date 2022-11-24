import json

import requests
import xmltodict
from django.conf import settings

from home.utils import log_request

payment_gw_url = settings.PAYMENT_GATEWAY_URL
payment_merchant_id = settings.PAYMENT_GATEWAY_MERCHANT_ID
payment_secret = settings.PAYMENT_GATEWAY_SECRET_KEY
get_banks_url = settings.BANK_URL
credit_wallet_url = settings.PAYMENT_CREDIT_WALLET_URL


def get_bank_codes():
    """
        Call PayArena's API to fetch all bank codes.
    """
    try:
        # requests.exceptions.RequestException
        response = requests.get(url=get_banks_url)
        log_request(f"url: {response.url}, response: {response.json()}")
        if response.status_code != 200:
            return False, "Request was not successful"
        response = response.json()
        # response = {
        #     "Success": True,
        #     "Message": "Successful",
        #     "Data": [
        #         {
        #             "CBNCode": "044",
        #             "Name": "Access Bank"
        #         },
        #         {
        #             "CBNCode": "011",
        #             "Name": "First Bank"
        #         },
        #         {
        #             "CBNCode": "058",
        #             "Name": "GTBank"
        #         },
        #         {
        #             "CBNCode": "057",
        #             "Name": "Zenith Bank"
        #         },
        #         {
        #             "CBNCode": "033",
        #             "Name": "United Bank of Africa"
        #         },
        #         {
        #             "CBNCode": "063",
        #             "Name": "Diamond Bank"
        #         },
        #         {
        #             "CBNCode": "068",
        #             "Name": "Standard Chartered"
        #         },
        #         {
        #             "CBNCode": "082",
        #             "Name": "Keystone Bank"
        #         },
        #         {
        #             "CBNCode": "076",
        #             "Name": "Polaris Bank"
        #         },
        #         {
        #             "CBNCode": "070",
        #             "Name": "Fidelity Bank"
        #         },
        #         {
        #             "CBNCode": "214",
        #             "Name": "FCMB Bank"
        #         },
        #         {
        #             "CBNCode": "035",
        #             "Name": "Wema Bank"
        #         },
        #         {
        #             "CBNCode": "032",
        #             "Name": "Union Bank"
        #         },
        #         {
        #             "CBNCode": "215",
        #             "Name": "Unity Bank"
        #         },
        #         {
        #             "CBNCode": "232",
        #             "Name": "Sterling Bank"
        #         },
        #         {
        #             "CBNCode": "050",
        #             "Name": "Ecobank"
        #         },
        #         {
        #             "CBNCode": "102",
        #             "Name": "Titan"
        #         },
        #         {
        #             "CBNCode": "306",
        #             "Name": "etranzact"
        #         },
        #         {
        #             "CBNCode": "565",
        #             "Name": "Hope PSB"
        #         }
        #     ]
        # }
        if response['Success']:
            return True, response
        return False, "Request was not successful"
    except (Exception, ) as err:
        return False, str(err)


def call_name_enquiry(bank_code: str, account_number: str):
    try:
        response = requests.get(url=f'{settings.NAME_ENQUIRY}/214/1774691015')
        # response = requests.get(url=f'{settings.NAME_ENQUIRY}/{bank_code}/{account_number}')
        if response.status_code != 200:
            return False, "Error while requesting for name enquiry"

        response_to_dict = xmltodict.parse(response.text)
        if response_to_dict['NameEnquiryResponse']['ResponseCode'] != '00':
            return False, response_to_dict['NameEnquiryResponse']['ErrorMessage']

        # response_to_dict = {
        #     'NameEnquiryResponse': {
        #         'ResponseCode': '200',
        #         'AccountNumber': '2114616054',
        #         'AccountName': 'Nwachukwu Wisdom',
        #         'PhoneNumber': '08057784796',
        #         'ErrorMessage': 'error'
        #     }
        # }

        return True, response_to_dict
    except (Exception, ) as err:
        return False, str(err)


def payment_for_wallet(**kwargs):
    link = None
    url = f"{payment_gw_url}/{payment_merchant_id}"
    header = dict()
    header["Accept"] = header["Content-Type"] = "application/json"
    data = dict()
    data["amount"] = kwargs.get("amount")
    data["currency"] = 566
    data["description"] = kwargs.get("narration")
    data["returnUrl"] = kwargs.get("callback_url")
    data["secretKey"] = payment_secret
    data["fee"] = 0
    data["CustomerName"] = kwargs.get("name")
    data["Email"] = kwargs.get("email")

    payload = json.dumps(data)

    response = requests.request("POST", url, headers=header, data=payload)
    if response.status_code == 200 and str(response.text).isnumeric():
        link = f"{payment_gw_url}/{response.text}"

    return link


def credit_wallet(**kwargs):
    url = str(credit_wallet_url)

    data = dict()
    data["account"] = kwargs.get("account")
    data["reference"] = kwargs.get("ref_number")
    data["amount"] = kwargs.get("amount")
    data["description"] = kwargs.get("narration")
    data["channel"] = 1

    payload = json.dumps(data)
    response = requests.request("POST", url, headers=None, data=payload).json()
    log_request(f"url: {url}, header: , payload: {payload}, response: {response}")
    return response


