# ottu-py

## Installation

```bash
pip install git+https://github.com/ottuco/ottu-py.git@session-apis
```

# APIs

## Initialization

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key")
)
```

Alternatively, you can pass the `username` and `password` instead of `api_key`.

```python
from ottu import Ottu
from ottu.auth import BasicAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=BasicAuth(
        "your-username",
        "your-password"
    )
)
```

APart from these (`host_url`, `api_key`, `username`, `password`), you can also pass the `customer_id`. This is used
while calling the checkout API and other situations.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
```

## APIs

### Checkout (aka Session Create)

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.checkout(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs", "ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    ...
)
print(response)
```

**Response**

```
{
    "success": true,
    "status_code": 201,
    "endpoint": "/b/checkout/v1/pymt-txn/",
    "response": {
        "amount": "20.230",
        "checkout_url": "https://hotfix.ottu.dev/b/checkout/redirect/start/?session_id=809429a6c912990b195e4e60652436fcae587757",
        "currency_code": "KWD",
        "expiration_time": "00:50:00",
        "session_id": "809429a6c912990b195e4e60652436fcae587757",
        "type": "payment_request",
        ...
    },
    "error": {}
}
```

You can also access these `Session` attributes using `ottu.session` property.

```python
print(ottu.session.session_id)
# 809429a6c912990b195e4e60652436fcae587757

print(ottu.session.checkout_url)
# https://hotfix.ottu.dev/b/checkout/redirect/start/?session_id=809429a6c912990b195e4e60652436fcae587757
```

It is also possible to use the `Session.create(...)` to create a new checkout session. That is, `ottu.checkout(...)` is
an aliase for `ottu.session.create(...)` method.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.session.create(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs", "ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    ...
)
print(response)
```

### Session Retrieve

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.retrieve(session_id="your-session-id")
print(response)
```

### Session Update

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.update(
    session_id="your-session-id",
    amount="1234.23",
)
print(response)
```

### Attachments (Special Case)

You can attach the file to session either while creating the session or updating the session using `attachment`
argument.

`attachment` argument accepts string which represents the path to the file.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
ottu.session.create(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs", "ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    attachment="path/to/file.pdf",  # or "/path/to/file.pdf"
)
# update the session with updated attachment
response = ottu.session.update(
    attachment="path/to/file-1234.pdf",  # or "/path/to/file
)
print(response)
```

### Accessing the payment methods

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
ottu.session.create(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs", "ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    attachment="path/to/file.pdf",  # or "/path/to/file.pdf"
)
print(ottu.session.payment_methods)
```

### Operations

All operartions are performed on the `ottu.session` object. Also, these methods accepts either `session_id`
or `order_no` as an argument. If `session_id` is not passed, then it will use the `session_id` from the `ottu.session`
object.

#### Cancel

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
ottu.session.retrieve(session_id="your-session-id")
response = ottu.session.cancel()
print(response)
```

To specify the `session_id` while canceling the session, you can pass the `session_id` as an argument to
the `cancel(...)` method.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.cancel(session_id="your-session-id")
print(response)
```

To specify the `order_no` while canceling the session, you can pass the `order_no` as an argument to the `cancel(...)`
method.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.cancel(order_id="your-order-id")
print(response)
```

#### Expire

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.expire(session_id="your-session-id")
print(response)
```

#### Delete

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.delete(session_id="your-session-id")
print(response)
```

#### Capture

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.capture(session_id="your-session-id", amount="20.23")
print(response)
```

#### Refund

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.refund(session_id="your-session-id", amount="20.23")
print(response)
```

#### Void

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.session.void(session_id="your-session-id")
print(response)
```

### Cards

#### List all cards for a customer

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.cards.list(type="sandbox")
print(response)
```

### Get latest card for a customer

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.cards.get(type="sandbox")
print(response)
```

### Delete a card for a customer using token

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.cards.delete(type="sandbox", token="your-card-token")
print(response)
```

### Auto Debit

1. Get the PGs that supports auto debit.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)

res = ottu.get_payment_methods(plugin="payment_request", tokenizable=True)
print(res)
# {
#     "success": true,
#     "status_code": 200,
#     "endpoint": "/b/pbl/v2/payment-methods/",
#     "response": {
#         "customer_payment_methods": [],
#         "payment_methods": [
#             {
#                 "code": "ottu_pg_kwd_tkn",
#                 "name": "ottu_pg_kwd_tkn",
#                 "pg": "Ottu PG",
#                 "is_sandbox": true,
#                 "logo": "https://beta.ottu.net/media/gateway/settings/logos/Visa-MasterCard002_WIcgTQz.png",
#                 "wallets": [],
#                 "default_currency": "KWD",
#                 "accepted_currencies": [
#                     "KWD",
#                     "SAR",
#                     "BHD"
#                 ],
#                 "operation": "purchase",
#                 "operations": [
#                     "refund"
#                 ]
#             },
#             {
#                 "code": "auto-debit",
#                 "name": "auto-debit",
#                 "pg": "Ottu PG",
#                 "is_sandbox": true,
#                 "logo": "https://beta.ottu.net/static/images/pg_icons/master_visa.svg",
#                 "wallets": [],
#                 "default_currency": "KWD",
#                 "accepted_currencies": [
#                     "KWD"
#                 ],
#                 "operation": "purchase",
#                 "operations": [
#                     "refund"
#                 ]
#             }
#         ]
#     },
#     "error": {}
# }
```

2. Specify the PG code during the checkout

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)

response = ottu.auto_debit_checkout(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["ottu_pg_kwd_tkn"],  # code that matches your criteria (currency, etc.) from the above response
    customer_phone="+96550000000",
    order_no="1234567890",
    agreement={
        "id": "agreement-id-of-your-choice",
        # other agreement attributes
    },
)

print(response["response"]["checkout_url"])
```

3. Complete the checkout manually using the checkout URL.
4. Now, create the session whenever you want to charge the customer using the saved card.
    * Get the card token
       ```python
      from ottu import Ottu
      from ottu.auth import APIKeyAuth

       ottu = Ottu(
           merchant_id="merchant.id.ottu.dev",
           auth=APIKeyAuth("your-secret-api-key"),
           customer_id="your-customer-id"
       )

       response = ottu.cards.get(
          pg_codes=["ottu_pg_kwd_tkn"] # PG code that used while creating the session
       )
       print(response)
       # {
       #     "customer_id": "your-customer-id",
       #     "brand": "MASTERCARD",
       #     "name_on_card": "JPG",
       #     "number": "**** 0008",
       #     "expiry_month": "01",
       #     "expiry_year": "39",
       #     "token": "9597918463428402",
       #     "pg_code": "ottu_pg_kwd_tkn",
       #     "is_preferred": false,
       #     "is_expired": false,
       #     "will_expire_soon": false,
       #     "cvv_required": true,
       #     "agreements": [
       #         "agreement-id-of-your-choice"
       #     ]
       # }
       ```
    * Create new session (with same or different amount, depending on your use case)
       ```python
       response = ottu.auto_debit_checkout(
           txn_type=TxnType.PAYMENT_REQUEST,
           amount="20.23",
           currency_code="KWD",
           pg_codes=["ottu_pg_kwd_tkn"],
           customer_phone="+96550000000",
           order_no="1234567890",
           agreement={
               "id": "agreement-id-of-your-choice",
               # other agreement attributes
           },
       )

       print(response["response"]["session_id"])
       # 809429a6c912990b195e4e60652436fcae587757
       ```
    * Charge the customer using the saved card
       ```python
       response = ottu.auto_debit(
           session_id="809429a6c912990b195e4e60652436fcae587757", # value from previous step
           token ="9597918463428402", # value from previous step
       )
       print(response)
       ```

### Auto Debit (auto-flow)

You can call a single method to charge the customer using a saved card. The method will take care of the PG code and
tokenized card.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.auto_flow(
    is_sandbox=True,
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    customer_phone="+96550000000",
    order_no="1234567890",
    agreement={
        "id": "agreement-id-of-your-choice",
        # other agreement attributes
    },
)
```

The `.auto_flow(...)` method is _almost_ identical to the `.auto_debit_checkout(...)` method, except

* `pg_codes` is not required as it will be automatically determined.
* a new parameter called `is_sandbox` which indicates whether the tokenized card is from sandbox or production.

## Django Integration

Add `ottu.dj_ottu` to your `INSTALLED_APPS` setting.

```python
INSTALLED_APPS = [
    ...,
    "ottu.contrib.django",
    ...,
]
```

Set values for following settings variables.

### Settings

#### Authentication Settings

1. **Basic Authentication**
    * `DJ_OTTU_AUTH_USERNAME` - Username (example: `username`)
    * `DJ_OTTU_AUTH_PASSWORD` - Password (example: `my-secret-password`)
2. **API Key Authentication**
    * `DJ_OTTU_AUTH_API_KEY` - API Key (example: `my-secret-api-key`)

#### Other Settings

* `DJ_OTTU_MERCHANT_ID` - Merchant ID (example: `merchant.id.ottu.dev`)
* `DJ_OTTU_WEBHOOK_KEY` - Webhook Key (example: `my-secret-webhook-key`)
* `DJ_OTTU_WEBHOOK_URL` - Webhook URL (example: `https://your-host.com/path/to/view/`)

In case of authentication, it is mandatory to set any set of authentication settings.

### Checkout

```python
# any_module.py
from ottu.dj_ottu.ottu import dj_ottu

response = dj_ottu.checkout(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs", "ottu_pg"],
    customer_id="your-customer-id",
    customer_phone="+96550000000",
    order_no="1234567890",
    ...
)
```

**Note**: The checkout sessions will be automatically saved (and updated if you configure the webhooks) to the database
if you use the `dj_ottu` instance.

### Webhooks

To accept webhooks, you must set both `DJ_OTTU_WEBHOOK_KEY` and `DJ_OTTU_WEBHOOK_URL` settings variables. Also, you must
setup the webhook receiver view that comes with the package.

```python
# views.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ottu.dj_ottu.views import WebhookViewAbstractView


@method_decorator(csrf_exempt, name="dispatch")
class WebhookReceiverView(WebhookViewAbstractView):
    pass


# urls.py
from django.urls import path
from .views import WebhookReceiverView

urlpatterns = [
    path("wh-view/", WebhookReceiverView.as_view(), name="wh-view"),
]
```
### Miscellaneous

### Webhook Verification
You can verify the webhook signature using `verify_signature(...)` function.

```python
from ottu.utils import verify_signature

webhook_data_received = {
   "amount":"86.000",
   "currency_code":"KWD",
   "customer_first_name":"example-customer",
   ...,  # other attributes
   "signature":"6143b8ad4bd283540721ab000f6de746e722231aaaa90bc38f639081d3ff9f67"
}
verified = verify_signature(
   payload=webhook_data_received,
   signature=webhook_data_received["signature"], # Usually, signature will be sent along with the webhook data.
   webhook_key=hmac_secret_key_recieved_from_ottu # HMAC Secret Key received from Ottu
)
```
