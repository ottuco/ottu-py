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
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key"
)
```

Alternatively, you can pass the `username` and `password` instead of `api_key`.

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    username="your-username",
    password="your-password"
)
```

APart from these (`host_url`, `api_key`, `username`, `password`), you can also pass the `customer_id`. This is used
while calling the checkout API and other situations.

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
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
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
session = ottu.checkout(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs","ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    ...
)
print(session)
```
It is also possible to use the `Session.create(...)` to create a new checkout session. That is, `ottu.checkout(...)` is an aliase for `ottu.session.create(...)` method.

```python
from ottu import Ottu
from ottu.enums import TxnType

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
session = ottu.session.create(
    txn_type=TxnType.PAYMENT_REQUEST,
    amount="20.23",
    currency_code="KWD",
    pg_codes=["mpgs","ottu_pg"],
    customer_phone="+96550000000",
    order_no="1234567890",
    ...
)
print(session)
```
### Session Retrieve

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
session = ottu.session.retrieve(session_id="your-session-id")
print(session)

# or you can just use `ottu.session` as a property
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.retrieve(session_id="your-session-id")
print(ottu.session)
```

### Session Update

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
session = ottu.session.update(
    session_id="your-session-id",
    amount="1234.23",
)
print(session) # or `print(ottu.session)`
```

### Attachments (Special Case)

You can attach the file to session either while creating the session or updating the session using `attachment` argument.

`attachment` argument accepts string which represents the path to the file.
```python
from ottu import Ottu
from ottu.enums import TxnType

ottu = Ottu(
    host_url="https://sub.domain.com",
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
ottu.session.update(
    attachment="path/to/file-1234.pdf", # or "/path/to/file
)
```

### Accessing the payment methods

```python
from ottu import Ottu
from ottu.enums import TxnType

ottu = Ottu(
    host_url="https://sub.domain.com",
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
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.retrieve(session_id="your-session-id")
ottu.session.cancel()
```
 To specify the `session_id` while canceling the session, you can pass the `session_id` as an argument to the `cancel(...)` method.

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.cancel(session_id="your-session-id")
```
To specify the `order_no` while canceling the session, you can pass the `order_no` as an argument to the `cancel(...)` method.

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.cancel(order_id="your-order-id")
```

#### Expire

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.expire(session_id="your-session-id")
```

#### Delete

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.delete(session_id="your-session-id")
```

#### Capture

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.capture(session_id="your-session-id", amount="20.23")
```

#### Refund

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.refund(session_id="your-session-id", amount="20.23")
```

#### Void

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
)
ottu.session.void(session_id="your-session-id", amount="20.23")
```

### Cards

#### List all cards for a customer

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
print(ottu.cards.list(type="sandbox"))
```
### Get latest card for a customer

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
print(ottu.cards.get(type="sandbox"))
```

### Delete a card for a customer using token

```python
from ottu import Ottu

ottu = Ottu(
    host_url="https://sub.domain.com",
    api_key="your-secret-api-key",
    customer_id="your-customer-id"
)
print(ottu.cards.delete(type="sandbox", token="your-card-token"))
```
