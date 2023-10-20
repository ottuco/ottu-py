import typing

from .enums import HTTPMethod

if typing.TYPE_CHECKING:
    from .ottu import Ottu


class TokenizedCard:
    customer_id: str
    brand: str
    name_on_the_card: str
    number: str
    expiry_month: str
    expiry_year: str
    token: str
    pg_code: str
    is_preferred: bool
    is_expired: bool
    will_expire_soon: bool
    can_be_charged_offline: bool
    cvv_required: bool

    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)

    def __str__(self):
        return f"<{self.__class__.__name__}({self.customer_id} - {self.number})>"

    def __repr__(self):
        return str(self)


class Card:
    url_card_list = "/b/pbl/v2/card/"
    _cards: list[TokenizedCard] = []

    def __init__(self, ottu: "Ottu"):
        self.ottu = ottu

    def _get_cards(self, type: str = "sandbox") -> None:
        ottu_py_response = self.ottu.send_request(
            path=self.url_card_list,
            method=HTTPMethod.GET,
            params={
                "customer_id": self.ottu.customer_id,
                "type": type,
            },
        )
        self._cards = [TokenizedCard(**card) for card in ottu_py_response.response]

    def get_cards(
        self,
        type: str = "sandbox",
        refresh: bool = False,
    ) -> list[TokenizedCard]:
        if refresh or self._cards is None:
            self._get_cards(type=type)
        return self._cards

    def list(self, type: str = "sandbox", refresh: bool = False) -> list[TokenizedCard]:
        return self.get_cards(type=type, refresh=refresh)

    def get(
        self,
        type: str = "sandbox",
        refresh: bool = False,
    ) -> typing.Optional[TokenizedCard]:
        cards = self.list(type=type, refresh=refresh)
        try:
            return cards[0]
        except IndexError:
            return None

    def delete(self, token: str, type: str = "sandbox"):
        for card in self._cards:
            if card.token == token:
                response = self.ottu.send_request(
                    path=f"{self.url_card_list}{card.token}/",
                    method=HTTPMethod.DELETE,
                    params={
                        "customer_id": self.ottu.customer_id,
                        "type": type,
                    },
                )
                self.get_cards()
                return response
