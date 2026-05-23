# gorest_api_tests/tests/functional/test_user_update_negative.py
import pytest
from src.api_client.gorest_client import GoRestClient
from src.models.user_models import User, UserUpdate
from src.models.error_models import ErrorResponse
from src.utils.data_generator import generate_unique_email

@pytest.mark.negative
class TestUserUpdateNegative:
    """
    Test suite for validating API's handling of invalid or conflicting updates
    to existing users (PATCH /users/{id}).
    """

    @pytest.mark.data_validation
    def test_update_user_invalid_status(self, gorest_client: GoRestClient, test_user: User):
        """
        Tests updating a user with an invalid status value. (TC-POST-004 logic re-used)
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        invalid_status = "pending"
        update_payload = {"status": invalid_status}
        print(f"\nAttempting to update user {test_user.id} with invalid status: {invalid_status}")

        response = gorest_client.patch(f"/users/{test_user.id}", payload=update_payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == "status" and ("can't be blank" in err.message or "can be active or inactive" in err.message) for err in error_response.root), \
            f"Expected 'status can't be blank/can be active or inactive' error, got {error_response.root}"
        print(f"Successfully caught invalid status update: {error_response.root}")

    @pytest.mark.data_validation
    def test_update_user_duplicate_email(self, gorest_client: GoRestClient, test_user: User, create_user_payload: dict, cleanup_user):
        """
        Tests updating a user's email to one that already exists for another user. (AC2.3 logic re-used)
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        # Create a second user to have a duplicate email
        second_user_payload = create_user_payload.copy()
        second_user_payload["email"] = generate_unique_email() # Ensure it's unique initially
        response_second_user = gorest_client.post("/users", payload=second_user_payload)
        assert response_second_user.status_code == 201, f"Failed to create second user: {response_second_user.text}"
        second_user_data = response_second_user.json().get("data") if "data" in response_second_user.json() else response_second_user.json()
        second_user = User.model_validate(second_user_data)
        cleanup_user(second_user.id) # Register second user for cleanup

        update_payload = UserUpdate(email=second_user.email).model_dump(exclude_unset=True)
        print(f"\nAttempting to update user {test_user.id} with duplicate email: {second_user.email}")

        response = gorest_client.patch(f"/users/{test_user.id}", payload=update_payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == "email" and "has already been taken" in err.message for err in error_response.root), \
            f"Expected 'email has already been taken' error, got {error_response.root}"
        print(f"Successfully caught duplicate email during update: {error_response.root}")

    def test_update_non_existent_user(self, gorest_client: GoRestClient, create_user_payload: dict):
        """
        Tests updating a user with a non-existent ID.
        Expects a 404 Not Found response.
        """
        non_existent_id = 999999999999999999 # A very large, unlikely ID
        update_payload = {"name": "Non Existent User Update"}
        print(f"\nAttempting to update non-existent user with ID: {non_existent_id}")

        response = gorest_client.patch(f"/users/{non_existent_id}", payload=update_payload)

        assert response.status_code == 404, \
            f"Expected status 404, got {response.status_code}. Response: {response.text}"
        assert "Resource not found" in response.text
        print(f"Successfully received 404 for updating non-existent user {non_existent_id}.")

    @pytest.mark.data_validation
    @pytest.mark.parametrize("field, value", [
        ("name", ""),
        ("email", ""),
        ("status", ""),
        ("gender", "")
    ])
    def test_update_user_empty_required_fields(self, gorest_client: GoRestClient, test_user: User, field: str, value: str):
        """
        Tests updating a user with empty string values for required fields.
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        update_payload = {field: value}
        print(f"\nAttempting to update user {test_user.id} with empty field '{field}': '{value}'")

        response = gorest_client.patch(f"/users/{test_user.id}", payload=update_payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == field and "can't be blank" in err.message for err in error_response.root), \
            f"Expected '{field} can't be blank' error, got {error_response.root}"
        print(f"Successfully caught empty required field '{field}' during update: {error_response.root}")
