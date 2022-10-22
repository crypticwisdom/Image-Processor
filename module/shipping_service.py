import datetime
import json

import requests
from django.conf import settings
from django.db.models import Sum

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
        # header = cls.get_header()
        # customer = kwargs.get('customer')
        # payment_mode = kwargs.get('payment_mode')

        pickup_date = datetime.datetime.today().date() + datetime.timedelta(days=2)
        pickup_time = datetime.datetime.now().time()
        seller = kwargs.get("seller")
        customer = kwargs.get("customer")
        customer_address = kwargs.get("customer_address")

        shipment = list()

        prod_weight = 0
        for product in kwargs.get("seller_prods"):
            quantity = product.get('quantity')
            weight = product.get("weight")
            price = product.get("price")
            prod_weight += (weight * quantity)
            prod = product.get("product")

            item = dict()
            item["PackageId"] = prod.id
            item["Quantity"] = quantity
            item["Weight"] = prod_weight
            item["ItemType"] = "Normal"
            # item["WeightRange"] = products.title()
            item["Name"] = prod.name
            item["Amount"] = 1000
            item["ShipmentType"] = "Regular"
            shipment.append(item)

        url = f"{base_url}/operations/quote"

        total_item_weight = list()
        for data in shipment:
            total_item_weight.append(data["Weight"])

        total_weight = sum(total_item_weight)

        payload = dict()
        # payload["PaymentMode"] = payment_mode
        # payload["Vehicle"] = kwargs.get("")
        payload["PickupTime"] = str(pickup_time)
        payload["PickupDate"] = str(pickup_date)
        payload["PickupLatitude"] = 6.639438
        payload["PickupLongitude"] = 3.330983
        # payload["PickupLatitude"] = seller.latitude
        # payload["PickupLongitude"] = seller.longitude
        payload["PickupAddress"] = seller.get_full_address()
        payload["SenderPhoneNumber"] = seller.phone_number
        payload["SenderName"] = seller.user.get_full_name()
        payload["ReceiverName"] = customer.user.get_full_name()
        payload["DeliveryAddress"] = customer_address.get_full_address()
        payload["DeliveryLatitude"] = 6.5483777
        payload["DeliveryLongitude"] = 3.3883414
        # payload["DeliveryLatitude"] = customer_address.latitude
        # payload["DeliveryLongitude"] = customer_address.longitude
        payload["ReceiverPhoneNumber"] = customer.phone_number
        payload["PickupState"] = seller.state
        payload["DeliveryState"] = customer_address.state
        payload["TotalWeight"] = total_weight
        # payload["InstantDelivery"] = 0
        # StationID to be implemented later
        payload["PickupStationId"] = 4
        payload["DeliveryStationId"] = 4
        ##################################
        payload["PickupCity"] = seller.city
        payload["DeliveryCity"] = customer_address.city
        payload["ShipmentItems"] = shipment

        payload = json.dumps(payload)

        # response = requests.request("POST", url, headers=header, data=payload).json()
        response = requests.request("POST", url, data=payload, headers={"Content-Type": "application/json"}).json()
        log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response

    @classmethod
    def get_shippers(cls):
        # header = cls.get_header()
        # url = f"{base_url}/operations/shippers"
        # response = requests.request("GET", url).json()
        # response = requests.request("GET", url, headers=header).json()
        response = [{"Id": "9", "Name": "Dellyman"}, {"Id": "1", "Name": "Gig Logistics"}, {"Id": "7", "Name": "Redstar"}]
        # log_request(f"url: {url}", f"response: {response}")
        # log_request(f"url: {url}", f"headers: {header}", f"response: {response}")
        return response





