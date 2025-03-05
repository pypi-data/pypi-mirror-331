import json

from django.conf import settings
from django.test import SimpleTestCase
from django.test import override_settings
from django.test.client import RequestFactory
from mock.mock import patch
from rest_framework import status

from tabby_payment.tests.mixins import MockResponseMixin

try:
    settings.configure()
except RuntimeError:
    pass


@override_settings(PZ_SERVICE_CLASS="tabby_payment.commerce.dummy.Service")
class TestCheckoutService(SimpleTestCase, MockResponseMixin):
    def setUp(self):
        from tabby_payment.commerce.checkout import CheckoutService
        self.service = CheckoutService()
        self.request_factory = RequestFactory()

    @patch("tabby_payment.commerce.dummy.Service.get")
    def test_retrieve(self, mock_get):
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"}
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/tabby/")
        request_path = "/orders/checkout/?page=OrderNotePage"
        response = self.service.retrieve(request, request_path)
        self.assertIn("pre_order", response)

        request = self.request_factory.get("/payment-gateway/tabby/")
        request_path = "/orders/checkout/?page=OrderNotePage"
        response = self.service.retrieve(request, request_path, json_key="pre_order")
        self.assertIn("basket", response)

        request = self.request_factory.get("/payment-gateway/tabby/")
        request_path = "/orders/checkout/?page=OrderNotePage"
        response = self.service.retrieve(request, request_path, json_key="fake_key")
        self.assertEqual(response, {})

    @patch("tabby_payment.commerce.dummy.Service.get")
    def test_get_tabby_context(self, mock_get):
        orders_checkout_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"}
        )
        user_orders_response = self._mock_response(
            status_code=200,
            content=self._get_response("user_orders_response"),
            headers={"Content-Type": "application/json"}
        )
        user_success_orders_response = self._mock_response(
            status_code=200,
            content=self._get_response("user_success_orders_response"),
            headers={"Content-Type": "application/json"}
        )
        user_profile_response = self._mock_response(
            status_code=200,
            content=self._get_response("user_profile_response"),
            headers={"Content-Type": "application/json"}
        )

        mock_get.side_effect = [orders_checkout_response, user_orders_response, user_success_orders_response,
                                user_profile_response]

        checkout_response = self._get_response("orders_checkout_response")
        pre_order = json.loads(checkout_response)["pre_order"]

        request = self.request_factory.get("/payment-gateway/tabby/")
        tabby_context = self.service.get_tabby_context(request)

        address = tabby_context["shipping_address"]
        shipping_address = pre_order["shipping_address"]
        self.assertEqual(address["city"], shipping_address["city"]["name"])
        self.assertEqual(address["address"], shipping_address["line"])
        self.assertEqual(address["zip"], shipping_address["postcode"])

        orders = tabby_context["order_items"]
        basket_items = pre_order["basket"]["basketitem_set"]
        self.assertEqual(len(orders), len(basket_items))

        for order, basket_item in zip(orders, basket_items):
            self.assertEqual(order["unit_price"], basket_item["unit_price"])
            self.assertEqual(order["title"], basket_item["product"]["name"])
            self.assertEqual(order["quantity"], basket_item["quantity"])
            self.assertEqual(order["category"], basket_item["product"]["category"]["name"])

        self.assertEqual(tabby_context["buyer_history"], {"registered_since": "2023-07-14T14:09:02.239805Z",
        "loyalty_level": 3})

        orders_history = tabby_context["order_history"]
        self.assertEqual(len(orders_history), 10)
        order_history = orders_history[0]

        self.assertEqual(order_history["purchased_at"], "2023-07-26T11:27:09.319962Z")
        self.assertEqual(order_history["amount"], "11.24")
        self.assertEqual(order_history["status"], "new")

        self.assertEqual(order_history["buyer"]["name"], "akinon net")
        self.assertEqual(order_history["buyer"]["phone"], "+905111111111")
        self.assertEqual(order_history["buyer"]["email"], "akinon.test@akinon.com")

        self.assertEqual(order_history["shipping_address"]["city"], "İstanbul")
        self.assertEqual(order_history["shipping_address"]["address"], "teknopark")
        self.assertEqual(order_history["shipping_address"]["zip"], "34020")

        self.assertEqual(order_history["order_items"],[{"unit_price": "5.62",
                                                        "title": "Jf Serisi Vücut Losyonu 200 Ml",
                                                        "quantity": 2,
                                                        "category": "Vücut Losyonu"}] )