# ottu-py

## Installation

```bash
pip install git+https://github.com/ottuco/ottu-py.git@session-apis
```

# APIs

## Initialization

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key"
)
```

Alternatively, you can pass the `username` and `password` instead of `api_key`.

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    username="your-username",
    password="your-password"
)
```

APart from these (`host_url`, `api_key`, `username`, `password`), you can also pass the `customer_id`. This is used
while calling the checkout API and other situations.

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
```

## APIs

### Checkout (aka Session Create)

```python
from ottu import Ottu
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
response = ottu.checkout(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs","ottu_pg"],
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
It is also possible to use the `Session.create(...)` to create a new checkout session. That is, `ottu.checkout(...)` is an aliase for `ottu.session.create(...)` method.

```python
from ottu import Ottu
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
response = ottu.session.create(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs","ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    ...
)
print(response)
```
### Session Retrieve

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.retrieve(session_id="your-session-id")
print(response)
```

### Session Update

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.update(
    session_id="your-session-id",
    amount="1234.23",
)
print(response)
```

### Attachments (Special Case)

You can attach the file to session either while creating the session or updating the session using `attachment` argument.

`attachment` argument accepts string which represents the path to the file.
```python
from ottu import Ottu
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
ottu.session.create(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs","ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    attachment="path/to/file.pdf", # or "/path/to/file.pdf"
)
# update the session with updated attachment
response = ottu.session.update(
    attachment="path/to/file-1234.pdf", # or "/path/to/file
)
print(response)
```

### Accessing the payment methods

```python
from ottu import Ottu
from ottu.enums import TxnType

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
ottu.session.create(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs","ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    attachment="path/to/file.pdf", # or "/path/to/file.pdf"
)
print(ottu.session.payment_methods)
```

### Operations
All operartions are performed on the `ottu.session` object. Also, these methods accepts either `session_id` or `order_no` as an argument. If `session_id` is not passed, then it will use the `session_id` from the `ottu.session` object.

#### Cancel

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
ottu.session.retrieve(session_id="your-session-id")
response = ottu.session.cancel()
print(response)
```
 To specify the `session_id` while canceling the session, you can pass the `session_id` as an argument to the `cancel(...)` method.

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.cancel(session_id="your-session-id")
print(response)
```
To specify the `order_no` while canceling the session, you can pass the `order_no` as an argument to the `cancel(...)` method.

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.cancel(order_id="your-order-id")
print(response)
```

#### Expire

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.expire(session_id="your-session-id")
print(response)
```

#### Delete

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.delete(session_id="your-session-id")
print(response)
```

#### Capture

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.capture(session_id="your-session-id", amount="20.23")
print(response)
```

#### Refund

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.refund(session_id="your-session-id", amount="20.23")
print(response)
```

#### Void

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
)
response = ottu.session.void(session_id="your-session-id")
print(response)
```

### Cards

#### List all cards for a customer

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
response = ottu.cards.list(type="sandbox")
print(response)
```
### Get latest card for a customer

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
response = ottu.cards.get(type="sandbox")
print(response)
```

### Delete a card for a customer using token

```python
from ottu import Ottu

ottu = Ottu(
    merchant_id="merchant.id.ottu.dev",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
response = ottu.cards.delete(type="sandbox", token="your-card-token")
print(response)
```
