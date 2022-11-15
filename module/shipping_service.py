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
        header = cls.get_header()
        url = f"{base_url}/operations/stateInfo?StateName={kwargs.get('state_name')}"
        if kwargs.get('city_name'):
            url = f"{base_url}/operations/stateInfo?StateName={kwargs.get('state_name')}&CityName={kwargs.get('city_name')}"

        response = requests.request("GET", url, headers=header).json()
        log_request(f"url: {url}", f"headers: {header}", f"response: {response}")
        return response

    @classmethod
    def get_all_states(cls):
        header = cls.get_header()
        url = f"{base_url}/operations/states"
        response = requests.request("GET", url, headers=header).json()
        log_request(f"url: {url}", f"headers: {header}", f"response: {response}")
        return response

    @classmethod
    def rating(cls, **kwargs):
        header = cls.get_header()

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
            # merchant["DeliveryCoordinate"]["Latitude"] = customer_address.latitude
            # merchant["DeliveryCoordinate"]["Longitude"] = customer_address.longitude
            merchant["DeliveryState"] = customer_address.state
            merchant["DeliveryStationId"] = 4
            merchant["DeliveryCity"] = customer_address.city
            merchant["Items"] = shipment
            shipment_information.append(merchant)

            prod_weight = 0
            uid = ""
            total_item_weight = list()

            for product in seller_products:
                item = dict()
                quantity = product.get('quantity')
                uid = product.get('cart_product_id')
                weight = product.get("weight")
                price = product.get("price")
                description = product.get("detail")
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
                item["Description"] = description
                total_item_weight.append(prod_weight)
                shipment.append(item)

            merchant_order_weight = sum(total_item_weight)
            merchant["Id"] = uid
            merchant["TotalWeight"] = merchant_order_weight
            overall_weight.append(merchant_order_weight)

        payload["TotalWeight"] = sum(overall_weight)
        payload = json.dumps(payload)

        url = f"{base_url}/operations/quote"

        response = requests.request("POST", url, data=payload, headers=header).json()
        log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response

    @classmethod
    def get_shippers(cls):
        header = cls.get_header()
        url = f"{base_url}/operations/shippers"
        response = requests.request("GET", url, headers=header).json()
        log_request(f"url: {url}", f"headers: {header}", f"response: {response}")
        return response

    @classmethod
    def pickup(cls, **kwargs):
        header = cls.get_header()

        pickup_date = datetime.datetime.today().date() + datetime.timedelta(days=2)
        pickup_time = datetime.datetime.now().time()

        order_product = kwargs.get("order_product")
        address = kwargs.get("address")
        order_number = f"PAYMALL-{order_product.order_id}{order_product.id}"
        seller = order_product.product_detail.product.store.seller
        customer = order_product.order.customer

        shipment_information = list()
        shipment = list()
        payload = dict()

        payload["ShipmentInformation"] = shipment_information
        payload["Summary"] = kwargs.get("order_summary")

        detail = dict()
        detail["ShipperName"] = order_product.shipper_name
        detail["OrderNo"] = order_number
        detail["CompanyId"] = order_product.company_id
        detail["Summary"] = order_product.product_detail.description
        detail["DeliveryRequestedTime"] = "06 AM to 09 PM"
        detail["PickupTime"] = str(pickup_time)
        detail["PickupDate"] = str(pickup_date)
        detail["PickupCoordinate"] = dict()
        detail["PickupCoordinate"]["Latitude"] = 6.639438
        detail["PickupCoordinate"]["Longitude"] = 3.330983
        # detail["PickupCoordinate"]["Latitude"] = seller.latitude
        # detail["PickupCoordinate"]["Longitude"] = seller.longitude
        detail["PickUpLandmark"] = seller.town
        detail["PickupAddress"] = seller.get_full_address()
        detail["SenderNumber"] = seller.phone_number
        detail["SenderName"] = seller.user.get_full_name()
        detail["SenderEmail"] = seller.user.email
        detail["RecipientEmail"] = customer.user.email
        detail["DeliveryAddress"] = address.get_full_address()
        detail["DeliveryCoordinate"] = dict()
        detail["DeliveryCoordinate"]["Latitude"] = 6.5483777
        detail["DeliveryCoordinate"]["Longitude"] = 3.3883414
        # detail["DeliveryCoordinate"]["Latitude"] = address.latitude
        # detail["DeliveryCoordinate"]["Longitude"] = address.longitude
        detail["DeliveryType"] = "Normal"
        detail["DeliveryTime"] = "4 AM to 7 PM"
        detail["ReceiverPhoneNumber"] = customer.phone_number
        detail["ReceiverName"] = customer.user.get_full_name()
        detail["PickupState"] = seller.state
        detail["DeliveryState"] = address.state
        detail["TotalWeight"] = order_product.product_detail.weight
        detail["PickupStationId"] = 4
        detail["DeliveryStationId"] = 4
        detail["SenderTownId"] = kwargs.get("sender_town_id")
        detail["ReceiverTownId"] = kwargs.get("receiver_town_id")
        detail["PickupCity"] = seller.city
        detail["DeliveryCity"] = address.city

        shipment_item = dict()
        shipment_item["PackageId"] = order_product.id
        shipment_item["IsDelivered"] = 0
        shipment_item["Name"] = order_product.product_detail.product.name
        shipment_item["Quantity"] = order_product.quantity
        shipment_item["Color"] = order_product.product_detail.color
        shipment_item["Size"] = order_product.product_detail.size
        shipment_item["Description"] = order_product.product_detail.description
        shipment_item["Distance"] = 5
        shipment_item["WeightRange"] = 0
        shipment_item["Weight"] = order_product.product_detail.weight
        shipment_item["Amount"] = float(order_product.total)
        shipment_item["ItemType"] = "Normal"
        shipment_item["ShipmentType"] = "Regular"
        shipment_item["PickUpGooglePlaceAddress"] = seller.get_full_address()
        shipment_item["DeliveryContactName"] = customer.user.get_full_name()
        shipment_item["DeliveryContactNumber"] = customer.phone_number
        shipment_item["DeliveryGooglePlaceAddress"] = address.get_full_address()
        shipment_item["DeliveryLandmark"] = address.town
        shipment_item["DeliveryState"] = address.state
        shipment_item["DeliveryCity"] = address.city
        shipment_item["PickupState"] = seller.state
        shipment_item["PickupCity"] = seller.city
        shipment.append(shipment_item)

        detail["ShipmentItems"] = shipment
        shipment_information.append(detail)

        payload = json.dumps(payload)

        url = f"{base_url}/operations/bookOrders"

        response = requests.request("POST", url, data=payload, headers=header).json()
        log_request(f"url: {url}", f"payload: {payload}", f"response: {response}")
        return response









