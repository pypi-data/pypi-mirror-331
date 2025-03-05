from django.conf.urls import url

from garantipay_payment.views import GarantiPayView

urlpatterns = [
    url(r"^$", GarantiPayView.as_view(), name="garantipay-payment"),
]
