import json

import requests
from django.conf import settings

from home.utils import log_request

base_url = settings.SHIPPING_BASE_URL
email = settings.SHIPPING_EMAIL
password = settings.SHIPPING_PASSWORD
header = {'Content-Type': 'application/json'}


class ShippingService:
    @classmethod
    def login(cls):
        url = f"{base_url}/login"
        payload = json.dumps({"email": email, "password": password})
        response = requests.request("POST", url, headers=header, data=payload).json()
        log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response

    @classmethod
    def rating(cls, **kwargs):
        all_product = "OrderProduct.objects.filter()"
        shipment = list()
        for products in all_product:
            item = dict()
            item["PackageId"] = products.title()
            item["Quantity"] = products.title()
            item["Weight"] = products.title()
            item["ItemType"] = products.title()
            item["WeightRange"] = products.title()
            item["Name"] = products.title()
            item["Amount"] = products.title()
            item["ShipmentType"] = products.title()
            item["Description"] = products.title()
            item["ImageUrl"] = products.title()
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
        payload["PickupType"] = kwargs.get("")
        payload["PickupStationId"] = kwargs.get("")
        payload["DeliveryStationId"] = kwargs.get("")
        payload["PickupCity"] = kwargs.get("")
        payload["DeliveryCity"] = kwargs.get("")
        payload["ShipmentItems"] = shipment

        response = requests.request("POST", url, headers=header, data=payload).json()
        log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response




