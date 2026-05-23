# gorest_api_tests/tests/security/test_authentication.py
import pytest
from src.api_client.gorest_client import GoRestClient
from src.models.user_models import User, UserUpdate, Status

@pytest.mark.security
class TestAuthentication:
    """
    Test suite for validating API's response to requests made without proper authentication.
    """

    def test_create_user_missing_auth_token(self, gorest_client: GoRestClient, create_user_payload: dict):
        """
        Tests user creation (POST /users) without an authentication token. (AC2.1)
        Expects a 401 Unauthorized response.
        """
        print(f"\nAttempting to create user without authentication.")
        response = gorest_client.post("/users", payload=create_user_payload, authenticated=False)

        assert response.status_code == 401, \
            f"Expected status 401, got {response.status_code}. Response: {response.text}"
        error_response = response.json()
        assert error_response.get("message") == "Authentication failed", \
            f"Expected 'Authentication failed' error, got {error_response}"
        print(f"Successfully received 401 Unauthorized for create without token: {error_response}")

    def test_get_user_missing_auth_token(self, gorest_client: GoRestClient, test_user: User):
        """
        Tests user retrieval (GET /users/{id}) without an authentication token.
        GoRest does not expose token-created users to unauthenticated requests.
        """
        print(f"\nAttempting to retrieve user {test_user.id} without authentication.")
        response = gorest_client.get(f"/users/{test_user.id}", authenticated=False)

        assert response.status_code == 404, \
            f"Expected status 404 for GET without auth, got {response.status_code}. Response: {response.text}"
        assert response.json().get("message") == "Resource not found"
        print(f"Successfully received 404 for unauthenticated retrieval of user {test_user.id}.")

    def test_update_user_missing_auth_token(self, gorest_client: GoRestClient, test_user: User):
        """
        Tests user update (PATCH /users/{id}) without an authentication token. (AC2.1)
        GoRest hides token-created users from unauthenticated requests.
        """
        update_payload = UserUpdate(status=Status.INACTIVE).model_dump(exclude_unset=True)
        print(f"\nAttempting to update user {test_user.id} without authentication.")
        response = gorest_client.patch(f"/users/{test_user.id}", payload=update_payload, authenticated=False)

        assert response.status_code == 404, \
            f"Expected status 404, got {response.status_code}. Response: {response.text}"
        assert response.json().get("message") == "Resource not found"
        print(f"Successfully received 404 for unauthenticated update of user {test_user.id}.")

    def test_delete_user_missing_auth_token(self, gorest_client: GoRestClient, test_user: User):
        """
        Tests user deletion (DELETE /users/{id}) without an authentication token. (AC2.1)
        GoRest hides token-created users from unauthenticated requests.
        """
        user_id_to_delete = test_user.id
        print(f"\nAttempting to delete user {user_id_to_delete} without authentication.")
        response = gorest_client.delete(f"/users/{user_id_to_delete}", authenticated=False)

        assert response.status_code == 404, \
            f"Expected status 404, got {response.status_code}. Response: {response.text}"
        assert response.json().get("message") == "Resource not found"
        print(f"Successfully received 404 for unauthenticated delete of user {user_id_to_delete}.")
