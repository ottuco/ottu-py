from dataclasses import asdict


class AsDictMixin:
    def as_dict(self) -> dict:
        return asdict(self)  # type: ignore
