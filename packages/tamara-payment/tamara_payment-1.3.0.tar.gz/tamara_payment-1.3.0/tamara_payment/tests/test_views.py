import django
from django.conf import settings
from django.http import Http404
from django.template.response import TemplateResponse
from django.test import SimpleTestCase
from django.test import override_settings
from django.test.client import RequestFactory
from mock.mock import patch
from rest_framework import status

from tamara_payment.tests.mixins import MockResponseMixin

if not settings.configured:
    settings.configure()


@override_settings(
    PZ_SERVICE_CLASS="tamara_payment.commerce.dummy.Service",
    TAMARA_EXTENSION_URL="http://example.com",
    HASH_SECRET_KEY="cgDywMThqhuxBOEEnjhfgeFGxBJZJJLa6Xc3WpqKn"
)
class TestTamaraPaymentRedirectView(SimpleTestCase, MockResponseMixin):
    def setUp(self):
        from tamara_payment.views import TamaraPaymentView
        django.setup()
        self.view = TamaraPaymentView
        self.request_factory = RequestFactory()

    @override_settings(TAMARA_EXTENSION_URL=None)
    def test_none_tamara_extension_url(self):
        request = self.request_factory.get("/payment-gateway/tamara/")
        request.GET = {"sessionid": "test-session-id"}
        with self.assertRaises(Http404):
            response = self.view.as_view()(request)

    @patch("tamara_payment.commerce.dummy.Service.get")
    def test_none_pre_order(self, mock_get):
        response = self._mock_response(
            status_code=200,
            content={},
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = response

        request = self.request_factory.get("/payment-gateway/tamara/")
        request.GET = {"sessionId": "test-session-id"}
        with self.assertRaises(Http404):
            self.view.as_view()(request)

    @patch("tamara_payment.commerce.dummy.Service.get")
    @patch("tamara_payment.commerce.checkout.CheckoutService.generate_hash")
    @patch("secrets.token_hex")
    def test_get(self, mock_token_hex, mock_generate_hash, mock_get):
        response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = response
        mock_generate_hash.return_value = "test-hash"
        mock_token_hex.return_value = "test-salt"

        request = self.request_factory.get("/payment-gateway/tamara/")
        request.GET = {"sessionId": "test-session-id"}
        response = self.view.as_view()(request)
        mock_generate_hash.assert_called_once_with("test-salt", "test-session-id")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "tamara_payment.html")

        context = response.context_data
        self.assertIn("tamara_form", context)
