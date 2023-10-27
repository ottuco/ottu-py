import typing

from ottu import urls

from .enums import HTTPMethod
from .request import OttuPYResponse
from .utils import remove_empty_values

if typing.TYPE_CHECKING:
    from .ottu import Ottu


class Card:
    def __init__(self, ottu: "Ottu"):
        self.ottu = ottu

    def _get_cards(
        self,
        type: str = "sandbox",
        customer_id: typing.Optional[str] = None,
        pg_codes: typing.Optional[list] = None,
        agreement_id: typing.Optional[str] = None,
    ) -> OttuPYResponse:
        if customer_id is None:
            customer_id = self.ottu.customer_id
        payload = {
            "type": type,
            "customer_id": customer_id,
            "pg_codes": pg_codes,
            "agreement_id": agreement_id,
        }
        payload = remove_empty_values(payload)
        return self.ottu.send_request(
            path=urls.USER_CARDS,
            method=HTTPMethod.POST,
            json=payload,
        )

    def get_cards(
        self,
        type: str = "sandbox",
        customer_id: typing.Optional[str] = None,
        pg_codes: typing.Optional[list] = None,
        agreement_id: typing.Optional[str] = None,
    ) -> dict:
        ottu_py_response = self._get_cards(
            type=type,
            customer_id=customer_id,
            pg_codes=pg_codes,
            agreement_id=agreement_id,
        )
        return ottu_py_response.as_dict()

    def get(
        self,
        type: str = "sandbox",
        customer_id: typing.Optional[str] = None,
        pg_codes: typing.Optional[list] = None,
        agreement_id: typing.Optional[str] = None,
    ) -> typing.Optional[dict]:
        ottu_py_response = self._get_cards(
            type=type,
            customer_id=customer_id,
            pg_codes=pg_codes,
            agreement_id=agreement_id,
        )
        if ottu_py_response.success:
            try:
                return ottu_py_response.response[0]
            except IndexError:
                pass
        return None

    def list(
        self,
        type: str = "sandbox",
        customer_id: typing.Optional[str] = None,
        pg_codes: typing.Optional[list] = None,
        agreement_id: typing.Optional[str] = None,
    ) -> dict:
        return self.get_cards(
            type=type,
            customer_id=customer_id,
            pg_codes=pg_codes,
            agreement_id=agreement_id,
        )

    def delete(
        self,
        token: str,
        type: str = "sandbox",
        customer_id: typing.Optional[str] = None,
    ) -> dict:
        customer_id = customer_id or self.ottu.customer_id
        ottu_py_response = self.ottu.send_request(
            path=f"{urls.USER_CARDS}{token}/",
            method=HTTPMethod.DELETE,
            params={
                "customer_id": customer_id,
                "type": type,
            },
        )
        return ottu_py_response.as_dict()
