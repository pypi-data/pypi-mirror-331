from django.conf.urls import url

from tabby_payment.views import TabbyExtensionRedirectView

urlpatterns = [
    url(r"^$", TabbyExtensionRedirectView.as_view(), name="tabby-payment"),
]
