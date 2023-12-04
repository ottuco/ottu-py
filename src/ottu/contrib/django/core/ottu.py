from ....auth import APIKeyAuth, BasicAuth
from ....ottu import Ottu as _Ottu
from .. import conf
from ..models import Checkout
from .session import Session


class Ottu(_Ottu):
    model = Checkout
    session_cls = Session

    def get_or_create_session(self):
        instance, _ = self.model.objects.get_or_create(
            session_id=self.session.session_id,
        )
        return instance

    def _create_or_update_dj_session(self):
        session_obj = self.get_or_create_session()
        for field, value in self.session.as_dict().items():
            setattr(session_obj, field, value)
        session_obj.save()

    def _update_session(self, session: Session):  # type: ignore[override]
        super()._update_session(session)
        self._create_or_update_dj_session()


basic_auth = BasicAuth(username=conf.AUTH_USERNAME, password=conf.AUTH_PASSWORD)
api_key_auth = APIKeyAuth(api_key=conf.AUTH_API_KEY)


def _generate_instance():
    return Ottu(
        merchant_id=conf.MERCHANT_ID,
        auth=basic_auth or api_key_auth,
        is_sandbox=conf.IS_SANDBOX,
    )


ottu = _generate_instance()
