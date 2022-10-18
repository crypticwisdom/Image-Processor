import json

import requests
from django.conf import settings

from home.utils import log_request

base_url = settings.SHIPPING_BASE_URL
email = settings.SHIPPING_EMAIL
password = settings.SHIPPING_PASSWORD


class ShippingService:
    @classmethod
    def login(cls):
        from home.utils import log_request
        url = f"{base_url}/login"
        payload = json.dumps({"email": email, "password": password})
        response = requests.request("POST", url, data=payload, headers={"Content-Type": "application/json"}).json()
        log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response["token"]

    @classmethod
    def get_header(cls):
        token = cls.login()
        header = dict()
        header["Authorization"] = f"Bearer {token}"
        header["Content-Type"] = "application/json"
        return header

    @classmethod
    def get_states_with_stations(cls, **kwargs):
        # header = cls.get_header()
        url = f"{base_url}/operations/stateInfo?StateName={kwargs.get('state_name')}"
        if kwargs.get('city_name'):
            url = f"{base_url}/operations/stateInfo?StateName={kwargs.get('state_name')}&CityName={kwargs.get('city_name')}"

        response = requests.request("GET", url).json()
        # response = requests.request("GET", url, headers=header).json()
        log_request(f"url: {url}", f"response: {response}")
        # log_request(f"url: {url}", f"headers: {header}", f"response: {response}")
        return response

    @classmethod
    def get_all_states(cls):
        # header = cls.get_header()
        url = f"{base_url}/operations/states"
        response = requests.request("GET", url).json()
        # response = requests.request("GET", url, headers=header).json()
        log_request(f"url: {url}", f"response: {response}")
        # log_request(f"url: {url}", f"headers: {header}", f"response: {response}")
        return response

    @classmethod
    def rating(cls, **kwargs):
        header = cls.get_header()
        all_product = "OrderProduct.objects.filter()"
        shipment = list()
        for product in all_product:
            item = dict()
            item["PackageId"] = product.id
            item["Quantity"] = products.title()
            item["Weight"] = products.title()
            item["ItemType"] = products.title()
            item["WeightRange"] = products.title()
            item["Name"] = products.title()
            item["Amount"] = products.title()
            item["ShipmentType"] = products.title()
            shipment.append(item)

        url = f"{base_url}/operations/quote"
        payload = dict()
        payload["PaymentMode"] = kwargs.get("")
        payload["Vehicle"] = kwargs.get("")
        payload["PickupTime"] = kwargs.get("")
        payload["PickupDate"] = kwargs.get("")
        payload["PickupLatitude"] = kwargs.get("")
        payload["PickupLongitude"] = kwargs.get("")
        payload["PickupAddress"] = kwargs.get("")
        payload["SenderPhoneNumber"] = kwargs.get("")
        payload["SenderName"] = kwargs.get("")
        payload["ReceiverName"] = kwargs.get("")
        payload["DeliveryAddress"] = kwargs.get("")
        payload["DeliveryLatitude"] = kwargs.get("")
        payload["DeliveryLongitude"] = kwargs.get("")
        payload["DeliveryLatitude"] = kwargs.get("")
        payload["ReceiverPhoneNumber"] = kwargs.get("")
        payload["PickupState"] = kwargs.get("")
        payload["DeliveryState"] = kwargs.get("")
        payload["Weight"] = kwargs.get("")
        payload["InstantDelivery"] = kwargs.get("")
        payload["PickupStationId"] = kwargs.get("")
        payload["DeliveryStationId"] = kwargs.get("")
        payload["PickupCity"] = kwargs.get("")
        payload["DeliveryCity"] = kwargs.get("")
        payload["ShipmentItems"] = shipment

        response = requests.request("POST", url, headers=header, data=payload).json()
        # log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response




