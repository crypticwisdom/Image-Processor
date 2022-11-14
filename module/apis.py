import requests
import xmltodict
from django.conf import settings


def get_bank_codes():
    """
        Call PayArena's API to fetch all bank codes.
    """
    try:
        # requests.exceptions.RequestException
        # response = requests.get(url="https://test.payarena.com:8088/mobile/get-banks")
        # if response.status_code != 200:
        #     return False, "Request was not successful"
        # response = response.json()
        response = {
            "Success": True,
            "Message": "Successful",
            "Data": [
                {
                    "CBNCode": "044",
                    "Name": "Access Bank"
                },
                {
                    "CBNCode": "011",
                    "Name": "First Bank"
                },
                {
                    "CBNCode": "058",
                    "Name": "GTBank"
                },
                {
                    "CBNCode": "057",
                    "Name": "Zenith Bank"
                },
                {
                    "CBNCode": "033",
                    "Name": "United Bank of Africa"
                },
                {
                    "CBNCode": "063",
                    "Name": "Diamond Bank"
                },
                {
                    "CBNCode": "068",
                    "Name": "Standard Chartered"
                },
                {
                    "CBNCode": "082",
                    "Name": "Keystone Bank"
                },
                {
                    "CBNCode": "076",
                    "Name": "Polaris Bank"
                },
                {
                    "CBNCode": "070",
                    "Name": "Fidelity Bank"
                },
                {
                    "CBNCode": "214",
                    "Name": "FCMB Bank"
                },
                {
                    "CBNCode": "035",
                    "Name": "Wema Bank"
                },
                {
                    "CBNCode": "032",
                    "Name": "Union Bank"
                },
                {
                    "CBNCode": "215",
                    "Name": "Unity Bank"
                },
                {
                    "CBNCode": "232",
                    "Name": "Sterling Bank"
                },
                {
                    "CBNCode": "050",
                    "Name": "Ecobank"
                },
                {
                    "CBNCode": "102",
                    "Name": "Titan"
                },
                {
                    "CBNCode": "306",
                    "Name": "etranzact"
                },
                {
                    "CBNCode": "565",
                    "Name": "Hope PSB"
                }
            ]
        }
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



