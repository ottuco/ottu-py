from ..ottu import Ottu
from ..session import Session
from . import conf
from .models import Checkout


class DJSession(Session):
    def create(self, *args, **kwargs):
        if conf.WEBHOOK_URL and not kwargs.get("webhook_url"):
            kwargs["webhook_url"] = conf.WEBHOOK_URL
        return super().create(*args, **kwargs)


class DJOttu(Ottu):
    model = Checkout
    session_cls = DJSession

    def get_or_create_session(self):
        instance, _ = self.model.objects.get_or_create(
            session_id=self.session.session_id,
        )
        return instance

    def _create_or_update_dj_session(self):
        session_obj = self.get_or_create_session()
        for field, value in self.session.__dict__.items():
            setattr(session_obj, field, value)
        session_obj.save()

    def _update_session(self, session: Session):
        super()._update_session(session)
        self._create_or_update_dj_session()


dj_ottu = DJOttu(
    merchant_id=conf.MERCHANT_ID,
    username=conf.AUTH_USERNAME,
    password=conf.AUTH_PASSWORD,
    api_key=conf.AUTH_API_KEY,
)
