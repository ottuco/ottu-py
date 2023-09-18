import base64
import typing

import httpx

from .enums import TxnType
from .errors import ConfigurationError
from .session import Session, SessionHandler


class Ottu:
    def __init__(
        self,
        host_url: str,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        api_key: typing.Optional[str] = None,
        customer_id: typing.Optional[str] = None,
    ) -> None:
        self.host_url = host_url
        self.username = username
        self.password = password
        self.api_key = api_key
        self.customer_id = customer_id

        # Validations
        self.__validate_init()

        # Other initializations
        self.request_session = self.__create_session()

    def __generate_auth_header(self) -> typing.Dict[str, str]:
        if self.api_key:
            value = f"Api-Key {self.api_key}"
        else:
            creds = base64.b64encode(
                f"{self.username}:{self.password}".encode(),
            ).decode("utf-8")
            value = f"Basic {creds}"
        return {"Authorization": value}

    def __create_session(self) -> httpx.Client:
        headers = {
            "Content-Type": "application/json",
            **self.__generate_auth_header(),
        }
        return httpx.Client(headers=headers)

    def __validate_init(self) -> None:
        self.__validate_auth_params()
        self.__validate_host_url()

    def __validate_host_url(self) -> None:
        """
        Validates host URL. URL must be
        1. https
        2. not end with /
        3. must contain domain name with protocol
            Example:
                1. https://example.com - Correct
                2. https://example.com/ - Incorrect
                3. https://example.com/anypath - Incorrect

        """
        msg_example = (
            "Example: `https://example.com`, "
            "but not `https://example.com/` or "
            "`https://example.com/anypath`"
        )
        if not self.host_url.startswith("https://"):
            msg = f"Host URL must start with https://. {msg_example}"
            raise ConfigurationError(msg)
        if self.host_url.endswith("/"):
            msg = f"Host URL must not end with /. {msg_example}"
            raise ConfigurationError(msg)
        if self.host_url.count("/") != 2:
            msg = f"Host URL must contain domain name with protocol. {msg_example}"
            raise ConfigurationError(msg)

    def __validate_auth_params(self) -> None:
        if self.api_key:
            # Authentication using API key, we don't need username and password
            if self.username or self.password:
                msg = (
                    "You are using API key for authentication, "
                    "username and password are not required"
                )
                raise ConfigurationError(msg)
        elif self.username and self.password:
            # Authentication using username and password, we don't need API key
            if self.api_key:
                msg = (
                    "You are using username and password "
                    "for authentication, API key is not required"
                )
                raise ConfigurationError(msg)
        else:
            msg = (
                "You must provide either API key or "
                "username and password for authentication"
            )
            raise ConfigurationError(msg)

    # Handle requests
    def send_request(
        self,
        path: str,
        method: str,
        **request_params,
    ) -> httpx.Response:
        func = getattr(self.request_session, method.lower())
        return func(
            url=f"{self.host_url}{path}",
            **request_params,
        )

    # Core Methods
    def checkout(
        self,
        txn_type: TxnType,
        amount: str,
        pg_codes: list[str],
        customer_id: typing.Optional[str] = None,
        customer_first_name: typing.Optional[str] = None,
        customer_last_name: typing.Optional[str] = None,
        **kwargs,
    ) -> Session:
        handler = SessionHandler(self)
        return handler.checkout(
            txn_type=txn_type,
            amount=amount,
            currency_code="KWD",
            pg_codes=pg_codes,
            customer_id=customer_id,
            customer_first_name=customer_first_name,
            customer_last_name=customer_last_name,
        )
