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
        header = cls.get_header()
        customer = kwargs.get('customer')
        # payment_mode = kwargs.get('payment_mode')

        pickup_date = datetime.datetime.today().date() + datetime.timedelta(days=2)
        pickup_time = datetime.datetime.now().time()
        seller_prods = kwargs.get("sellers")
        customer = kwargs.get("customer")
        customer_address = kwargs.get("customer_address")

        shipment_information = list()
        payload = dict()

        overall_weight = list()
        payload["ShipmentInformation"] = shipment_information

        for order_prod in seller_prods:
            seller = order_prod["seller"]
            seller_products = order_prod["products"]
            shipment = list()

            merchant = dict()

            merchant["PickupAddress"] = seller.get_full_address()
            merchant["PickupCoordinate"] = dict()
            merchant["PickupCoordinate"]["Latitude"] = 6.639438
            merchant["PickupCoordinate"]["Longitude"] = 3.330983
            # merchant["PickupCoordinate"]["Latitude"] = seller.latitude
            # merchant["PickupCoordinate"]["Longitude"] = seller.longitude
            merchant["PickupTime"] = str(pickup_time)
            merchant["PickupDate"] = str(pickup_date)
            merchant["PickupCity"] = seller.city
            merchant["PickupState"] = seller.state
            merchant["PickupStationId"] = 4
            merchant["SenderNumber"] = seller.phone_number
            merchant["SenderName"] = seller.user.get_full_name()
            merchant["ReceiverName"] = customer.user.get_full_name()
            merchant["ReceiverPhoneNumber"] = customer.phone_number
            merchant["DeliveryAddress"] = customer_address.get_full_address()
            merchant["DeliveryCoordinate"] = dict()
            merchant["DeliveryCoordinate"]["Latitude"] = 6.5483777
            merchant["DeliveryCoordinate"]["Longitude"] = 3.3883414
            merchant["DeliveryState"] = customer_address.state
            merchant["DeliveryStationId"] = 4
            merchant["DeliveryCity"] = customer_address.city
            merchant["Items"] = shipment
            shipment_information.append(merchant)

            prod_weight = 0
            total_item_weight = list()

            for product in seller_products:
                item = dict()
                quantity = product.get('quantity')
                weight = product.get("weight")
                price = product.get("price")
                amount = (price * quantity)
                prod_weight += (weight * quantity)
                prod = product.get("product")

                item["PackageId"] = prod.id
                item["Quantity"] = quantity
                item["Weight"] = prod_weight
                item["ItemType"] = "Normal"
                item["Name"] = prod.name
                item["Amount"] = float(amount)
                item["ShipmentType"] = "Regular"
                total_item_weight.append(prod_weight)
                shipment.append(item)

            merchant_order_weight = sum(total_item_weight)
            merchant["TotalWeight"] = merchant_order_weight
            overall_weight.append(merchant_order_weight)
        payload["TotalWeight"] = sum(overall_weight)

        url = f"{base_url}/operations/quote"

        payload = json.dumps(payload)

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





