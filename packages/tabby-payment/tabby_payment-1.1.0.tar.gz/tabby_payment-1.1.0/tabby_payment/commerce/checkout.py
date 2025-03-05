from importlib import import_module
import hashlib
from django.conf import settings
from tabby_payment.commerce.enums import OrderServiceStatus, OrderCommerceStatus


module, _class = settings.PZ_SERVICE_CLASS.rsplit(".", 1)

Service = getattr(import_module(module), _class)


class   CheckoutService(Service):
    def retrieve(self, request, path, json_key=None):
        response = self.get(path, request=request, headers={"X-Requested-With": "XMLHttpRequest"})
        normalize_response = self.normalize_response(response)
        if not json_key:
            return normalize_response.data
        return normalize_response.data.get(json_key, {})

    @staticmethod
    def generate_hash(session_id, salt):
        hash_key = settings.HASH_SECRET_KEY
        hash_str = f"{salt}|{session_id}|{hash_key}"
        return hashlib.sha512(hash_str.encode("utf-8")).hexdigest()

    @staticmethod
    def _get_order_status(commerce_order_status_value):
        order_status = OrderServiceStatus.unknown
        if commerce_order_status_value in [OrderCommerceStatus.waiting.value,
                                     OrderCommerceStatus.payment_waiting.value,
                                     OrderCommerceStatus.confirmation_waiting.value]:
            order_status = OrderServiceStatus.new
        elif commerce_order_status_value in [OrderCommerceStatus.approved.value,
                                       OrderCommerceStatus.preparing.value,
                                       OrderCommerceStatus.shipped.value,
                                       OrderCommerceStatus.shipped_and_informed.value,
                                       OrderCommerceStatus.ready_for_pickup.value,
                                       OrderCommerceStatus.attempted_delivery.value]:
            order_status = OrderServiceStatus.PROCESSING
        elif commerce_order_status_value == OrderCommerceStatus.delivered.value:
            order_status = OrderServiceStatus.COMPLETE
        elif commerce_order_status_value == OrderCommerceStatus.refunded.value:
            order_status = OrderServiceStatus.REFUNDED
        elif commerce_order_status_value == OrderCommerceStatus.cancelled.value:
            order_status = OrderServiceStatus.CANCELED
        return order_status.value

    @staticmethod
    def __group_by_product_id(order_items):
        grouped_order_items = {}
        for order_item in order_items:
            product_id = order_item["product"]["pk"]
            if product_id in grouped_order_items:
                grouped_order_items[product_id]["quantity"] += 1
            else:
                grouped_order_items[product_id] = {
                    "unit_price": order_item["price"],
                    "title": order_item["product"]["name"],
                    "quantity": 1,
                    "category": order_item["product"]["category"]["name"],
                }
        return list(grouped_order_items.values())

    def get_tabby_context(self, request):
        order_not_page_path = "/orders/checkout/?page=OrderNotePage"
        pre_order = self.retrieve(request, order_not_page_path, json_key="pre_order")

        order_history_path = "/users/orders/?limit=10"
        orders_history = self.retrieve(request, order_history_path, json_key="results")

        success_orders_history_path = "/users/orders/?limit=1&status=550"
        success_orders_count = self.retrieve(request,
                                             success_orders_history_path,
                                             json_key="count")

        user_profile_path = "/users/profile/"
        user_date_joined = self.retrieve(request, user_profile_path, json_key="date_joined")

        context = {
            "shipping_address": {
                "city": pre_order["shipping_address"]["city"]["name"],
                "address": pre_order["shipping_address"]["line"],
                "zip": pre_order["shipping_address"]["postcode"],
            },
            "order_items": [
                {
                    "unit_price": item["unit_price"],
                    "title": item["product"]["name"],
                    "quantity": item["quantity"],
                    "category": item["product"]["category"]["name"],
                }
                for item in pre_order["basket"]["basketitem_set"]
            ],
            "buyer_history": {
               "registered_since": user_date_joined,
               "loyalty_level": success_orders_count,
            },
            "order_history": [
                {
                    "purchased_at": order_history["created_date"],
                    "amount": order_history["amount"],
                    "status": self._get_order_status(order_history["status"]["value"]),
                    "buyer": {
                        "phone": order_history["billing_address"]["phone_number"],
                        "email": order_history["billing_address"]["email"],
                        "name": (
                            f"{order_history['billing_address']['first_name']} "
                            f"{order_history['billing_address']['last_name']}"
                        ),
                    },
                    "shipping_address": {
                        "city": order_history["shipping_address"]["city"]["name"],
                        "address": order_history["shipping_address"]["line"],
                        "zip": order_history["shipping_address"]["postcode"],
                    },
                    "order_items": self.__group_by_product_id(order_history["orderitem_set"]),
                }
                for order_history in orders_history
            ]
        }

        return context
