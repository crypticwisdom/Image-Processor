import json

import requests
from django.conf import settings
from home.utils import log_request


base_url = settings.BILLING_BASE_URL
email = settings.BILLING_EMAIL
password = settings.BILLING_PASSWORD


class BillingService:
    @classmethod
    def login(cls):
        payload = json.dumps({"email": email, "password": password})
        url = f"{base_url}/login"
        response = requests.request("POST", url, data=payload, headers={"Content-Type": "application/json"}).json()
        log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response["token"]

    @classmethod
    def get_header(cls):
        token = settings.SHIPPING_TOKEN
        header = dict()
        header["Authorization"] = f"Bearer {token}"
        header["Content-Type"] = "application/json"
        return header

    @classmethod
    def validate_customer(cls, email):
        url = f"{base_url}/validate-customer"
        payload = json.dumps({
            "companyId": settings.BILLING_USER_ID,
            "customerEmail": email
        })
        header = {"Content-Type": "application/json"}
        response = requests.request("POST", url, headers=header, data=payload).json()
        return response

    # @classmethod
    # def register_client(cls):
    #     header =

