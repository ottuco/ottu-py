from inspect import signature

from ottu import Ottu
from ottu.cards import Card


class TestOttuGetCards:
    def test_get_cards_signature(
        self,
        ottu_instance,
    ):
        parameters = dict(signature(Card.get_cards).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == set()
        assert optional_fields == {"agreement_id", "customer_id", "pg_codes", "type"}

    def test_list_signature(
        self,
        ottu_instance,
    ):
        parameters = dict(signature(Card.list).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == set()
        assert optional_fields == {"agreement_id", "customer_id", "pg_codes", "type"}

    def test_get_signature(
        self,
        ottu_instance,
    ):
        parameters = dict(signature(Card.get).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == set()
        assert optional_fields == {"agreement_id", "customer_id", "pg_codes", "type"}

    def test_delete_signature(
        self,
        ottu_instance,
    ):
        parameters = dict(signature(Card.delete).parameters)
        parameters.pop("self")
        required_fields = {
            name for name, param in parameters.items() if param.default is param.empty
        }
        optional_fields = set(parameters) - required_fields
        assert required_fields == {"token"}
        assert optional_fields == {"customer_id", "type"}

    def test_get_cards_200(
        self,
        httpx_mock,
        auth_api_key,
        response_user_cards,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = Card(ottu).get_cards()

        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": "/b/pbl/v2/card/",
            "error": {},
            "response": response_user_cards,
        }
        assert response == expected_response

    def test_get_cards_200_with_customer_id(
        self,
        httpx_mock,
        auth_api_key,
        response_user_cards,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = Card(ottu).get_cards(customer_id="test-id-123")

        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 200,
            "endpoint": "/b/pbl/v2/card/",
            "error": {},
            "response": response_user_cards,
        }
        assert response == expected_response

    def test_get_cards_non_200(
        self,
        httpx_mock,
        auth_api_key,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=502,
            json={"error": "Bad Gateway"},
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = Card(ottu).get_cards()

        # Assert the responses
        expected_response = {
            "success": False,
            "status_code": 502,
            "endpoint": "/b/pbl/v2/card/",
            "error": {"error": "Bad Gateway"},
            "response": {},
        }
        assert response == expected_response

    def test_get_single_card(
        self,
        httpx_mock,
        auth_api_key,
        response_user_cards,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=response_user_cards,
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = Card(ottu).get()

        # Assert the responses
        assert response == response_user_cards[0]

    def test_get_empty(
        self,
        httpx_mock,
        auth_api_key,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=200,
            json=[],
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = Card(ottu).get()

        # Assert the responses
        assert response is None

    def test_get_error(
        self,
        httpx_mock,
        auth_api_key,
    ):
        httpx_mock.add_response(
            url="https://test.ottu.dev/b/pbl/v2/card/",
            method="POST",
            status_code=502,
            json={"error": "Bad Gateway"},
        )
        ottu = Ottu(merchant_id="test.ottu.dev", auth=auth_api_key)

        # Make the request
        response = Card(ottu).get()

        # Assert the responses
        assert response is None

    def test_delete(
        self,
        httpx_mock,
        auth_api_key,
    ):
        token = "9918766711067353"
        httpx_mock.add_response(
            url=(
                f"https://test.ottu.dev/b/pbl/v2/card/{token}/"
                "?customer_id=test-customer-id&type=sandbox"
            ),
            method="DELETE",
            status_code=204,
            json={},
        )
        ottu = Ottu(
            merchant_id="test.ottu.dev",
            auth=auth_api_key,
            customer_id="test-customer-id",
        )

        # Make the request
        response = Card(ottu).delete(token=token)

        # Assert the responses
        expected_response = {
            "success": True,
            "status_code": 204,
            "endpoint": f"/b/pbl/v2/card/{token}/",
            "response": {},
            "error": {},
        }
        assert response == expected_response
