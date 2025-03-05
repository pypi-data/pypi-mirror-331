from decimal import Decimal
import json

from unittest.mock import Mock
from django.http import Http404
from django.conf import settings
from django.test import SimpleTestCase
from django.test import override_settings
from django.test.client import RequestFactory
from mock.mock import patch
from rest_framework import status

from tamara_payment.tests.mixins import MockResponseMixin

try:
    settings.configure()
except RuntimeError:
    pass


@override_settings(
    HASH_SECRET_KEY="test-hash-secret-key",
    PZ_SERVICE_CLASS="tamara_payment.commerce.dummy.Service",
)
class TestCheckoutService(SimpleTestCase, MockResponseMixin):
    def setUp(self):
        from tamara_payment.commerce.checkout import CheckoutService

        self.service = CheckoutService()
        self.request_factory = RequestFactory()

    @patch("tamara_payment.commerce.dummy.Service.get")
    @patch("tamara_payment.commerce.checkout.CheckoutService.generate_hash")
    @patch("tamara_payment.commerce.checkout.CheckoutService.generate_salt")
    def test_get_data(self, mock_generate_salt, mock_generate_hash, mock_get):
        mock_generate_hash.return_value = "test-hash"
        mock_generate_salt.return_value = "test-salt"
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/tamara/")
        basket_data = self.service.get_pre_order_data(request)
        basket_data = json.loads(basket_data)

        self.assertEqual(basket_data["salt"], "test-salt")
        self.assertEqual(basket_data["hash"], "test-hash")

        self.assertEqual(basket_data["tax_amount"], {"amount": "37.92"})
        self.assertEqual(basket_data["shipping_amount"], {"amount": "33.00"})
        self.assertEqual(basket_data["shipping_address"], {
            "city": "İstanbul",
            "country_code": "TR",
            "first_name": "akinon",
            "last_name": "akinon",
            "line1": "YTÜ-Davutpaşa Kampüsü Teknopark Bölgesi B2 Blok D:Kat:2, No: 417",
            "phone_number": "0555555555",
            "region": "ESENLER"
        })
        self.assertEqual(basket_data["billing_address"], {
            "city": "İstanbul",
            "country_code": "TR",
            "first_name": "akinon",
            "last_name": "akinon",
            "line1": "YTÜ-Davutpaşa Kampüsü Teknopark Bölgesi B2 Blok D:Kat:2, No: 417",
            "phone_number": "0555555555",
            "region": "ESENLER"
        })

        basket_items = [
            {
                "name": "Petıt / 110x170cm Dijital Baskılı Halı",
                "type": "Halı",
                "reference_id": 923,
                "sku": "2672881033026",
                "quantity": 4,
                "total_amount": {
                    "amount": "224.76"
                }
            },
            {
                "name": "50cm Bombeli Saat Desen 13",
                "type": "Duvar Saatleri",
                "reference_id": 922,
                "sku": "2672880349036",
                "quantity": 2,
                "total_amount": {
                    "amount": "79.84"
                }
            },
            {
                "name": "Demet Lavanta Çiçek 62cm",
                "type": "Yapay Çiçek",
                "reference_id": 921,
                "sku": "2672881041106",
                "quantity": 3,
                "total_amount": {
                    "amount": "30.96"
                }
            }
        ]
        self.assertEqual(basket_data["order_items"],  basket_items)

    @patch("tamara_payment.commerce.dummy.Service.get")
    def test_retrieve_pre_oder(self, mock_get):
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/tamara/")
        response = self.service._retrieve_pre_order(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("pre_order", response.data)

    @patch("tamara_payment.commerce.dummy.Service.get")
    def test_get_basket_items(self, mock_get):
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/tamara/")
        request_body = self.service._get_order_data(request)

        self.assertEqual(request_body.total_tax_amount, "37.92")
        self.assertEqual(request_body.shipping_amount, "33.00")

        expected_basket_item = [
            {
                "name": "Petıt / 110x170cm Dijital Baskılı Halı",
                "type": "Halı",
                "reference_id": 923,
                "sku": "2672881033026",
                "quantity": 4,
                "total_amount": {
                    "amount": "224.76"
                }
            },
            {
                "name": "50cm Bombeli Saat Desen 13",
                "type": "Duvar Saatleri",
                "reference_id": 922,
                "sku": "2672880349036",
                "quantity": 2,
                "total_amount": {
                    "amount": "79.84"
                }
            },
            {
                "name": "Demet Lavanta Çiçek 62cm",
                "type": "Yapay Çiçek",
                "reference_id": 921,
                "sku": "2672881041106",
                "quantity": 3,
                "total_amount": {
                    "amount": "30.96"
                }
            }
        ]
        self.assertEqual(
            request_body.basket_items, expected_basket_item
        )
        self.assertNotEqual(request_body.shipping_address, None)
        self.assertNotEqual(request_body.billing_address, None)

    @patch("hashlib.sha512")
    def test_get_hash(self, mock_sha512):
        session_id = "test-session-id"
        self.service.generate_hash("test-salt", session_id)
        mock_sha512.assert_called_once_with(
            "test-salt|test-session-id|test-hash-secret-key".encode("utf-8")
        )

    @patch("secrets.token_hex")
    def test_generate_salt(self, mock_token_hex):
        self.service.generate_salt()
        mock_token_hex.assert_called_once()
        
    def test_get_product_name(self):
        product_name = None
        self.assertEqual(self.service._get_product_name(product_name), "none")
        
        product_name = "t" * 254
        self.assertEqual(self.service._get_product_name(product_name), product_name)
             
        product_name = "t" * 255
        self.assertEqual(self.service._get_product_name(product_name), product_name)
        
        product_name = "t" * 256
        self.assertEqual(self.service._get_product_name(product_name), "t" * 255)
        
    def test__find_decimal_places(self):
        self.assertEqual(self.service._find_decimal_places("10.000"), 3)
        self.assertEqual(self.service._find_decimal_places("10.00"), 2)
        self.assertEqual(self.service._find_decimal_places("10.0"), 1)
        self.assertEqual(self.service._find_decimal_places("10"), 0)
        
    def test__get_quantize_format(self):
        self.assertEqual(self.service._get_quantize_format("10.000"), Decimal(".001"))
        self.assertEqual(self.service._get_quantize_format("10.00"), Decimal(".01"))
        self.assertEqual(self.service._get_quantize_format("10.0"), Decimal(".1"))
        self.assertEqual(self.service._get_quantize_format("10"), Decimal("0"))
    
    def test__validate_checkout_step(self):
        mock_resp = Mock()
        mock_resp.data = {}
        
        with self.assertRaises(Http404):
            self.service._validate_checkout_step(mock_resp)
        
        mock_resp.data = {"pre_order": {"shipping_option": None}}
        with self.assertRaises(Http404):
            self.service._validate_checkout_step(mock_resp)

        mock_resp.data = {
            "context_list": [{"page_name": "ShippingOptionSelectionPage"}],
            "pre_order": {
                "shipping_option": {
                    "pk": 2,
                    "name": "Yurtici Kargo",
                    "slug": "yurtici",
                    "logo": None,
                    "shipping_amount": "9.99",
                    "description": None,
                    "kwargs": {}
                        }
                }
        }
        with self.assertRaises(Http404):
            self.service._validate_checkout_step(mock_resp)
            
        mock_resp.data = {
            "context_list": [{"page_name": "PaymentOptionSelectionPage"}],
            "pre_order": {
                "shipping_option": {
                    "pk": 2,
                    "name": "Yurtici Kargo",
                    "slug": "yurtici",
                    "logo": None,
                    "shipping_amount": "9.99",
                    "description": None,
                    "kwargs": {}
                },
                 "unpaid_amount": 10,
            },
        }
        self.service._validate_checkout_step(mock_resp)

    def test_shipping_address(self):
        _shipping_address = self.service._get_address({
              "pk": 50,
              "email": "akinon@akinon.com",
              "phone_number": "0555555555",
              "first_name": "akinon",
              "last_name": "akinon",
              "country": {
                  "pk": 1,
                  "name": "Türkiye",
                  "code": "tr"
              },
              "city": {
                  "pk": 47,
                  "name": "İstanbul",
                  "country": 1
              },
              "line": "YTÜ-Davutpaşa Kampüsü Teknopark Bölgesi B2 Blok D:Kat:2, No: 417",
              "title": "ofis",
              "township": {
                  "pk": 209,
                  "name": "ESENLER",
                  "city": 47
              },
              "district": {
                  "pk": 2194,
                  "name": "ÇİFTEHAVUZLAR/ESENLER",
                  "city": 47,
                  "township": 209
              },
              "postcode": "34220",
              "notes": None,
              "company_name": "",
              "tax_office": "",
              "tax_no": "",
              "e_bill_taxpayer": False,
              "is_corporate": False,
              "primary": False,
              "identity_number": None,
              "extra_field": None
        })
        self.assertEqual(_shipping_address, {
                "city": "İstanbul",
                "country_code": "TR",
                "first_name": "akinon",
                "last_name": "akinon",
                "line1": "YTÜ-Davutpaşa Kampüsü Teknopark Bölgesi B2 Blok D:Kat:2, No: 417",
                "phone_number": "0555555555",
                "region": "ESENLER"
            }
        )
