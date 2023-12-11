import httpx

from ottu import Ottu


class TestRequest:
    def test_process_response_json(self, httpx_mock, auth_basic):
        httpx_mock.add_response(
            url="https://test.ottu.dev/any/path",
            method="GET",
            status_code=200,
            json={"message": "success"},
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_basic)
        response = ottu.send_request(path="/any/path", method="GET")
        expected_response = {
            "endpoint": "/any/path",
            "error": {},
            "response": {"message": "success"},
            "status_code": 200,
            "success": True,
        }
        assert response.as_dict() == expected_response

    def test_process_response_text(self, httpx_mock, auth_basic):
        httpx_mock.add_response(
            url="https://test.ottu.dev/any/path",
            method="GET",
            status_code=200,
            text="this is text",
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_basic)
        response = ottu.send_request(path="/any/path", method="GET")
        expected_response = {
            "endpoint": "/any/path",
            "error": {},
            "response": {"detail": "this is text"},
            "status_code": 200,
            "success": True,
        }
        assert response.as_dict() == expected_response

    def test_process_httpx_error(self, mocker, auth_api_key):
        mocker.patch(
            "httpx._client.Client.request",
            side_effect=httpx.HTTPError("error"),
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)
        response = ottu.send_request(path="/any/path", method="GET")
        expected_response = {
            "endpoint": "/any/path",
            "error": {"detail": "error"},
            "response": {},
            "status_code": 500,
            "success": False,
        }
        assert response.as_dict() == expected_response

    def test_process_any_error(self, mocker, auth_api_key):
        mocker.patch("httpx._client.Client.request", side_effect=Exception("error"))
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)
        response = ottu.send_request(path="/any/path", method="GET")
        expected_response = {
            "endpoint": "/any/path",
            "error": {"detail": "error"},
            "response": {},
            "status_code": 500,
            "success": False,
        }
        assert response.as_dict() == expected_response
