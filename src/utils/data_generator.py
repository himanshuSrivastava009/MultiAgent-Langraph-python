# gorest_api_tests/src/utils/data_generator.py
from faker import Faker
from src.models.user_models import Gender, Status
import random
import time

# Initialize Faker for generating realistic-looking data
fake = Faker()

def generate_unique_email() -> str:
    """
    Generates a unique email address using a timestamp and a UUID.
    This helps prevent conflicts when creating multiple users in tests.
    """
    timestamp = int(time.time() * 1000) # Millisecond timestamp for uniqueness
    return f"testuser_{timestamp}_{fake.uuid4()}@example.com"

def generate_random_name() -> str:
    """
    Generates a random full name.
    """
    return fake.name()

def get_random_gender() -> Gender:
    """
    Returns a random gender from the Gender enum.
    """
    return random.choice([Gender.MALE, Gender.FEMALE])

def get_random_status() -> Status:
    """
    Returns a random status from the Status enum.
    """
    return random.choice([Status.ACTIVE, Status.INACTIVE])

def generate_unique_user_payload() -> dict:
    """
    Generates a dictionary representing a unique and valid user creation payload.
    """
    return {
        "name": generate_random_name(),
        "email": generate_unique_email(),
        "gender": get_random_gender().value, # .value to get the string representation
        "status": get_random_status().value, # .value to get the string representation
    }
