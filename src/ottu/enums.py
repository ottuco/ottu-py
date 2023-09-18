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

    # Identically as Payment requests, but with different config
    # ie: different mail/sms, default email. Sole purpose of this duplicate
    # is for the merchant to be able to define different configs
    BULK = "bulk"

    # Merchant market and sells single product
    CATALOGUE = "catalogue"

    # Customer pays by himself an amount to the merchant
    CUSTOMER_PAYMENT = "customer_payment"

    # Similar to e-commerce, but from third party providers
    # through plugins. IE: Shopify and Air Cairo
    SHOPIFY = "shopify"

    # Event management and booking
    EVENT = "event"

    # Food ordering
    FOOD_ORDERING = "food_ordering"

    # Basically the same as e-commerce but only related to flight tickets from iata
    IATA = "iata"

    # Real Estate
    REAL_ESTATE = "real_estate"
