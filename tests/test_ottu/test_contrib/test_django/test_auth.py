from django.core.cache import cache

from ottu.auth import BasicAuth, KeycloakClientAuth, KeycloakPasswordAuth
from ottu.ottu import Ottu


class KCAuthTestMixin:
    __test__ = False
    auth: BasicAuth
    match_headers: dict

    def teardown_method(self):
        cache.clear()

    def test_kc_auth(self, httpx_mock):
        httpx_mock.add_response(
            url="https://test.ottu.dev/api/v1/health-check/",
            method="GET",
            status_code=200,
            json={},
            match_headers=self.match_headers,
        )
        httpx_mock.add_response(
            url=(
                "https://ssolb.ottu.dev/auth/realms/"
                "test-realm/protocol/openid-connect/token"
            ),
            method="POST",
            status_code=200,
            json={
                "access_token": "5223400d-8214-461c-ad6e-74af7bdf8061",
                "expires_in": 300,
            },
        )

        ottu = Ottu(merchant_id="test.ottu.dev", auth=self.auth)
        response = ottu.send_request(path="/api/v1/health-check/", method="GET")
        assert response.status_code == 200

        # Make sure that the token is fetched from the cache
        response = ottu.send_request(path="/api/v1/health-check/", method="GET")
        assert response.status_code == 200


class TestKeycloakPasswordAuth1(KCAuthTestMixin):
    """
    `auth` doesn't have `client_secret` attribute
    """

    __test__ = True
    match_headers = {
        "Authorization": "Bearer 5223400d-8214-461c-ad6e-74af7bdf8061",
    }

    auth = KeycloakPasswordAuth(
        username="username",
        password="password",
        client_id="backend",
        host="ssolb.ottu.dev",
        realm="test-realm",
        caching=True,
    )


class TestKeycloakPasswordAuth2(KCAuthTestMixin):
    """
    `auth` has `client_secret` attribute
    """

    __test__ = True
    match_headers = {
        "Authorization": "Bearer 5223400d-8214-461c-ad6e-74af7bdf8061",
    }

    auth = KeycloakPasswordAuth(
        username="username",
        password="password",
        client_id="backend",
        client_secret="8b603c51-5342-4ad6-b9e0-c9d4893a13d4",
        host="ssolb.ottu.dev",
        realm="test-realm",
        caching=True,
    )


class TestKeycloakClientAuth(KCAuthTestMixin):
    __test__ = True
    match_headers = {
        "Authorization": "Bearer 5223400d-8214-461c-ad6e-74af7bdf8061",
        "X-Service-ID": "test-realm",
    }
    auth = KeycloakClientAuth(
        client_id="backend",
        client_secret="8b603c51-5342-4ad6-b9e0-c9d4893a13d4",
        host="ssolb.ottu.dev",
        realm="test-realm",
        caching=True,
    )
