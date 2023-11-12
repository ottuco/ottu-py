import pytest

from ottu.auth import APIKeyAuth, BasicAuth
from ottu.ottu import Ottu


@pytest.mark.parametrize(
    "auth_instance, expected_header",
    [
        (
            BasicAuth(username="username", password="password"),
            "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
        ),
        (APIKeyAuth(api_key="U6cGFzc3dvcmQ"), "Api-Key U6cGFzc3dvcmQ"),
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
