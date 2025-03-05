# Tabby Redirect View

This app provides order related data to the Tabby payment extension when plugged-in to project zero.

## Installation

Add the package to requirements.txt file and install it via pip:

    tabby-payment

## Adding App

Add the following lines in `omnife_base.settings`:

    INSTALLED_APPS.append('tabby_payment')
    TABBY_EXTENSION_URL = 'https://extension-url.akinon.net/'
    PZ_SERVICE_CLASS = "omnife.core.service.Service"
    HASH_SECRET_KEY = "your-hash-secret-key"

Add url pattern to `omnife_base.urls` like below:

    urlpatterns = [
        ...
        path('payment-gateway/tabby/', include('tabby_payment.urls')),
    ]

## Running Tests

    python -m unittest discover

## Python Version Compatibility

This package is compatible with the following Python versions:
  - Python 3.8
  - Python 3.9