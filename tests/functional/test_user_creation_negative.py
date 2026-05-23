# gorest_api_tests/tests/functional/test_user_creation_negative.py
import pytest
from src.api_client.gorest_client import GoRestClient
from src.models.error_models import ErrorResponse
from src.utils.data_generator import generate_unique_email

@pytest.mark.negative
class TestUserCreationNegative:
    """
    Test suite for validating API's handling of invalid or duplicate input
    during user creation (POST /users).
    """

    @pytest.mark.data_validation
    @pytest.mark.parametrize("email_format", [
        "invalid-email",
        "user@.com",
        "@example.com",
        "user@",
        "user example.com"
    ])
    def test_create_user_invalid_email_format(self, gorest_client: GoRestClient, create_user_payload: dict, email_format: str):
        """
        Tests user creation with an invalid email format. (AC2.2, TC-POST-002)
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        payload = create_user_payload.copy()
        payload["email"] = email_format
        print(f"\nAttempting to create user with invalid email: {payload['email']}")

        response = gorest_client.post("/users", payload=payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == "email" and "is invalid" in err.message for err in error_response.root), \
            f"Expected 'email is invalid' error, got {error_response.root}"
        print(f"Successfully caught invalid email format: {error_response.root}")

    @pytest.mark.data_validation
    @pytest.mark.parametrize("gender_value", [
        "other",
        "unknown",
        "", # Empty string
        None # Null value
    ])
    def test_create_user_invalid_gender_value(self, gorest_client: GoRestClient, create_user_payload: dict, gender_value):
        """
        Tests user creation with an invalid gender value. (AC2.2, TC-POST-003)
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        payload = create_user_payload.copy()
        payload["gender"] = gender_value
        print(f"\nAttempting to create user with invalid gender: {payload['gender']}")

        response = gorest_client.post("/users", payload=payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == "gender" and ("can't be blank" in err.message or "can be male of female" in err.message) for err in error_response.root), \
            f"Expected 'gender can't be blank/can be male of female' error, got {error_response.root}"
        print(f"Successfully caught invalid gender value: {error_response.root}")

    @pytest.mark.data_validation
    def test_create_user_duplicate_email(self, gorest_client: GoRestClient, test_user, create_user_payload: dict):
        """
        Tests user creation with an email that already exists. (AC2.3, TC-POST-005)
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        payload = create_user_payload.copy()
        payload["email"] = test_user.email # Use an existing user's email
        print(f"\nAttempting to create user with duplicate email: {payload['email']}")

        response = gorest_client.post("/users", payload=payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == "email" and "has already been taken" in err.message for err in error_response.root), \
            f"Expected 'email has already been taken' error, got {error_response.root}"
        print(f"Successfully caught duplicate email: {error_response.root}")

    @pytest.mark.data_validation
    @pytest.mark.parametrize("missing_field", ["name", "email", "gender", "status"])
    def test_create_user_missing_required_fields(self, gorest_client: GoRestClient, create_user_payload: dict, missing_field: str):
        """
        Tests user creation with a missing required field. (TC-POST-006)
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        payload = create_user_payload.copy()
        del payload[missing_field]
        print(f"\nAttempting to create user with missing field: {missing_field}")

        response = gorest_client.post("/users", payload=payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == missing_field and "can't be blank" in err.message for err in error_response.root), \
            f"Expected '{missing_field} can't be blank' error, got {error_response.root}"
        print(f"Successfully caught missing required field '{missing_field}': {error_response.root}")

    @pytest.mark.data_validation
    @pytest.mark.parametrize("field, value", [
        ("name", ""),
        ("email", ""),
        ("status", ""),
        ("gender", "")
    ])
    def test_create_user_empty_required_fields(self, gorest_client: GoRestClient, create_user_payload: dict, field: str, value: str):
        """
        Tests user creation with empty string values for required fields. (TC-POST-007)
        Expects a 422 Unprocessable Entity response with a specific error message.
        """
        payload = create_user_payload.copy()
        payload[field] = value
        print(f"\nAttempting to create user with empty field '{field}': '{value}'")

        response = gorest_client.post("/users", payload=payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"
        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == field and "can't be blank" in err.message for err in error_response.root), \
            f"Expected '{field} can't be blank' error, got {error_response.root}"
        print(f"Successfully caught empty required field '{field}': {error_response.root}")

    @pytest.mark.boundary
    @pytest.mark.data_validation
    def test_create_user_long_string_values(self, gorest_client: GoRestClient, create_user_payload: dict):
        """
        Tests user creation with very long string values for name and email. (TC-POST-008)
        GoRest enforces a 200 character limit for name and email.
        """
        long_name = "A" * 256 # Very long name
        long_email = f"longemail{'B' * 200}@{generate_unique_email().split('@')[1]}" # Very long email
        payload = create_user_payload.copy()
        payload["name"] = long_name
        payload["email"] = long_email
        print(f"\nAttempting to create user with long name ({len(long_name)}) and email ({len(long_email)})")

        response = gorest_client.post("/users", payload=payload)

        assert response.status_code == 422, \
            f"Expected status 422, got {response.status_code}. Response: {response.text}"

        error_response = ErrorResponse.model_validate(response.json())
        assert any(err.field == "name" and "too long" in err.message for err in error_response.root), \
            f"Expected name length error, got {error_response.root}"
        assert any(err.field == "email" and "too long" in err.message for err in error_response.root), \
            f"Expected email length error, got {error_response.root}"
        print(f"Caught expected length validation error for long strings: {error_response.root}")
