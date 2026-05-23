# gorest_api_tests/tests/conftest.py
import pytest
from src.api_client.gorest_client import GoRestClient
from src.api_client.config import BASE_URL, API_TOKEN
from src.models.user_models import User, UserCreate, UserUpdate, Gender, Status
from src.models.error_models import ErrorResponse
from src.utils.data_generator import generate_unique_user_payload, generate_unique_email, generate_random_name

@pytest.fixture(scope="session")
def gorest_client() -> GoRestClient:
    """
    Fixture to provide an authenticated GoRestClient instance for all tests.
    Scope: session ensures the client is initialized once per test run,
    improving efficiency by reusing the requests.Session.
    """
    print ("Himanshu1 - inside the conftest")
    return GoRestClient(base_url=BASE_URL, token=API_TOKEN)

@pytest.fixture
def create_user_payload() -> dict:
    """
    Fixture to generate a unique user payload for creation requests.
    Scope: function ensures a new, unique payload for each test function that uses it.
    """
    return generate_unique_user_payload()

@pytest.fixture
def cleanup_user(gorest_client: GoRestClient):
    """
    Fixture that provides a function to delete a user by ID.
    It collects user IDs during the test and performs cleanup in the teardown phase.
    This ensures data integrity and prevents test pollution. (NFR3)
    """
    user_ids_to_cleanup = []

    def _cleanup(user_id: int):
        """Registers a user ID for deletion after the test completes."""
        if user_id not in user_ids_to_cleanup:
            user_ids_to_cleanup.append(user_id)

    yield _cleanup # Provide the cleanup function to tests

    # Teardown: Delete all users registered for cleanup during the test function
    for user_id in user_ids_to_cleanup:
        print(f"\nCleaning up user with ID: {user_id}")
        response = gorest_client.delete(f"/users/{user_id}")
        # Assert cleanup success, but don't fail tests on cleanup failure
        # 204 No Content for successful deletion, 404 Not Found if already deleted
        assert response.status_code in [204, 404], \
            f"Failed to cleanup user {user_id}: {response.status_code} - {response.text}"

@pytest.fixture
def test_user(gorest_client: GoRestClient, create_user_payload: dict, cleanup_user) -> User:
    """
    Fixture to create a user before a test and ensure its deletion afterwards.
    This provides a clean, isolated user for tests requiring an existing user. (NFR3)
    """
    # Create user
    response = gorest_client.post("/users", payload=create_user_payload)
    assert response.status_code == 201, f"Failed to create test user: {response.text}"

    user_data = response.json().get("data") if "data" in response.json() else response.json()
    created_user = User.model_validate(user_data) # Validate response schema (AC1.1)

    # Register user for cleanup
    cleanup_user(created_user.id)

    yield created_user # Provide the created user (Pydantic model) to the test

    # Teardown is implicitly handled by the cleanup_user fixture
