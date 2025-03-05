from django.conf import settings
from django.template.response import TemplateResponse
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


@override_settings(
    TABBY_EXTENSION_URL="tabby/extension_url",
    PZ_SERVICE_CLASS="tabby_payment.commerce.dummy.Service",
    HASH_SECRET_KEY="hash_secret_key",
)
class TabbyExtensionRedirectViewTest(SimpleTestCase, MockResponseMixin):

    def setUp(self):
        self.request_factory = RequestFactory()

    @patch("tabby_payment.commerce.dummy.Service.get")
    def test_get(self, mock_get):
        from tabby_payment.views import TabbyExtensionRedirectView

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

        mock_get.side_effect = [orders_checkout_response,
                                user_orders_response,
                                user_success_orders_response,
                                user_profile_response]

        request = self.request_factory.get("/payment-gateway/tabby/")
        response = TabbyExtensionRedirectView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "tabby-extension-redirect-form.html")

        context = response.context_data
        self.assertIn("data_form", context)
