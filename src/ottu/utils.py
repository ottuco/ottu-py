import hashlib
import hmac


def remove_empty_values(d: dict):
    """
    Removes empty values from a dictionary.
    """
    return {k: v for k, v in d.items() if v}


def verify_signature(
    payload: dict,
    signature: str,
    webhook_key: str,
) -> bool:
    calculated_signature = calculate_hmac_signature(
        payload=payload,
        hmac_key=webhook_key,
    )
    return calculated_signature == signature


def calculate_hmac_signature(payload: dict, hmac_key: str) -> str:
    # List of fields that are considered for the HMAC signature
    keys = [
        "amount",
        "currency_code",
        "customer_first_name",
        "customer_last_name",
        "customer_email",
        "customer_phone",
        "customer_address_line1",
        "customer_address_line2",
        "customer_address_city",
        "customer_address_state",
        "customer_address_country",
        "customer_address_postal_code",
        "gateway_name",
        "gateway_account",
        "order_no",
        "reference_number",
        "result",
        "state",
    ]

    # Extract and sort the payload keys based on the 'keys' list,
    # and ignore any missing or empty string values
    message = [(k, payload[k]) for k in sorted(payload) if k in keys and payload[k]]

    # Concatenate the key-value pairs
    message_str = "".join([f"{k}{v}" for (k, v) in message])

    # Compute the HMAC signature
    digest = hmac.new(
        bytes(hmac_key, encoding="utf8"),
        bytes(message_str, encoding="utf8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return digest
