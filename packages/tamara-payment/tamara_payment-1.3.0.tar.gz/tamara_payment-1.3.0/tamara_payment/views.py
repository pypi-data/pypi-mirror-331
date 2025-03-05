import logging

from django.http import Http404, JsonResponse
from django.views.generic import View
from django.template.response import TemplateResponse

from tamara_payment.commerce.checkout import CheckoutService
from tamara_payment.forms import TamaraForm
from tamara_payment.extensions import TamaraPayment


logger = logging.getLogger(__name__)


class TamaraPaymentView(View):
    checkout_service = CheckoutService()
    _tamara_payment = TamaraPayment()
    http_method_names = ["get"]

    def get(self, request):
        session_id = request.GET.get("sessionId")
        if not session_id:
            logging.exception("Missing sessionId")
            raise Http404

        data = self.checkout_service.get_pre_order_data(request)
        tamara_form = TamaraForm(
            initial={"data": data}
        )

        return TemplateResponse(
            request=request,
            template="tamara_payment.html",
            context={
                "action_url": f"{self._tamara_payment.url}/form-page?sessionId={session_id}",
                "action_method": "POST",
                "tamara_form": tamara_form,
            },
        )


class TamaraPaymentCheckAvailabilityView(View):
    checkout_service = CheckoutService()
    http_method_names = ["get"]
    _tamara_payment = TamaraPayment()

    def get(self, request):
        request_body = self.checkout_service.check_availability_request_body(request)
        is_available = self._tamara_payment.check_availability(request_body)
        return JsonResponse({"is_available": is_available})
