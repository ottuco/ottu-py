import pytest

from ottu.auth import (
    APIKeyAuth,
    BasicAuth,
    BasicAuthorizationHeaderAuth,
    KeycloakClientAuth,
    KeycloakPasswordAuth,
    TokenAuth,
)
from ottu.ottu import Ottu


@pytest.mark.parametrize(
    "auth_instance, expected_header",
    [
        (
            BasicAuth(username="username", password="password"),
            "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
        ),
        (APIKeyAuth(api_key="U6cGFzc3dvcmQ"), "Api-Key U6cGFzc3dvcmQ"),
        (APIKeyAuth(api_key="U6cGFzc3dvcmQ", prefix="Custom"), "Custom U6cGFzc3dvcmQ"),
        (
            BasicAuthorizationHeaderAuth(header="Custom-Header: Custom-Value"),
            "Custom-Header: Custom-Value",
        ),
        (
            TokenAuth(token="1234", prefix="Bearer"),
            "Bearer 1234",
        ),
    ],
)
def test_auth(httpx_mock, auth_instance, expected_header):
    httpx_mock.add_response(
        url="https://test.ottu.dev/any/path",
        method="GET",
        status_code=200,
        json={"message": "success"},
    )
    ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_instance)
    ottu.send_request(path="/any/path", method="GET")
    request = httpx_mock.get_request()
    auth_header = request.headers.get("Authorization")
    assert auth_header == expected_header


class KCAuthTestMixin:
    def test_kc_auth(self, httpx_mock):
        httpx_mock.add_response(
            url="https://test.ottu.dev/api/v1/health-check/",
            method="GET",
            status_code=200,
            json={},
            match_headers={
                "Authorization": "Bearer 5223400d-8214-461c-ad6e-74af7bdf8061",
                "X-Service-ID": "test-realm",
            },
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


class TestKeycloakPasswordAuth1(KCAuthTestMixin):
    """
    `auth` doesn't have `client_secret` attribute
    """

    auth = KeycloakPasswordAuth(
        username="username",
        password="password",
        client_id="backend",
        host="ssolb.ottu.dev",
        realm="test-realm",
    )


class TestKeycloakPasswordAuth2(KCAuthTestMixin):
    """
    `auth` has `client_secret` attribute
    """

    auth = KeycloakPasswordAuth(
        username="username",
        password="password",
        client_id="backend",
        client_secret="8b603c51-5342-4ad6-b9e0-c9d4893a13d4",
        host="ssolb.ottu.dev",
        realm="test-realm",
    )


class TestKeycloakClientAuth(KCAuthTestMixin):
    auth = KeycloakClientAuth(
        client_id="backend",
        client_secret="8b603",
        host="ssolb.ottu.dev",
        realm="test-realm",
    )


class TestKCAuthCache(KCAuthTestMixin):
    auth = KeycloakClientAuth(
        client_id="backend",
        client_secret="8b603",
        host="ssolb.ottu.dev",
        realm="test-realm",
        caching=True,
    )
