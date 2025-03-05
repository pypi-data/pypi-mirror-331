from django.conf.urls import url


from tamara_payment.views import TamaraPaymentView, TamaraPaymentCheckAvailabilityView

urlpatterns = [
    url("check-availability/", TamaraPaymentCheckAvailabilityView.as_view(), name="check-availability"),
    url(r"^$", TamaraPaymentView.as_view(), name="tamara-payment"),
]
