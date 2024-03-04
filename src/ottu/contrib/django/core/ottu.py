from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

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


def _generate_instance():
    try:
        auth_conf = conf.AUTH.copy()
        auth_cls = import_string(auth_conf["class"])
    except AttributeError:
        raise ImproperlyConfigured(
            "Must set `OTTU_AUTH` in the settings file",
        )
    except KeyError:
        raise ImproperlyConfigured(
            "The 'class' key is required in the 'AUTH' dictionary",
        )
    except ImportError:
        raise ImproperlyConfigured("The 'class' key is not a valid import path")
    auth_conf.pop("class")
    auth_instance = auth_cls(**auth_conf)
    return Ottu(
        merchant_id=conf.MERCHANT_ID,
        auth=auth_instance,
        is_sandbox=conf.IS_SANDBOX,
    )


ottu = _generate_instance()
