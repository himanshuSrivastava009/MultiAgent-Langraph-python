# gorest_api_tests/tests/functional/test_user_retrieval_negative.py
import pytest
from src.api_client.gorest_client import GoRestClient

@pytest.mark.negative
class TestUserRetrievalNegative:
    """
    Test suite for validating API's handling of requests for non-existent users
    during retrieval (GET /users/{id}).
    """

    def test_get_non_existent_user(self, gorest_client: GoRestClient):
        """
        Tests retrieval of a user with a non-existent ID. (TC-GET-002)
        Expects a 404 Not Found response.
        """
        non_existent_id = 999999999999999999 # A very large, unlikely ID
        print(f"\nAttempting to retrieve non-existent user with ID: {non_existent_id}")

        response = gorest_client.get(f"/users/{non_existent_id}")

        assert response.status_code == 404, \
            f"Expected status 404, got {response.status_code}. Response: {response.text}"
        # GoRest API returns a simple "Resource not found" message for 404
        assert "Resource not found" in response.text
        print(f"Successfully received 404 for non-existent user {non_existent_id}.")

    @pytest.mark.parametrize("invalid_id", ["abc", "0", "-1", "1.5"])
    def test_get_user_invalid_id_format(self, gorest_client: GoRestClient, invalid_id: str):
        """
        Tests retrieval of a user with an invalid ID format (e.g., non-integer, zero, negative).
        GoRest API handles these as 404, 406, or 422 depending on internal routing.
        """
        print(f"\nAttempting to retrieve user with invalid ID format: {invalid_id}")

        response = gorest_client.get(f"/users/{invalid_id}")

        assert response.status_code in [404, 406, 422], \
            f"Expected status 404, 406, or 422, got {response.status_code}. Response: {response.text}"
        print(f"Successfully handled invalid ID format '{invalid_id}' with status {response.status_code}.")
