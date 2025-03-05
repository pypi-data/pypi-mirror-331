import hashlib
import uuid

from django.conf import settings
from django.forms import formset_factory
from django.template.response import TemplateResponse
from django.views.generic import View

from tabby_payment.commerce.checkout import CheckoutService
from tabby_payment.forms import DataForm


class TabbyExtensionRedirectView(View):
    checkout_service = CheckoutService()

    def get(self, request):
        context = self.checkout_service.get_tabby_context(request)
        session_id = request.GET.get("sessionId")

        salt = uuid.uuid4().hex[:10]
        _hash = self.checkout_service.generate_hash(session_id=session_id,
                                                    salt=salt)
        context.update({"hash": _hash, "salt": salt})

        data_form = DataForm(initial={"data": context, "hash": _hash, "salt": salt})
        result_context = {
            "action_url": f"{settings.TABBY_EXTENSION_URL}?sessionId={session_id}",
            "action_method": "POST",
            "data_form": data_form,
        }
        return TemplateResponse(
            request=request,
            template="tabby-extension-redirect-form.html",
            context=result_context
        )
