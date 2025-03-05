from django import forms


class DataForm(forms.Form):
    data = forms.CharField()
    hash = forms.CharField()
    salt = forms.CharField()

    def __init__(self, *args, **kwargs):
        kwargs["label_suffix"] = ""
        super().__init__(*args, **kwargs)
