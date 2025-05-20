# ottu-py

[![PyPI version](https://img.shields.io/pypi/v/ottu-py.svg)](https://pypi.python.org/pypi/ottu-py)

## Installation

```bash
pip install ottu-py
```

For Django integration, use the following command.

```bash
pip install ottu-py[django]
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

Instead of `APIKeyAuth`, you can also use other authentication methods or your own custom auth classes. For more details, see [authentication](#authentication) section.


Apart from these `merchant_id` and `auth`, you can also pass the `customer_id` and `is_sandbox` values. This is used
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
#### Checkout API with dynamic argument(s)

Developers can pass any number of dynamic arguments to the `checkout(...)` method. The dynamic arguments will be passed to the API as it is.

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

    extra_name="John", # dynamic argument 1
    extra_age="25", # dynamic argument 2
    extra_country="Kuwait", # dynamic argument 3
)
print(response)
```
Here, `extra_name`, `extra_age`, and `extra_country` are the dynamic arguments which are not supported by the SDK, but may be supported by the API.
```python

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

`attachment` argument accepts a string that represents the path to the file.

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

All operations are performed on the `ottu.session` object. Also, these methods accept either `session_id`
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
response = ottu.session.capture(session_id="your-session-id", amount="20.23", tracking_key="your-tracking-key")
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
response = ottu.session.refund(session_id="your-session-id", amount="20.23", tracking_key="your-tracking-key")
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
response = ottu.session.void(session_id="your-session-id", tracking_key="your-tracking-key")
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
response = ottu.cards.list()
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
response = ottu.cards.get()
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
response = ottu.cards.delete(token="your-card-token")
print(response)
```


### Checkout Autoflow
Create a checkout session without specifying the PG codes. The PG codes will be automatically
selected based on the currency code, either from the cache or payment method API.

Behind the scenes, `ottu-py` will automatically fetch the payment methods from the cache or payment method API and
select the PG codes based on the currency code.
```python
from ottu import Ottu
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.checkout_autoflow(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
)
print(response)
```

### Auto-debit Autoflow
Completing the auto-debit transaction without specifying the PG codes. The PG codes will be automatically
selected based on the currency code from the payment method API. You must pass the value for `token` that represents the saved card token.

Behind the scenes, `ottu-py` will automatically fetch the token from the database (only if you use the Django integration) and
select the PG codes based on the currency code by calling the payment method API.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.auto_debit_autoflow(
   txn_type=TxnType.PAYMENT_REQUEST,
   amount="20.23",
   currency_code="KWD",
   token="your-card-token",
   agreement={
         "id": "test-agreement-id",
         # other agreement attributes
     },

)
print(response)
```

Optionally, you can pass the `pg_codes` to `auto_debit_autoflow(...)` method. If you pass the `pg_codes`, then the
`ottu-py` will not call the payment method API to fetch the PG codes.

```python
from ottu import Ottu
from ottu.auth import APIKeyAuth
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    customer_id="your-customer-id"
)
response = ottu.auto_debit_autoflow(
   txn_type=TxnType.PAYMENT_REQUEST,
   amount="20.23",
   currency_code="KWD",
   token="your-card-token",
   pg_codes=["ottu_pg"],
   agreement={
      "id": "test-agreement-id",
      # other agreement attributes
   },

)
print(response)
```

## Django Integration

Add `ottu.contrib.django` to your `INSTALLED_APPS` setting.

```python
INSTALLED_APPS = [
    ...,
    "ottu.contrib.django",
    ...,
]
```

Set values for the following settings variables.

### Settings

#### Authentication Settings

`OTTU_AUTH` - The variable `OTTU_AUTH` is a dictionary that represents the authentication settings. It should contain mandatory field named `class` which represents the _dotted path_ to the authentication class.
`OTTU_AUTH` can also contain other fields that are required by the authentication class.

```python
# settings.py

OTTU_AUTH = {
    "class": "ottu.auth.BasicAuth",
    "username": "dj_username",
    "password": "dj_password",
}
```
OR
```python
# settings.py

OTTU_AUTH = {
    "class": "ottu.auth.APIKeyAuth",
    "api_key": "my-api-key",
}
```
#### Other Settings

* `OTTU_MERCHANT_ID` - Merchant ID (example: `merchant.id.ottu.dev`)
* `OTTU_WEBHOOK_KEY` - Webhook Key (example: `my-secret-webhook-key`)
* `OTTU_WEBHOOK_URL` - Webhook URL (example: `https://your-host.com/path/to/view/`)
* `OTTU_IS_SANDBOX` - Sandbox environment or not (example: `True` or `False`). Default is `False`.

In the case of authentication, it is mandatory to set any set of authentication settings.

### Checkout

```python
# any_module.py
from ottu.contrib.django.core.ottu import ottu

response = ottu.checkout(
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
if you use the `ottu` instance.

### Auto-debit Autoflow
Same as [Auto-debit Autoflow](#auto-debit-autoflow) but it is optional to pass the `token`. If you don't pass the `token`, `ottu-py` will automatically fetch the token from the DB. The token is identified by the `customer_id` and `agreement.id`.
```python
from ottu.contrib.django.core.ottu import ottu

response = ottu.auto_debit_autoflow(
      txn_type=TxnType.PAYMENT_REQUEST,
      amount="20.23",
      currency_code="KWD",
      customer_id="your-customer-id",
      agreement={
            "id": "test-agreement-id",
            # other agreement attributes
        },
      ...
)
```

### Webhooks

To accept webhooks, you must set both `OTTU_WEBHOOK_KEY` and `OTTU_WEBHOOK_URL` settings variables. Also, you must
setup the webhook receiver view that comes with the package.

```python
# views.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ottu.contrib.django.views import WebhookViewAbstractView


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

### Authentication

The `ottu-py` supports a few authentication methods, usually suitable in most of the cases. `BasicAuth`, `APIKeyAuth`, `KeycloakPasswordAuth` and `KeycloakClientAuth` are the available authentication methods.
* `BasicAuth` - Basic authentication, using `username` and `password`.
   ```python
   from ottu import Ottu
   from ottu.auth import BasicAuth

   ottu = Ottu(
       merchant_id="merchant.id.ottu.dev",
       auth=BasicAuth(
           username="your-username",
           password="your-password"
       )
   )
   ```
* `BasicAuthorizationHeaderAuth` - Basic auth setup for header based authentication. You can pass the entire`Authorization` header value into the constructor.
  ```python
  from ottu import Ottu
  from ottu.auth import BasicAuthorizationHeaderAuth

  token = "Your-Token-Here"
  ottu = Ottu(
      merchant_id="merchant.id.ottu.dev",
      auth=BasicAuthorizationHeaderAuth(
          header=f"Token {token}"
      )
  )
  ```
* `TokenAuth` - Same as `BasicAuthorizationHeaderAuth`, but, the constructor accepts the token and prefix as separate arguments. This is useful when you want to use a different prefix than `Token`.
  ```python
  from ottu import Ottu
  from ottu.auth import TokenAuth

  token = "Your-Token-Here"
  ottu = Ottu(
      merchant_id="merchant.id.ottu.dev",
      auth=TokenAuth(
          token=token,
          prefix="Token",
      )
  )
  ```
* `APIKeyAuth` - Authentication using API Key. This is also same as `TokenAuth` but, constructor accepts the `api_key` instead of `token`.
   ```python
   from ottu import Ottu
   from ottu.auth import APIKeyAuth

   ottu = Ottu(
       merchant_id="merchant.id.ottu.dev",
       auth=APIKeyAuth(
          api_key="your-api-key"
       )
   )
   ```
* `KeycloakPasswordAuth` - Authentication using Keycloak using `password` grant type.
   ```python
   from ottu import Ottu
   from ottu.auth import KeycloakPasswordAuth

   ottu = Ottu(
       merchant_id="merchant.id.ottu.dev",
       auth=KeycloakPasswordAuth(
            username="your-username",
            password="your-password",
            client_id="your-client-id",
       )
   )
   ```
  You may also need to supply `client_secret` if it is required by the Keycloak server.
    ```python
    from ottu import Ottu
    from ottu.auth import KeycloakPasswordAuth

    ottu = Ottu(
        merchant_id="merchant.id.ottu.dev",
        auth=KeycloakPasswordAuth(
            username="your-username",
            password="your-password",
            client_id="your-client-id",
            client_secret="your-client-secret"
        )
    )
    ```
* `KeycloakClientAuth` - Authentication using Keycloak using `client_credentials` grant type.
    ```python
    from ottu import Ottu
    from ottu.auth import KeycloakClientAuth

    ottu = Ottu(
        merchant_id="merchant.id.ottu.dev",
        auth=KeycloakClientAuth(
            client_id="your-client-id",
            client_secret="your-client-secret"
        )
    )
    ```
### Payment Methods
You can call the `Ottu.get_payment_methods(...)` method to get the available payment methods for the given merchant.
```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
response = ottu.get_payment_methods(
    plugin="payment_request",
    currencies=["KWD", "USD"],
    customer_id="your-customer-id",
    operation="purchase",
    tokenizable=False,
    pg_names=[]
)
print(response)
```

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

### API Response Structure

All API calls must have the following structure.

```json
{
   "success": true,
   "status_code": 200,
   "endpoint": "/path/to/api/endpoint/",
   "response": {},
   "error": {}
}
```
* `success` - Boolean value that represents the success of the API call.
* `status_code` - HTTP status code of the API call.
* `endpoint` - API endpoint of the last API call.
* `response` - Response from the API call.
* `error` - Error from the API call.

If the call was `success`, the `response` field will be present and the `error` field will be empty, and vice-versa.

In most of the cases, the `error` will be a JSON object with a key of `detail` and value of the error message.

```json
{
   "success": false,
   "status_code": 400,
   "endpoint": "/path/to/api/endpoint/",
   "response": {},
   "error": {
      "detail": "Error message"
   }
}
```
### Timeout

You can set the `timeout` value for all requests made by the SDK. The default value is `30` seconds.

**Method 1** - Set the timeout value while initializing the `Ottu` object.
```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
    timeout=60 # Set the timeout to 60 seconds
)
```

**Method 2** - Set the timeout value using the `timeout` property.
```python
from ottu import Ottu
from ottu.auth import APIKeyAuth

class MyOttu(Ottu):
  default_timeout = 50 # Set the default timeout to 50 seconds

ottu = MyOttu(
    merchant_id="merchant.id.ottu.dev",
    auth=APIKeyAuth("your-secret-api-key"),
)
```

**Note:** The timeout value set using the `timeout` parameter will override the value set by the `default_timeout` attribute.


## Test

```bash
# Install the dependencies
pip install .[test]

# Run tests
python -m pytest
```

## Release
```base
# do a dry-run first -
bump2version --dry-run --verbose [major|minor|patch]

# if everything looks good, run the following command to release
bump2version --verbose [major|minor|patch]

# push the changes to remote
git push origin master --tags
```
