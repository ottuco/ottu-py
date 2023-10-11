from enum import Enum


class HTTPMethod(str, Enum):
    """
    HTTP Methods
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class TxnType(str, Enum):
    """
    Transaction type
    """

    # Request from API, usually e-commerce
    E_COMMERCE = "e_commerce"

    # Merchant requests for a payment to somebody
    PAYMENT_REQUEST = "payment_request"
