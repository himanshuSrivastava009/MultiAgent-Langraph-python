# gorest_api_tests/tests/functional/test_user_crud.py
import pytest
from src.api_client.gorest_client import GoRestClient
from src.models.user_models import User, UserCreate, UserUpdate, Status
from src.utils.data_generator import generate_unique_email, generate_random_name

@pytest.mark.crud
class TestUserCRUD:
    """
    Test suite for validating the full CRUD (Create, Retrieve, Update, Delete)
    lifecycle for a user in the GoRest API.
    """

    def test_create_user_success(self, gorest_client: GoRestClient, create_user_payload: dict, cleanup_user):
        """
        Tests successful creation of a new user. (AC1.1)
        Verifies status code, response schema, and data integrity.
        """
        print(f"\nAttempting to create user with payload: {create_user_payload}")
        response = gorest_client.post("/users", payload=create_user_payload)
        print (response.text)
        assert response.status_code == 201, \
            f"Expected status 201, got {response.status_code}. Response: {response.text}"

        user_data = response.json().get("data") if "data" in response.json() else response.json()
        created_user = User.model_validate(user_data) # Validate response schema

        # Register the created user for cleanup after the test
        cleanup_user(created_user.id)

        # Assertions for data integrity
        assert created_user.name == create_user_payload["name"]
        assert created_user.email == create_user_payload["email"]
        assert created_user.gender.value == create_user_payload["gender"]
        assert created_user.status.value == create_user_payload["status"]
        assert created_user.id is not None and created_user.id > 0

        print(f"Successfully created user: {created_user.model_dump_json(indent=2)}")

    def test_get_user_success(self, gorest_client: GoRestClient, test_user: User):
        """
        Tests successful retrieval of an existing user by ID. (AC1.2)
        Verifies status code, response schema, and data integrity.
        """
        print(f"\nAttempting to retrieve user with ID: {test_user.id}")
        response = gorest_client.get(f"/users/{test_user.id}")

        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}. Response: {response.text}"

        user_data = response.json().get("data") if "data" in response.json() else response.json()
        retrieved_user = User.model_validate(user_data) # Validate response schema

        # Assertions for data integrity
        assert retrieved_user.id == test_user.id
        assert retrieved_user.name == test_user.name
        assert retrieved_user.email == test_user.email
        assert retrieved_user.gender == test_user.gender
        assert retrieved_user.status == test_user.status

        print(f"Successfully retrieved user: {retrieved_user.model_dump_json(indent=2)}")

    def test_update_user_status_success(self, gorest_client: GoRestClient, test_user: User):
        """
        Tests successful update of a user's status. (AC1.3)
        Verifies status code, response schema, and confirms update via a subsequent GET.
        """
        new_status = Status.INACTIVE
        update_payload = UserUpdate(status=new_status).model_dump(exclude_unset=True)
        print(f"\nAttempting to update user {test_user.id} with payload: {update_payload}")

        response = gorest_client.patch(f"/users/{test_user.id}", payload=update_payload)

        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}. Response: {response.text}"

        user_data = response.json().get("data") if "data" in response.json() else response.json()
        updated_user = User.model_validate(user_data) # Validate response schema

        assert updated_user.id == test_user.id
        assert updated_user.status == new_status
        print(f"Successfully updated user: {updated_user.model_dump_json(indent=2)}")

        # Verify the update with a subsequent GET request
        get_response = gorest_client.get(f"/users/{test_user.id}")
        assert get_response.status_code == 200, \
            f"Expected status 200 on GET after update, got {get_response.status_code}. Response: {get_response.text}"

        get_user_data = get_response.json().get("data") if "data" in get_response.json() else get_response.json()
        confirmed_user = User.model_validate(get_user_data)
        assert confirmed_user.status == new_status
        print(f"Confirmed user status is '{new_status.value}' after update.")

    def test_delete_user_success(self, gorest_client: GoRestClient, test_user: User):
        """
        Tests successful deletion of an existing user. (AC1.4)
        Verifies status code and confirms deletion via a subsequent GET.
        """
        user_id_to_delete = test_user.id
        print(f"\nAttempting to delete user with ID: {user_id_to_delete}")

        response = gorest_client.delete(f"/users/{user_id_to_delete}")

        assert response.status_code == 204, \
            f"Expected status 204, got {response.status_code}. Response: {response.text}"
        print(f"Successfully deleted user {user_id_to_delete}.")

        # Verify deletion with a subsequent GET request
        get_response = gorest_client.get(f"/users/{user_id_to_delete}")
        assert get_response.status_code == 404, \
            f"Expected status 404 after deletion, got {get_response.status_code}. Response: {get_response.text}"
        print(f"Confirmed user {user_id_to_delete} is no longer found (404).")
