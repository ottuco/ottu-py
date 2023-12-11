import json
from typing import Any

from .session import PaymentMethod


class PaymentMethodEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, PaymentMethod):
            return o.as_dict()
        return json.JSONEncoder.default(self, o)
