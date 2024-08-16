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

    def test_default_timeout(self, httpx_mock, auth_api_key):
        httpx_mock.add_response(
            url="https://test.ottu.dev/any/path",
            method="GET",
            status_code=200,
            json={"message": "success"},
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)
        ottu.send_request(path="/any/path", method="GET")
        request = httpx_mock.get_request()
        timeout = request.extensions.get("timeout", {})
        assert timeout == {"connect": 30, "pool": 30, "read": 30, "write": 30}

    def test_dynamic_timeout_via_constructor(self, httpx_mock, auth_api_key):
        httpx_mock.add_response(
            url="https://test.ottu.dev/any/path",
            method="GET",
            status_code=200,
            json={"message": "success"},
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key, timeout=23)
        ottu.send_request(path="/any/path", method="GET")
        request = httpx_mock.get_request()
        timeout = request.extensions.get("timeout", {})
        assert timeout == {"connect": 23, "pool": 23, "read": 23, "write": 23}

    def test_dynamic_timeout_via_cls_var(self, httpx_mock, auth_api_key):
        class CustomOttu(Ottu):
            default_timeout = 12

        httpx_mock.add_response(
            url="https://test.ottu.dev/any/path",
            method="GET",
            status_code=200,
            json={"message": "success"},
        )
        ottu = CustomOttu(merchant_id="test.ottu.dev", auth=auth_api_key)
        ottu.send_request(path="/any/path", method="GET")
        request = httpx_mock.get_request()
        timeout = request.extensions.get("timeout", {})
        assert timeout == {"connect": 12, "pool": 12, "read": 12, "write": 12}

    def test_timeout_all_in_one(self, httpx_mock, auth_api_key):
        class CustomOttu(Ottu):
            default_timeout = 12

        httpx_mock.add_response(
            url="https://test.ottu.dev/any/path",
            method="GET",
            status_code=200,
            json={"message": "success"},
        )
        ottu = CustomOttu(merchant_id="test.ottu.dev", auth=auth_api_key, timeout=22)
        ottu.send_request(path="/any/path", method="GET")
        request = httpx_mock.get_request()
        timeout = request.extensions.get("timeout", {})
        assert timeout == {"connect": 22, "pool": 22, "read": 22, "write": 22}
